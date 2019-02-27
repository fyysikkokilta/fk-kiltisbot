import sqlite3

conn = sqlite3.connect('kiltis.db')

c = conn.cursor()

c.execute("""
            CREATE TABLE inventory
            (nimi text, hinta int, maara int)
            """)

c.execute("""
            CREATE TABLE users
            (id int, nick text, nimi text, saldo int)
            """)

c.execute("""
            CREATE TABLE transactions
            (user int, tuote text, hinta int, aika text)
            """)


#
# c.execute("INSERT INTO inventory VALUES ('Snickers', 70, 10)")

# tuotteet = [('Tupla', 60, 20),
#             ('Limu', 100, 40),
#             ('Nuudelit', 70, 7)]
#
# c.executemany("INSERT INTO inventory VALUES (?,?,?)", tuotteet)


tuotteet = [('Tupla', 60, 20),
            ('Limu', 100, 40),
            ('Nuudelit', 70, 7),
            ('Snickers', 70, 10)]

c.executemany("INSERT INTO inventory VALUES (?,?,?)", tuotteet)


conn.commit()
