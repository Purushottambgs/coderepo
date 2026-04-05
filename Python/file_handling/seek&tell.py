# seek and tell function

with open('puru.txt', 'r') as f:
    print(f.read(10))
    print(f.tell())
    print(f.seek(15))
    print(f.read(5))