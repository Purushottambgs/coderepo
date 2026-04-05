import json

L=[1,5,6,9,3,1,4,5,7]

with open('demo.json', 'w')as f:
    json.dump(L,f)