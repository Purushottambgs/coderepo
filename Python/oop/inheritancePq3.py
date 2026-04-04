"""
Problem-3: Write a program that has a class Point. Define another class Location which has two objects (Location & Destination) of class Point. Also define a function in Location that prints the reflection of Destination on the x axis.
"""

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Location:
    def __init__(self, source, destination):
        self.source = source          
        self.destination = destination  

    def reflect_on_x_axis(self):
        # reflection on x-axis → (x, y) → (x, -y)
        new_x = self.destination.x
        new_y = -self.destination.y

        print("Reflection of Destination on X-axis:",
              f"({new_x}, {new_y})")



p1 = Point(2, 3)     
p2 = Point(4, 5)     

# creating Location object
loc = Location(p1, p2)

# calling function
loc.reflect_on_x_axis()