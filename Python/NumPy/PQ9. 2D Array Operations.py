# Q9. 2D Array Operations 

# Given:

# a = np.array([[1,2,3],
#               [4,5,6],
#               [7,8,9]])

#  Find:

# row-wise sum
# column-wise sum

import numpy as np

a=np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12]])
print(a)
print(a.sum(axis=0))
print(a.sum(axis=1))