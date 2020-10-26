from configparser import ConfigParser
import discord
from discord.ext import commands

#read config file
config_object = ConfigParser()


config_object.read("config.ini")

serverinfo = config_object["SERVERCONFIG"]


client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('bot is ready')


@client.event
async def on_member_join(member):
    None

#add game to playable list
@client.command()
async def add(ctx, game):
    await ctx.send("added {} {}".format(ctx.author, game))


@client.command()
async def summon(ctx, game):
    await ctx.send("summoning people for {}".format(game))

client.run(serverinfo['clientid'])