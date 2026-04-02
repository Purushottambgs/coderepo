# Simple intrest calculator

principle= float(input("Enter principal= "))
rate_of_interest= float(input("Enter rate of interest ="))
time= float(input("Enter time(in years) = "))

simple_interest = (principle*rate_of_interest* time)/100
print("Simple Interest", simple_interest)