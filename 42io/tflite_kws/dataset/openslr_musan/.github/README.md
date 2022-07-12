### Download features for openslr musan + google speech commands 0-9

    ~$ apt install gcc lrzip wget
    ~$ wget https://github.com/42io/dataset/releases/download/v1.0/musan.lrz
    ~$ lrunzip musan.lrz -o musan.data # md5 f782c905cdba015527d570941d1d4ca6
    ~$ wget https://github.com/42io/dataset/releases/download/v1.0/0-9up.lrz
    ~$ lrunzip 0-9up.lrz -o 0-9up.data # md5 87fc2460c7b6cd3dcca6807e9de78833

### NumPy example

Slow:

    import numpy as np

    data = np.loadtxt('0-9up.data', dtype='float32')
    x_train = data[data[:,0] < 12][:,1:]
    y_train = data[data[:,0] < 12][:,0]
    x_test  = data[data[:,0] > 23][:,1:]
    y_test  = data[data[:,0] > 23][:,0] - 24
    x_valid = data[len(x_train):-len(x_test)][:,1:]
    y_valid = data[len(y_train):-len(y_test)][:,0] - 12
    x_train = x_train[y_train < 10]
    x_valid = x_valid[y_valid < 10]
    x_test  = x_test[y_test < 10]
    y_train, y_valid, y_test = [len(x_train), len(x_valid), len(x_test)]

    data = np.loadtxt('musan.data', dtype='float32')
    x_train = np.concatenate([x_train, data[:y_train]])
    x_valid = np.concatenate([x_valid, data[y_train:y_train + y_valid]])
    x_test  = np.concatenate([x_test , data[y_train + y_valid:y_train + y_valid + y_test]])
    y_train = np.concatenate([np.full(y_train, True), np.full(y_train, False)])
    y_valid = np.concatenate([np.full(y_valid, True), np.full(y_valid, False)])
    y_test  = np.concatenate([np.full(y_test , True), np.full(y_test , False)])

    np.savez_compressed('musan-0-9up.npz',
                        x_train = x_train, y_train = y_train,
                        x_test  = x_test,  y_test  = y_test,
                        x_valid = x_valid, y_valid = y_valid)

Fast:

    import numpy as np
    dset = np.load('musan-0-9up.npz') # md5 3a65d6a64314e5c343ae52997d078ace
    print(dset.files)