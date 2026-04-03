class Phone:
    def __init__(self, brand, price, camra_px):
        print("inside a constructor")
        self.brand=brand
        self.price=price
        self.camra_px=camra_px

    def bay(self):
        print("buing a phone")

class Smartphone(Phone):
    def __init__(self, brand, price, camra_ox):
        self.brand='one plush'
        self.price=19300
        self.camra_px= 23
        print("child class constructos")

    def new_phone(self):
        print("buy new phone")
    
s=Smartphone('sumsung',89500,5)
s.new_phone()
s.bay()
print(s.camra_px)
