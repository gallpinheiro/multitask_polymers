import torch
import torch.nn.functional as F

from torch_geometric.nn import GINConv, MLP
from torch_geometric.utils import scatter, softmax


class Net(torch.nn.Module):

    def __init__(self, input_feat, hidden_channels, out_channels, dropout):
        super(Net, self).__init__()

        self.hidden_channels = hidden_channels
        self.encoder = torch.nn.ModuleList()
        for _ in range(3):
            mlp = MLP([input_feat, hidden_channels, hidden_channels], norm=None)
            self.encoder.append(GINConv(nn=mlp, train_eps=False))
            input_feat = hidden_channels

        self.fc_q = torch.nn.Linear(hidden_channels, hidden_channels)
        self.fc_k = torch.nn.Linear(hidden_channels, hidden_channels)
        self.fc_v = torch.nn.Linear(hidden_channels, hidden_channels)

        self.dropout = torch.nn.Dropout(dropout)

        self.outputs = torch.nn.ModuleList()
        for task_id in range(out_channels):
            self.outputs.append(
                torch.nn.Sequential(
                    torch.nn.Linear(hidden_channels + int(task_id in [13, 23, 35, 36, 37]), hidden_channels),
                    torch.nn.ReLU(),
                    torch.nn.Linear(hidden_channels, 1)
                )
            )

        # self.init_emb()

    def init_emb(self):
        for m in self.modules():
            if isinstance(m, torch.nn.Linear):
                torch.nn.init.xavier_uniform_(m.weight.data)
                if m.bias is not None:
                    m.bias.data.fill_(0.0)

    def forward(self, loader, task_id):

        x = loader.x
        fractions = loader.ratio.unsqueeze(1)
        _, monomer = torch.unique_consecutive(
            loader.monomer_id,
            return_inverse=True
        )

        # message-passing
        for conv in self.encoder:
            x = conv(x, loader.edge_index).relu()

        monomer_emb = scatter(x, monomer, reduce='mean')
        monomer_fraction = scatter(fractions, monomer, reduce='min')

        q = self.fc_q(monomer_emb) * monomer_fraction
        v = self.fc_v(monomer_emb)
        k = self.fc_k(monomer_emb) * monomer_fraction
        batch_index = scatter(loader.batch, monomer, reduce='min')
        k = scatter(k, batch_index, reduce='sum')
        energy = (q * k[batch_index]) / (self.hidden_channels ** .5)
        attention = softmax(energy, batch_index)

        polymer_embedding = v * attention

        # polymer-level readout
        polymer_embedding = scatter(polymer_embedding, batch_index, reduce='sum')
        polymer_embedding = self.dropout(polymer_embedding)
        if task_id in [13, 23, 35, 36, 37]:
            polymer_embedding = torch.cat((polymer_embedding, loader.feats), dim=1)

        return self.outputs[task_id](polymer_embedding).squeeze(1)


def train(task_id, task_count, task_iter_train, task_dataloader_train, model, device):

    model.train()
    if task_count[task_id] % len(task_dataloader_train[task_id]) == 0:
        task_iter_train[task_id] = iter(task_dataloader_train[task_id])
    task_count[task_id] += 1

    batch = next(task_iter_train[task_id])
    predictions = model(batch.to(device), task_id)
    return F.mse_loss(predictions, batch.y)

def evaluation(
    train_loader, val_loader, test_loader, task_id, model, epochId,
    step, max_num_iter, rep, lr, std, device, seed, output,
    best_val, norm_test_loss, test_loss
):

    @torch.no_grad()
    def predict(dataloader):
        batch_size = 0
        loss, znorm_loss = 0, 0
        model.eval()
        for batch in dataloader:
            predictions = model(batch.to(device), task_id)
            loss += (predictions * std[task_id] - batch.y * std[task_id]).abs().sum().item()
            znorm_loss += (predictions - batch.y).abs().sum().item()
            batch_size += batch.y.size(0)
        model.train()
        return float(znorm_loss) / batch_size, float(loss) / batch_size

    norm_val_loss, val_loss = predict(val_loader[task_id])
    norm_train_loss, train_loss = predict(train_loader[task_id])

    if best_val is None or val_loss <= best_val:
        model_path = output / 'best_model_epoch_{}_step_{}_rep_{}.pth'.format(epochId, step, rep)
        torch.save(model.state_dict(), model_path)
        best_val = val_loss
        norm_test_loss, test_loss = predict(test_loader[task_id])

    with open(output / 'history.txt', 'a') as f:
        f.write('Epoch: {:03d}, Step: {:04d}/{:04d}, Rep: {:02d} - Task id {:02d}, LR: {:7f}, Loss (Norm/Real): {:.7f}/{:.7f}, Val Loss (Norm/Real): {:.7f}/{:.7f}, Test Loss (Norm/Real): {:.7f}/{:.7f}\n'.format(
            epochId, step, max_num_iter, rep, task_id, lr,
            norm_train_loss, train_loss,
            norm_val_loss, val_loss,
            norm_test_loss, test_loss
        ))
    return best_val, norm_test_loss, test_loss
