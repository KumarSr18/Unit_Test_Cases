import uuid #for generating unique ids (Surrogate keys)
from datetime import datetime #for getting the current date and time
import pandas as pd
import pyodbc
import requests


#default args for the dag
#default_args = {
#    'owner': 'airscholar',  #owner of the dag
#    'start_date': datetime(2023, 9, 3, 10, 00)  #start date of the dag
#}

print("Getting the data from API (Random User)")
#fetching data from randomuser api
def get_data():
    res = requests.get("https://randomuser.me/api/")
    res = res.json()
    res = res['results'][0]
    return res

def format_data(res):
    data = {}
    location = res['location']
    data['id'] = uuid.uuid4()
    data['first_name'] = res['name']['first']
    data['last_name'] = res['name']['last']
    data['gender'] = res['gender']
    data['address'] = f"{str(location['street']['number'])} {location['street']['name']}, " \
                      f"{location['city']}, {location['state']}, {location['country']}"
    data['post_code'] = location['postcode']
    data['email'] = res['email']
    data['username'] = res['login']['username']
    data['dob'] = res['dob']['date']
    data['registered_date'] = res['registered']['date']
    data['phone'] = res['phone']
    data['picture'] = res['picture']['medium']
    return data  # Return the formatted data



#res = get_data()

# Format the data from the JSON response
#data = format_data(res)


def load(data):
    # Convert data to DataFrame
    df = pd.DataFrame([data])

    # Optionally, save DataFrame to CSV
    df.to_csv('file1.csv')

    print("Connecting to the SQL Server")
    # Connection string to connect to SQL Server
    conn_str = "Driver={SQL Server};Server=LAPTOP-CU043492\SQLEXPRESS;Database=master;Uid=KumarSr;Pwd=Srijivas@123;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    print("Inserting data into the SQL Server table")
    # Insert data into SQL Server table
    for index, row in df.iterrows():
        cursor.execute("""
            INSERT INTO RandomData (id, first_name, last_name, gender, address, post_code, email, username, dob, registered_date, phone, picture)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row['id'], row['first_name'], row['last_name'], row['gender'], row['address'],
             row['post_code'], row['email'], row['username'], row['dob'], row['registered_date'],
             row['phone'], row['picture'])
        conn.commit()

    print('Insertion complete')
    # Close the cursor and connection
    cursor.close()
    conn.close()

#print("Creating a DataFrame from the formatted data")
# Create a DataFrame from the formatted data
#df = pd.DataFrame([data])

#df.to_csv('file1.csv')

#print("Connecting the SQL Server")
# Connect to the SQL Server
#conn_str = "Driver={SQL Server};Server=LAPTOP-CU043492\SQLEXPRESS;Database=master;Uid=KumarSr;Pwd=Srijivas@123;"
#conn = pyodbc.connect(conn_str)
#cursor = conn.cursor()


#print("Inserting to the SQL Server table")
# Insert data into SQL Server table
#for index, row in df.iterrows():
#    cursor.execute("""
#        INSERT INTO RandomData (id, first_name, last_name, gender, address, post_code, email, username, dob, registered_date, phone, picture)
#        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#    """, data['id'], data['first_name'], data['last_name'], data['gender'], data['address'],
#         data['post_code'], data['email'], data['username'], data['dob'], data['registered_date'],
#         data['phone'], data['picture'])
#    conn.commit()
#print('insertion complete')

#cursor.close()
#conn.close()
   
def main():
    # Call get_data to fetch data
    data = get_data()
    
    # Call format_data to format the fetched data
    formatted_data = format_data(data)
    
    # Call load to load the formatted data into the database
    load(formatted_data)
    
    print("Data processing complete.")

if __name__ == "__main__":
    main()   