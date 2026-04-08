import numpy as np

a=np.arange(12).reshape(3,4)
b=np.arange(12,24).reshape(4,3)
print(a)
print(b)

print(np.dot(a,b))
print(np.exp(a))
c=np.ceil(np.random.random((2,3))*100)
print(c)
