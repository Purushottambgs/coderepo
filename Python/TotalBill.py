# Total Bill Amount With GST

price= float(input("pls enter toal price of item"))
quantity= int(input("pls enter item quantity"))
total_price=price*quantity

gst= total_price *18/100
final_price= total_price+gst
print("Total price", total_price)
print("GST", gst)
print("Final Amount", final_price)