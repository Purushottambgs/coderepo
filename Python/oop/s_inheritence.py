# single inheritence

class phone:
    def __init__(self, price, brand, camra):
        self.price=price
        self.brand=brand
        self.camra=camra

    def sell(self):
        print("please sell This product")

class Smartphone(phone):
    pass

s=Smartphone(4500,'nokia', 5)
print(s.brand)
print(s.sell())