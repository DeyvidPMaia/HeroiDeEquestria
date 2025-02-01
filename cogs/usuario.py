import discord
from discord.ext import commands
import random
from discord import Embed, Interaction, ui
from globals import *
from paginacaoPersonagens import PaginacaoPersonagens

class Usuario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Salva aleatoriamente uma certa quantidade de personagens.")
    async def horoscopo(self, ctx):
        elementos = ["Fogo 🔥", "Água 💧", "Terra 🌍", "Ar 🌬️"]
        mensagens = [
            "Hoje é um bom dia para explorar novos horizontes!",
            "Sua criatividade estará em alta, use-a sabiamente.",
            "Cuidado com decisões impulsivas, respire fundo antes de agir.",
            "O universo está conspirando a seu favor!"
        ]

        elemento = random.choice(elementos)
        mensagem = random.choice(mensagens)

        await ctx.send(f"🔮 **Seu elemento do dia é {elemento}!**\n{mensagem}")


# Setup para registrar o cog
async def setup(bot):
    await bot.add_cog(Usuario(bot))
