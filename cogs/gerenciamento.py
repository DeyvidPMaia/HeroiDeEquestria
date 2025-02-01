import discord
from discord.ext import commands
import random
from discord import Embed, Interaction, ui
from globals import *
from paginacaoPersonagens import PaginacaoPersonagens
from funcoes import *

class Gerenciamento(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Salva aleatoriamente uma certa quantidade de personagens.")
    @commands.has_permissions(administrator=True)
    async def salvar_aleatorio(self, ctx, quantidade: int):
        # Exemplo básico do que você já tinha
        global personagens_disponiveis, personagens_salvos

        if quantidade <= 0 or quantidade > len(personagens_disponiveis):
            await ctx.send("❌ Quantidade inválida!")
            return

        personagens_selecionados = random.sample(personagens_disponiveis, quantidade)

        for personagem in personagens_selecionados:
            personagens_disponiveis.remove(personagem)
            personagens_salvos.append(personagem)

        await ctx.send(f"✅ Os seguintes {quantidade} personagens salvos aleatoriamente.")
        view = PaginacaoPersonagens(personagens_selecionados, ctx)
        await view.send_pagina()
        
        # Salvar dados e exibir embed como você já fazia...

    @commands.command(help="Habilita ou desabilita a regra de um usuário salvar apenas um personagem por vez.")
    @apenas_moderador()
    async def alterar_restricao(self, ctx):
        global restricao_usuario_unico
        """Alterna a restrição na qual um usuário pode salvar apenas um personagem por vez."""
        restricao_usuario_unico
        restricao_usuario_unico = not restricao_usuario_unico
        estado = "**habilitada**" if restricao_usuario_unico else "**desabilitada**"
        mensagem = "só pode resgatar **um personagem por vez**" if restricao_usuario_unico else "pode **resgatar personagens à vontade**"
        await ctx.send(f"⚖️ *A regra de restrição foi.* {estado} Agora você {mensagem}")

# Setup para registrar o cog
async def setup(bot):
    await bot.add_cog(Gerenciamento(bot))
