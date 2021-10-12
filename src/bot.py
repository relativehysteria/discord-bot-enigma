import socket
import threading
from time import gmtime
from time import strftime

import discord
from discord.ext import commands

from utils import get_list, get_dir
from settings import *


class BotWrapper(commands.Bot):
    # Trackuje botuv VC (muze byt vzdy pripojen pouze do jednoho VC najednou)
    currentVoiceClient  = None

    hlaskyList = get_list(f"{HLASKYPATH}")
    rejoinList = get_list(f"{REJOINPATH}")
    audioList  = get_dir(f"{AUDIODIR}")

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
            filename = self.audioList[int(filename)-1]
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
