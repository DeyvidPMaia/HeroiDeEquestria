import discord
from discord import Embed, Interaction, ui
from discord.ext import commands
import json
from funcoes import *
import random
from paginacaoPersonagens import PaginacaoPersonagens
import time
import globals

# Variáveis globais ***
# Dicionário para armazenar o timestamp do último resgate de cada usuário
ultimo_resgate_por_usuario = {}

# Variável global para o tempo de bloqueio (em segundos); padrão: 300 segundos (5 minutos)
tempo_impedimento = 300

ultimo_usuario_salvador = None
personagens_inicial = carregar_personagens()
personagens_disponiveis = personagens_inicial.copy()
personagens_salvos = []
contador_personagens_salvos = {}
# Dicionário para registrar quais personagens cada usuário salvou
personagens_por_usuario = {}

restricao_usuario_unico = False
user_cache = {}  # Cache de nomes de usuários

# Carrega o estado salvo ou, se não existir, os personagens iniciais
personagens_disponiveis, personagens_salvos, contador_personagens_salvos, personagens_por_usuario = carregar_estado()


# Função para carregar os dados do arquivo JSON
def carregar_dados():
    try:
        with open("resources/dados.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar dados: {e}")
        return None
    

# Configurações do Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!!', intents=intents)


@bot.event
async def on_ready():
    global user_cache
    for guild in bot.guilds:
        for member in guild.members:
            user_cache[member.id] = member
    print(f"Bot conectado como {bot.user}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        # Envia mensagem de permissão negada
        await ctx.send("❌ **Você não tem permissão para usar este comando.**")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ **Comando não encontrado. Use !!help para ver os comandos disponíveis.**")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ **Faltando argumentos no comando. Use !!help para ver os comandos disponíveis.**")
    else:
        await ctx.send("⚠️ **Ocorreu um erro inesperado. Tente novamente mais tarde.**")
        raise error

@bot.command(help="Exibe a lista de comandos disponíveis para o usuário.")
async def comandos(ctx):
    comandos_usuario = []
    comandos_admin = []
    
    # Itera por todos os comandos registrados no bot
    for command in bot.commands:
        # Verifica se o comando tem o atributo 'admin_only'
        if hasattr(command.callback, "admin_only") and command.callback.admin_only:
            comandos_admin.append(f"!!{command.name} - {command.help}")
        else:
            comandos_usuario.append(f"!!{command.name} - {command.help}")
    
    # Formata as listas
    texto_comandos_usuario = "\n".join(comandos_usuario) if comandos_usuario else "Nenhum comando disponível."
    texto_comandos_admin = "\n".join(comandos_admin) if comandos_admin else "Nenhum comando restrito."
    
    mensagem = (
        "✨ **Comandos disponíveis:** ✨\n"
        f"{texto_comandos_usuario}\n\n"
        "🔒 **Comandos restritos (Admin):** 🔒\n"
        f"{texto_comandos_admin}"
    )
    
    await ctx.send(mensagem)


# Comando listar_personagens atualizado
@bot.command(help="Lista todos os personagens disponíveis.")
@apenas_moderador()
async def listar_personagens(ctx):
    if personagens_disponiveis:
        view = PaginacaoPersonagens(personagens_disponiveis, ctx)
        await view.send_pagina()
    else:
        await ctx.send("🎉 **Todos os personagens foram salvos!** 🎉", file=discord.File("resources/fim.png"))

