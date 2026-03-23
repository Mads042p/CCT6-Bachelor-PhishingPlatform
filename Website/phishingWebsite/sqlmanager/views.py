from django.shortcuts import render
import sqlite3

def cursorConnect():
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()
    
    return conn, cursor
    

def InsertData(tableName, data):
    conn, cursor = cursorConnect()
    print("From SQL:", data)
    query = f"INSERT INTO {tableName} (Name, Email, Password, Company, IsAdmin) VALUES (?, ?, ?, ?, ?);"
    cursor.execute(query, data)
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
    query = f"SELECT Password FROM {tableName} WHERE Email = ?;"
    cursor.execute(query, (email,))
    conn.commit()
    x = cursor.fetchall()[0][0]
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