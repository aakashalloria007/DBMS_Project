# import requests
# from bing_image_urls import bing_image_urls
#
# products = ['iPhone 13 Pro Max', 'Samsung Galaxy Watch 4', 'Logitech G Pro X Superlight', 'Sony WH-1000XM4', 'HP Spectre x360', 'Dell XPS 15', 'Asus ROG Strix Scar 15', 'GAP Hoodie', 'Gucci Ace Sneakers', 'Louis Vuitton Monogram Shirt', 'Converse Chuck Taylor All Star', 'Prada Nylon Backpack', 'Tommy Hilfiger Polo Shirt', 'Versace Baroque Print Silk Shirt', 'Adidas Ultraboost', 'Nike Air Max 270', 'Puma Future Z 1.1 FG/AG', 'Asics Gel-Kayano 28', 'Reebok Nano X1', 'Jordan Jumpman Backpack', 'New Balance Fresh Foam 1080v11', 'iPhone 12', 'Samsung Galaxy Tab S7', 'Logitech MX Master 3', 'Sony PlayStation 5', 'HP ENVY 13', 'Dell Alienware m15 R6', 'Asus ZenBook 14', 'GAP T-Shirt', 'Gucci GG Marmont Bag', 'Louis Vuitton Keepall Bandoulière 55', 'Converse Chuck 70 High Top', 'Prada Saffiano Leather Wallet', 'Tommy Hilfiger Denim Jacket', 'Versace Medusa Head Belt', 'Adidas Predator Freak.1 FG', 'Nike ZoomX Vaporfly NEXT% 2', 'Puma RS-Fast Sneakers', 'Asics Gel-Nimbus 24', 'Reebok Classic Leather', 'Jordan Jumpman T-Shirt', 'New Balance Fresh Foam Hierro v6', 'iPad Air (2022)', 'Samsung Galaxy Buds Pro', 'Logitech G502 Hero', 'Sony WH-CH710N', 'HP Pavilion 15', 'Dell Inspiron 14', 'Asus VivoBook 15', 'GAP Slim Fit Jeans']
#
#
# def get_image(image_url,image_name):
#     response = requests.get(image_url,timeout=5)
#     try:
#         img_data = response.content
#         if str(response.headers['content-type'].split("/")[0]) == "image":
#             with open(f"./downloads/{image_name}.{response.headers['content-type'].split('/')[1]}", 'wb') as handler:
#                 handler.write(img_data)
#             print(image_name)
#             return True
#     except Exception as e:
#         return False
#
#
# print("running")
# for i in products:
#     print(f"{products.index(i)}: {len(products)}")
#     urls = bing_image_urls(i, limit=5)
#     for url in urls:
#         try:
#             if get_image(url,i):
#                 break
#         except Exception as e:
#             print(e)
#             print("getting alternate image")
#             pass
#
import os
import mysql.connector
import csv
con = mysql.connector.connect(host='localhost', user='root',password='aak20f031', database='dbms_project')

#
# filenames = os.listdir("./downloads")
# for file in filenames:
#     filename,fileextension = os.path.splitext(file)
#     cursor = con.cursor()
#     cursor.execute(f"UPDATE products set Product_Url = '{file}' where ProductName = '{filename}'")
#     con.commit()
# print("done")
#
cursor = con.cursor()
cursor.execute("Select * from products")
rows = cursor.fetchall()
fp = open('products.csv', 'w')
myFile = csv.writer(fp)
myFile.writerows(rows)
fp.close()