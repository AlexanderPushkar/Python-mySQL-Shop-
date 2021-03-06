#!/usr/bin/python
'''
Alexander Pushkar
4/11/2021

GUI to interact with the store database
load new information, search for current, or remove

'''

#Imports are kind of wacky and honestly some things
#which it says arnt accessed breaks the entire thing
#if removed
from __future__ import print_function
from ast import Delete, IsNot
from asyncio.base_futures import _FINISHED
from asyncio.windows_events import NULL
from asyncore import write
from cgitb import text
from contextlib import nullcontext
from ctypes import sizeof
from distutils.sysconfig import customize_compiler
from encodings import utf_8, utf_8_sig
from gzip import READ
from itertools import product
from msilib import type_string
from pickle import TRUE
from re import I
from sre_compile import isstring
from textwrap import fill
import this
from tkinter.font import BOLD
from tkinter.tix import INTEGER
from turtle import bgcolor, right, title
import unicodedata
from xml.etree.ElementTree import tostring
import mysql.connector
import csv
from tkinter import *  
from tkinter import DISABLED
import tkinter as tk
import random
from mysqlx import Row
from setuptools import Command
import hashlib
import re 
from datetime import date, datetime



######
'''
AS A POINT OF NOTE
The CSV file this project is based on came with
absolute NIL documentation so assignment of ID's 
and relations has been jerryrigged and creative 
liberaties have been taken
'''
######

###
"""
There are a few garbage values
inside DB from testing, can 
run Inital Data Loader to refresh
the DB
"""
###

#######
"""
Naming Convention For Frames/Functions

beggining denotes function:
s = search
aN = add new
d = delete
v = view

End denote table:
OL = order log
C = customer
P = product

EX:
aNOL = add new order log
dC = delete customer
"""
#######


#######
"""
Planned But Non Implimented Features Due To Time Crunch:
 - Search by typing page number
      -Just rework the page display system in general, straight garbage
 - Refactor displays to use tree view/allow for best fit searching
 - Do more with Sales table
 - Spruce up GUI
 - Rework dateEntry system
 - Rework how displays call for info and grab from db in specific rows instead of entire db being put into array
 - Better sanatization
 - More robust feedback info on bad data
 - Make server accessible outside local
 - Loading time reduction by optimization   
"""
#######



#Creates Connection to DB
mydb = mysql.connector.connect(
    #host = "localhost",
    host = "127.0.0.1",
    user = "root",
    password = "Snickerdoodle",
    database = "customerschema",
    autocommit = True
)





#Creates new screen and titles it
win = tk.Tk(screenName="Data Portal")
win.title("Data Managment Tool")
#win.attributes("-fullscreen", True)
#win.wm_attributes("-topmost", 1)

#Below closes on escape, speeds up testing  
win.bind("<Escape>", lambda event:win.destroy())

#Frame to hold seelection Buttons
selectionButtons = Frame(win, bg="#F2D199")
#selectionButtons.grid(columnspan=1)

#Frame that output and input options displayed in, seperate frame to ease in deletion
outPutFrame = Frame(win)
outPutFrame.grid(row = 1, column = 1) 



#Function to ease creating popup Windows
def popupwin(insert_val):
   #Create a Toplevel window
   top= Toplevel(win, border=4)
   #Create a Button to print something in the Entry widget
   Label(top,text= insert_val, font=("Segoe UI", 15)).pack(pady= 5,side=TOP)
   #Create a Button Widget in the Toplevel Window
   button= Button(top, text="Ok", font=("Segoe UI", 15), command=lambda:top.destroy())
   button.pack(pady=5, side= TOP)
   #Moves top level popup to ~Center
   top.geometry(f"+{500}+{500}")





#Function to clear widgets in output window
def clearOutPutWindow():
    for widget in outPutFrame.winfo_children():
        widget.destroy()





#Creates Date Entry function to ease data entry later in, actually DateEntry project abondonded in Python 2.0
class DateEntry(tk.Frame):
    def __init__(self, master, frame_look={}, **look):
        args = dict(relief=tk.SUNKEN, border=1)
        args.update(frame_look)
        tk.Frame.__init__(self, master, **args)

        # arguments to update 
        args = {'relief': tk.FLAT}
        args.update(look)

        #Labels and entry that create layout with arguments
        self.entry_1 = tk.Entry(self, width=2, **args)
        self.label_1 = tk.Label(self, text='/', **args)
        self.entry_2 = tk.Entry(self, width=2, **args)
        self.label_2 = tk.Label(self, text='/', **args)
        self.entry_3 = tk.Entry(self, width=4, **args)

        #Foratming above alables and entries 
        self.entry_1.pack(side=tk.LEFT)
        self.label_1.pack(side=tk.LEFT)
        self.entry_2.pack(side=tk.LEFT)
        self.label_2.pack(side=tk.LEFT)
        self.entry_3.pack(side=tk.LEFT)

        #Used to make accesssing each parameter easier
        self.entries = [self.entry_1, self.entry_2, self.entry_3]

        #To allow program to ensure inputted values dont exceed length and delete if they do on typing them
        #***Breaks if typed to quickly, reallllly bad  
        #No Documentation on onValidate, all Stack fourms on topic just have code, no explination
        #{Possibly use duel threading to have checks run parralel instead of garbage bind system}
        self.entry_1.bind('<KeyRelease>', lambda e: self._check(0, 2))
        self.entry_2.bind('<KeyRelease>', lambda e: self._check(1, 2))
        self.entry_3.bind('<KeyRelease>', lambda e: self._check(2, 4))

    #Function removes if values become too long in entry box
    def _backspace(self, entry):
        cont = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, cont[:-1])

    #Checks if entry excedes its size in date entry and backspaces ***FIND BETTER WAY TO DO THIS
    def _check(self, index, size):
        entry = self.entries[index]
        next_index = index + 1
        next_entry = self.entries[next_index] if next_index < len(self.entries) else None
        data = entry.get()

        #Will either backspace is len is greater otherwise if its equal tabs to next widget entry bxo
        if len(data) > size or not data.isdigit():
            self._backspace(entry)
        if len(data) >= size and next_entry:
            next_entry.focus()

    def get(self):
        return [e.get() for e in self.entries]










