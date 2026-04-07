def my_decorator(func):
    def wrapper():
        print('**************')
        func()
        print('**************')
    return wrapper
@my_decorator
def hello():
    print("hello")

def display():
    print("hello purushottam")

hello()

b=my_decorator(display)
b()