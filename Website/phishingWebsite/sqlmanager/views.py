from django.shortcuts import render
import sqlite3
import json

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

def getQuiz(quizID):
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()    

    query = """SELECT Question
               FROM Quiz
               WHERE QuizID = ?"""
    cursor.execute(query, (quizID,))
    
    rows = cursor.fetchall()
    conn.close()

    # Convert each row's JSON string into a dict
    quiz_list = [json.loads(row[0]) for row in rows]

    return quiz_list

def upsertScore(UserID, SourceID, Score, DateTaken):
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()    
    query = f"""INSERT INTO UserPoints (UserID, SourceID, Score, DateTaken)                
                Values (?, ?, ?, ?)
                ON CONFLICT(UserID, SourceID)
                DO UPDATE SET
                    Score = excluded.Score,
                    DateTaken = excluded.DateTaken"""
    cursor.execute(query, (UserID, SourceID, Score, DateTaken,))
    conn.commit()
    conn.close()

def getScore(UserID, SourceID):
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()    
    query = f"""SELECT Score
                FROM UserPoints
                WHERE UserID = ? AND SourceID = ?"""
    cursor.execute(query, (UserID, SourceID,))
    conn.commit()
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None