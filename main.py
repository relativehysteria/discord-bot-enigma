#!/usr/bin/env python
from random import choice
from time import gmtime
from time import strftime
import os
import socket
import threading

import discord
from discord.ext import commands
from discordID import discordID

## SETTINGS ####################################################################

# Bot nastaveni
PREFIX     = commands.when_mentioned_or("bota ")
DESC       = "Zeus, ult now!"
PICDIR     = "pics"
AUDIODIR   = "audio"
TXTDIR     = "txt"
FILEEXT    = "||"
ADMIN_ID   = [discordID["Ruziro"], discordID["Dement"]]
NEWLINE    = "NEWLINE"
SOCKETPORT = 11337

## MISC ########################################################################

def _sorted_ls(path):
    """
    `listdir`, ale serazeny podle data pridani (od nejstarsiho po nejnovejsi)
    """
    # https://stackoverflow.com/a/4500607
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))

def _get_list(file):
    """Nacte radky souboru do listu a vrati ho."""
    getList = list()
    with open(file) as f:
        for line in f:
            getList.append(line.strip())
    return getList


def _get_dict(directory):
    """
    Nacte soubory z nejakeho adresare do dictu a prilozi jim ID.
    Pouziva to `bota naga`
    """
    getDict = dict()
    counter = 1

    for i in _sorted_ls(directory):
        getDict[counter] = i
        counter += 1

    return getDict


def _format_audio() -> str:
    """
    Naformatuje hodnotu vracenou z `_get_dict()` tak, aby to bylo citelne.
    Pouziva to `bota naga`
    """
    message = ""
    for key in audioDict.keys():
        value = audioDict[key]
        value = value.replace(".mp3", "").replace("_", " ")
        message += f"{key}: {value}\n"
    return message

## BOT #########################################################################

class BotWrapper(commands.Bot):
    # Trackuje botuv VC (muze byt vzdy pripojen pouze do jednoho VC najednou)
    currentVoiceClient  = None

    async def on_message(self, message):
        # Nezajimame se o boty
        if message.author.bot:
            return
        await self.process_commands(message)


    def play(self, filename: str) -> None:
        if self.currentVoiceClient is None:
            return

        if self.currentVoiceClient.is_playing:
            self.currentVoiceClient.stop()

        try:
            filename = audioDict[int(filename)]
        except:
            filename = filename

        print(f'\033[36m{strftime("%H:%M:%S", gmtime())} > {filename}\033[0m')
        filename = f"{AUDIODIR}/{filename}"

        self.currentVoiceClient.play(discord.FFmpegPCMAudio(filename))


    def socket_server(self) -> None:
        """
        Vytvori socket, na kterem bude poslouchat pro nazvy souboru, ktere
        jsou pote spusteny v `play`.
        """
        thread = threading.Thread(target=self._socket_listen)
        thread.start()
        # Zadny join neni potreba - tento socket posloucha nekonecne


    def _socket_listen(self) -> None:
        """
        Socket, na kterem bot posloucha pro `play` commandy
        Je to tady z duvodu, ze neni vzdycky cas napsat do discordu
        `bota naga x`, ale vetsinou je cas na nejaky keybind. :)
        """
        s = socket.create_server(("localhost", SOCKETPORT))
        while True:
            s.listen(1)
            conn, _ = s.accept()
            while True:
                data = conn.recv(1024)
                if not data: break

                print(f"Socket: \033[36m{data.decode()}\033[0m")
                if not self.currentVoiceClient:
                    print("\033[31mcurrentVoiceClient = None\033[0m\n")
                    conn.sendall(b"currentVoiceClient = None")
                else:
                    self.play(data.decode())
                    conn.sendall(b"nice")


## GLOBAL SPACE ################################################################
_hlaskyFName         = f"{TXTDIR}/hlasky"
_rejoinFName         = f"{TXTDIR}/rejoin"

hlaskyList = _get_list(_hlaskyFName)
rejoinList = _get_list(_rejoinFName)

audioDict  = _get_dict(f"{AUDIODIR}")

activity = discord.Game("Techies mid")
bot = BotWrapper(command_prefix=PREFIX, description=DESC, activity=activity)

## READY #######################################################################

@bot.event
async def on_connect():
    print("Startup latency: {}ms\n".format(int(bot.latency * 1000)))
    print(f"hlaskyList:         {len(hlaskyList)}")
    print(f"rejoinList:         {len(rejoinList)}")
    print(f"audioDict:          {len(audioDict)}")
    print("\nAUDIO:")
    print("  " + _format_audio().replace("\n", "\n  "))

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
    msg = choice(hlaskyList)
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
    global hlaskyList
    await context.send(str(len(hlaskyList)))

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
        await context.send(choice(rejoinList))
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
        message += _format_audio()
        message += '```'

        await context.send(message)
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
