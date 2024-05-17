import os
import random
import shutil


import numpy as np
import torch
from pathlib import Path
from torch_geometric.loader import DataLoader

from arguments import arg_parse
from data import *
from model import *
from kfold import *


def seed_everything(seed=1234):
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


if __name__ == '__main__':

    args = arg_parse()
    seed = args.seed
    device = torch.device(args.device)
    epochs = args.epochs
    lr = args.lr
    batch_size = args.batch_size
    dropout = args.dropout
    weight_decay = args.weight_decay
    hidden_channels = args.hidden_channels
    target_task = args.target_task

    seed_everything(seed)
    if target_task < 35:
        raise ValueError('Target task ID should be greater than or equal to 35.')

    test_loader = [[] for _ in range(47)]
    val_loader = [[] for _ in range(47)]
    train_loader = [[] for _ in range(47)]
    aux_tasks = np.arange(47)
    aux_tasks = aux_tasks[aux_tasks != target_task]
    if target_task == 40: # CO2/N2 Selectivity
        aux_tasks = aux_tasks[aux_tasks != 42] # N2 permeability
        aux_tasks = aux_tasks[aux_tasks != 43] # CO2 permeability
    elif target_task == 41: # CO2/CH4 Selectivity
        aux_tasks = aux_tasks[aux_tasks != 43] # CO2 permeability
        aux_tasks = aux_tasks[aux_tasks != 44] # CH4 permeability
    elif target_task == 42: # N2 permeability
        aux_tasks = aux_tasks[aux_tasks != 40] # CO2/N2 Selectivity
    elif target_task == 43: # CO2 permeability
        aux_tasks = aux_tasks[aux_tasks != 40] # CO2/N2 Selectivity
        aux_tasks = aux_tasks[aux_tasks != 41] # CO2/CH4 Selectivity
    elif target_task == 44: # CH4 permeability
        aux_tasks = aux_tasks[aux_tasks != 41] # CO2/CH4 Selectivity

    num_of_aux_task = len(aux_tasks)
    std = torch.zeros(47)
    tasks = np.empty(num_of_aux_task * 2, dtype=int)
    tasks[1::2] = np.full(num_of_aux_task, target_task)

    # train/val splits.
    for i in aux_tasks:
        dataset = Polymers('datasets/dataset{}'.format(i), i)

        # Split datasets.
        nsamples = len(dataset) // 10
        mean = dataset[nsamples:].y.mean(dim=0, keepdim=True)
        std[i] = dataset[nsamples:].y.std(dim=0, keepdim=True)
        dataset._data.y = (dataset._data.y - mean) / std[i]
        if i in [13, 23, 35, 36, 37]:
            feats_mean = dataset[nsamples:].feats.mean(dim=0, keepdim=True)
            feats_std = dataset[nsamples:].feats.std(dim=0, keepdim=True)
            dataset._data.feats = (dataset._data.feats - feats_mean) / feats_std

        val_loader[i] = DataLoader(dataset[:nsamples], batch_size=batch_size, shuffle=False)
        train_loader[i] = DataLoader(dataset[nsamples:], batch_size=batch_size if len(dataset[nsamples:]) > 1000 else len(dataset[nsamples:]), shuffle=True)

    # k-fold split.
    k = 10
    dataset = Polymers('datasets/dataset{}'.format(target_task), target_task)
    folds = get_folds(n_samples=len(dataset), k=k, random_state=seed)
    train_fold_idx, val_fold_idx, test_fold_idx = get_indices(k=k)

    test_fold_idx = [folds[test_fold_idx[fold_id]] for fold_id in range(k)]
    val_fold_idx = [folds[val_fold_idx[fold_id]] for fold_id in range(k)]
    train_fold_idx = [np.hstack([folds[i] for i in train_fold_idx[fold_id]]) for fold_id in range(k)]

    has_features = target_task in [13, 23, 35, 36, 37]
    for fold_id in range(k):

        output = '{}_fold_{}_dropout_{}_target_task_{}'.format(
            args.output, fold_id, dropout, target_task
        )
        output = Path(output)
        if output.exists():
            shutil.rmtree(output)
        output.mkdir(parents=True)

        std = std.to('cpu')
        dataset = Polymers('datasets/dataset{}'.format(target_task), target_task)

        test_index = test_fold_idx[fold_id] # return the training idx for this specific task (i) and fold (fold_id)
        val_index = val_fold_idx[fold_id] # return the training idx
        train_index = train_fold_idx[fold_id] # return the training idx

        # standardizing experimental target
        mean = dataset[train_index].y.mean(dim=0, keepdim=True)
        std[target_task] = dataset[train_index].y.std(dim=0, keepdim=True)
        dataset._data.y = (dataset._data.y - mean) / std[target_task]
        if has_features:
            feats_mean = dataset[train_index].feats.mean(dim=0, keepdim=True)
            feats_std = dataset[train_index].feats.std(dim=0, keepdim=True)
            dataset._data.feats = (dataset._data.feats - feats_mean) / feats_std

        test_loader[target_task] = DataLoader(dataset[test_index], batch_size=batch_size, shuffle=False)
        val_loader[target_task] = DataLoader(dataset[val_index], batch_size=batch_size, shuffle=False)
        train_loader[target_task] = DataLoader(dataset[train_index], batch_size=len(dataset[train_index]), shuffle=True)
        std = std.to(device)

        # training process starts here
        num_features = dataset[0].x.shape[1]
        num_outputs = len(train_loader)

        model = Net(num_features, hidden_channels, num_outputs, dropout)
        model.to(device)

        task_num_iters = [len(train) for train in train_loader]
        task_ave_iter_list = sorted(task_num_iters)
        max_num_iter = task_ave_iter_list[-1]
        task_iter_train = {i: None for i in range(num_outputs)}
        task_count = {i: 0 for i in range(num_outputs)}

        optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

        best_val = None
        norm_test_loss = None
        test_loss = None
        for epochId in range(0, epochs):
            model.train()
            for step in range(max_num_iter):
                tasks[0::2] = np.random.permutation(aux_tasks)
                rep = 0
                for task_id in tasks:
                    loss = train(task_id, task_count, task_iter_train, train_loader, model, device)
                    loss.backward()
                    optimizer.step()
                    model.zero_grad()
                    if (task_id == target_task) and (task_count[task_id] % len(train_loader[task_id]) == 0):
                        best_val, norm_test_loss, test_loss = evaluation(
                            train_loader, val_loader, test_loader, target_task, model, epochId, step, max_num_iter, rep,
                            lr, std, device, seed, output,
                            best_val, norm_test_loss, test_loss
                        )
                        rep += 1
