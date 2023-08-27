# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 12:35:12 2023

@author: Alan.G
"""

"""
   A     L            A     N   N       EEEEE   SSSS      U   U   N   N   BBBBB    OOO    TTTTTTT
  A A    L           A A    NN  N       E      S          U   U   NN  N   B   B   O   O      T
 AAAAA   L          AAAAA   N N N       EEEE    SSS       U   U   N N N   BBBBB   O   O      T
A     A  L         A     A  N  NN       E          S      U   U   N  NN   B   B   O   O      T
A     A  LLLLL     A     A  N   N       EEEEE   SSSS       UUU    N   N   BBBBB    OOO       T


Working bot on: https://discord.gg/e7pcsgxtwH

"""

import os  
import discord
import openai
from discord.ext import commands
import logging
import random
import asyncio

feedback_data = {
    "positive": 0,
    "negative": 0
}
# Configuración de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s', handlers=[logging.FileHandler('bot.log'), logging.StreamHandler()])
logging.debug("Importando las librerias...")

# Configuración de tokens y claves
openai.api_key = os.getenv('OPENAI_API_KEY')
logging.debug("OpenAI API key configurado.")

intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)
channel_context = {}

@bot.event
async def on_message(message):
    logging.debug("Entrando a la función on_message.")
    print(f"Mensaje recibido de {message.author}: {message.content}")

    if message.author == bot.user:
        return

    channel_id = message.channel.id
    channel_context.setdefault(channel_id, []).append(message.content)
    channel_context[channel_id] = channel_context[channel_id][-10:] # Limitando a los últimos 10 mensajes para mantener relevancia
    
    await bot.process_commands(message)
    # Si el mensaje no comienza con el prefijo del comando y se cumple una cierta probabilidad
    if not message.content.startswith(bot.command_prefix):
        probabilidad_respuesta = 0.2  # Probabilidad de 20% de enviar una respuesta basada en el contexto
        if random.random() < probabilidad_respuesta:
           await process_alan(message.channel, message.content)
    logging.debug("Saliendo de la función on_message.")


STOPWORDS = set([
    "a", "actualmente", "adelante", "además", "afirmó", "agregó", "ahora", 
    "ahí", "al", "algo", "alguna", "algunas", "alguno", "algunos", "algún", 
    "alrededor", "ambos", "ampleamos", "ante", "anterior", "antes", "apenas", 
    "aproximadamente", "aquel", "aquellas", "aquellos", "aqui", "aquí", "arriba", 
    "aseguró", "así", "atras", "aunque", "ayer", "añadió", "aún", "bajo", 
    "bastante", "bien","dan", "todo", "intenta", "usas", "podemos", "las", 
    "toda", "explicó", "manifestó", "última", "éstos", "intentar", "esos", 
    "debe", "dicen", "serían", "hacerlo", "hubieran", "estuvieras", "hubiera",
    "fueseis", "luego", "a", "tuviste", "tenidas", "voy", "parece", "solamente",
    "estuvierais", "buenos", "nosotras", "bastante", "diferentes", "habría",
    "junto", "están", "míos", "durante", "después", "dos", "pasado", "apenas",
    "había", "empleo", "propia", "habían", "demás", "eras", "mi", "fue", 
    # ... (puedes agregar más stopwords si es necesario)
])

def detectar_tema(mensaje):
    logging.debug("Entrando a la función detectar_tema.")
    palabras = mensaje.split()
    temas = [palabra.lower() for palabra in palabras if palabra.lower() not in STOPWORDS]
    logging.debug("Saliendo de la función detectar_tema.")
    return temas

FEEDBACK_EMOJIS = ["👍", "👎"]  # Puedes añadir o cambiar los emojis según tus necesidades


async def process_alan(ctx, pregunta: str):
    logging.debug("Entrando a la función process_alan.")
    #Este es una pequeña descripcion de como se comportará el bot y el como funcionará
    contexto_base = (
        "Alan es un estudiante de 18 años en México apasionado por la inteligencia artificial, "
        "videojuegos, música y socializar con amigos. Estudia ingeniería en Inteligencia artificial "
        "y es un ávido aprendiz. Ama las conversaciones profundas y ayuda a otros con sus conocimientos."
    )

    # Verifica si el contexto es un Contexto de Comando o un Canal de Texto
    if isinstance(ctx, commands.Context):
        channel_id = ctx.channel.id
    else:  # Si es un TextChannel
        channel_id = ctx.id

    historia = " ".join(channel_context[channel_id])
    temas_mensaje = detectar_tema(pregunta)
    contexto_tema = f"El usuario está discutiendo sobre: {' '.join(temas_mensaje)}." if temas_mensaje else ""

    # Creación del nuevo prompt
    prompt = f"Basado en el contexto: '{contexto_base} Conversación reciente: {historia}. {contexto_tema} Pregunta: '{pregunta}''. ¿Cómo responderías?"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.7
    )

    respuesta = response.choices[0].text.strip()

    # Procesar la respuesta para mejorarla
    mejoras = [
        ("Respondiendo a la pregunta, podría decir:", ""),
        ("Respondería:", ""),
        ("Yo respondería:", ""),
        ("R:", ""),
        ("Respuesta:", ""),
        
        # ... (puedes agregar más sustituciones si es necesario)
    ]
    for viejo, nuevo in mejoras:
        respuesta = respuesta.replace(viejo, nuevo)
    
    respuesta = respuesta.strip()  # Elimina cualquier espacio adicional después de las sustituciones
    

    if not respuesta or respuesta == ".":
        respuesta = "Lo siento, no sé cómo responder a eso. ¿Puedes ser más específico o intentar con otra pregunta?"

    respuestas_simples = {
        "hola": "¡Hola!, soy Alan ¿En qué puedo ayudarte?",
        "como estas": "Estoy bien, gracias por preguntar. ¿Y tú?",
        "que haces": "Estoy aquí para ayudarte y responder tus preguntas. ¿En qué puedo asistirte?",
        "jugar": "Me encantarí, puedo ayudarte con información sobre juegos si quieres.",
        "habla": "¡Claro! ¿Sobre qué tema te gustaría que hable?"
    }
    
    for key, value in respuestas_simples.items():
        if key in pregunta.lower():
            respuesta = value
            break

    # Enviar respuesta y añadir reacciones de feedback
    msg = await ctx.send(respuesta)
    for emoji in FEEDBACK_EMOJIS:
        await msg.add_reaction(emoji)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in FEEDBACK_EMOJIS

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        pass

    else:
       if str(reaction.emoji) == "👍":
          feedback_data["positive"] += 1
         
       elif str(reaction.emoji) == "👎":
          feedback_data["negative"] += 1
            

    
    
    logging.debug("Saliendo de la función process_alan.")


@bot.command(name='alan')
async def alan_command(ctx, *, pregunta: str):
    await process_alan(ctx, pregunta.lower())
    logging.debug(f"Processed command 'alan' with question '{pregunta}'.")
    

ADMIN_CODE = "Codigo secreto :0 "

@bot.command(name='admin')
@commands.is_owner()  # Solo permite que el propietario del bot use este comando (opcional pero recomendado)
async def admin_command(ctx, codigo: str, *, mensaje: str):
    """Envía un mensaje a un canal específico en todos los servidores."""
    if codigo != ADMIN_CODE:
        await ctx.send("Código incorrecto.")
        return

    nombre_del_canal = "general"  # Cambia esto por el nombre del canal al que deseas enviar el mensaje

    # Recorre todos los servidores donde se encuentra el bot
    for guild in bot.guilds:
        # Encuentra el canal por nombre
        channel = discord.utils.get(guild.text_channels, name=nombre_del_canal)
        
        # Si el canal existe, envía el mensaje
        if channel:
            await channel.send(mensaje)

    await ctx.send("Mensaje enviado correctamente.")
    
@bot.command(name='helpalan')
async def custom_help(ctx):
    embed = discord.Embed(
        title="Ayuda de Alan Bot",
        description="Aquí tienes una lista de los comandos disponibles:",
        color=0x00ff00
    )
    
    # Añadir comandos y sus descripciones al embed
    embed.add_field(name="!alan [pregunta]", value="Haz una pregunta y obtén una respuesta basada en el contexto de Alan.", inline=False)
    
    # Puedes añadir más comandos aquí si los tienes
    
    await ctx.send(embed=embed)
    

@bot.command(name='feedback')
@commands.is_owner()  # Solo permite que el propietario del bot use este comando (opcional pero recomendado)
async def view_feedback(ctx):
    embed = discord.Embed(
        title="Feedback acumulado",
        description=f"Positivo: {feedback_data['positive']}\nNegativo: {feedback_data['negative']}",
        color=0x00ff00
    )
    await ctx.send(embed=embed)
  #pon aqui tu Token de discord ;D
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
