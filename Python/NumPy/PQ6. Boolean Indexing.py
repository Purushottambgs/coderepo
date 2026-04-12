# Q6. Boolean Indexing 

#  Given:

# a = np.array([5, 12, 7, 18, 3, 20])

#  Print karo:

# sirf values jo 10 se badi ho

import numpy as np
a= np.array([5,12,7,18,3,20,52,63,88,78,52,63,7,60])
print(a>10)

# Q7. np.where() use karo

#  Same array:

# a = np.array([5, 12, 7, 18, 3, 20])

#  Condition:

# 10 → "Big"

# else → "Small"

print(np.where(a==63, "big", "small"))