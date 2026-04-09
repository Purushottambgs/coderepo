import numpy as np

a=np.arange(12)
b=np.arange(12, dtype=float).reshape(3,4)
c=np.arange(8).reshape(2,2,2)

print(a)
print(b)
print(c)

# indexing

# print(a[-1])
# print(b[1,0])
# print(b[1,3])
# print(c[1,1,1])
# print(c[0,0,0])
# print(c[1,1,0])

# # slicing
# print(b[:,1])
# print(b[1:,1])
# print(b[2,:])
# print(b[0:2])
# print(b[1:, 1:3])
# print(b[::2,::3])
#print(b[:1:,2:4])
#print(b[1::, 2:4])
print(b[0::2, 1:4:1])
print(b[::3])