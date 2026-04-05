import json

class Person:
    def __init__(self, fname, lname, age, gender):
        self.fname=fname
        self.lname=lname
        self.age=age
        self.gender=gender

person=Person('purushottam','kumar',23,'male')

def check_object(person):
    if isinstance(person, Person):
        return "your first name {} last name {} age {} and gender {}".format(person.fname, person.lname, person.age, person.gender)
    
with open('demo.json', 'w') as f:
    json.dump(person, f, default=check_object)