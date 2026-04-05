import json

d= {
  "name":"purushottam",
  "age":26,
  "roll_num":"Y24271026"
}

with open('demo.json', 'w') as f:
    json.dump(d, f, indent=4)