#Below are ALL Button Functions




def aNCButtonFunc():#function of the button to Add a New Customer
    clearOutPutWindow()
    aNCButtonFrame = Frame(outPutFrame)
    aNCButtonFrame.grid(row = 4, column = 1, pady=10)

    #Creates Label to indicate Name
    Label(aNCButtonFrame, text='Name', font=("Segoe UI", 15)).grid(row=4, column = 1) 

    #Creates Entry and allignes it with Label above
    nameEntry = Entry(aNCButtonFrame, font=("Segoe UI", 15))  
    nameEntry.grid(row=4, column=2) 

    #Function for submitButton
    def submitButtonFunc():

        #Wipes Entry widgit and sets variable 'name' to value in list
        name = nameEntry.get() 
        nameEntry.delete(0, 'end')
        
        #Creates new cursor to wipe its fetchall values
        mycursor = mydb.cursor()

        #Grabs all customers name to ensure entry not already made
        mycursor.execute("SELECT customerName FROM customers")
        outPutName = mycursor.fetchall()


        #Checks name is valid by comparing to REGEX (Yes I know it can be done better ****FIX )
        if re.search("^[a-zA-Z][a-zA-Z]+ {1}[a-zA-Z]+[a-zA-Z]$" ,name) == None:
            popupwin("Error, Invalid Name\nPlease follow format eg (John Smith))")

        else:
            
            #Splits first and last in string name into list
            nameSplit = name.split(sep = " ")
            #Id is Initals, which grabbing from 0 and 1+index of a space does, then hashes name with current datetime
            #into unique int of length 5 (With date to allow same name but diff unique ID)
            id = ("%s%s-%s") % (nameSplit[0][0], nameSplit[1][0], str(abs(hash(name + str((datetime.now()).strftime("%d/%m/%Y %H:%M:%S")))))[:5])

            #Inserts values into customers and print success message with uniqe ID
            mycursor = mydb.cursor()
            mycursor.execute("INSERT INTO customers VALUES (%s, %s)", (id, name))
            popupwin("New Customer %s\nWith Id %s\nAdded To Data Base" % (name, id))
            mycursor.close()
        mycursor.close()

        

    #Submit button to add customer to customer table in DB
    submitButton = Button(aNCButtonFrame, text='Submit', font=("Segoe UI", 15), command=submitButtonFunc).grid(row=5, column = 2)
   








##DELETE,     Inputs:  Name, Category, Sub Category

