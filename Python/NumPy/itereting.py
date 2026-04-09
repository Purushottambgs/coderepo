import numpy as np

a=np.arange(12)
b=np.arange(12, dtype=float).reshape(3,4)
c=np.arange(17)

# for i in a:
#     print(i)

# for i in b:
#     print(b)

# for i in c:
#     print(c)

for i in np.nditer(c):
    print(i)