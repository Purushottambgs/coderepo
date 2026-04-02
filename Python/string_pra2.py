# Extract username from a given email.
# eg if the email is nitish24singh@gamil.com
# then the username should be nitish24singh


s= input("Enter the email:- ")
pos= s.index('@')
print(s[0:pos])
