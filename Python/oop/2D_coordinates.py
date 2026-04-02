""" Write OOP classes to handle the following scenarios: 
   A user can create and view 2D coordinates
   A user find out the distance between 2 coordinates
   A user can check if a point lies on a given line 
   A user can find the distance between a given 2D point and a given line """

class point:
    def __init__(self, x,y):
        self.x_cod=x
        self.y_cod=y

    def __str__(self):
        return "<{},{}>".format(self.x_cod, self.y_cod)
    
    def howtodistance(self, other):
        return ((self.x_cod - other.x_cod)**2 + (self.y_cod-other.y_cod)**2)**0.5
    

class line:
    def __init__(self, A,B,C):
        self.A=A
        self.B=B
        self.C=C

    def __str__(self):
        return "{}x + {}y + {} = 0".format(self.A, self.B, self.C)
    
    def linecheck(self, point):
        if self.A*point.x_cod + self.B*point.y_cod + self.C == 0:
            return "lies on the line"
        else:
            return "does not lie on the line"
        
    def shortest_distance(line, point):
        return abs(line.A*point.x_cod+ line.B *point.y_cod+ line.C)/(line.A**2 + line.B**2)


l1 = line(1,1,-2)
l2 = point(1,1)

print(l1)
print(l2)

print(l1.shortest_distance(l2))

