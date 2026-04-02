
email= input("Enter your email id:- ")
password= int(input("Enter your password:- "))

if email=='bgspurushottamjha@gmail.com' and password==123:
    print("welcome to my page")
elif email=='bgspurushottamjha@gamil.com' and password !=123:
    print("invalid password")
    password= input("Enter a valid password")
    if password ==123:
        print("wolcome finally")
    else:
        print("reset password")
else:
    print("pls enter again")