@bot.command(help="Exibe os personagens salvos por um usuário.")
async def meus_personagens(ctx, user: discord.User = None):
    user = user or ctx.author
    personagens = personagens_por_usuario.get(user.id, [])
    if personagens:
        lista = "\n".join([f"{p['nome']} ({p['especie']})" for p in personagens])
        embed = Embed(
            title=f"Personagens salvos por {user.name}",
            description=lista,
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ **Nenhum personagem salvo por {user.name}.**")

@bot.command(help="Salva um personagem desaparecido.")
async def resgatar(ctx, *, nome):
    global personagens_disponiveis, personagens_salvos, ultimo_usuario_salvador, contador_personagens_salvos, restricao_usuario_unico, personagens_por_usuario, ultimo_resgate_por_usuario

    nome = nome.strip()
    if not nome:
        await ctx.send("❌ **Por favor, insira o nome de um personagem para salvar.**")
        return

    # Tempo de bloqueio
    tempo_bloqueio = tempo_impedimento
    agora = time.time()

    # Verifica se o usuário já resgatou recentemente
    if ctx.author.id in ultimo_resgate_por_usuario:
        tempo_passado = agora - ultimo_resgate_por_usuario[ctx.author.id]
        if tempo_passado < tempo_bloqueio:
            tempo_restante = int(tempo_bloqueio - tempo_passado)
            minutos = tempo_restante // 60
            segundos = tempo_restante % 60
            await ctx.send(f"❌ **Você deve esperar {minutos} minuto(s) e {segundos} segundo(s) para resgatar outro personagem.**")
            return

    if not personagens_disponiveis:
        await ctx.send("❌ **Todos os personagens já foram salvos!**", file=discord.File(verificar_imagem("resources/fim.png")))
        return

    if restricao_usuario_unico and ultimo_usuario_salvador == ctx.author.id:
        await ctx.send("❌ **Você foi o último a salvar um personagem. Espere que mais alguém salve outro personagem!**", file=discord.File(verificar_imagem("resources/naoencontrado.gif")))
        return

    # Verifica se o personagem já foi resgatado
    personagem_resgatado = next((p for p in personagens_salvos if p["nome"].lower() == nome.lower()), None)
    if personagem_resgatado:
        await ctx.send(f"❌ **O personagem '{nome}' já foi resgatado!**", file=discord.File(verificar_imagem("resources/nao.gif")))
        return

    # Procura o personagem na lista de personagens disponíveis
    personagem = next((p for p in personagens_disponiveis if p["nome"].lower() == nome.lower()), None)
    if personagem:
        personagens_disponiveis.remove(personagem)
        personagens_salvos.append(personagem)
        ultimo_usuario_salvador = ctx.author.id

        contador_personagens_salvos[ctx.author.id] = contador_personagens_salvos.get(ctx.author.id, 0) + 1

        # Registra o personagem no dicionário por usuário
        if ctx.author.id not in personagens_por_usuario:
            personagens_por_usuario[ctx.author.id] = []
        personagens_por_usuario[ctx.author.id].append(personagem)

        # Atualiza o timestamp do último resgate do usuário
        ultimo_resgate_por_usuario[ctx.author.id] = agora

        if not personagens_disponiveis:
            imagem = verificar_imagem(f"resources/poneis/{personagem['nome']}.png")
            await ctx.send(f"✅ **'{personagem['nome']}' foi salvo por {ctx.author.name}!**", file=discord.File(imagem))
            await ctx.send(f"🎉 **'{personagem['nome']}' foi o último personagem salvo! Todos estão seguros agora!** 🎉", file=discord.File(verificar_imagem("resources/fim.png")))
        else:
            imagem = verificar_imagem(f"resources/poneis/{personagem['nome']}.png")
            await ctx.send(f"✅ **'{personagem['nome']}' foi salvo por {ctx.author.name}!**", file=discord.File(imagem))
        
        # Salva os dados após salvar personagem
        salvar_dados(personagens_disponiveis, personagens_salvos, contador_personagens_salvos, personagens_por_usuario)
    else:
        await ctx.send(f"❌ **O personagem '{nome}' não foi encontrado!**", file=discord.File(sortear_naoencontrado()))


@bot.command(help="Lista todos os personagens salvos até agora.")
@apenas_moderador()
async def listar_salvos(ctx):
    if personagens_salvos:

        # Instancia a view de paginação passando a lista 'personagens_selecionados'
        view = PaginacaoPersonagens(personagens_salvos, ctx)
        await ctx.send("Estes personagens já estão em casa.**")
        await view.send_pagina()
    else:
        await ctx.send("🎉 **Nenhum personagem foi salvo ainda.**")

@bot.command(help="Mostra quantos personagens cada usuário salvou.")
async def ranking(ctx):
    if contador_personagens_salvos:
        ranking_lista = []
        for user_id, count in sorted(contador_personagens_salvos.items(), key=lambda item: item[1], reverse=True):
            if user_id not in user_cache:
                user_cache[user_id] = await bot.fetch_user(user_id)
            ranking_lista.append(f"{user_cache[user_id].name}: **{count} personagens salvos**")
        await ctx.send("🏆 **Ranking de Salvadores de Personagens:** 🏆\n" + "\n".join(ranking_lista))
    else:
        await ctx.send("🎉 **Nenhum personagem foi salvo ainda.**")

@bot.command(help="Reinicia a lista de personagens disponíveis e limpa o progresso.")
@apenas_moderador()
async def reiniciar_personagens(ctx):
    global personagens_disponiveis, personagens_salvos, contador_personagens_salvos, ultimo_usuario_salvador
    personagens_disponiveis = personagens_inicial.copy()
    personagens_salvos = []
    contador_personagens_salvos.clear()
    ultimo_usuario_salvador = None
    salvar_dados(personagens_disponiveis, personagens_salvos, contador_personagens_salvos, personagens_por_usuario)  # Salvar dados após reiniciar
    await ctx.send("🌀 **A lista de personagens foi reiniciada e todo o progresso foi apagado!**")

@bot.command(help="Habilita ou desabilita a regra de um usuário salvar apenas um personagem por vez.")
@apenas_moderador()
async def alterar_restricao(ctx):
    """Alterna a restrição na qual um usuário pode salvar apenas um personagem por vez."""
    global restricao_usuario_unico
    restricao_usuario_unico = not restricao_usuario_unico
    estado = "**habilitada**" if restricao_usuario_unico else "**desabilitada**"
    mensagem = "só pode resgatar **um personagem por vez**" if restricao_usuario_unico else "pode **resgatar personagens à vontade**"
    await ctx.send(f"⚖️ *A regra de restrição foi.* {estado} Agora você {mensagem}")


@bot.command(help="Veja seu horóscopo mágico do dia!")
async def horoscopo(ctx):
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


@bot.command(help="Altera o tempo de impedimento para resgatar personagens (em segundos). Exemplo: !!alterar_tempo_impedimento 180")
@apenas_moderador()
async def alterar_tempo_impedimento(ctx, tempo: int):
    global tempo_impedimento
    if tempo < 0:
        await ctx.send("❌ **O tempo deve ser um valor positivo.**")
        return

    tempo_impedimento = tempo
    minutos = tempo_impedimento // 60
    segundos = tempo_impedimento % 60
    await ctx.send(f"✅ **O tempo de impedimento foi alterado para {minutos} minuto(s) e {segundos} segundo(s).**")


@bot.command(help="Salva aleatoriamente uma certa quantidade de personagens. Exemplo: !!salvar_aleatorio 150")
@apenas_moderador()
async def salvar_aleatorio(ctx, quantidade: int):
    global personagens_disponiveis, personagens_salvos, contador_personagens_salvos, personagens_por_usuario

    if quantidade <= 0:
        await ctx.send("❌ **A quantidade deve ser maior que 0!**")
        return

    if quantidade > len(personagens_disponiveis):
        await ctx.send("❌ **A quantidade excede o número de personagens disponíveis!**")
        return

    # Seleciona aleatoriamente os personagens a serem salvos
    personagens_selecionados = random.sample(personagens_disponiveis, quantidade)

    # Move os personagens selecionados para a lista de personagens salvos
    for personagem in personagens_selecionados:
        personagens_disponiveis.remove(personagem)
        personagens_salvos.append(personagem)

    salvar_dados(personagens_disponiveis, personagens_salvos, contador_personagens_salvos, personagens_por_usuario)

    # Instancia a view de paginação passando a lista 'personagens_selecionados'
    view = PaginacaoPersonagens(personagens_selecionados, ctx)
    await ctx.send("Os seguintes personagens foram salvos aleatoriamente.**")
    await view.send_pagina()

import os

@bot.command(help="Adiciona um novo personagem com nome, espécie e uma imagem. Exemplo: !!adicionar_personagem <nome> <espécie>")
@apenas_moderador()
async def adicionar_personagem(ctx, nome: str, especie: str):
    global personagens_disponiveis, personagens_inicial

    # Verifica se há um anexo (imagem) na mensagem
    if not ctx.message.attachments:
        await ctx.send("❌ **Você deve anexar uma imagem para o personagem.**")
        return

    # Obtém o primeiro anexo (esperando que seja a imagem)
    attachment = ctx.message.attachments[0]

    # Define a pasta e o nome do arquivo a ser salvo
    diretorio = os.path.join("resources", "poneis")
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)

    # Extrai a extensão do arquivo e define o nome final, por exemplo: "NomeDoPersonagem.png"
    extensao = attachment.filename.split('.')[-1]
    nome_sanitizado = nome.replace(" ", "_")  # substitui espaços por underline para evitar problemas
    nome_arquivo = f"{nome_sanitizado}.{extensao}"
    caminho_imagem = os.path.join(diretorio, nome_arquivo)

    try:
        # Salva o anexo localmente
        await attachment.save(caminho_imagem)
    except Exception as e:
        await ctx.send(f"❌ **Erro ao salvar a imagem: {e}**")
        return

    # Verifica se o personagem já existe na lista de disponíveis
    if any(p["nome"].lower() == nome.lower() for p in personagens_disponiveis):
        await ctx.send(f"❌ **O personagem '{nome}' já existe no jogo!**")
        return

    # Cria o novo personagem e adiciona às listas globais
    novo_personagem = {"nome": nome, "especie": especie}
    personagens_disponiveis.append(novo_personagem)
    personagens_inicial.append(novo_personagem)

    # Salva os dados atualizados (certifique-se de que a função salvar_dados aceita o parâmetro personagens_por_usuario, se for o caso)
    salvar_dados(personagens_disponiveis, personagens_salvos, contador_personagens_salvos, personagens_por_usuario)

    await ctx.send(f"✅ **Personagem '{nome}' ({especie}) foi adicionado com sucesso!**")


# Lê o token do arquivo token.txt
try:
    with open("resources/token.txt", "r") as token_file:
        token = token_file.read().strip()
except FileNotFoundError:
    print("Erro: O arquivo 'resources/token.txt' não foi encontrado.")
    exit(1)

# Inicia o bot com tratamento de erros
try:
    bot.run(token)
except discord.LoginFailure:
    print("Erro: Token inválido. Verifique o arquivo 'resources/token.txt'.")
except Exception as e:
    print(f"Erro inesperado: {e}")