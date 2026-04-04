"""
Problem-1: Class inheritence
Create a Bus child class that inherits from the Vehicle class. The default fare charge of any vehicle is seating capacity * 100. If Vehicle is Bus instance, we need to add an extra 10% on full fare as a maintenance charge. So total fare for bus instance will become the final amount = total fare + 10% of the total fare.

Note: The bus seating capacity is 50. so the final fare amount should be 5500. You need to override the fare() method of a Vehicle class in Bus class.
"""

class vehicle:
    def __init__(self, name, seating_capacity):
        self.name=name
        self.seating_capacity=seating_capacity

    def fare(self):
        fare= self.seating_capacity*100
        return fare

    
class Bus(vehicle):
    def fare(self):
        print("this fare is child class")

        base_fire= super().fare()
    
        extra=base_fire*0.10
        total= base_fire+extra
        return total
    


se=Bus('purushottam bus',50)
print("seating capacity are",se.seating_capacity)
print("total_fire is =", se.fare())




