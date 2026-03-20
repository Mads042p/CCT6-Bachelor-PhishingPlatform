import sqlite3

conn = sqlite3.connect("db.db")
cursor = conn.cursor()

tableName = "UserData"
coloums = ("Name", "Email", "Password", "Company Relation", "IsAdmin")
email = "JohJohnsen@gmail.com"

def InsertData(tableName, data):
    query = f"INSERT INTO {tableName} (Name, Email, Password, Company, IsAdmin) VALUES (?, ?, ?, ?, ?);"
    cursor.execute(query, data)
    conn.commit()

def GetData(tableName):
    query = f"SELECT * FROM {tableName}"
    cursor.execute(query)
    return cursor.fetchall()

def DeleteData(tableName, email):
    
    query = f"DELETE FROM {tableName} WHERE Email = ?;"
    cursor.execute(query, (email,))
    conn.commit()
    
    
def getHashedPassword(tableName, email):
    
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