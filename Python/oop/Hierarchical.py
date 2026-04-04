#  Hierarchical

class phone:
    def __init__(self, brand, price, camra):
        self.brand=brand
        self.price=price
        self.camra=camra

    def bay(self):
        print("plesase bay this phone")

class smartphone(phone):
    pass

class customer(phone):
    pass

s=smartphone('realme', 89565,7)
print(s.brand)
s.bay()
cus=customer('vivo', 85266, 7)
print(cus.brand)
print(cus.price)
cus.bay()
