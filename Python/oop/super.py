
class Phone:
    def __init__(self, price, brand, camra):
        self.price=price
        self.brand=brand
        self.camra=camra

    def bay(self):
        print("please bay my phone")

class Smartphone(Phone):
    def __init__(self, price, brand, camra):
        print("sell smartphone")
        super().__init__(price, brand, camra)
        print("this is my boss phone")
        self.price=7800
        self.brand='realme'
        self.camra=32

    def bay(self):
        print("please bay my smartphone")
        super().bay()   # supur keyword use and access parent class methods

s=Smartphone(45800,'jjhdlj',2)
print(s.brand)
s.bay()