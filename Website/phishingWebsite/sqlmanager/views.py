from django.shortcuts import render
import sqlite3

def cursorConnect():
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()
    
    return conn, cursor
    
# Command for inserting new data into the database.
def insertData(table_name, data):
    conn, cursor = cursorConnect()

    """Inserts data into the specified table securely using parameterized queries."""
    columns = ", ".join(data.keys())
    # Make the input from the user to a paremterized quiery using variabels.
    placeholders = ", ".join(["?" for _ in data])
    values = tuple(data.values())
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    

def GetData(tableName):
    conn, cursor = cursorConnect()
    query = f"SELECT * FROM {tableName}"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

def DeleteData(tableName, email):
    conn, cursor = cursorConnect()
    query = f"DELETE FROM {tableName} WHERE Email = ?;"
    cursor.execute(query, (email,))
    conn.commit()
    conn.close()
    
    
def getHashedPassword(tableName, email):
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()    
    query = f"SELECT * FROM {tableName} WHERE Email = ?;"
    cursor.execute(query, (email,))
    conn.commit()
    x = cursor.fetchall()[0]
    conn.close()

    return x 
    
def getUserAchievements(UserID):
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()    
    query = f"""SELECT *
                FROM Achievements A
                INNER JOIN UserAchievements UA
                ON A.AchievementID = UA.AchievementID
                WHERE UserID = ?"""
    cursor.execute(query, (UserID,))
    conn.commit()
    result = cursor.fetchall()
    conn.close()

    return result

def getEmployees(company):
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()    
    query = f"""SELECT ID, Name, Email
                FROM UserData
                WHERE Company = ?"""
    cursor.execute(query, (company,))
    conn.commit()
    result = cursor.fetchall()
    conn.close()

    return result