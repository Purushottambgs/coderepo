
class phone:
    def __init__(self, brand, price, camra_px):
        print("Inside phone constacture")
        self.brand=brand
        self.price=price
        self.camra_px= camra_px

    def buy(self):
        print("buying a phone")

class Smartphone(phone):

    None

s=Smartphone('realme', 16800, 13)
print(s.buy())