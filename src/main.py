#!/usr/bin/env python
from random import choice
from random import randint
from time import gmtime
from time import strftime

import discord
from discord.ext import commands

from bot import BotWrapper
from utils import format_audio
from settings import *


bot = BotWrapper(command_prefix=PREFIX, description=DESC, activity=ACTIVITY)


@bot.event
async def on_connect():
    print("Startup latency: {}ms\n".format(int(bot.latency * 1000)))
    print(f"hlaskyList:         {len(bot.hlaskyList)}")
    print(f"rejoinList:         {len(bot.rejoinList)}")
    print(f"audioList:          {len(bot.audioList)}")
    print("\nAUDIO:")
    print("  " + format_audio(bot.audioList).replace("\n", "\n  "))

@bot.event
async def on_ready():
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    print("\033[92mREADY\033[0m")

## COMMANDS ####################################################################

@bot.command()
async def wtf(context):
    """
    Ukáže humor
    """
    msg = choice(bot.hlaskyList)
    msg = msg.replace(NEWLINE, "\n")

    # Pokud se ve zprave nachazi `FILEEXT`, tak posleme nejaky soubor
    if msg.count(FILEEXT) >= 1:
        msplit = msg.split(FILEEXT)
        msg = FILEEXT.join(msplit[:-1])
        fileName = discord.File(f"{PICDIR}/" + msplit[-1].strip())
    else:
        fileName = None

    await context.send(msg, file=fileName)


@bot.command()
async def count(context):
    """
    Spočítá humor
    """
    await context.send(str(len(bot.hlaskyList)))

@bot.command()
async def gank(context, *args):
    """
    Gankne ti voice chat
    """
    # Pokud nekdo posle ID nejakeho voice chatu, gankne dany voice chat
    if len(args) == 1:
        try:
            voiceChannel = discord.utils.get(
                context.guild.voice_channels,
                id=int(args[0])
            )
        except:
            return
    # Jinak bez ID to gankne ten voice chat, ve kterem se nachazi autor zpravy
    elif context.author.voice is not None:
        voiceChannel = context.author.voice.channel

    # Bot se nesmi jiz nachazet v nejakem voice chatu
    if bot.currentVoiceClient is not None:
        await context.send(choice(bot.rejoinList))
        return

    bot.currentVoiceClient  = await voiceChannel.connect()


@bot.command()
async def naga(context, *args):
    """
    Něco ti zahraje ve voice chatu
    """
    if len(args) == 0:
        message  = "Příklad: `bota naga 3`\n"
        message +=  '```\n'
        message += format_audio(bot.audioList)
        message += '```'

        await context.send(message)
        return

    if args[0] == "random":
        randomNumber = randint(1, len(bot.audioList) + 1)
        bot.play(randomNumber)
        return

    bot.play(args[0])


@bot.command()
async def feed(context):
    """
    Feedne ti voice chat
    """

    if bot.currentVoiceClient is not None:
        await bot.currentVoiceClient.disconnect()
        bot.currentVoiceClient  = None

################################################################################

bot.socket_server()

with open("TOKEN") as f:
    bot.run(f.read().strip())