def aNPButtonFunc():#function of the button
    clearOutPutWindow()
    aNPButtonFrame = Frame(outPutFrame)
    aNPButtonFrame.grid(row = 4, column = 1, pady=10)

    #Creates Label to indicate Name
    Label(aNPButtonFrame, text='Name', font=("Segoe UI", 15)).grid(row=4, column = 1) 
    Label(aNPButtonFrame, text='Category', font=("Segoe UI", 15)).grid(row=6, column = 1)
    Label(aNPButtonFrame, text='Sub Category', font=("Segoe UI", 15)).grid(row=8, column = 1)


    prodNameEntry = Entry(aNPButtonFrame, font=("Segoe UI", 15))
    prodNameEntry.grid(row=4, column = 2)
  

    # Dropdown menu options for category
    categoryOptions = [
        "Furniture",
        "Office Supplies",
        "Technology"
    ]

    #Dropdown menu options for sub-category
    subCategoryOption = [
        "Bookcases",        #-=-=-
        "Chairs",           # Indexs 0-3 = Furniture
        "Furnishings",
        "Tables",           #-=-=-

        "Appliances",       #+|+|+
        "Art",
        "Binders",
        "Envelopes",
        "Fasteners",        # Index 4-12 = Office Supplies
        "Labels",
        "Paper",
        "Storage",
        "Supplies",         #+|+|+

        "Accessories",      #[{}]
        "Copiers",          # Index 13-16 = Technology
        "Machines",
        "Phones",           #[{}]
    ]



    #Will Be Used to update Sub-Category Checkbox to become interactable with specific selections
    #once the category checkbox has a selection made
    subClicked = StringVar()
    subClicked.set( "Select Sub-Category" )

    subSubCategoryOptions = [0]

    #Options menu for subcategory 
    subDrop = OptionMenu(aNPButtonFrame , subClicked , *subSubCategoryOptions)
    subDrop.grid(row=8, column=2)
    subDrop.config(font=("Segoe UI", 15))
    subDrop.configure(state='disabled')
    subMenu = aNPButtonFrame.nametowidget(subDrop.menuname)
    subMenu.config(font=("Segoe UI", 15))








    #Button for when Category is selected
    def OptionMenu_CheckButton(event):  
        #Actives menu and deletes all values within in
        subDrop.configure(state='active')      
        subClicked.set('')
        subDrop['menu'].delete(0, 'end')

        #By the selection of the category optionmenu sets subSubCategoryOptions to specific values
        if clicked.get() == "Furniture":
            subSubCategoryOptions = subCategoryOption[0:4]
        elif clicked.get() == "Office Supplies":
            subSubCategoryOptions = subCategoryOption[4:12]
        else:
            subSubCategoryOptions = subCategoryOption[13:17]

        #Adds each element in above defined list to subDrop as no way to change entire selection at once
        for choice in subSubCategoryOptions:
            subDrop['menu'].add_command(label=choice, command=tk._setit(subClicked, choice))
        subClicked.set( "Select Sub-Category") 

        pass




    # datatype of menu text
    clicked = StringVar()
    clicked.set( "Select Category" )
    
    #Main category
    categoryDrop = OptionMenu(aNPButtonFrame , clicked , *categoryOptions, command = OptionMenu_CheckButton )
    categoryDrop.grid(row=6, column=2)
    categoryDrop.config(font=("Segoe UI", 15))
    categoryDropMenu = aNPButtonFrame.nametowidget(categoryDrop.menuname)
    categoryDropMenu.config(font=("Segoe UI", 15))
    
    

    #Function for submitButton
    def submitButtonFunc():
        prodName = prodNameEntry.get()
        prodNameEntry.delete(0, 'end')
        print(prodName)
        #Creates new cursor to wipe its fetchall values
        mycursor = mydb.cursor()

        #Grabs all customers name to ensure entry not already made
        mycursor.execute("SELECT productID FROM products ORDER BY productID DESC LIMIT 1;")
        maxProdID = mycursor.fetchall()

        #Grabs all customers name to ensure entry not already made
        mycursor.execute("SELECT productName FROM products")
        outPutProducts = mycursor.fetchall()
        
       #Input Validation
        if prodName in outPutProducts:
            popupwin("Error, Name Already In Use")
        elif len(prodName) == 0 or clicked.get()=="Select Category" or subClicked.get()=="Select Sub-Category":
            popupwin("Please Input Values")

        else:
            #Creates ID bassed on category, subcategory, and what the current max prodect ID is plus a random number(Original Data Set had no documentation for it)
            id = ("%s-%s-%s") % (clicked.get()[0:3].upper(), subClicked.get()[0:2].upper(), int(((maxProdID[0][0])[7:17])) + random.randrange(1,30))
            
            mycursor.execute("INSERT INTO products VALUES (%s, %s, %s, %s)", (prodName , id, clicked.get(), subClicked.get()))
            popupwin(("New Product %s\nWith Id %s,\n%s,%s\nAdded To Data Base" % (prodName, id, clicked.get(), subClicked.get())))
            
            #Resets optionsmenu and boxes
            subClicked.set("Select Sub Category")
            subDrop.configure(state='disabled')      
            subDrop['menu'].delete(0, 'end')
            clicked.set("Select Category")

        mycursor.close()

    #Submit button to add customer to customer table in DB
    submitButton = Button(aNPButtonFrame, text='Submit', font=("Segoe UI", 15), command=submitButtonFunc).grid(row=10, column = 2)










