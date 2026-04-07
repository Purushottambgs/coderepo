def purushottam(name):
    def vijay():
        print("are you my mad")
        name()
        print("no bro you are mad")
    return vijay

@purushottam
def name():
    print("my name is purushottam kumar")

name()