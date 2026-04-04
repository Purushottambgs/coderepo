# multiple inherritence

class phone:
    def __init__(self, brand, price, camra):
        self.brand=brand
        self.price=price
        self.camra=camra

    def sell(self):
        print("please sell this product")

class seelar(phone):
    pass

class customer(seelar):
    pass

cus=customer('realme',78900,5)
print(cus.brand)
cus.sell()