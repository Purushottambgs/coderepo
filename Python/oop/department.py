"""create a class Student with: 
Requirements: Private variables: __marks Methods: set_marks(marks) →
only allow 0–100 get_marks() 
grade() → return: A (>=80) B (>=60) C (>=40) Fail (<40)"""

# class student:
#     def __init__(self, name, department, sem, marks):
#         self.name=name
#         self.department=department
#         self.sem=sem
#         self.marks=marks

#     def mca(self):
#         print("what is your name",self.name, "your department",self.department, "your semester", self.sem, "your marks", self.marks)


# s=student("purushottam", "mca", "4th", "86")
# print(s.name)
# print(s.mca())


class student:
    def __init__(self):
        self.__marks=0

    def set_marks(self, marks):
        if 0<= marks <=100:
            self.__marks= marks
        else:
            return "Invalid marks please enter between 0 to 100"
        
    def get_marks(self):
        return self.__marks
    
    def marks(self):
        if self.__marks >=80:
            return "A+ Grade"
        elif self.__marks>=60:
            return "A Grade"
        elif self.__marks>=45:
            return "B Grade"
        elif self.__marks>=30:
            return "C Grade"
        else:
            return "fail"
        

s=student()