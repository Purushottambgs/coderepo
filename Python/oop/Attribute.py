
class attribute:
    def __init__(self, name_input, country_input):
        self.name= name_input
        self.country=country_input

    def greey(self):
        if self.country=="india":
         print("Namste", self.name)
        else:
         print("hello", self.name)
    
p=attribute("purushottam", "india")
a=attribute("joya","pakishtan")

print(p.name)
print(p.country)
print(p.greey())
print(a.greey())

# Attribute creation from outside of the class
p.gender="male"
print(p.gender) 