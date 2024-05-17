import numpy as np


from sklearn.model_selection import KFold

def get_indices(k):

    val_idx = np.arange(k)
    test_idx = (val_idx + 1) % k

    train_idx = np.arange(k)
    train_idx = np.vstack([np.setdiff1d(train_idx, (test_idx[i], val_idx[i])) for i in range(k)])

    return train_idx, val_idx, test_idx


def get_folds(n_samples, k, random_state):

    kf = KFold(n_splits=k, shuffle=True, random_state=random_state)    
    indices = np.arange(n_samples)

    return [fold for _, fold in kf.split(indices)]
