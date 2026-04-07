def modify(defc, num):
    return defc(num)

def squre(num):
    return num*10

a=modify(squre, 5)
print(a)