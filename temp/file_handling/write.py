with open("demo.txt","w") as file:
    file.write("i am anurag")
    l=['\n purushottam \n', 'rahul\n', 'anurag \n']
    file.writelines(l)