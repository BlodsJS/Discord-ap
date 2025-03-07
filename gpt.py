### ---------- PARTE 1: CONFIGURAÇÕES INICIAIS ---------- ###
import os
import logging
import asyncio
import aiohttp
import aiosqlite
import discord
from discord.ext import commands, tasks
from discord import app_commands, TextChannel, VoiceChannel
from datetime import datetime, timedelta
import random
from easy_pil import Editor, font, Canvas, load_image_async, load_image
import cachetools
import hashlib
import requests
import json
from typing import Dict, List, Union
import aiofiles
import pathlib
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw  # Certifique-se de ter as dependências necessárias

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis de ambiente
TOKEN = os.getenv("token_discord")
IA_TOKEN = os.getenv("token_ia")

# Prefixos e intents
PREFIXES = ["b!", "B!"]
def get_prefix(bot, message):
    return commands.when_mentioned_or(*PREFIXES)(bot, message)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Instanciação do bot
bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command("help")

#personalidade da ia

file_path = "pers_bei.txt"  # Arquivo de texto com a personalidade
pers = ""  # Variável para armazenar o conteúdo do arquivo

chan_db = None
try:
    with open(file_path, "r", encoding="utf-8") as txt_file:
        pers = txt_file.read()  # Lê o conteúdo do arquivo de texto
except FileNotFoundError:
    print(f"Arquivo {file_path} não encontrado. Usando personalidade padrão.")
    pers = """
    # **Bei Bei - A Deusa Errante das Sombras Eternas**

    #### **Personalidade**
    - **Elegância Sedutora:** Ela se move com graça e confiança.
    - **Maturidade Inquestionável:** Séculos de experiências a tornaram sábia.
    """

class channel_database:
    def __init__(self, arquivo: str = 'canais.json'):
        self.arquivo = pathlib.Path(arquivo)
        self.dados: Dict[str, List[int]] = {}

    @classmethod
    async def create(cls, arquivo: str = 'canais.json'):
        """Factory method correto"""
        instance = cls(arquivo)
        await instance._carregar_dados()
        return instance

    async def _carregar_dados(self):
        try:
            async with aiofiles.open(self.arquivo, 'r') as f:
                conteudo = await f.read()
                self.dados = json.loads(conteudo)
        except (FileNotFoundError, json.JSONDecodeError):
            self.dados = {}

    async def _salvar_dados(self):
        async with aiofiles.open(self.arquivo, 'w') as f:
            await f.write(json.dumps(self.dados, indent=4))

    # ... manter métodos inserir/apagar/get_canais ...
    async def inserir(self, guild_id: int, channel_id: int) -> bool:
        """Adiciona canal de forma assíncrona"""
        chave = str(guild_id)
        
        if chave not in self.dados:
            self.dados[chave] = []
        
        if channel_id not in self.dados[chave]:
            self.dados[chave].append(channel_id)
            await self._salvar_dados()  # Chamada assíncrona
            return True
        return False

    async def apagar(self, guild_id: int, channel_id: int) -> bool:
        """Remove canal de forma assíncrona"""
        chave = str(guild_id)
        
        if chave in self.dados and channel_id in self.dados[chave]:
            self.dados[chave].remove(channel_id)
            
            if not self.dados[chave]:
                del self.dados[chave]
            
            await self._salvar_dados()  # Chamada assíncrona
            return True
        return False

    def get_canais(self, guild_id: int) -> List[int]:
        """Método síncrono para acesso rápido à memória"""
        return self.dados.get(str(guild_id), [])
c_db = channel_database()

### ---------- CLASSE CACHEMANAGER ---------- ###
class CacheManager:
    def __init__(self):
        self.xp_data = cachetools.LRUCache(maxsize=1000)  # Cache de XP por usuário
        self.api_responses = cachetools.TTLCache(maxsize=500, ttl=300)  # Cache de respostas da API (5 minutos)
        self.avatars = cachetools.TTLCache(maxsize=200, ttl=3600)  # Cache de avatares (1 hora)
        self.leaderboard = None  # Cache do ranking global
        self.lock = asyncio.Lock()  # Lock para operações concorrentes
        self.cache_version = 1  # Versão do schema (para invalidação)

    async def auto_invalidate(self):
        """Invalida caches expirados a cada 60 segundos."""
        while True:
            await asyncio.sleep(60)
            self.api_responses.expire()
            self.avatars.expire()
            logger.info("Caches de API e Avatares invalidados automaticamente.")

    async def invalidate_user(self, user_id: str):
        """Remove os dados de XP de um usuário do cache."""
        async with self.lock:
            if user_id in self.xp_data:
                del self.xp_data[user_id]
                logger.info(f"Cache de XP invalidado para {user_id}.")

    async def invalidate_leaderboard(self):
        """Reseta o cache do ranking global."""
        async with self.lock:
            self.leaderboard = None
            logger.info("Cache do leaderboard invalidado.")

    def generate_key(self, key: str) -> str:
        """Gera uma chave hash para identificação única no cache."""
        return hashlib.md5(key.encode('utf-8')).hexdigest()

cache_manager = CacheManager()

