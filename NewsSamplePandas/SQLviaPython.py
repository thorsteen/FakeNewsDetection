import psycopg2

conn = psycopg2.connect(database='test', user='kaspito', password='admin', host='localhost', port="5432")
cursor = conn.cursor()

cursor.execute('SELECT article_id FROM article')
table = cursor.fetchall()

for row in table:
  print("article id = ", str(row[0]))

conn.close()
