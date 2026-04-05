# benefit? -> to load a big file in memory

# big_L=['hello purushottam' for i in range(1000)]

# with open('big.txt', 'w') as f:
#     f.writelines(big_L)


with open('big.txt', 'r') as f:
    char_size=100

    while len(f.read(char_size))>0:
        print(f.read(char_size), end=" ")
        print(char_size)