def aNOLButtonFunc():#function of the add new order log button
    clearOutPutWindow()

    #Creates Frame in outPutFrame
    aNOLButtonFrame = Frame(outPutFrame)
    aNOLButtonFrame.grid(row = 4, column = 1, pady=10)

    #Block for productID entry field
    Label(aNOLButtonFrame, text='Product ID:', font=("Segoe UI", 15)).grid(row=4, column = 1) 
    productIDEntry = Entry(aNOLButtonFrame, font=("Segoe UI", 15))
    productIDEntry.grid(row=4, column = 2)

    #Block for customerID entry field
    Label(aNOLButtonFrame, text='Cusomer ID:', font=("Segoe UI", 15)).grid(row=6, column = 1)
    customerIDEntry = Entry(aNOLButtonFrame, font=("Segoe UI", 15))
    customerIDEntry.grid(row=6, column = 2)

    #Filler for GUI
    Label(aNOLButtonFrame, text='').grid(row=7, column = 1)


    #Block for shippingMethod entry field
    selectedShipMethod = StringVar()
    selectedShipMethod.set('Select Shipping')
    shipMethods = ["Standard Class", "Second Class", "First Class"]
    Label(aNOLButtonFrame, text='Shipping:', font=("Segoe UI", 15)).grid(row=8, column = 1)
    shipMethodEntry = OptionMenu(aNOLButtonFrame, selectedShipMethod, *shipMethods)
    shipMethodEntry.config(font=("Segoe UI", 15))
    shipMenu = aNOLButtonFrame.nametowidget(shipMethodEntry.menuname)
    shipMenu.config(font=("segeo UI", 15))
    shipMethodEntry.grid(row=8, column = 2)
    
    #Block for segment entry field
    selectedSegment = StringVar()
    selectedSegment.set('Select Segment')
    segments = ["Home Office", "Consumer", "Corporate"]
    Label(aNOLButtonFrame, text='Segment:', font=("Segoe UI", 15)).grid(row=10, column = 1)
    segmentEntry = OptionMenu(aNOLButtonFrame, selectedSegment, *segments)
    segmentEntry.config(font=("Segoe UI", 15))
    segmentMenu = aNOLButtonFrame.nametowidget(segmentEntry.menuname)
    segmentMenu.config(font=("segeo UI", 15))
    segmentEntry.grid(row=10, column = 2)

    #Block for orderDate entry field
    Label(aNOLButtonFrame, text='Order Date', font=("Segoe UI", 15)).grid(row=11, column=1)
    orderDate = DateEntry(aNOLButtonFrame, font=("Segoe UI", 15))
    orderDate.grid(row = 11, column = 2)

    #Block for shipDate entry field
    #WARNING, HYPER FIDDILY, PROCEED WITH CAUTION
    Label(aNOLButtonFrame, text='Ship Date', font=("Segoe UI", 15)).grid(row=12, column=1)
    shipDate = DateEntry(aNOLButtonFrame, font=("Segoe UI", 15))
    shipDate.grid(row = 12, column = 2)

    #Filler for GUI
    Label(aNOLButtonFrame, text='(EX: CT, AB, FL)', font=("Segoe UI", 5), pady=12).grid(row=13, column = 1)


    #Block for State Selection
    Label(aNOLButtonFrame, text='State:', font=("Segoe UI", 15)).grid(row=14, column = 1)
    stateEntry = Entry(aNOLButtonFrame, font=("Segoe UI", 15))
    stateEntry.grid(row=14, column = 2)

    #Block for City Selection
    Label(aNOLButtonFrame, text='City:', font=("Segoe UI", 15)).grid(row=15, column = 1)
    cityEntry = Entry(aNOLButtonFrame, font=("Segoe UI", 15))
    cityEntry.grid(row=15, column = 2)
    
    #Block for Region Selection
    selectedRegion = StringVar()
    selectedRegion.set('Select Region')
    regions = ["North", "South", "West", "East", "Central"]
    Label(aNOLButtonFrame, text='Region:', font=("Segoe UI", 15)).grid(row=16, column = 1)
    regionEntry = OptionMenu(aNOLButtonFrame, selectedRegion, *regions)
    regionEntry.config(font=("Segoe UI", 15))
    regionMenu = aNOLButtonFrame.nametowidget(regionEntry.menuname)
    regionMenu.config(font=("segeo UI", 15))
    regionEntry.grid(row=16, column = 2)

    #Block for Zip Selection
    Label(aNOLButtonFrame, text='Zip:', font=("Segoe UI", 15)).grid(row=18, column = 1)
    zipEntry = Entry(aNOLButtonFrame, font=("Segoe UI", 15))
    zipEntry.grid(row=18, column = 2)


    def submitButtonFunc():

        #Helps with validating date
        def isDateValid(widget):
            month = int(widget.get()[0])
            day = int(widget.get()[1])
            year = int(widget.get()[2])
            if 12 >= month >= 1 and 31 >= day >= 1 and (date.today()).year >= year > 1900:
                return True
            else:
                return False

        #Helps with validating dates make sense
        def isEarlier(shipDate, orderDate):
            if shipDate.get()[2] >= orderDate.get()[2]:
                return True
            if shipDate.get()[1] >= orderDate.get()[1]:
                return True
            if shipDate.get()[0] >= orderDate.get()[0]:
                return True
            return False
        #Checks if dates are valid
       
        #Checks if all fields filled in
        if  len(productIDEntry.get()) == 0 or len(customerIDEntry.get()) == 0 or len(zipEntry.get()) == 0 or len(cityEntry.get()) == 0 or len(stateEntry.get()) == 0 or selectedSegment.get() == "Select Segment" or selectedRegion.get() == "Select Region" or selectedShipMethod.get() == "Select Shipping":
            popupwin("Please Fill All Values")
            return 0

        #Creates three arrays for value verification
        mycursor = mydb.cursor()
        mycursor.execute("SELECT productID FROM products")
        productID = [item for t in mycursor.fetchall() for item in t]
        mycursor.execute("SELECT customerID FROM customers")
        customerID = [item for t in mycursor.fetchall() for item in t]
        
        #Only realizing in post CSV file uses full state names not abbreviations, but this is easier for data input 
        states = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
               'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
               'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
               'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
               'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

        #Block handles Improperly entered values
        errorMessage = ""

        #Concatonates different error messages before displaying
        if not isDateValid(shipDate) or not isDateValid(orderDate) or not isEarlier(shipDate, orderDate):
            errorMessage += "Invalid Date\n"
        if productIDEntry.get() not in productID:
            errorMessage += "Product ID not found\n"
        if customerIDEntry.get() not in customerID:
            errorMessage += ("Customer ID not found\n")
        if stateEntry.get() not in states:
            errorMessage += ("Enter State As Abbreviation\n")
        if len(errorMessage) != 0:
            popupwin(errorMessage)
            return 0

        
        #Grabs last digits of ID's from orderIDs and sorts to allow to accsses latest value 
        mycursor.execute("SELECT substring(orderID,9,14) FROM orders")
        orderIDList = mycursor.fetchall()
        orderIDList.sort()
        maxOrderID = int(orderIDList[1][0])

        orderID = ("%s-%s-%d" % ((stateEntry.get())[0:2].upper(), orderDate.get()[2], maxOrderID+1))
        
        #Formating here to mySQL compatiable date format for ease of use, (YEAR:MONTH:DATE)
        shipDateFormatted = "%s-%s-%s" % (shipDate.get()[2],shipDate.get()[0],shipDate.get()[1])
        orderDateFormatted = "%s-%s-%s" % (orderDate.get()[2],orderDate.get()[0],orderDate.get()[1])

        inputTuple = (orderID, productIDEntry.get(), customerIDEntry.get(), orderDateFormatted, shipDateFormatted, selectedShipMethod.get(), selectedSegment.get(), "USA", cityEntry.get(), stateEntry.get(), selectedRegion.get(), zipEntry.get())

                                                             #Tuple hell
        mycursor.execute("INSERT INTO orders VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", inputTuple)
        mycursor.close
        popupwin("Following Order Was Added\nOrderID:%s\tProduct ID:%s\tCustomer ID:%s\nOrder Date:%s\tShip Date:%s\tShip Mode:%s\nSegment:%s\tCountry:%s\tCity:%s\nState:%s\tRegion:%s\tPostal Code:%s" % inputTuple)

        #Defaults all values when finsished 
        productIDEntry.delete(0, 'end')
        customerIDEntry.delete(0, 'end')
        selectedShipMethod.set("Select Shipping")
        selectedSegment.set("Select Segment")
        stateEntry.delete(0, 'end')
        cityEntry.delete(0, 'end')
        selectedRegion.set("Select Region")
        zipEntry.delete(0, 'end')


    Button(aNOLButtonFrame, text='Submit', font=("Segoe UI", 15), command=submitButtonFunc).grid(row=20, column = 2)










