import numpy as np

a=np.arange(10)
# print(a)

b=np.arange(12, dtype=float).reshape(3,4)
# print(b)

c= np.arange(8).reshape(2,2,2)
# print(c)

print(c.ndim)
print(b.shape)
print(b.size)
print(a.itemsize)
print(a.dtype)
print(b.dtype)
print(c.dtype)