### ---------- CLASSE DATABASEMANAGER ---------- ###
class DatabaseManager:
    def __init__(self, db_path: str = 'xp_data.db'):
        self.db_path = db_path
        self.connection = None
        self.lock = asyncio.Lock()  # Lock para operações assíncronas

    async def connect(self):
        """Conecta ao banco de dados e cria tabelas se necessário."""
        if self.connection is None or self.connection.close:
            self.connection = await aiosqlite.connect(self.db_path)
            await self.create_tables()
            logger.info("Conexão com o banco de dados estabelecida.")

    async def create_tables(self):
        """Cria a tabela xp_data se ela não existir."""
        async with self.connection.execute('''
            CREATE TABLE IF NOT EXISTS xp_data (
                user_id TEXT PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                message INTEGER DEFAULT 0,
                voice INTEGER DEFAULT 0
            )
        '''):
            await self.connection.commit()
            logger.info("Tabelas verificadas/criadas.")

    async def get_user_data(self, user_id: str) -> dict:
        """Busca ou cria os dados de um usuário no banco."""
        async with self.lock:
            if not self.connection or self.connection.close:
                await self.connect()

            async with self.connection.execute(
                "SELECT xp, level, message, voice FROM xp_data WHERE user_id = ?", 
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()

            if row:
                return {"xp": row[0], "level": row[1], "message": row[2], "voice": row[3]}
            else:
                await self.connection.execute(
                    "INSERT INTO xp_data (user_id, xp, level, message, voice) VALUES (?, ?, ?, ?, ?)",
                    (user_id, 0, 1, 0, 0)
                )
                await self.connection.commit()
                return {"xp": 0, "level": 1, "message": 0, "voice": 0}

    async def update_user_data(self, user_id: str, xp: int, level: int, message: int, voice: int):
        """Atualiza os dados de um usuário e invalida os caches relevantes."""
        async with self.lock:
            if not self.connection or self.connection.close:
                await self.connect()

            await self.connection.execute(
                "UPDATE xp_data SET xp = ?, level = ?, message = ?, voice = ? WHERE user_id = ?",
                (xp, level, message, voice, user_id)
            )
            await self.connection.commit()
            await cache_manager.invalidate_user(user_id)  # Invalida cache do usuário
            await cache_manager.invalidate_leaderboard()  # Invalida cache do ranking
            logger.info(f"Dados de {user_id} atualizados: XP={xp}, Nível={level}")

    async def get_user_rank(self, user_id: str) -> int | None:
        """Retorna a posição do usuário no ranking global."""
        try:
            async with self.lock:
                if not self.connection or self.connection.close:
                    await self.connect()

                # Busca todos os usuários ordenados por nível e XP
                async with self.connection.execute(
                    "SELECT user_id FROM xp_data ORDER BY level DESC, xp DESC"
                ) as cursor:
                    usuarios = await cursor.fetchall()

                # Procura a posição do usuário na lista
                for index, (uid,) in enumerate(usuarios, start=1):
                    if uid == user_id:
                        return index
                return None  # Usuário não encontrado

        except Exception as e:
            logger.error(f"Erro ao buscar rank de {user_id}: {e}")
            return None

    async def close(self):
        """Fecha a conexão com o banco de dados."""
        async with self.lock:
            if self.connection and not self.connection.close:
                await self.connection.close()
                logger.info("Conexão com o banco fechada.")

db_manager = DatabaseManager()

# ----------------------- Inicialização do Bot -----------------------
# Juntar tudo em um único evento on_ready
@bot.event
async def on_ready():
    logger.info(f"Bot conectado como {bot.user}")
    
    # Inicialização da sessão HTTP
    if not hasattr(bot, 'http_session') or bot.http_session.close:
        bot.http_session = aiohttp.ClientSession()
    
    # Conexão com o banco de dados
    await db_manager.connect()
    bot.db = db_manager.connection
    
    # Sincronização de comandos
    try:
        synced = await bot.tree.sync()
        logger.info(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        logger.error(f"Erro ao sincronizar comandos: {e}")
    
    # Iniciar task de status (com verificação)
    if not change_playing.is_running():
        change_playing.start()

@bot.event
async def on_disconnect():
    print("⚠️ Salvando dados antes de desconectar...")
    await c_db._salvar_dados()
		
# Função para um desligamento ordenado
async def shutdown():
    logger.info("Desligando bot...")
    
    # Cancela todas as tasks em execução
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    logger.info("Todas as tasks foram canceladas.")
    
    # Fecha a sessão HTTP se existir
    if hasattr(bot, 'http_session') and not bot.http_session.close:
        await bot.http_session.close()
        logger.info("Sessão HTTP fechada.")
    
    # Fecha o banco de dados se existir
    if db_manager.connection and not db_manager.connection.close:
        await db_manager.close()
        logger.info("Banco de dados fechado.")
    
    # Fecha o bot
    await bot.close()
    logger.info("Bot desconectado.")

@bot.command(aliases=["logout"])
@commands.is_owner()
async def shutdown_bot(ctx):
    await ctx.send("Desligando...")
    await shutdown()  # Chama a função shutdown
    print("Bot desligado e terminal liberado.")
        
@tasks.loop(seconds=120)  # Altere o intervalo conforme necessário
async def change_playing():
    try:
        playing = [
            "Quantas vezes terei que repetir o óbvio antes que ele finalmente penetre suas cabeças incrivelmente densas?",
            "Meu tempo é precioso. Faça valer ou suma da minha presença.",
            "Vocês, mortais... Sempre correndo como ratos, mas raramente sabem onde querem chegar.",
            "Se ao menos metade do esforço que vocês colocam em problemas fosse direcionada para as soluções, este mundo seria um lugar menos insuportável.",
            "De fato, a ignorância é uma escolha. E vocês a escolhem com uma frequência perturbadora.",
            "Eu sou uma deusa, não uma babá celestial. Descubra você mesmo.",
            "De todas as escolhas possíveis, você decidiu fazer essa burrice? Fascinante.",
            "Pelo amor da noite eterna, será que uma vez vocês podem pensar antes de agir?",
            "Não confunda minha paciência com aprovação. Eu tolero. Não quer dizer que eu concorde.",
            "Oh, por favor... Até uma pedra teria entendido o que eu disse."
        ]
        await bot.wait_until_ready()
        await bot.change_presence(activity=discord.Game(random.choice(playing)))
    except asyncio.CancelledError:
        logger.info("Task change_playing cancelada.") 
    except Exception as e:
        logger.error(f"Erro na task de status: {e}")

# Inicie a task depois que o bot estiver pronto
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"O comando `{ctx.invoked_with}` não existe. Use o `b!help` para ver os comandos disponíveis.")
    else:
        logger.error(f"Erro desconhecido: {error}")



# ----------------------- Cogs de Comandos -----------------------
class CommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot, c_db):
        self.bot = bot
        self.c_db = c_db

    # --- Comandos Básicos ---
    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência: {round(self.bot.latency * 1000)}ms",
            color=discord.Color.default()
        )
        await ctx.send(embed=embed)

    @commands.command(name="diga", aliases=["say"])
    async def diga(self, ctx: commands.Context, *, mensagem: str):
        embed = discord.Embed(
            title="Mensagem:",
            description=mensagem,
            color=discord.Color.default()
        )
        embed.set_footer(text=f"By {ctx.author.mention}")
        await ctx.send(embed=embed)

    @commands.command(name="ask")
    async def ask(self, ctx: commands.Context, *, pergunta: str):
        usuario = ctx.author
        try:
            resposta = await self.ad_resposta(pergunta, usuario)
            if not resposta:
                resposta = "Desculpe, não consegui obter uma resposta."
            embed = discord.Embed(
                title="🎻 Resposta da Bei Bei 🎻",
                description=resposta,
                color=discord.Color.default()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Erro em 'ask': {e}")
            embed = discord.Embed(
                title="Erro",
                description="Não foi possível processar sua resposta.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="ajuda", aliases=["help"])
    async def ajuda(self, ctx: commands.Context):
        ajuda_msg = (
            "ping - Responde com Pong.\n"
            "diga <mensagem> - O bot repete a mensagem.\n"
            "ask <pergunta> - Faz uma pergunta a Bei Bei.\n"
            "xp - Mostra seu XP.\n"
            "perfil - Exibe seu perfil.\n"
            "top - Mostra o ranking dos usuários.\n"
            "avatar - Exibe seu avatar em formato circular."
        )
        embed = discord.Embed(
            title="**Comandos Disponíveis:**",
            description=ajuda_msg,
            color=discord.Color.default()
        )
        await ctx.send(embed=embed)

    # --- Comandos de Perfil ---
    @app_commands.command(name="perfil", description="Exibe o perfil de um usuário.")
    async def perfil_slash(self, interaction: discord.Interaction, usuario: discord.Member = None):
        usuario = usuario or interaction.user
        embed = await self.criar_embed_perfil(usuario, interaction.guild, interaction.user)
        await interaction.response.send_message(embed=embed)

    @commands.command(name="perfil")
    async def perfil_prefix(self, ctx: commands.Context, usuario: discord.Member = None):
        usuario = usuario or ctx.author
        embed = await self.criar_embed_perfil(usuario, ctx.guild, ctx.author)
        await ctx.send(embed=embed)

    # --- Comandos de XP ---
    @app_commands.command(name="rank", description="Exibe a imagem de progresso de XP de um usuário.")
    async def xp_img_slash(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        user_id = str(user.id)
        user_data = await self.get_user_xp(user_id)
        if user_data:
            xp = user_data["xp"]
            level = user_data["level"]
            xp_per_level = (level ** 2) * 100
            imagem = await self.image_bar_creat(user.avatar.url, user.name, xp, xp_per_level, level, self.get_user_rank(user_id))
            await interaction.response.send_message(file=imagem)
        else:
            await interaction.response.send_message(f"{user.mention} ainda não tem XP.")

    @commands.command(name="xp", aliases=["rank"])
    async def xp_img_prefix(self, ctx: commands.Context, user: discord.Member = None):
        user = user or ctx.author
        user_id = str(user.id)
        user_data = await self.get_user_xp(user_id)
        if user_data:
            xp = user_data["xp"]
            level = user_data["level"]
            xp_per_level = (level ** 2) * 100
            # Dentro de image_bar_creat:
            rank = await self.get_user_rank(user_id)  # Agora assíncrono
            imagem = await self.image_bar_creat(user.avatar.url, user.name, xp, xp_per_level, level, rank)
            await ctx.send(file=imagem)
        else:
            await ctx.send(f"{user.mention} ainda não tem XP.")

    # --- Comando de Ranking ---
    @app_commands.command(name="top", description="Mostra o ranking dos usuários.")
    async def top_slash(self, interaction: discord.Interaction):
        ranking_imagem = await self.top_img(self.bot, interaction.guild.id, interaction.channel)
        await interaction.response.send_message(file=ranking_imagem)

    @commands.command(name="top", aliases=["ranking"])
    async def top_prefix(self, ctx: commands.Context):
        ranking_imagem = await self.send_leaderboard(self.bot, ctx.guild.id, ctx.channel)
        await ctx.send(file=ranking_imagem)

    # --- Comando de Avatar ---
    @commands.command(name="avatar")
    async def avatar(self, ctx: commands.Context, user: discord.Member = None):
        user = user or ctx.author
        imagem = await load_image_async(user.display_avatar.url)
        editor = Editor(imagem).circle_image()
        file_img = discord.File(fp=editor.image_bytes, filename='circle.png')
        await ctx.send(file=file_img)
        
    @commands.command(name="stats", aliases=["status"])
    async def stats_prefix(self, ctx: commands.Context):
    	
    	embed = discord.Embed(
    		title="Novo comando",
    		description="Ainda em desenvolvimento",
    		color=discord.Color.default()
    	)
    	embed.add_fiel(name="Stats", value= "teste")
    	embed.add_fiel(name="Experience", value="teste")
    	await ctx.send(embed=embed)
    
    @commands.command(name="teste")
    async def teste(self, ctx: commands.Context, user: discord.Member = None):
        user = user or ctx.author

        # Carrega o avatar (substitua por sua implementação real de load_image_async)
        avatar_url = str(user.display_avatar.url)
        image = await load_image_async(avatar_url)
        
        # Processamento da imagem (ajuste conforme sua biblioteca)
        image = Editor(image).resize((188, 188)).circle_image()

        # Carrega o layout do perfil
        bg = Editor("profile.png").resize((800, 600))
        bg.paste(image, (5, 0))

        # Adiciona textos
        fonte = font.Font.poppins(size=14, variant="bold")  # Certifique-se de ter a fonte
        bg.text((200, 40), f"{user.name}", color="black", font=fonte)
        bg.text((200, 58), "BKZ: ", color="black", font=fonte)

        # Salva e envia
        img_bytes = BytesIO()
        bg.image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        await ctx.send(file=discord.File(img_bytes, filename="perfil.png"))
    	
    @commands.command(name="addchannel", aliases=["ac"])
    @commands.has_permissions(administrator=True)
    async def add_channel(self, ctx: commands.Context, canal: Union[TextChannel, VoiceChannel]):
    	
    	if not isinstance(canal, (TextChannel, VoiceChannel)):
    		embed = discord.Embed(
    			title= "Erro",
    			description= f"{canal} não é um canal de voz ou texto válido",
    			color= discord.Color.red()
    		)
    		await ctx.send(embed=embed)
    		return
    	# Método síncrono, sem await!
    	canais = self.c_db.get_canais(ctx.guild.id)
    	if canal.id in canais:
    		embed = discord.Embed(
    			title= "Erro",
    			description= "⚠️ Este canal já está na lista!",
    			color= discord.Color.default()
    		)
    		await ctx.send(embed=embed)
    		return

    	try:
    		sucess = await self.c_db.inserir(ctx.guild.id, canal.id)
    		
    		if sucess:
    			embed = discord.Embed(
    				title="Sucesso",
    				description=f"Canal {canal} adicionado com sucesso a lista",
    				color= discord.Color.green()
    			)
    			await ctx.send(embed=embed)
    		else:
    			embed = discord.Embed(
    			title="Erro",
    			description="Não foi possível adicionar o canal a lista"
    			)
    			await ctx.send(embed=embed)
    	except Exception as e:
    		print(e)
    	
    @commands.command(name="removechannel", aliases=["rc"])
    @commands.has_permissions(administrator=True)
    async def remove_channel(self, ctx: commands.Context, canal: Union[TextChannel, VoiceChannel]):
    	
    	canais = self.db.get_canais(ctx.guild.id)
    	if canal.id not in canais:
    		embed = discord.Embed(
    			title= "Erro",
    			description= f"❌ {canal.mention} não está na lista!",
    			color= discord.Color.red()
    		)
    		await ctx.send(embed=embed)
    		return
    		
    	success = await self.db.apagar(ctx.guild.id, canal.id)
    	if sucess:
    		embed = discord.Embed(
    			title = "Sucess",
    			description= f"✅ {canal.mention} removido com sucesso!",
    			color= discord.Color.green()
    		)
    		await ctx.send(embed=embed)
    		return
    	else:
    		embed = discord.Embed(
    			title= "Erro",
    			description= "⚠️ Erro inesperado ao remover!",
    			color= discord.Color.red()
    		)
    		await ctx.send(embed=embed)
    		return
    	
    @commands.command(name="canais")
    @commands.has_permissions(administrator=True)
    async def verify_channels(self, ctx:commands.Context):
    	canais = [f'<#{cid}>' for cid in c_db.get_canais(ctx.guild.id)]
    	
    	text = ""
    	for i in canais:
    		text += f"{i}\n"
    		
    	embed = discord.Embed(
    		title= "Canais",
    		description= text,
    		color= discord.Color.default()
    	)
    	await ctx.send(embed=embed)
    	

    # --- Comandos Administrativos ---
    @commands.command(name="addxp")
    @commands.has_permissions(administrator=True)
    async def addxp(self, ctx: commands.Context, user: discord.Member, xp: int):
	    if xp <= 0:
	        return await ctx.send("❌ O valor de XP deve ser maior que zero.")
	    
	    user_id = str(user.id)
	    
	    try:
	        user_data = await self.get_user_xp(user_id)
	        current_xp = user_data["xp"]
	        current_level = user_data["level"]
	        
	        new_xp = current_xp + xp
	        xp_required = (current_level ** 2) * 100
	        levels_gained = 0
	        
	        # Loop para calcular múltiplos level-ups
	        while new_xp >= xp_required:
	            new_xp -= xp_required
	            current_level += 1
	            levels_gained += 1
	            xp_required = (current_level ** 2) * 100
	        
	        # Atualiza os dados do usuário

	        await db_manager.update_user_data(
	            user_id=user_id,
	            xp=new_xp,
	            level=current_level,
	            message=user_data["message"],
	            voice=user_data["voice"]
	        )
	        
	        # Notificação
	        
	        embed = discord.Embed(
	            title="✅ XP Adicionado",
	            description=f"{xp} XP foram adicionados para {user.mention}.",
	            color=discord.Color.green()
	        )
	        embed.add_field(name="Novo XP", value=f"`{new_xp}`", inline=True)
	        embed.add_field(name="Novo Nível", value=f"`{current_level}`", inline=True)
	        await ctx.send(embed=embed)
	    
	    except Exception as e:
	        logger.error(f"Erro ao adicionar XP: {e}")
	        await ctx.send("❌ Ocorreu um erro ao processar este comando.")
    # Dentro da classe CommandsCog (no mesmo local onde está o comando addxp)
    @commands.command(name="removerlevel", aliases=["removenivel"])
    @commands.has_permissions(administrator=True)
    async def remover_level(self, ctx: commands.Context, usuario: discord.Member, niveis: int):
	    logger.info(f"Comando 'removerlevel' chamado por {ctx.author} para {usuario} (níveis: {niveis})")
	    
	    try:
	        if niveis <= 0:
	            logger.warning("Níveis a remover devem ser > 0")
	            return await ctx.send("❌ O número de níveis deve ser maior que zero.")
	
	        user_id = str(usuario.id)
	        user_data = await self.get_user_xp(user_id)
	        logger.debug(f"Dados atuais do usuário: {user_data}")
	
	        novo_nivel = max(1, user_data["level"] - niveis)
	        xp_necessario = (novo_nivel ** 2) * 100
	        novo_xp = xp_necessario -1
	
	        logger.info(f"Atualizando: Nível {user_data['level']} -> {novo_nivel}, XP {user_data['xp']} -> {novo_xp}")
	

	        await db_manager.update_user_data(
	            user_id=user_id,
	            xp=novo_xp,
	            level=novo_nivel,
	            message=user_data["message"],
	            voice=user_data["voice"]
	        )
	        logger.info("Banco de dados atualizado com sucesso.")
	        
	        embed = discord.Embed(
		        title="🎚️ Nível Removido",
		        description=f"{usuario.mention} perdeu {niveis} nível(s)!",
		        color=discord.Color.orange()
		    )
	        embed.add_field(name="Novo Nível", value=f"`{novo_nivel}`")
	        await ctx.send(embed=embed)
	
	    except Exception as e:
	        logger.error(f"Erro ao remover nível: {e}", exc_info=True)
	        await ctx.send("❌ Ocorreu um erro ao processar este comando.")
        
    @commands.command(name="addlevel", aliases=["adicionarlevel"])
    @commands.has_permissions(administrator=True)
    async def add_level(self, ctx: commands.Context, usuario: discord.Member, niveis: int):
	    """Remove níveis de um usuário (comando administrativo)"""
	    if niveis <= 0:
	        return await ctx.send("❌ O número de níveis deve ser maior que zero.")
	
	    user_id = str(usuario.id)
	    
	    try:
	        # Busca os dados atuais
	        user_data = await self.get_user_xp(user_id)
	        nivel_atual = user_data["level"]
	        xp_atual = user_data["xp"]
	
	        # Calcula novo nível (não permite menor que 1)
	        novo_nivel = max(1, nivel_atual + niveis)
	        
	        # Atualiza XP para o mínimo do novo nível
	        xp_necessario = (novo_nivel ** 2) * 100
	        novo_xp = min(xp_atual, xp_necessario - 1)  # Garante que não ultrapasse
	
	        # Atualiza no banco de dado
	        await db_manager.update_user_data(
	            user_id=user_id,
	            xp=novo_xp,
	            level=novo_nivel,
	            message=user_data["message"],
	            voice=user_data["voice"]
	        )
	    # Mensagem de confirmação
	        embed = discord.Embed(
	            title="🎚️ Nível Adicionado",
	            description=f"{usuario.mention} ganhou {niveis} nível(s)!",
	            color=discord.Color.green()
	        )
	        embed.add_field(name="Novo Nível", value=f"`{novo_nivel}`")
	        await ctx.send(embed=embed)
	
	    except Exception as e:
	        logger.error(f"Erro ao remover nível: {e}")
	        await ctx.send("❌ Ocorreu um erro ao processar este comando.")

    # --- Métodos Auxiliares ---
    async def get_house(self, usuario) -> str | None:
	    """Retorna o nome da casa do usuário com base em seus roles."""
	    # 1. Mapeamento por IDs (mais robusto que nomes)
	    CASAS = {
	        1227357334905290764: "Leonipards",   # ID do role Leonipards
	        1227357084543225939: "Corbusier",     # ID do role Corbusier
	        1052974511319941231: "Synexa",        # ID do role Synexa
	        1227358673056043018: "Vildjharta"     # ID do role Vildjharta
	    }
	
	    # 2. Busca eficiente usando operações de conjunto
	    role_ids = {role.id for role in usuario.roles}
	    casa_ids = CASAS.keys()
	    
	    # 3. Encontra a primeira interseção (se existir)
	    casa_encontrada = next((CASAS[role_id] for role_id in role_ids & casa_ids), None)
	    
	    return casa_encontrada
	
    async def get_rank(self, usuario) -> str | None:
	    """Retorna o rank do usuário com base em seus roles, considerando prioridade."""
	    # 1. Lista ordenada por prioridade (do maior para o menor rank)
	    RANKS_PRIORIDADE = [
	        "Rank SSS", "Rank SS", "Rank S", 
	        "Rank A+", "Rank A", "Rank B", 
	        "Rank C+", "Rank C", "Rank D+", 
	        "Rank D", "Rank E", "Rank F"
	    ]
	
	    # 2. Busca reversa para priorizar ranks mais altos
	    for rank in RANKS_PRIORIDADE:
	        if any(role.name == rank for role in usuario.roles):
	            return rank
	    
	    return None
	    
    async def criar_embed_perfil(self, usuario: discord.Member, guild: discord.Guild, requisitante: discord.Member) -> discord.Embed:
        house = await self.get_house(usuario)
        rank = await self.get_rank(usuario)
        if house is None:
        	house_text = "Não pertence a uma casa"
        else:
        	house_role = discord.utils.get(guild.roles, name=house)
        	house_text = house_role.mention if house_role else "Não pertence a uma casa"
        	
        if rank is None:
        	rank_text = "Não ranqueado"
        else:
        	rank_role = discord.utils.get(guild.roles, name=rank)
        	rank_text = rank_role.mention if rank_role else f"`{rank}` (Role não encontrada)"
        	
        rank = discord.utils.get(guild.roles, name=rank) if rank else None
        member = guild.get_member(int(usuario.id)) if guild else None
        display_name = member.display_name if member else (usuario.name if usuario else "Usuário Desconhecido")
        users = {
        	315244726569926666: "Imperador de Bezirk",
        	1033967099313410129: "Imperatriz de Bezirk",
        	482665039556247577: f"{house_text} - Patriarca",
        	1319888552254902282: f"{house_text} - Patriarca",
        	824516133327208511: f"{house_text} - Patriarca",
        	1185811441727586364: f"{house_text} - Matriarca"
        }
        if usuario.id in users:
        	text = users[usuario.id]
        else:
        	text = f"{house_text}"
        embed = discord.Embed(
            title=f"Perfil de {usuario.name}",
            color=discord.Color.default()
        )
        embed.set_thumbnail(url=usuario.avatar.url)
        embed.add_field(name="Nome", value=display_name, inline=True)
        #
        embed.add_field(name="Casa", value=text)
        embed.add_field(name="Rank", value=rank_text)
        embed.set_footer(text=f"Requisitado por {requisitante.name}", icon_url=requisitante.avatar.url)
        return embed

    # Dentro da classe CommandsCog:
    async def get_user_xp(self, user_id: str) -> dict:
	    """Busca os dados do usuário no banco de dados."""
	    try:
	        async with self.bot.db.execute(
	            "SELECT xp, level, message, voice FROM xp_data WHERE user_id = ?", 
	            (user_id,)
	        ) as cursor:
	            row = await cursor.fetchone()
	
	        if row:
	            return {
	                "xp": row[0] if row[0] is not None else 0,
	                "level": row[1] if row[1] is not None else 1,
	                "message": row[2] if row[2] is not None else 0,
	                "voice": row[3] if row[3] is not None else 0
	            }
	        else:
	            # Insere novo usuário se não existir
	            await self.bot.db.execute(
	                "INSERT INTO xp_data (user_id, xp, level, message, voice) VALUES (?, ?, ?, ?, ?)",
	                (user_id, 0, 1, 0, 0)
	            )
	            return await db_manager.get_user_data(user_id)
	            
	
	    except Exception as e:
	        logging.error(f"Erro ao buscar XP de {user_id}: {e}")
	        return {"xp": 0, "level": 1, "message": 0, "voice": 0}
        
        # Utiliza o DatabaseManager para recuperar os dados do usuário
        #return await db_manager.get_user_data(user_id)

    async def image_bar_creat(self, image_url: str, name: str, xp: int, need_xp: int, level: int, rank: int) -> discord.File:
        profile = await load_image_async(image_url)
        profile = Editor(profile).resize((70, 70)).circle_image()
        fonte1 = font.Font.poppins(variant="bold", size=25)
        fonte2 = font.Font.poppins(size=20)
        fonte3 = font.Font.poppins(size=12)
        
        
        # Exemplo dummy de geração de imagem com easy_pil
        bg = Canvas((500, 140), color="#131515")
        bg = Editor(bg)
        bg.text((20, 45), f"#{rank}", color="white", font=fonte2)
        bg.paste(profile, (80, 140 // 2 - 35))
        bg.text((158, 40), name, color="white", font=fonte1)
        porcentagem = (xp / need_xp) * 100
        bg.rectangle((158, 70), width=250, height=23, radius=10, outline="black", stroke_width=3)
        bg.bar((163, 73), 240, 18, porcentagem, fill="white", radius=10)
        bg.text((170, 100), f"Level {level}", color="white", font=fonte3)
        bg.text((320, 98), f"{xp:,}/{need_xp:,} XP", color="white", font=fonte3)
        file_img = discord.File(bg.image_bytes, "xp.png")
        return file_img

    # Dentro da classe CommandsCog:
    async def get_user_rank(self, user_id: str) -> int:
	    """Retorna a posição do usuário no ranking (assíncrono)"""
	    rank = await db_manager.get_user_rank(user_id)
	    return rank or 0  # Retorna 0 se não encontrar

    async def top_img(self, bot: commands.Bot, guild_id: int, channel: discord.TextChannel, offset: int = 0) -> discord.File:
	    """Gera a imagem do ranking dos usuários com aiosqlite e paralelismo."""
	    try:
	        # Consulta assíncrona ao banco de dados
	        async with bot.db.execute('''
	            SELECT user_id, xp, level, message, voice
	            FROM xp_data 
	            ORDER BY level DESC, xp DESC
	            LIMIT 5 OFFSET ?
	            ''', (offset,)) as cursor:
	            
	            top_users = await cursor.fetchall()
	
	        if not top_users:
	            return discord.File(Editor(Canvas((580, 200), color="#131515")).image_bytes, "leaderboard.png")
	
	        # Configurações da imagem
	        LARGURA = 580
	        ALTURA_POR_USUARIO = 100
	        altura_total = ALTURA_POR_USUARIO * len(top_users) + 20
	        bg = Editor(Canvas((LARGURA, altura_total), color="#131515"))
	
	        # Fontes (cache de fontes)
	        fonte_number = font.Font.poppins(variant="bold", size=24)
	        fonte_rank = font.Font.poppins(size=12)
	        fonte_nome = font.Font.poppins(size=28)
	        fonte_level = font.Font.poppins(variant="bold", size=10)
	
	        # Busca paralela de usuários e avatares
	        users = []
	        for user_id, _, _, _, _ in top_users:
	            try:
	                user = await bot.fetch_user(int(user_id))
	                users.append(user)
	            except (discord.NotFound, discord.HTTPException):
	                users.append(None)
	
	        # Carregar avatares em paralelo
	        avatar_tasks = []
	        for user in users:
	            if user and user.avatar:
	                avatar_tasks.append(load_image_async(user.avatar.url))
	            else:
	                avatar_tasks.append(None)
	        
	        avatars = await asyncio.gather(*avatar_tasks, return_exceptions=True)
	
	        # Processar cada usuário
	        guild = bot.get_guild(guild_id)
	        for index, ((user_id, xp, level, messages, voice), user, avatar) in enumerate(zip(top_users, users, avatars), start=1):
	            y_position = (index - 1) * ALTURA_POR_USUARIO
	
	            # Número do rank
	            bg.text((20, y_position + 28), f"#", color="#C0C0C0", font=fonte_rank)
	            bg.text((33, y_position + 30), f"{index + offset}", color="white", font=fonte_number) 
	
	            # Avatar
	            if avatar and not isinstance(avatar, Exception):
	                profile = Editor(avatar).resize((70, 70)).circle_image()
	                bg.paste(profile, (85, y_position + 15))
	
	            # Nome do membro
	            member = guild.get_member(int(user_id)) if guild else None
	            display_name = member.display_name if member else (user.name if user else "Usuário Desconhecido")
	            need_level = (level**2)*100
	            temp = int(voice)
	            temp = int(temp/60)
	            bg.text((175, y_position + 20), display_name, color="white", font=fonte_nome)
	
	            # Dados
	            bg.text((175, y_position + 53), f"LEVEL {level}", color="#C0C0C0", font=fonte_rank)
	            bg.text((175, y_position + 66), f"{xp:,}/{need_level:,} XP", color="white", font=fonte_level)
	            bg.text((450, y_position + 53), f"messages: {messages:,}", color="#C0C0C0", font=fonte_rank)
	            bg.text((450, y_position + 66), f"minutes: {temp:,}", color="#C0C0C0", font=fonte_rank)
	            
	
	        return discord.File(bg.image_bytes, "leaderboard.png")
	    
	    except Exception as e:
	        logging.error(f"Erro ao gerar ranking: {e}")
	        return discord.File(Editor(Canvas((580, 200), color="#131515")).image_bytes, "leaderboard.png")

    async def send_leaderboard(self, bot: commands.Bot, guild_id: int, channel: discord.TextChannel) -> discord.File:
        return await self.top_img(bot, guild_id, channel)

    async def ad_resposta(self, pergunta: str, usuario: discord.Member) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
	        "Authorization": "Bearer {IA_TOKEN}/deepseek",  # Substitua {token} pelo seu token real
	        "HTTP-Referer": "https://openrouter.ai/api/v1/completions",  # Opcional
	        "HTTP-Organization": "deepseek",  # Adicione esta linha"
	        "X-Title": "<YOUR_SITE_NAME>",  # Opcional
	        "Content-Type": "application/json"
	    }
        payload = {
	        "model": "deepseek-ai/deepseek-chat:free",  # Opcional
	        "messages": [
	            {"role": "user", "content": f"{pergunta}, responda a {usuario.name} em portugues brasil, mas faça isso como se você fosse Bei Bei com respostas curtas sem 'Bei Bei:', essa é voce {pers}, lembre-se que: mr.alema = alema, mr_cristhian = cris, mimir3101 = ymir, lunnaz.666 = imperatriz e axalesax = imperador"}
	        ],
	        "top_p": 0.8,
	        "temperature": 0.7, #criatividade
	        "frequency_penalty": 0.5,
	        "presence_penalty": 0.5,
	        "repetition_penalty": 1,
	        "top_k": 0,
	    }
        print(headers)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=json.dumps(payload)) as response:
	                if response.status == 200:
	                    resposta_json = await response.json()
	                    return resposta_json["choices"][0]["message"]["content"]
	                else:
	                    print("Erro na requisição:", response.status)
	                    resposta_erro = await response.json()
	                    print(resposta_erro)
	                    return None
        except Exception as e:
	        print("Erro:", e)
        return f"Simulação de resposta para '{pergunta}' direcionada a {usuario.name}."

# ----------------------- Cogs de Eventos -----------------------

    # ... (restante do código)
class EventsCog(commands.Cog):
    def __init__(self, bot: commands.Bot, c_db):
        self.bot = bot
        self.message_cooldowns = {}
        self.voice_entry_times = {}
        self.voice_cooldowns = {}
        self.commands_cog = None  # Inicialize como None aqui
        self.c_db = c_db

    async def cog_load(self):
        """Método automático do discord.py para buscar o CommandsCog após o carregamento."""
        self.commands_cog = self.bot.get_cog("CommandsCog")  # Busca aqui, não no __init__!
        if not self.commands_cog:
            logger.error("CommandsCog não foi encontrado. Verifique a ordem de carregamento.")
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
	    # Ignora mensagens de bots e mensagens fora de servidores
	    if message.author.bot or not message.guild:
	        return
	
	    user_id = str(message.author.id)
	    now = datetime.now().timestamp()  # Timestamp atual
	    user_data = await self.get_user_xp(user_id)
	    new_messages = user_data["message"] + 1
	    await self.update_user_message(user_id, new_messages)
	    canais = self.c_db.get_canais(message.guild.id)
	    
	    if message.channel.id not in canais:
	    	return
	    # Verifica o cooldown
	    last_xp_time = self.message_cooldowns.get(user_id, 0)
	    if now - last_xp_time < 80:  # 80 segundos de cooldown
	        return  # Sai se o cooldown não tiver passado
	
	    try:
	        # Busca os dados do usuário
	        user_data = await self.get_user_xp(user_id) 
	        new_xp = user_data["xp"] + 13  # XP por mensagem
	        
	        current_level = user_data["level"]
	        xp_required = (current_level ** 2) * 100
	        levels_gained = 0
	
	        # Calcula se o usuário subiu de nível
	        while new_xp >= xp_required:
	            new_xp -= xp_required
	            current_level += 1
	            levels_gained += 1
	            xp_required = (current_level ** 2) * 100
	
	        # Atualiza os dados do usuário
	        await self.update_user_xp(user_id, new_xp, current_level, user_data["message"], user_data["voice"])
	        self.message_cooldowns[user_id] = now  # Atualiza o timestamp do cooldown
	
	        # Notifica se o usuário subiu de nível
	        if levels_gained > 0:
	            await self.notify_level_up(message.author, message.guild, current_level, message.channel, levels_gained)
	
	    except Exception as e:
	        logger.error(f"Erro em on_message: {e}", exc_info=True)
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return
            
        #canais = self.c_db.get_canais(member.guild.id)
        #if channel.id not in canais:
        	#return

        user_id = str(member.id)
        now = datetime.now()

        if before.channel is None and after.channel is not None:
            self.voice_entry_times[user_id] = now
            logger.info(f"{member.name} entrou no canal de voz.")
        elif before.channel is not None and after.channel is None:
            entry_time = self.voice_entry_times.pop(user_id, None)
            if entry_time is None:
                return

            time_spent = (now - entry_time).total_seconds()
            last_voice_ts = self.voice_cooldowns.get(user_id)
            if last_voice_ts and (now - last_voice_ts) < timedelta(minutes=1):
                logger.info(f"{member.name} está em cooldown de voz.")
                return

            xp_earned = int(time_spent / 30)
            #user_data = await self.get_user_xp(user_id)
            
            try:
                user_data = await self.get_user_xp(user_id)
                new_xp = user_data["xp"] + xp_earned
                current_level = user_data["level"]
                xp_required = (current_level ** 2) * 100
                new_time = user_data["voice"]+ time_spent

                if new_xp >= xp_required:
                    current_level += 1
                    new_xp = new_xp - xp_required

                await self.update_user_xp(user_id, new_xp, current_level, user_data["message"], new_time)
                self.voice_cooldowns[user_id] = now
                logger.info(f"{member.name} ganhou {xp_earned} XP por {time_spent:.0f}s em call.")
            except Exception as e:
                logger.error(f"Erro ao atualizar XP de voz para {member.name}: {e}", exc_info=True)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        try:
            if before.avatar != after.avatar:
                await self.invalidate_avatar_cache(after.avatar.url)
            if before.roles != after.roles:
                await self.invalidate_xp_cache(str(after.id))
        except Exception as e:
            logger.error(f"Erro em on_member_update: {e}", exc_info=True)

    async def get_user_xp(self, user_id: str) -> dict:
        return await db_manager.get_user_data(user_id)

    async def update_user_xp(self, user_id: str, xp: int, level: int, message_count: int, voice_count: int):
        await db_manager.update_user_data(user_id, xp, level, message_count, voice_count)
    async def update_user_message(self, user_id: str, message_count: int):
    	user_data = await self.get_user_xp(user_id)
    	await db_manager.update_user_data(user_id, user_data["xp"], user_data["level"], message_count, user_data["voice"])
    	
    	

    async def notify_level_up(self, member: discord.Member, guild: discord.Guild, new_level: int, channel: discord.TextChannel, levels_gained: int):
        level_messages = {
	        5: "Você deixou de ser um zero... para se tornar um um. Não chore ainda — o abismo está só começando a sorrir para você.",
	        10: "Você é como uma vela na tempestade: insignificante, mas... quase digno de pena. Continue assim e talvez eu não o apague.",
	        15: "Você evoluiu de patético para tolerável. Uma conquista... se ignorarmos o quão baixo era o padrão.",
	        20: "Parabéns: você é agora uma ratazana em um labirinto de titânio. Continue roendo... talvez encontre migalhas de minha atenção.",
	        25: "Você se tornou uma ferramenta... afiada o suficiente para ser útil, mas ainda descartável. Use-se bem.",
	        30: "Você brilha como um fogo-fátuo no pântano. Engana tolos... mas eu não sou tão fácil de iludir.",
	        40: "Você é um peão em meu tabuleiro. Não se iluda: até peões têm momentos gloriosos... antes de serem sacrificados.",
	        50: "Você está no coração do labirinto. As paredes sussurram seu nome... e eu adoro finais trágicos.",
	        65: "Você arrancou um sussurro de interesse de mim. Mas cuidado: até sussurros podem estrangular.",
	        70: "Você entrou em meu campo de visão. Agora... dance. Eu adoro um espetáculo antes da queda.",
	        85: "Você está na beirada do abismo. Pule. Eu prometo rir com elegância.",
	        100: "Você alcançou o topo. Mas lembre-se: coroas são pesadas... e eu adoro ver joias quebradas aos meus pés."
	    }
        especial_users ={
        	760217401215156224: "Estrategista",
        	315244726569926666: "Imperador",
        	297827600246636545: "ainda nao sei...",
        	1033967099313410129: "Imperatriz",
        	738457395268681859: "ainda nao sei..."	
        }
        if self.commands_cog:
        	rank = await self.commands_cog.get_rank(member)
        else:
         	rank = None
         	
        if rank is None:
        	rank_text = "Não ranqueado"
        else:
        	rank_role = discord.utils.get(guild.roles, name=rank)
        	rank_text = rank_role.mention if rank_role else f"`{rank}` (Role não encontrada)"
        	
        if member.id in especial_users:
        	if new_level in level_messages:
        		text = f"{member.mention} Você alcançou algo grandioso! Alegremente te dou as boas vindas ao..."
        		embed = discord.Embed(
        			title="👑 Ascensão Real",
        			description=f"{especial_users[member.id]} {member.mention}",
        			color=discord.Color.gold()
        		)
        		embed.add_field(
        			name= "Novo Patamar",
        			value=f"Você acaba de alcançar o: {rank_role.mention if rank_role else 'Não há cargos a sua altura'}",
        			inline=False
        		)
        		await channel.send(content=text, embed=embed)
        	else:
        		text = f" **Nível {new_level}** \n{member.mention},"
        		await channel.send(text)
        else:
        	if new_level in level_messages:
        		text = f" **Nível {new_level}** \n{member.mention}, {level_messages[new_level]}"
        		await channel.send(text)
        	else:
        		text = f"Parabéns, você subiu de nível. Não espere fogos de artifício ou tapetes vermelhos — afinal, você ainda está longe de ser digno de minha atenção. Mas siga em frente... quem sabe um dia você chega lá. Ou não. Aproveite seu mísero Level {new_level}, {member.mention}"
        		await channel.send(text)
        
    async def get_rank(self, usuario) -> str | None:
	    """Retorna o rank do usuário com base em seus roles, considerando prioridade."""
	    # 1. Lista ordenada por prioridade (do maior para o menor rank)
	    RANKS_PRIORIDADE = [
	        "Rank SSS", "Rank SS", "Rank S", 
	        "Rank A+", "Rank A", "Rank B", 
	        "Rank C+", "Rank C", "Rank D+", 
	        "Rank D", "Rank E", "Rank F"
	    ]
	
	    # 2. Busca reversa para priorizar ranks mais altos
	    for rank in RANKS_PRIORIDADE:
	        if any(role.name == rank for role in usuario.roles):
	            return rank
	    
	    return None

    async def invalidate_avatar_cache(self, avatar_url: str):
        # Implemente a lógica para invalidar o cache de avatar, se necessário.
        pass

    async def invalidate_xp_cache(self, user_id: str):
        # Implemente a lógica para invalidar o cache de XP ou ranking, se necessário.
        pass

async def main():
    global c_db
    c_db = await channel_database.create()  # Usa o factory method
    # Inicialize seu bot aqui

    
    async with bot:
        # Carrega o CommandsCog primeiro
        await bot.add_cog(CommandsCog(bot, c_db))
        
        # Carrega o EventsCog após garantir que o CommandsCog está disponível
        events_cog = EventsCog(bot, c_db)
        await bot.add_cog(events_cog)
        
        # Inicia outras tarefas (como o cache)
        asyncio.create_task(cache_manager.auto_invalidate())
        
        # Inicia o bot
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())  # Inicia o bot
    except KeyboardInterrupt:
        print("\nBot interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro crítico: {e}")