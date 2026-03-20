from django.shortcuts import render
import sqlite3

def cursorConnect():
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()
    
    return conn, cursor
    

tableName = "UserData"
coloums = ("Name", "Email", "Password", "Company Relation", "IsAdmin")
email = "JohJohnsen@gmail.com"

def InsertData(tableName, data):
    conn, cursor = cursorConnect()
    query = f"INSERT INTO {tableName} (Name, Email, Password, Company, IsAdmin) VALUES (?, ?, ?, ?, ?);"
    cursor.execute(query, data)
    conn.commit()
    conn.close()

def GetData(tableName):
    conn, cursor = cursorConnect()
    query = f"SELECT * FROM {tableName}"
    cursor.execute(query)
    conn.close()
    return cursor.fetchall()

def DeleteData(tableName, email):
    conn, cursor = cursorConnect()
    query = f"DELETE FROM {tableName} WHERE Email = ?;"
    cursor.execute(query, (email,))
    conn.commit()
    conn.close()
    
    
def getHashedPassword(tableName, email):
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()    
    query = f"SELECT Password FROM {tableName} WHERE Email = ?;"
    cursor.execute(query, (email,))
    conn.commit()
    
    
    return cursor.fetchall()[0][0]


def main():
    #InsertData(tableName, data)
    #DeleteData(tableName, email)
    print(getHashedPassword(tableName, email))
    

    """TableData = GetData(tableName)
    for row in TableData:
        print("\n")
        print(row)
    """
    
    
if __name__ == "__main__":
    main()
