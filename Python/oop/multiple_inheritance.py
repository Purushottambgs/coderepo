# multiple inheritance

class phone:
    def __init__(self, brand, price,camra):
        self.brand=brand
        self.price=price
        self.camra=camra

    def bay(self):
        print("please bay my phone ")

class product:
    def produ(self):
        print("this  is new product")

class customer(phone, product):
    def customer_info(self):
        print("customer details from begusarai bihar")

s=customer('one-plush', 256000,18)
print(s.price)
print(s.brand)
print(s.camra)
s.bay()
s.produ()
s.customer_info()
