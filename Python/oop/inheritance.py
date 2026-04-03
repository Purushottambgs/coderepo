# Inheritance

class teacher:
    def __init__(self):
        self.name='Pangambbam'

    def login(self):
        print("login success")

class student(teacher):
    # def __init__(self):
    #     self.course='MCA'
    
    def enroll(self):
        print("you are successfull enroll this course")

t1=teacher()
s1=student()
print(s1.name)
print(s1.login())
print(s1.enroll())