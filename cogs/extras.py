import discord
from discord.ext import commands
import json
import os
import random

class Extras(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Gliss", help="Lista todos os comandos disponíveis.", hidden=True)
    async def gliss(self, ctx):
        """Responde com uma mensagem carinhosa."""
        await ctx.send("💫 **Gliss Fufita** 💫") 

    @commands.command(help="Expressa amor pelo usuário.")
    async def amor(self, ctx):
        """Responde com uma mensagem carinhosa sorteada de um arquivo JSON."""
        
        # Caminho do arquivo JSON
        caminho_arquivo = "resources/mensagens_carinhosas.json"
        
        # Verifica se o arquivo existe
        if os.path.exists(caminho_arquivo):
            # Abre o arquivo JSON e carrega os dados
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
            
            # Verifica se há mensagens no arquivo
            if "mensagens" in dados:
                mensagem = random.choice(dados["mensagens"])  # Sorteia uma mensagem
                await ctx.send(mensagem)
            else:
                await ctx.send("Ops! Não há mensagens carinhosas disponíveis no momento.")
        else:
            await ctx.send("Erro: O arquivo de mensagens carinhosas não foi encontrado.")


# Setup para registrar o cog
async def setup(bot):
    await bot.add_cog(Extras(bot))
