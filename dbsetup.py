import sqlite3

value = input('Are you sure you want to run this. it will erase all current data (y/n)')
if value == 'n':
    exit


conn = sqlite3.connect('data.db')

c = conn.cursor()
c.execute("""
    DROP TABLE IF EXISTS users;
    """)

c.execute("""
    DROP TABLE IF EXISTS games;
    """)

c.execute("""
    DROP TABLE IF EXISTS usergame;
    """)

c.execute("""CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name text unique,
    userid int
    )
    """)

c.execute("""CREATE TABLE usergame (
    id INTEGER PRIMARY KEY,
    userid int,
    gameid int
    )
   """)


c.execute("""CREATE TABLE games (
    id INTEGER PRIMARY KEY,
    name blob unique,
    minplayer int,
    maxplayer int,
    client blob,
    ranked bool
    )
    """)


conn.commit()

conn.close()

