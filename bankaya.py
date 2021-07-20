import pymongo
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient


try:
#Establish Connection to MySQL DB and DWH  
    bankaya = mysql.connector.connect(host='localhost',
                                         database='Bankaya',
                                         user='root',
                                         password='******')
    dwh = mysql.connector.connect(host='localhost',
                                      database='BankayaDWH',
                                      user='root',
                                      password='******')

#Only proceed if connection is succesful
    if bankaya.is_connected():
#Get data that is in the DB and what´s already in the DWH
        cursorInput = bankaya.cursor(buffered=True)
        cursorOutput = dwh.cursor(buffered=True)
        items = "SELECT * from Items"
        cursorInput.execute(items)
        records = cursorInput.fetchall()
        queryItemsInDWH = "SELECT * FROM Items;"
        cursorOutput.execute(queryItemsInDWH)
        resultsItemsInDWH = cursorOutput.fetchall()
        itemsInDWH = []
        
#This is only for processing data, a more elegant solution is to be implemented
        for item in resultsItemsInDWH:
            itemsInDWH.append(item[0])

        for item in records:
#Only adds data that is not already in the DWH
            if item[0] not in itemsInDWH:
                itemDWH = "INSERT INTO Items(item_id, item_name, item_price) VALUES(%s, %s, %s);"
                data = (item[0], item[1], item[2])
                cursorOutput.execute(itemDWH, data)
                dwh.commit()
            
#The following code is the same logic as before just with different tables, one could define functions for this. This was done for speed and easy debugging

        customers = "SELECT * FROM Customers"
        cursorInput.execute(customers)
        records = cursorInput.fetchall()
        queryCustomersInDWH = "SELECT * FROM Customers;"
        cursorOutput.execute(queryCustomersInDWH)
        resultsCustomersInDWH = cursorOutput.fetchall()
        customersInDWH = []
        for customer in resultsCustomersInDWH:
            customersInDWH.append(customer[0])

        for customer in records:
            if customer[0] not in customersInDWH:
                customerDWH = "INSERT INTO Customers(customer_id, customer_name," \
                          " phone_number, CURP, RFC) VALUES(%s, %s, %s, %s, %s);"
                data = (customer[0], customer[1] + " " + customer[2], customer[3], customer[4], customer[5])
                cursorOutput.execute(customerDWH, data)
                addressDWH = "INSERT INTO Addresses(street, " \
                             "external_number, internal_number, delegation," \
                             "suburb, state, city, zip_code, country) " \
                             "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                data = (customer[6], customer[7], customer[8], customer[9], customer[10], customer[11],
                        customer[12], customer[13], customer[14])
                cursorOutput.execute(addressDWH, data)
                dwh.commit()


        itemsBought = "SELECT * FROM Items_Bought;"
        cursorInput.execute(itemsBought)
        records = cursorInput.fetchall()
        queryItemsBoughtInDWH = "SELECT * FROM Orders;"
        cursorOutput.execute(queryItemsBoughtInDWH)
        resultsItemsBoughtInDWH = cursorOutput.fetchall()
        ordersInDWH = []
        for order in resultsItemsBoughtInDWH:
            ordersInDWH.append(order[0])

        for order in records:
            if order[0] not in ordersInDWH:
                orderDWH = "INSERT INTO Orders(order_number, customer_id," \
                          " address_id, order_date, total, comment) VALUES(%s, %s, %s, %s, %s, %s);"
                data = (order[0], order[5], order[5], order[1], order[2], order[3])
                cursorOutput.execute(orderDWH, data)
                boughtItemDWH = "INSERT INTO Items_Bought(item_id, order_number) " \
                             "VALUES(%s, %s);"
                data = (order[4], order[0])
                cursorOutput.execute(boughtItemDWH, data)
                dwh.commit()
                
                
#The following is the same logic but for the MongoDB DB.
                
                
    client = MongoClient('localhost', 27017)
    db = client.test
    Customers = db.Customers
    queryCustomersInDWH = "SELECT * FROM Customers;"
    cursorOutput.execute(queryCustomersInDWH)
    resultsCustomersInDWH = cursorOutput.fetchall()
    customersInDWH = []
    for customer in resultsCustomersInDWH:
        customersInDWH.append(customer[1])


    for customer in Customers.find():
        if customer["firstname"] + " " + customer["lastname"] not in customersInDWH:
            orderDWH = "INSERT INTO Customers(customer_name," \
                       " phone_number, CURP, RFC) VALUES ('" + customer["firstname"] + " " + customer["lastname"] + "', NULL, NULL, NULL);"
            cursorOutput.execute(orderDWH)
            dwh.commit()

            
    db = client.test
    Items = db.Items
    queryItemsInDWHInDWH = "SELECT * FROM Items;"
    cursorOutput.execute(queryItemsInDWH)
    resultsItemsInDWH = cursorOutput.fetchall()
    itemsInDWH = []
    for item in resultsItemsInDWH:
        itemsInDWH.append(item[1])

    for item in Items.find():
        if item["title"] not in itemsInDWH:
            orderDWH = "INSERT INTO Items(item_name, item_price) VALUES (%s, %s);"
            data = (item["title"], item["price"])
            cursorOutput.execute(orderDWH, data)
            dwh.commit()

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if bankaya.is_connected():
        cursorInput.close()
        cursorOutput.close()
        bankaya.close()
        dwh.close()
        print("MySQL connection is closed")
