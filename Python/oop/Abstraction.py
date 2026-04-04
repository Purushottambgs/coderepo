from abc import ABC, abstractmethod

class BankApp(ABC):

    def databases(self):
        print("connected to database")
    @abstractmethod
    def security(self):
        pass

class Mobile_App(BankApp):
    def mobile_login(self):
        print('login into mobile')

    def security(self):
       print("mobile security")

mob=Mobile_App()
mob.mobile_login()
mob.security()
