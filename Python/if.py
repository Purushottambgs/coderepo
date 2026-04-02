
price= int(input("Enter product price:- "))

if price>=5000:
    print("you are eligible for offer", price)
    
    print("Enter you mode of pyment")
    mode= input("A-Cash B-Card C-UPI")
    if mode == "B":
        print("you are eligible for discount")
    elif mode =="A" or mode == "c":
        print("you are not eligible for discount")
    else:
        ("In-valid-input")

elif price<0 or price<5000:
    print("you are not eligible for offer", price)

else:
    print("Pls bay product")