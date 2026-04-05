import json

class student:
    def __init__(self, name, age, gender, marks):
        self.name=name
        self.age=age
        self.gender=gender
        self.marks=marks

Student=student("purushottam",23,'male',88)

def details_student(Student):
    if isinstance(Student, student):
        return {
    'Student name': Student.name,
    'age': Student.age,
    'gender': Student.gender,
    'student marks': Student.marks
}
with open('demo.json', 'w') as f:
    json.dump(Student, f,default=details_student)

with open('demo.json', 'r') as p:
    d=json.load(p)
    print(d)
    print(type(d))