# Methos Overriding

class Phone:
    def __init__(self, price, brand, camra):
        self.price= price
        self.brand= brand
        self.camra=camra

    def bay(self):
        print("pls bay this phone")

class Smartphone(Phone):
    def __init__(self, price, brand, camra):
        self.price=price
        self.brand=brand
        self.camra=camra

    def bay(self):
        print("Please bay my new smartphone") # overriding

s=Smartphone(5600,"nokia", 5)
print(s.brand)
print(s.bay())
