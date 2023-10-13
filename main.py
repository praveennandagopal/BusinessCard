import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import cv2
import pandas as pd
import numpy as np
import mysql as sql
import sqlalchemy as sa
from io import BytesIO


myHost ="localhost"
myUser="root"
myPassword = "password"
myDatabaseName = "BizCard"

try:
    engine =sa.create_engine("mysql+mysqlconnector://{}:{}@{}/{}".format(myUser,myPassword,myHost,myDatabaseName),echo=False)
    alchemyconnection = engine.connect()
except:
    pass


mydb = sql.connector.connect(
host=myHost,
user=myUser,
password=myPassword
)
mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE if not exists {}".format(myDatabaseName))
mycursor.execute("USE {}".format(myDatabaseName))
# Create a table to store the business card information
mycursor.execute('''CREATE TABLE IF NOT EXISTS Business_card 
              (id INT AUTO_INCREMENT PRIMARY KEY,
              name TEXT,
              position TEXT,
              address TEXT,
              pincode VARCHAR(25),
              phone VARCHAR(25),
              email TEXT,
              website TEXT,
              company TEXT
             
              )''')


with st.sidebar:
    selected =option_menu(
        menu_title=None,
        options= [ "Home", "Project"],
        icons=["house","book"],
        default_index=0,
    )
    
if selected == "Home":
    st.title ("Business Card Data Extraction")
    st.divider()
    st.write('<style>p {  font-style: italic;  font-size: 30px;</style>', unsafe_allow_html=True)
    
    st.markdown('''Developing a :green[Streamlit application] that allows users to
upload an image of a :green[business card and extract relevant information] from it using
:green[easyOCR]. The extracted information will be Stored in :green[ Mysql db] and we can Perform :green[CRUD operation]
    ''')
    
    
if selected == "Project":
    st.header (":blue[Extracting Business Card Data with OCR]")
    file_upload = st.file_uploader(":blue[Business Card :]",
                               type=["jpg", "jpeg", "png", "tiff", "tif", "gif"])
    
    data = ['Insert Data', 'Show Data', 'Update Card', 'Delete Data']
    st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    choose = st.radio("Select An Option", data)
      
      
    
    if choose == 'Insert Data':
        if file_upload == None:
            st.write("Please Upload Business Card ")
        else:
            image = cv2.imdecode(np.fromstring(file_upload.read(), np.uint8), 1)
            st.image(image, caption='Uploaded Successfully', use_column_width=True)

            reader = easyocr.Reader(['en'])
            if st.button('upload Data'):
                bsc = reader.readtext(image, detail=0)
                text = "\n".join(bsc)               
               
                # values = (bsc[0], bsc[1], bsc[2], bsc[3], bsc[4], bsc[5], bsc[6], bsc[7])
                sql_data = "INSERT INTO Business_card (name, position, address, pincode, phone, email, website, company) VALUES ( %s, %s,%s, %s,%s, %s,%s, %s)"
                values = (bsc[0], bsc[1], bsc[2], bsc[3], bsc[4], bsc[5], bsc[6], bsc[7])
                
                mycursor.execute(sql_data, values)
                mydb.commit()
                
                st.success("Data Inserted")


    if choose == 'Show Data':
        
        
        mycursor.execute("SELECT * FROM Business_card")
        result = mycursor.fetchall()
        df = pd.DataFrame(result,
                        columns=['id', 'name', 'position', 'address', 'pincode', 'phone', 'email', 'website', 'company'])
        st.write(df)
    
    if choose == 'Update Card':
        try:
            mycursor.execute("SELECT id, name FROM Business_card")
            result = mycursor.fetchall()
            business_cards = {}

            for row in result:
                business_cards[row[1]] = row[0]
            select_card_name = st.selectbox("Select Card To Edit", list(business_cards.keys()))

        
            mycursor.execute("SELECT * FROM Business_card WHERE name=%s", (select_card_name,))
            result = mycursor.fetchone()
            # image_bytes = bytes(result[9])
            # image_stream = BytesIO(image_bytes)
        
            name = st.text_input("Name", result[1])
            position = st.text_input("Position", result[2])
            address = st.text_input("Address", result[3])
            pincode = st.text_input("Pincode", result[4])
            phone = st.text_input("Phone", result[5])
            email = st.text_input("Email", result[6])
            website = st.text_input("Website", result[7])
            company = st.text_input("Company_Name", result[8])
        
            
            
            if st.button("Update"):
            
                mycursor.execute(
                    "UPDATE Business_card SET name=%s, position=%s, address=%s, pincode=%s, phone=%s, email=%s, website=%s, company=%s WHERE name=%s",
                    (name, position, address, pincode, phone, email, website, company, select_card_name))
                mydb.commit()
                st.success("Card Data Updated")
        except:
            pass
            
        
    if choose == 'Delete Data':
       
        mycursor.execute("SELECT id, name FROM Business_card")
        result = mycursor.fetchall()
        business_cards = {}

        for row in result:
            business_cards[row[1]] = row[0]
        select_card_name = st.selectbox("Select Card To Delete", list(business_cards.keys()))

        
        if st.button("Delete Card"):
            
            mycursor.execute("DELETE FROM Business_card WHERE name=%s", (select_card_name,))
            mydb.commit()
            st.success("Card Data Deleted")       

   
