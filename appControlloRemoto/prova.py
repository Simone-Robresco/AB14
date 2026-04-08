import sqlite3

conn = sqlite3.connect("./istruzioniAlpha.db")
cursor = conn.cursor()

comando = "'triangolo'"

cursor.execute("SELECT cod FROM istruzioni WHERE nome = "+comando+";")

fetch = cursor.fetchall()
print(fetch[0][0])