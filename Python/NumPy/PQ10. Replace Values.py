# Q10. Replace Values (Important)

#  Given:

# a = np.array([1, 2, 3, 4, 5, 6])

#  Replace karo:

# even numbers → 0
# odd numbers → same

import numpy as np

a=np.array([1,2,5,6,38,9,4,78,5,6,9,10,25,89,52,62,12,78,52])
print(np.where(a%2==0,"even",a))