def vCButtonFunc():#function of view Customers the button
    clearOutPutWindow()
    vCButtonFrame = Frame(outPutFrame)
    vCButtonFrame.grid(row = 1, column = 2)
    

    Label(vCButtonFrame, text="Customer ID:", font=("Segoe UI", 15)).grid(row = 0, column = 0)
    Label(vCButtonFrame, text="Customer Name", font=("Segoe UI", 15)).grid(row = 0, column = 1)



    mycursor = mydb.cursor()

    #YEs I know this is bad practice and extremlly slow but would require refactoring the entierty
    #Of the view functions to allow for row calling, would be easier to just rewrite from scratch
    mycursor.execute("SELECT * FROM customers")
    outPutRows = mycursor.fetchall()

    #Finds total pages by taking int division or outputrows length / 20 and adds 1
    totPages = (int(len(outPutRows)/20)+1)

    #Startvalue list to allow acess outside of function below
    startValue = []
    startValue.append(0)

    #Creates label to dispaly number of pages 
    vCPageNumber = Label(vCButtonFrame, text=("Page number: 1 / %d" % totPages), font=("Segoe UI", 15))
    vCPageNumber.grid(row = 25, column = 0)


    #Used as lambda function for next and foward buttons, takes start index and direction of travel
    def resultOutputerFunc(start, dir):


        #Increments start value of index by either +20 or -20 depending on scrolling and if not end of page
        if dir==1 and startValue[0]<len(outPutRows)-20:
            startValue[0] = (start+20)
        elif dir==-1 and startValue[0]!=0:
            startValue[0] = (start-20)

        #Handels last page to not go out of bounds
        count = 20
        if startValue[0]+20 > len(outPutRows):
            count = len(outPutRows)%20
        #Else needed to reset if go to back page
        else:
            count = 20

        #Prints results into grid.
        rows = []
        for r in range(20):

            cols = []

            for c in range(2):

                e = Entry(vCButtonFrame, relief=GROOVE, font=("Segoe UI", 15))
                
                e.grid(row=r+1, column=c, sticky=NSEW)

                #If end of list, values are overridden with blank space
                if count-r > 0:
                    e.insert(END, "%s" % ((outPutRows[r+startValue[0]])[c]))
                else:
                    e.insert(END, '')

                e['state'] = "readonly"
                cols.append(e)

            rows.append(cols)

        #Updates page number
        vCPageNumber.config(text= ("Page number: %d / %d" % ((((startValue[0] / 20)+1),  totPages))))

        #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    #Next and back buttons created, 1 means foward and -1 means backwards
    nextButton = Button(vCButtonFrame, text="Next Page", font=("Segoe UI", 15), command = lambda: resultOutputerFunc(int(startValue[0]), 1))
    backButton = Button(vCButtonFrame, text="Previous Page", font=("Segoe UI", 15), command= lambda: resultOutputerFunc(int(startValue[0]), -1))
    nextButton.grid(row = 25, column = 2)
    backButton.grid(row = 25, column = 1)
    
    #Initial load of table
    resultOutputerFunc(0, 0)

    mycursor.close()











def vPButtonFunc():#function of the button to view Products
    clearOutPutWindow()
    vPButtonFrame = Frame(outPutFrame)
    vPButtonFrame.grid(row = 1, column = 2)
    
    Label(vPButtonFrame, text="Product Name:", font=("Segoe UI", 15)).grid(row = 0, column = 0)
    Label(vPButtonFrame, text="Product ID", font=("Segoe UI", 15)).grid(row = 0, column = 1)
    Label(vPButtonFrame, text="Category:", font=("Segoe UI", 15)).grid(row = 0, column = 2)
    Label(vPButtonFrame, text="Sub Category", font=("Segoe UI", 15)).grid(row = 0, column = 3)

    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM products")
    outPutRows = mycursor.fetchall()

    #Gets Total Number of Pages
    totPages = (int(len(outPutRows)/20)+1)

    #Start value list used to allow acsess withen function and outside
    startValue = []
    startValue.append(0)

    #Page number label
    vPPageNumber = Label(vPButtonFrame, text=("Page number: 1 / %d" % totPages), font=("Segoe UI", 15))
    vPPageNumber.grid(row = 25, column = 0)




    #Displays the result page
    def resultOutputerFunc(start, dir):

        #Checks if trying to progress foward or back one page
        if dir==1 and startValue[0]<len(outPutRows)-20:
            startValue[0] = (start+20)
        elif dir==-1 and startValue[0]!=0:
            startValue[0] = (start-20)

        #Count set by deault to 20 unless the last page where its set to remaining elements
        count = 20
        if startValue[0]+20 > len(outPutRows):
            count = len(outPutRows)%20

        #For every row we want to display, and each column, new entry is created to display
        rows = []
        for r in range(20):

            cols = []

            for c in range(4):

                e = Entry(vPButtonFrame, relief=GROOVE, font=("Segoe UI", 15))
                
                e.grid(row=r+1, column=c, sticky=NSEW)
                if count-r > 0:
                    e.insert(END, "%s" % ((outPutRows[r+startValue[0]])[c]))
                else:
                    e.insert(END, '')
                e['state'] = "readonly"
                cols.append(e)

            rows.append(cols)

        #Page number updated
        vPPageNumber.config(text= ("Page number: %d / %d" % ((((startValue[0] / 20)+1),  totPages))), font=("Segoe UI", 15))



    #Buttons to move foward one and back one
    nextButton = Button(vPButtonFrame, text="Next Page", font=("Segoe UI", 15), command = lambda: resultOutputerFunc(int(startValue[0]), 1))
    backButton = Button(vPButtonFrame, text="Previous Page", font=("Segoe UI", 15), command= lambda: resultOutputerFunc(int(startValue[0]), -1))
    nextButton.grid(row = 25, column = 3)
    backButton.grid(row = 25, column = 2)

    #Initilazies first page  
    resultOutputerFunc(0, 0)


    mycursor.close()









