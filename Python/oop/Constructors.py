# child can't access private members of the class

class Phone:
    def __init__(self, price, brand, camra_px):
        self.__price=price
        self.brand=brand
        self.camra_px=camra_px

    def show(self):
        print(self.__price)

class Smartphone(Phone):
    def check(self):
        print(self.__price)

s=Smartphone(5600, 'sumsung',10)
s.show()
print(s.brand)
#s.check()   error
