# readling entire using redline

f=open('puru.txt', 'r')
while True:
    data=f.readline()

    if data==' ':
        break
    else:
        print(data, end=' ')
  
f.close()