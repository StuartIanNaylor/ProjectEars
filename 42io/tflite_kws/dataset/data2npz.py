import numpy as np
data = np.loadtxt('kws.data', dtype='float32')

# 10 KW + Noise + Unknown
#x_train = data[data[:,0] < 12][:,1:]
#y_train = data[data[:,0] < 12][:,0]
#x_test  = data[data[:,0] > 23][:,1:]
#y_test  = data[data[:,0] > 23][:,0] - 24
#x_valid = data[len(x_train):-len(x_test)][:,1:]
#y_valid = data[len(y_train):-len(y_test)][:,0] - 12

# 1 KW + Noise + Unknown
#x_train = data[data[:,0] < 3][:,1:]
#y_train = data[data[:,0] < 3][:,0]
#x_test  = data[data[:,0] > 5][:,1:]
#y_test  = data[data[:,0] > 5][:,0] - 6
#x_valid = data[len(x_train):-len(x_test)][:,1:]
#y_valid = data[len(y_train):-len(y_test)][:,0] - 3

# 5 KW + Noise + Unknown
x_train = data[data[:,0] < 7][:,1:]
y_train = data[data[:,0] < 7][:,0]
x_test  = data[data[:,0] > 13][:,1:]
y_test  = data[data[:,0] > 13][:,0] - 14
x_valid = data[len(x_train):-len(x_test)][:,1:]
y_valid = data[len(y_train):-len(y_test)][:,0] - 7


print(np.shape(data))
np.savez_compressed('kws.npz',
                    x_train = x_train, y_train = y_train,
                    x_test  = x_test,  y_test  = y_test,
                    x_valid = x_valid, y_valid = y_valid)
