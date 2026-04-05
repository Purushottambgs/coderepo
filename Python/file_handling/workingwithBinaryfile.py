# working with binary file

with open('E:\\coderepo\\Python\\file_handling\\car.jpg', 'rb') as f:
    with open('new_car_copy.jpg', 'wb') as wf:
        wf.write(f.read())