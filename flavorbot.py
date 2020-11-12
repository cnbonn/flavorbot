from configparser import ConfigParser

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

import sqlite3
from sqlite3 import Error
import os
from os import environ


#read config file
config_object = ConfigParser()
config_object.read("config.ini")


serverinfo = config_object["SERVERCONFIG"]

#command prefix
client = commands.Bot(command_prefix = '!')

#database info
db = config_object["DBCONFIG"]

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(db['dbname'])
    except Error as e:
        print (e)

    return conn

@client.event
async def on_ready():
    print('bot is ready\n')
    
@client.event
async def on_member_join(member):
    None

@has_permissions(manage_roles=True, manage_channels=True)
@client.command(name='game', help='game add|remove <game>')
async def game(ctx, choice, *, gamename):
    if choice == 'add':
        conn = create_connection()
        c = conn.cursor()
        
        print("gamename: {}".format(gamename))
        try:
            c.execute("INSERT INTO games Values (?,?)", (None, gamename, ))
            conn.commit()
            await ctx.send('added {} to games list'.format(gamename))

        except Error as e:
            print(e)
            await ctx.send('{} already exists as a game'.format(gamename))
        
        conn.close()
        

    elif choice == 'delete':
        conn = create_connection()
        c = conn.cursor()
        try:
            c.execute("DELETE FROM games WHERE name = (?)", (gamename, ))
            conn.commit()
            await ctx.send('removed {} to games list'.format(gamename))
        except Error as e:
            await ctx.send('Game does not exist')

        conn.close()
        
    else:
        await ctx.send('invalid response')

@client.command(name='list', help='list games|users <game>')
async def list(ctx, choice, gamename = 'none'):
    #print list of games

    if choice == 'games':
        await ctx.send('---GAME LIST---')
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM games")
        items = c.fetchall()

        for item in items:
            await ctx.send(item[1])
        conn.commit()
        conn.close()    

    #print list of users
    elif choice == 'users':
        if gamename == 'none':
            await ctx.send('---USER LIST---')
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM users")
            users = c.fetchall()

            for user in users:
                await ctx.send("<{}>".format(user[1]))
            
            conn.commit()
            conn.close()
        #print list of users for a game
        else:
            conn = create_connection()
            c = conn.cursor()
            try:
                c.execute("""
                SELECT u.*
                FROM users u,
                     usergame ug,
                     games g
                WHERE g.name = ?
                AND g.rowid = ug.id
                AND ug.userid = u.rowid
                """, (gamename, ))

                userlist = c.fetchall()

                await ctx.send("--- USER LIST FOR {}---".format(gamename))
                for user in userlist:
                    await ctx.send("<{}>".format(user[1]))

            except Error as e:
                await ctx.send(e)

            conn.close()

    #invalid command
    else:
        await ctx.send('invalid response')

@client.command(name='register', help='register')
async def register(ctx):
    user = ctx.author
    uid = ctx.author.id

    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?,?,?)", (None, str(user), uid))
        conn.commit()
        await ctx.send('{} has been registered'.format(ctx.author))

    except Error:
        await ctx.send('{} has already been registered'.format(ctx.author))

    conn.close()
    
@client.command()
async def join(ctx, *, gamename):
    conn = create_connection()
    c = conn.cursor()
    userid = ctx.author
    try:
        c.execute("select * from users where name = ?", (str(userid), ))
        user = c.fetchone()
    except Error as e:
        print(e)
        await ctx.send("user is not registered")
        return 

    try:
        c.execute("select * from games where name = (?)", (gamename, ))
        game = c.fetchone()
    except Error as e:
        await ctx.send("Game does not exist")
        return

    try:
        c.execute("INSERT INTO usergame VALUES (?,?,?)", (None,user[0],game[0]))
        conn.commit()
        await ctx.send("{} added to {}".format(userid, gamename))
    except Error as e:
        print(e)

    conn.close()

@client.command()
async def leave(ctx, *, gamename):
    conn = create_connection()
    c = conn.cursor()
    userid = ctx.author
    try:
        c.execute("select * from users where name = ?", (str(userid), ))
        user = c.fetchone()
    except Error as e:
        print(e)
        await ctx.send("user is not registered")
        return 

    try:
        c.execute("select * from games where name = (?)", (gamename, ))
        game = c.fetchone()
    except Error as e:
        await ctx.send("Game does not exist")
        return

    try:
        c.execute("""DELETE FROM usergame WHERE userid = ? AND gameid = ?""", (user[0],game[0]))
        conn.commit()
        await ctx.send("{} removed from {}".format(userid, gamename))
    except Error as e:
        print(e)

    conn.close()

@client.command()
async def summon(ctx, *, gamename):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("""
        SELECT u.*
        FROM users u,
             usergame ug,
             games g
             WHERE g.name = ?
             AND g.rowid = ug.id
             AND ug.userid = u.rowid
             """, (gamename, ))

        userlist = c.fetchall()

        await ctx.send("summoning people for {}".format(gamename))

        for user in userlist:
            await ctx.send("<@!{}>".format(user[2]))

    except Error as e:
        await ctx.send(e)


#run bot
#client.run(serverinfo['clientid'])
client.run(os.getenv('BOT_TOKEN'))

