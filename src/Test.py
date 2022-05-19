import numpy as np
import time

begin = time.time()
a = np.arange(4*13).reshape(4,13)
print(a.shape)
print(a)
print(np.sum(a[:,:2], axis = 0))
print(a[:,:2])
print(a[:,2+1:])

#a = np.array([[0,12,2,3,4,5],[0,12,2,3,4,5],[0,13,2,3,4,5]])
print(a)
for ii in range(a.shape[1]):
    print(a[:,np.arange(a.shape[1]) != ii])