# if you want to create a method overloading

class circle:
    def area(self, a,b=0):
        if b==0:
            return 3.14*a*a
        else:
            return a*b


c=circle()
print(c.area(5))
c.area(5)