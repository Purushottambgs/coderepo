try:
    f= open('sample.txt', 'r')
    a=10/0

except FileNotFoundError:
    print("this file is not exit in my system ")
except ZeroDivisionError:
    print("zero not divided in any number")
else:
    print("try again")