def vOLButtonFunc(): #Function to view Order Logs
    clearOutPutWindow()
    vOLButtonFrame = Frame(outPutFrame)
    vOLButtonFrame.grid(row = 1, column = 2)

    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM orders")
    outPutRows = mycursor.fetchall()

    #Gets Total Number of Pages
    totPages = (int(len(outPutRows)/25)+1)

    #Start value list used to allow acsess withen function and outside
    startValue = []
    startValue.append(0)

    #Page number label
    vOLPageNumber = Label(vOLButtonFrame, text=("Page number: 1 / %d" % totPages), font=("Segoe UI", 15))
    vOLPageNumber.grid(row = 30, column = 0)


    #Displays the result page
    def resultOutputerFunc(start, dir):

        #Headers for Columns
        Label(vOLButtonFrame, text="Order ID", font=("Segoe UI", 10)).grid(row = 0, column = 0)
        Label(vOLButtonFrame, text="Product ID", font=("Segoe UI", 10)).grid(row = 0, column = 1)
        Label(vOLButtonFrame, text="Customer ID", font=("Segoe UI", 10)).grid(row = 0, column = 2)
        Label(vOLButtonFrame, text="Date Ordered", font=("Segoe UI", 10)).grid(row = 0, column = 3)
        Label(vOLButtonFrame, text="Date Shipped", font=("Segoe UI", 10)).grid(row = 0, column = 4)
        Label(vOLButtonFrame, text="Shipping Class", font=("Segoe UI", 10)).grid(row = 0, column = 5)
        Label(vOLButtonFrame, text="Segment", font=("Segoe UI", 10)).grid(row = 0, column = 6)
        Label(vOLButtonFrame, text="Country", font=("Segoe UI", 10)).grid(row = 0, column = 7)
        Label(vOLButtonFrame, text="City", font=("Segoe UI", 10)).grid(row = 0, column = 8)
        Label(vOLButtonFrame, text="State", font=("Segoe UI", 10)).grid(row = 0, column = 9)
        Label(vOLButtonFrame, text="Region", font=("Segoe UI", 10)).grid(row = 0, column = 10)
        Label(vOLButtonFrame, text="Zip", font=("Segoe UI", 10),).grid(row = 0, column = 11)

        #Checks if trying to progress foward or back one page
        if dir==1 and startValue[0]<len(outPutRows)-25:
            startValue[0] = (start+25)
        elif dir==-1 and startValue[0]!=0:
            startValue[0] = (start-25)

        #Count set by deault to 25 unless the last page where its set to remaining elements
        count = 25
        if startValue[0]+25 > len(outPutRows):
            count = len(outPutRows)%25

        #For every row we want to display, and each column, new entry is created to display
        #Being Entierlly Frank I have no clue what rows and cols is used for but removing them breaks this function.
        rows = []
        for r in range(25):

            cols = []

            for c in range(12):

            
                if c <= 9:
                    e = Entry(vOLButtonFrame, font=("Segoe UI", 8), width = 16)
                else:
                    e = Entry(vOLButtonFrame, font=("Segoe UI", 8), width = 8)

                e.grid(row=r+1, column=c, sticky=NSEW)
                #If not empty value fill with curr value
                if count-r > 0:
                    e.insert(END, "%s" % ((outPutRows[r+startValue[0]])[c]))
                #If empty fill with blanks
                else:
                    e.insert(END, '')
                e['state'] = "readonly"
                cols.append(e)

            rows.append(cols)

        #Page number updated
        vOLPageNumber.config(text= ("Page number: %d / %d" % ((((startValue[0] / 20)+1),  totPages))), font=("Segoe UI", 8))



    #Buttons to move foward one and back one
    nextButton = Button(vOLButtonFrame, text="Next Page", font=("Segoe UI", 10), command = lambda: resultOutputerFunc(int(startValue[0]), 1))
    backButton = Button(vOLButtonFrame, text="Previous Page", font=("Segoe UI", 10), command= lambda: resultOutputerFunc(int(startValue[0]), -1))
    nextButton.grid(row = 30, column = 2)
    backButton.grid(row = 30, column = 1)

    #Initilazies first page  
    resultOutputerFunc(0, 0)


    mycursor.close()









