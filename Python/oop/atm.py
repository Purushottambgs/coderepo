class atm:
    def __init__(self):
        self.pin=''
        self.balance=0
        self.menu()
        

    def menu(self):
        user_input=input("""
        Hi how can i help you?
        1. Press 1 to create pin
        2. Press 2 to change pin
        3. Press 3 to check balance
        4. Press 4 to withdraw
        5. Anythin else to exit
       """)
        
        if user_input=='1': 
           # create pin
           self.create_pin()
        elif user_input=='2':
          # change pin
          self.change_pin()
          
        elif user_input=='3':
         # check balance
          self.check_balance()
        elif user_input =='4':
        # check withdraw
          self.withdraw()
        else:
            exit()
    
    def create_pin(self):
        user_pin=int(input("Enter your pin:- "))
        self.pin= user_pin

        user_balance= int(input("Enter balance:- "))
        self.balance=user_balance

        print("pin created succesfully")
        self.menu()

    def change_pin(self):
       old_pin=int(input('enter old pin:- '))

       if old_pin==self.pin:
          new_pin= int(input('enter your new pin:- '))
          self.pin=new_pin
          print("pin change succesfully")
          self.menu()
       else:
          print("wrong pin")
          self.menu()

    def check_balance(self):
       enter_pin=int(input("enter your pin"))
       if enter_pin==self.pin:
          print("your balance is", self.balance)
          self.menu()
       else:
          print('worng pin')
          self.menu()
    
    def withdraw(self):
       enter_pin=int(input("enter a pin"))
       amount= int(input("enter amount"))
       if enter_pin==self.pin and self.balance>amount:
          print("successfull withdraw")
          self.balance=self.balance-amount
          print('balance is', self.balance)
          self.menu()

       else: 
          print("not withdraw")
          self.menu()



obj= atm()



