import sqlite3

#Establish the connection and the cursor to the database
conn = sqlite3.connect("db.db")
cursor = conn.cursor()

#Harcode the dashboard, since ther's only one.
tableName = "UserData"

#Insert data into the DB, using parameterized quries
def InsertData(tableName, data):
    query = f"INSERT INTO {tableName} (Name, Email, Password, Company, IsAdmin) VALUES (?, ?, ?, ?, ?);"
    cursor.execute(query, data)
    conn.commit()

#Get the data from the database, based on their email. This returns an array with all of their information.
def GetData(tableName):
    query = f"SELECT * FROM {tableName}"
    cursor.execute(query)
    return cursor.fetchall()

#Delete a row, based on the users email.
def DeleteData(tableName, email):
    
    query = f"DELETE FROM {tableName} WHERE Email = ?;"
    cursor.execute(query, (email,))
    conn.commit()
    
#Get the hashed password, which is used for authentication in the login phase.
def getHashedPassword(tableName, email):
    
    query = f"SELECT Password FROM {tableName} WHERE Email = ?;"
    cursor.execute(query, (email,))
    conn.commit()
    
    return cursor.fetchall()[0][0]