def sCButtonFunc(): #Function to search customers
    clearOutPutWindow()
    sCButtonFrame = Frame(outPutFrame)
    sCButtonFrame.grid(row = 1, column = 2)


    Label(sCButtonFrame, text='Customer Name/ID', font=("Segoe UI", 15), justify=RIGHT).grid(row=1, column = 1) 
    

    #entry box for names
    nameEntry = Entry(sCButtonFrame, font=("Segoe UI", 15)) 
    nameEntry.grid(row=1, column=2) 
 
    
    outputLabel1 = Label(sCButtonFrame, text = '', font=("Segoe UI", 15))
    outputLabel1.grid(row=5, column = 1)

    outputLabel2 = Label(sCButtonFrame, text = '', font=("Segoe UI", 15))
    outputLabel2.grid(row=5, column = 2)



    def submitButtonFunc():
        #Checks if value empty
        if nameEntry.get() == '':
            outputLabel1.config(text = "Please enter Value")
            return 0


        #Sets list to entered value of ent1
        val = (nameEntry.get(), nameEntry.get())

        mycursor = mydb.cursor()

        #Searches for names that have it either in first or last and any customer ID that matches input ID
        mycursor.execute("SELECT * FROM customers WHERE (customerName LIKE %s || customerID LIKE %s)", val)
        rows = mycursor.fetchall() 

        #checks if actually in DB
        if len(rows)==0:
            outputLabel1.config(text = "No Results Found")
        else:
            outPutText = "" 
            for i in range(len(rows)):
                if i < 5:
                    outPutText += ("Name: %s\n ID: %s\n\n" % (rows[i][1], rows[i][0]))

            outputLabel1.config(text = outPutText)

        mycursor.close()
        nameEntry.delete(0,last=END)

    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    ent3 = Button(sCButtonFrame, text='Submit', font=("Segoe UI", 15), command=submitButtonFunc).grid(row=4, column = 2)
    
# -=-=-=-==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-    
    





def sPButtonFunc():
    clearOutPutWindow()
    sPButtonFrame = Frame(outPutFrame)
    sPButtonFrame.grid(row = 1, column = 2)


    Label(sPButtonFrame, text='Product Name/ID', font=("Segoe UI", 15), justify=RIGHT).grid(row=1, column = 1) 
    

    #Entry box 
    nameEntry = Entry(sPButtonFrame, font=("Segoe UI", 15)) 
    nameEntry.grid(row=1, column=2) 
 
    #Label for output
    outputLabel = Label(sPButtonFrame, text = '', font=("Segoe UI", 15))
    outputLabel.grid(row=5, column = 1)
    
    def submitButtonFunc():
        #Checks if value empty
        if nameEntry.get() == '':
            outputLabel.config(text = "Please enter Value")
            return 0

        val = (nameEntry.get(), nameEntry.get())

        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM products WHERE (productName =  %s || productID = %s);", val)
        rows = mycursor.fetchall()

        if len(rows)==0:
            outputLabel.config(text = "No Results Found")
        else:
            outputLabel.config(text = ("Product Name: %s\nProduct ID: %s\nCategory: %s\nSub Category: %s") % (rows[0][0], rows[0][1], rows[0][2], rows[0][3]))

        mycursor.close()
        nameEntry.delete(0,last=END)


    ent3 = Button(sPButtonFrame, text='Submit', font=("Segoe UI", 15) , command=submitButtonFunc).grid(row=4, column = 2)









def dCButtonFunc():
    clearOutPutWindow()
    dCButtonFrame = Frame(outPutFrame)
    dCButtonFrame.grid(row = 1, column = 1)

    #Label and entry widgits
    Label(dCButtonFrame, text = "Enter Customer ID To Remove: ", font=("Segoe UI", 15)).grid(row = 0, column = 0)
    selectedCustomer = Entry(dCButtonFrame, font=("Segoe UI", 15)   )
    selectedCustomer.grid(row = 0, column = 1)
    Label(dCButtonFrame, text = "WARNING, Will Cascade", font=("Segoe UI", 10) ).grid(row = 1, column = 0)


    def submitButtonFunc():
        mycursor = mydb.cursor()
        #Takes input from Entry box and ensures following format using REGEX
        if re.search("^[A-Z]{2}[-]{1}[0-9]{5}$" , selectedCustomer.get()) == None:
            popupwin("Please Input Proper Customer ID")
            return 0

        #Used to check if value actually exsits instead of giving garbage query 
        mycursor.execute("SELECT * FROM customers WHERE customerID = '%s'" % selectedCustomer.get())
        IDs = mycursor.fetchall()


        #Checks if value found and removes then prompts popup message
        if len(IDs)>0:
            mycursor.execute("DELETE FROM customers WHERE customerID = '%s'" % selectedCustomer.get())
            popupwin("Customer Name: {} \nCustomer ID: {} \ndeleted from the Database".format(IDs[0][1], selectedCustomer.get()))

        else:
            popupwin("Customer ID not found")
            
        selectedCustomer.delete(0, END)    
        mycursor.close()
            
    
    Button(dCButtonFrame, text = 'Submit', font=("Segoe UI", 15), command = submitButtonFunc).grid(row = 1, column = 1)










def dPButtonFunc():
    clearOutPutWindow()
    dPButtonFrame = Frame(outPutFrame)
    dPButtonFrame.grid(row = 1, column = 1)
    Label(dPButtonFrame, text = "Enter Product ID To Remove: ", font=("Segoe UI", 15) ).grid(row = 0, column = 0)
    selectedProduct = Entry(dPButtonFrame, font=("Segoe UI", 15))
    selectedProduct.grid(row = 0, column = 1)
    Label(dPButtonFrame, text = "WARNING, Will Cascade", font=("Segoe UI", 10) ).grid(row = 1, column = 0)

    def submitButtonFunc():
        mycursor = mydb.cursor()
        #Regex ensures proper formating of ID 
        if re.search("^[A-Z]{3}[-]{1}[A-Z]{2}[-]{1}[0-9]{8}$" , selectedProduct.get()) == None:
            popupwin("Please Input Proper Product ID")
            return 0

        #No issues with duplication as productID unique 
        mycursor.execute("SELECT * FROM products WHERE productID = %s" % selectedProduct.get())
        IDs = mycursor.fetchall()

        #Checks if value actally found then removes and prompts popup
        if len(IDs)>0:
            mycursor.execute("DELETE FROM products WHERE productID = %s" % selectedProduct.get())
            popupwin("Product Name: {}  \nProduct ID: {} \nDeleted from the Database".format(IDs[0][0], selectedProduct.get()))

        else:
            popupwin("Product ID not found")
            
        selectedProduct.delete(0, END)    
        mycursor.close()

    Button(dPButtonFrame, text = 'Submit', font=("Segoe UI", 15) , command = submitButtonFunc).grid(row = 1, column = 1)    








