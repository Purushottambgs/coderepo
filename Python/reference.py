class Person:
    def __init__(self, name, gender):
        self.name=name
        self.gender=gender

def greet(person):
    print('Hi my name is', person.name, 'and i am a', person.gender)
    # p1= Person('nitish','male')
    # return p1


p= Person('purushottam', 'male')
x=greet(p)
