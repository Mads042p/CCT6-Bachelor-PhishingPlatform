from django.shortcuts import render
import sqlite3
import json

def cursorConnect():
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()
    
    return conn, cursor
    
# Command for inserting new data into the database.
def insertData(table_name, data):
    """Inserts data into the specified table securely using parameterized queries."""

    conn, cursor = cursorConnect()

    columns = ", ".join(data.keys())
    # Make the input from the user to a paremterized quiery using variabels.
    placeholders = ", ".join(["?" for _ in data])
    values = tuple(data.values())
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, values)
    conn.commit()
    conn.close()


def insertUserData(table_name, data):
    """Inserts user data into the specified table. If someone is the first to register with a company, they will be made admin. If not, they will be made a regular user."""

    conn, cursor = cursorConnect()

    columns = ", ".join(data.keys())
    # Make the input from the user to a paremterized quiery using variabels.
    placeholders = ", ".join(["?" for _ in data])
    values = tuple(data.values())
    query = f"""INSERT INTO {table_name} ({columns}, isAdmin) 
                VALUES ({placeholders}, 
                    CASE
                        WHEN EXISTS (SELECT 1 FROM {table_name} WHERE Company = ?)
                        THEN 0
                        ELSE 1
                    END
                )"""
    cursor.execute(query, (*values, data.get("company")))
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

def getUserCompanyScores(email):
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()
    
    query = """SELECT u.Email AS UserEmail, u.Name, SUM(up.Score) AS TotalScore
               FROM UserData u 
               JOIN UserPoints up ON u.ID = up.UserID
               WHERE u.Company = (SELECT Company FROM UserData WHERE Email = ?)
               GROUP BY u.Email, u.Name;"""
    
    cursor.execute(query, (email,))
    result = cursor.fetchall()
    conn.close()
    
    # Convert into JSON
    leaderboard_data = [
        {"name": row[1], "points": row[2]}  # row = (Email, Name, Score)
        for row in result
    ]

    print(leaderboard_data)
    return leaderboard_data

# ---------------- INDIVIDUAL ACHIEVEMENTS ----------------

def achTrainingComplete(UserID):
    """Achievement: Complete all training courses"""
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()    
    query = f"""INSERT OR IGNORE INTO UserAchievements (UserID, AchievementID)
                SELECT :uid, 1
                WHERE (
	                (SELECT COUNT(DISTINCT QuizID) FROM Quiz) = 
	                (SELECT COUNT(DISTINCT SourceID) FROM UserPoints WHERE UserID = :uid))"""
    cursor.execute(query, {"uid": UserID})
    conn.commit()
    conn.close()

def achAPlusStudent(UserID):
    """Achievement: Complete all training courses with 100% accuracy"""
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()    
    query = f"""INSERT OR IGNORE INTO UserAchievements (UserID, AchievementID)
                SELECT :uid, 2
                WHERE (
	                (SELECT COUNT(DISTINCT QuizID) FROM Quiz) = 
	                (SELECT COUNT(DISTINCT SourceID) FROM UserPoints WHERE UserID = :uid AND Score = 100))"""
    cursor.execute(query, {"uid": UserID})
    conn.commit()
    conn.close()

def achTheGameIsAfoot(UserID):
    """Achievement: Sign up for mailing list"""
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()    
    query = f"""INSERT OR IGNORE INTO UserAchievements (UserID, AchievementID)
                SELECT :uid, 3
                WHERE EXISTS(
	                SELECT email
	                FROM NewsletterEmails
	                WHERE email = (
		                SELECT Email FROM UserData WHERE ID = :uid))"""
    cursor.execute(query, {"uid": UserID})
    conn.commit()
    conn.close()

def achMaster(UserID):
    """Achievement: Reach top 3 in your company leaderboard"""
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()    
    query = f"""INSERT OR IGNORE INTO UserAchievements (UserID, AchievementID)
                SELECT :uid, 12
                WHERE :uid IN (
                    SELECT UP.UserID
                    FROM UserPoints UP
                    JOIN UserData UD ON UP.UserID = UD.ID
                    WHERE UD.Company = (
                        SELECT Company FROM UserData WHERE ID = :uid
                    )
                    GROUP BY UP.UserID
                    ORDER BY SUM(UP.Score) DESC
                    LIMIT 3)"""
    cursor.execute(query, {"uid": UserID})
    conn.commit()
    conn.close()