def dOLButtonFunc(): #Delete Order Log
    clearOutPutWindow()
    dOLButtonFrame = Frame(outPutFrame)
    dOLButtonFrame.grid(row = 1, column = 1)
    Label(dOLButtonFrame, text = "Enter Order ID To Remove: ", font=("Segoe UI", 15) ).grid(row = 0, column = 0)
    selectedOrderID = Entry(dOLButtonFrame, font=("Segoe UI", 15))
    selectedOrderID.grid(row = 0, column = 1)
    Label(dOLButtonFrame, text = "Enter Product ID In Assocation with Order: ", font=("Segoe UI", 12)).grid(row = 1, column = 0)
    selectedProductID = Entry(dOLButtonFrame, font=("Segoe UI", 15))
    selectedProductID.grid(row = 1, column = 1)
    Label(dOLButtonFrame, text = "WARNING, Will Cascade", font=("Segoe UI", 10) ).grid(row = 2, column = 0)

    def submitButtonFunc():
        mycursor = mydb.cursor()

        if selectedOrderID.get() == "" or selectedProductID.get() == "":
            popupwin("Please Input All Values")
            return 0


    # US-2017-147655 {For reference to regex}
        if re.search("[A-Z]{2}[-]{1}[0-9]{4}[-]{1}[0-9]{6}" , selectedOrderID.get()) == None or re.search("^[A-Z]{3}[-]{1}[A-Z]{2}[-]{1}[0-9]{8}$" , selectedProductID.get()) == None:
             popupwin("You Have Input An Improper Value")
             return 0

        mycursor.execute("SELECT * FROM orders WHERE OrderID = %s AND Products_productID = %s", (selectedOrderID.get(), selectedProductID.get()))
        orderLog = mycursor.fetchall()

        if len(orderLog)>0:
            print(selectedProductID.get())
            mycursor.execute("DELETE FROM orders WHERE OrderID = %s AND Products_productID = %s", (selectedOrderID.get(), selectedProductID.get()))
            popupwin("Order ID: {}  \nProduct ID: {} \nCustomer ID: {}\nDeleted from the Database".format(selectedOrderID.get(), selectedProductID.get(),orderLog[0][2]))

        else:
            popupwin("Order Log Not Found")
   
        selectedProductID.delete(0, END)
        selectedOrderID.delete(0, END)     

        mycursor.close()


    Button(dOLButtonFrame, text = 'Submit', font=("Segoe UI", 15) , command = submitButtonFunc).grid(row = 2, column = 1)    













#Creates buttons and formats them
selectionLable = tk.Label(win, text="Please Choose a Selection", font=("Segoe UI", 20, BOLD))
selectionButtons = tk.Frame(win, bg='light blue')
aNCButton = tk.Button(selectionButtons, text="Add New Customer", font=("Segoe UI", 15), command=aNCButtonFunc)
aNCButton.pack(fill='both')
aNPButton = tk.Button(selectionButtons, text="Add New Product", font=("Segoe UI", 15), command = aNPButtonFunc)
aNPButton.pack(fill='both')
aNOLButton = tk.Button(selectionButtons, text="Add New Order Log", font=("Segoe UI", 15), command = aNOLButtonFunc)
aNOLButton.pack(fill='both')
vCButton = tk.Button(selectionButtons, text="View Customers", font=("Segoe UI", 15), command = vCButtonFunc)
vCButton.pack(fill='both')
vPButton = tk.Button(selectionButtons, text="View Products", font=("Segoe UI", 15), command = vPButtonFunc)
vPButton.pack(fill='both')
vOLButton = tk.Button(selectionButtons, text="View Orders", font=("Segoe UI", 15), command = vOLButtonFunc)
vOLButton.pack(fill='both')
sCButton = tk.Button(selectionButtons, text="Search Customers", font=("Segoe UI", 15), command = sCButtonFunc)
sCButton.pack(fill='both')
sPButton = tk.Button(selectionButtons, text="Search Products", font=("Segoe UI", 15), command = sPButtonFunc)
sPButton.pack(fill='both')
dCButton = tk.Button(selectionButtons, text="Remove Customer", font=("Segoe UI", 15), command = dCButtonFunc) 
dCButton.pack(fill='both')
dPButton = tk.Button(selectionButtons, text="Remove Product", font=("Segoe UI", 15), command = dPButtonFunc) 
dPButton.pack(fill='both')
dOLButton = tk.Button(selectionButtons, text="Remove Order", font=("Segoe UI", 15), command = dOLButtonFunc) 
dOLButton.pack(fill='both')
cButton = tk.Button(selectionButtons, text="Clear Window", font=("Segoe UI", 15), command = clearOutPutWindow)
cButton.pack(fill='both')

selectionLable.grid(row=0, column=0, pady = 10)
selectionButtons.grid(row=1, column=0, stick = "news") #sticky='news'
selectionButtons.grid_rowconfigure(0, weight=1)
selectionButtons.grid_columnconfigure(0, weight=1)



win.mainloop()