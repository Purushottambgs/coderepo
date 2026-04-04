"""
Create a Bus class that inherits from the Vehicle class. Give the capacity argument of Bus.seating_capacity() a default value of 50.

Use the following code for your parent Vehicle class.
"""

class vehicle:
    def __init__(self, name, seating_capacity):
        self.name=name
        self.seating_capacity= seating_capacity

    def fare(self):
        return self.seating_capacity*100
    
class bus(vehicle):
    def __init__(self, name, seating_capacity=50):
        super().__init__(name, seating_capacity)

Bus=bus('Purushottam bus')
buss=bus('purushottam bus',30)
print(Bus.name, Bus.seating_capacity)
print(buss.name, buss.seating_capacity)
        


