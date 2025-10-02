
# swthdc.py - Bot de Discord com Painel Web (Flask)
# -----------------------------------------------------------------------
# Descrição: Bot multifuncional (comandos de moderação, utilidades e social)
#           que inclui um painel administrativo básico via Flask.
# Autor: Sasa (Discord ID: 13wxz)
# Versão: 1.0 (2025)
# -----------------------------------------------------------------------


import os
import discord  # type: ignore
from discord.ext import commands
from typing import Optional
from discord import app_commands 
from flask import Flask, render_template_string, request, redirect, url_for
import threading
import hashlib
import asyncio

# O código irá procurar uma variável de ambiente chamada DISCORD_TOKEN
TOKEN = os.environ.get('DISCORD_TOKEN') 

# ----------------------------------------------------
# >>> ID do canal de Boas-Vindas atualizado
WELCOME_CHANNEL_ID = 1422958989959893113 
# ----------------------------------------------------

intents = discord.Intents.default() 
intents.message_content = True # Necessário para ler o conteúdo das mensagens
intents.members = True  # Necessário para listar membros no painel
intents.voice_states = True # Necessário para comandos relacionados a voz

bot = commands.Bot(command_prefix='!', intents=intents, fetch_members=True)

# Painel Flask
app = Flask(__name__)

# HTML do painel
HTML = """
<!doctype html>
<html lang='pt-br'>
<head>
        <meta charset='utf-8'>
        <title>Painel do Bot Discord</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&family=Quicksand:wght@500;700&display=swap" rel="stylesheet">
        <style type="text/css">
                :root {
                        --frost-bg: rgba(255,255,255,0.82);
                        --frost-dark: rgba(40, 20, 50, 0.82);
                        --main-bg: #fff;
                        --main-bg-dark: linear-gradient(135deg, #101014 0%, #23232a 100%);
                        --main-color: #1a2a3a;
                        --main-color-dark: #f6f6fa;
                        --accent: #3a7bd5;
                        --accent2: #6ec6ff;
                        --input-bg: rgba(255,255,255,0.95);
                        --input-bg-dark: rgba(32,32,38,0.72);
                        --footer: #3a7bd5;
                        --footer-dark: #bfc1c7;
                        --shadow: 0 8px 32px 0 rgba(58, 123, 213, 0.10);
                        --shadow-dark: 0 6px 24px 0 rgba(0,0,0,0.13);
                }
                [data-theme="dark"] {
                        --main-bg: linear-gradient(135deg, #101014 0%, #23232a 100%);
                        --main-color: #f6f6fa;
                        --panel-bg: rgba(24, 24, 27, 0.82);
                        --frost-bg: rgba(24, 24, 27, 0.82);
                        --input-bg: rgba(32,32,38,0.72);
                        --accent: #f6f6fa;
                        --accent2: rgba(255,255,255,0.18);
                        --footer: #bfc1c7;
                        --shadow: 0 6px 24px 0 rgba(0,0,0,0.13);
                }
                html, body {
                        height: 100%;
                }
                body {
                        background: var(--main-bg);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-family: 'Quicksand', 'Nunito', 'gg sans', 'Segoe UI', Arial, sans-serif;
                        color: var(--main-color);
                        transition: background 0.5s cubic-bezier(.4,0,.2,1);
                }
                .painel {
                        background: var(--frost-bg);
                        border-radius: 22px;
                        box-shadow: var(--shadow);
                        padding: 36px 32px 28px 32px;
                        min-width: 320px;
                        max-width: 410px;
                        border: 1.5px solid rgba(255,255,255,0.18);
                        margin: 18px;
                        backdrop-filter: blur(22px) saturate(1.3);
                        -webkit-backdrop-filter: blur(22px) saturate(1.3);
                        display: flex;
                        flex-direction: column;
                        align-items: stretch;
                        transition: background 0.5s, border 0.3s;
                }
                [data-theme="dark"] .painel {
                        background: var(--frost-bg);
                        border: 1.5px solid rgba(255,255,255,0.13);
                }
                .bot-header {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 16px;
                        margin-bottom: 16px;
                }
                .bot-avatar {
                        width: 56px;
                        height: 56px;
                        border-radius: 50%;
                        border: 2.5px solid rgba(255,255,255,0.18);
                        box-shadow: 0 2px 8px 0 rgba(0,0,0,0.10);
                        background: #fff;
                        object-fit: cover;
                        transition: border 0.3s;
                }
                .bot-name {
                        font-size: 1.32em;
                        font-weight: 700;
                        color: var(--accent);
                        font-family: 'Quicksand', Arial, sans-serif;
                        letter-spacing: 0.5px;
                        text-shadow: 0 2px 8px #eaf6ff88;
                }
                h2 {
                        text-align: center;
                        margin-bottom: 16px;
                        font-weight: 700;
                        letter-spacing: 0.5px;
                        color: var(--accent);
                        font-family: 'Quicksand', 'gg sans', Arial, sans-serif;
                        font-size: 1.18em;
                        text-shadow: 0 2px 8px #eaf6ff55;
                }
                label {
                        display: block;
                        margin-top: 16px;
                        margin-bottom: 6px;
                        font-size: 1.07em;
                        color: var(--footer);
                        font-weight: 600;
                        letter-spacing: 0.1px;
                }
                input, select {
                        width: 100%;
                        padding: 14px 18px;
                        border-radius: 12px;
                        border: 1.5px solid var(--accent2);
                        margin-bottom: 14px;
                        background: var(--input-bg);
                        color: var(--main-color);
                        font-size: 1.08em;
                        outline: none;
                        font-family: 'SF Pro Display', 'San Francisco', 'Quicksand', 'Nunito', 'gg sans', 'Segoe UI', Arial, sans-serif;
                        transition: box-shadow 0.18s, border 0.18s;
                        box-sizing: border-box;
                        text-align: center;
                }
                input:focus, select:focus {
                        box-shadow: 0 0 0 2px var(--accent);
                        border: 1.5px solid var(--accent);
                }
                button {
                        width: 100%;
                        padding: 13px 0;
                        margin-top: 18px;
                        background: rgba(255,255,255,0.82);
                        color: var(--accent);
                        border: none;
                        border-radius: 12px;
                        font-size: 1.13em;
                        font-weight: 700;
                        font-family: 'SF Pro Display', 'San Francisco', 'Quicksand', 'Nunito', 'gg sans', 'Segoe UI', Arial, sans-serif;
                        cursor: pointer;
                        letter-spacing: 0.5px;
                        box-shadow: 0 2px 8px 0 rgba(0,0,0,0.10);
                        transition: background 0.18s, color 0.18s, box-shadow 0.18s, transform 0.09s;
                        position: relative;
                        overflow: hidden;
                        backdrop-filter: blur(6px) saturate(1.1);
                }
                [data-theme="dark"] button {
                        background: rgba(24,24,27,0.82);
                        color: var(--accent);
                }
                button:hover {
                        background: rgba(255,255,255,0.95);
                        box-shadow: 0 4px 16px 0 rgba(0,0,0,0.13);
                        filter: brightness(1.04);
                }
                [data-theme="dark"] button:hover {
                        background: rgba(24,24,27,0.95);
                        filter: brightness(1.08);
                }
                button:active {
                        transform: scale(0.98);
                        filter: brightness(0.97);
                }
                button::after {
                        content: '';
                        position: absolute;
                        left: 50%;
                        top: 50%;
                        width: 0;
                        height: 0;
                        background: rgba(0,0,0,0.04);
                        border-radius: 50%;
                        transform: translate(-50%, -50%);
                        transition: width 0.3s cubic-bezier(.4,0,.2,1), height 0.3s cubic-bezier(.4,0,.2,1);
                        z-index: 1;
                }
                button:active::after {
                        width: 180%;
                        height: 180%;
                }
                .footer {
                        margin-top: 24px;
                        text-align: center;
                        font-size: 0.98em;
                        color: var(--footer);
                        font-family: 'Nunito', 'gg sans', Arial, sans-serif;
                        letter-spacing: 0.1px;
                }
                .footer a {
                        color: var(--accent);
                        text-decoration: underline;
                }
                .custom-select-wrapper {
                        position: relative;
                        width: 100%;
                        margin-bottom: 10px;
                }
                .custom-select {
                        background: var(--input-bg);
                        color: var(--main-color);
                        border-radius: 12px;
                        border: 1.5px solid var(--accent2);
                        padding-right: 38px;
                        font-size: 1em;
                        font-family: 'Nunito', 'gg sans', Arial, sans-serif;
                        cursor: pointer;
                        appearance: none;
                        -webkit-appearance: none;
                        -moz-appearance: none;
                }
                .custom-select:focus {
                        box-shadow: 0 0 0 2px var(--accent);
                        border: 1.5px solid var(--accent);
                }
                .custom-arrow {
                        position: absolute;
                        right: 18px;
                        top: 50%;
                        transform: translateY(-50%);
                        pointer-events: none;
                        color: var(--accent);
                        font-size: 1.2em;
                        font-family: 'Quicksand', 'Nunito', Arial, sans-serif;
                        text-shadow: 0 2px 8px #eaf6ff88;
                }
                .feedback {
                        margin-top: 10px;
                        text-align: center;
                        font-size: 1.04em;
                        color: var(--accent);
                        font-weight: 600;
                        min-height: 24px;
                        transition: color 0.18s;
                }
                .toggle-dark {
                        position: absolute;
                        top: 18px;
                        right: 18px;
                        background: var(--frost-bg);
                        border: 1.5px solid var(--accent2);
                        border-radius: 50%;
                        width: 38px;
                        height: 38px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        cursor: pointer;
                        transition: background 0.18s, border 0.18s;
                        z-index: 10;
                        box-shadow: 0 2px 8px 0 var(--accent2)33;
                        backdrop-filter: blur(8px) saturate(1.2);
                }
                .toggle-dark:hover {
                        border: 1.5px solid var(--accent);
                }
                @media (max-width: 600px) {
                        .painel {
                                min-width: unset;
                                max-width: 98vw;
                                padding: 16px 4vw 16px 4vw;
                        }
                        .bot-header {
                                flex-direction: column;
                                gap: 7px;
                        }
                }
        </style>
</head>

                <div id="colorBtnWrap" style="position:absolute;top:18px;right:66px;z-index:11;width:38px;height:38px;">
                        <span id="colorBtnBg" style="position:absolute;left:0;top:0;width:38px;height:38px;display:flex;align-items:center;justify-content:center;font-size:1.3em;pointer-events:none;user-select:none;
                                background:var(--frost-bg);border-radius:50%;border:1.5px solid var(--accent2);box-shadow:0 2px 8px 0 var(--accent2)33;backdrop-filter:blur(8px) saturate(1.2);transition:background 0.18s,border 0.18s;"></span>
                        <span style="position:absolute;left:0;top:0;width:38px;height:38px;display:flex;align-items:center;justify-content:center;font-size:1.3em;pointer-events:none;user-select:none;">🎨</span>
                        <input type="color" id="colorPicker" value="#3a7bd5" title="Mudar cor do tema" style="width:38px;height:38px;border-radius:50%;border:none;box-shadow:none;cursor:pointer;outline:none;opacity:0;position:absolute;left:0;top:0;">
                </div>
                <div class="toggle-dark" onclick="toggleTheme()" title="Alternar tema">
                        <span id="theme-icon">🌙</span>
                </div>
                <div class="painel">
                <div class="bot-header">
                        <img src="{{ bot_avatar }}" class="bot-avatar" alt="Avatar do bot">
                        <span class="bot-name">{{ bot_name }}</span>
                </div>
                <h2>Status: {{ status }}</h2>
                <form method="post" action="/send" id="msgform" autocomplete="off">
                        <label>Canal de envio:</label>
                        <div class="custom-select-wrapper">
                                <select name="channel_id" class="custom-select" required>
                                        <option value="" disabled selected>Selecione um canal...</option>
                                        {% for channel in channels %}
                                                <option value="{{ channel.id }}">#{{ channel.name }}</option>
                                        {% endfor %}
                                </select>
                                <span class="custom-arrow">▼</span>
                        </div>
                        <label>Membro (opcional):</label>
                        <div class="custom-select-wrapper">
                                <select name="member_id" class="custom-select">
                                        <option value="">Nenhum</option>
                                        {% for member in members %}
                                                <option value="{{ member.id }}">{{ member.name }}#{{ member.discriminator }}</option>
                                        {% endfor %}
                                </select>
                                <span class="custom-arrow">▼</span>
                        </div>
                        <label>Cor do Embed (Opcional):</label>
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                                <input name="embed_color" type="color" value="#3a7bd5" title="Selecione a cor do Embed" style="width: 50px; height: 50px; padding: 0; margin-bottom: 0;">
                                <input name="embed_title" maxlength="256" placeholder="Título do Embed (Opcional)" style="flex-grow: 1; margin-bottom: 0;">
                        </div>
                        <label style="margin-top: 10px;">Conteúdo Principal (Mensagem ou Descrição do Embed):</label>
                        <input name="message" required maxlength="2000" placeholder="Digite a mensagem simples OU a descrição do Embed...">
                        
                        <label>URL da Imagem (Opcional):</label>
                        <input name="embed_image_url" maxlength="2048" placeholder="https://exemplo.com/sua-imagem.png">
                        <button type="submit" id="sendbtn">Enviar Mensagem</button>
                        <div class="feedback" id="feedback">{{ feedback }}</div>
                </form>
                <div class="footer">Bot Discord &copy; 2025<br>Criado por <b>Sasa</b> (<a href="https://discord.com/users/13wxz" target="_blank">13wxz</a>)</div>
        </div>
                                <style type="text/css">
                                        #colorBtnWrap:hover #colorBtnBg {
                                                border: 1.5px solid var(--accent);
                                        }
                                </style>
                        <script>
                        // Dark mode toggle
                        function toggleTheme() {
                                const html = document.documentElement;
                                const icon = document.getElementById('theme-icon');
                                if (html.getAttribute('data-theme') === 'dark') {
                                        html.removeAttribute('data-theme');
                                        icon.textContent = '🌙';
                                        localStorage.setItem('theme', 'light');
                                } else {
                                        html.setAttribute('data-theme', 'dark');
                                        icon.textContent = '☀️';
                                        localStorage.setItem('theme', 'dark');
                                }
                        }
                        // Load theme from storage
                        (function() {
                                const theme = localStorage.getItem('theme');
                                if (theme === 'dark') {
                                        document.documentElement.setAttribute('data-theme', 'dark');
                                        document.getElementById('theme-icon').textContent = '☀️';
                                }
                                // Carregar cor customizada
                                const accent = localStorage.getItem('accent');
                                if (accent) {
                                        setAccentColor(accent);
                                        document.getElementById('colorPicker').value = accent;
                                }
                        })();
                        // Feedback visual após envio
                        document.getElementById('msgform').addEventListener('submit', function() {
                                document.getElementById('sendbtn').disabled = true;
                                document.getElementById('feedback').textContent = 'Enviando...';
                        });
                        // Troca cor do tema
                                        function setAccentColor(color) {
                                                document.documentElement.style.setProperty('--accent', color);
                                                document.documentElement.style.setProperty('--accent2', color + '99');
                                                document.documentElement.style.setProperty('--footer', color);
                                                localStorage.setItem('accent', color);
                                        }
                        document.getElementById('colorPicker').addEventListener('input', function(e) {
                                setAccentColor(e.target.value);
                        });
                </script>
</body>
</html>
"""

@app.route('/') # Página principal do painel
def index():
        status = "Online" if bot.is_ready() else "Desconectado"
        members = []
        channels = []
        bot_avatar = "https://cdn.discordapp.com/embed/avatars/0.png"
        bot_name = "Bot Discord"
        if bot.guilds:
                guild = bot.guilds[0]
                members = [m for m in guild.members if not m.bot]
                channels = [c for c in guild.text_channels]
        if bot.user:
                bot_avatar = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
                bot_name = bot.user.name
        feedback = request.args.get('feedback', '')
        return render_template_string(HTML, status=status, members=members, channels=channels, bot_avatar=bot_avatar, bot_name=bot_name, feedback=feedback)


@app.route('/send', methods=['POST']) # Rota para enviar mensagem
def send():
        print("[PAINEL] Pedido de envio recebido!")
        channel_id = request.form.get('channel_id') # ID do canal
        message_content = request.form.get('message', '').strip() # Conteúdo principal (Mensagem/Descrição)
        member_id = request.form.get('member_id') # ID do membro (opcional)
        
        # Campos NOVOS para Embed
        embed_title = request.form.get('embed_title', '').strip()
        embed_color_hex = request.form.get('embed_color', '#3a7bd5').replace('#', '0x')
        embed_image_url = request.form.get('embed_image_url', '').strip() # NOVO CAMPO LIDO
        
        feedback = ''
        if not channel_id or not message_content:
                feedback = 'Preencha o canal e o conteúdo da mensagem.'
                return redirect(url_for('index', feedback=feedback))
        try:
                channel_id = int(channel_id)
        except Exception:
                feedback = 'Canal inválido.'
                return redirect(url_for('index', feedback=feedback))
        
        # Tenta converter a cor HEX para inteiro
        try:
                embed_color = int(embed_color_hex, 16)
        except ValueError:
                embed_color = 0x3a7bd5 
                
        # 1. Tenta criar um Embed se houver título
        if embed_title:
                try:
                        embed = discord.Embed(
                                title=embed_title,
                                description=message_content,
                                color=embed_color
                        )
                        
                        # Adiciona a imagem se a URL for fornecida
                        if embed_image_url:
                            # O Discord requer que a URL seja válida
                            if embed_image_url.lower().startswith(('http://', 'https://')):
                                embed.set_image(url=embed_image_url)
                            else:
                                print(f"[PAINEL] Aviso: URL de imagem inválida: {embed_image_url}")

                        sendable = embed 
                        content_prefix = ''
                except Exception as e:
                        print(f"[PAINEL] Erro ao criar Embed: {e}. Enviando como mensagem simples.")
                        sendable = message_content
                        content_prefix = ''
        
        # 2. Se não houver título, envia como mensagem simples
        else:
                sendable = message_content
                content_prefix = ''

        # 3. Adiciona a menção do membro, se houver
        if member_id:
                content_prefix = f'<@{member_id}> '

        channel = bot.get_channel(channel_id)
        if channel:
                print(f"[PAINEL] Enviando mensagem para canal {channel_id}...")
                try:
                        # Verifica se é um Embed ou texto simples e envia
                        if isinstance(sendable, discord.Embed):
                                asyncio.run_coroutine_threadsafe(channel.send(content=content_prefix, embed=sendable), bot.loop)
                        else:
                                final_message = f'{content_prefix}{sendable}'
                                asyncio.run_coroutine_threadsafe(channel.send(final_message), bot.loop)
                                
                        feedback = 'Mensagem/Embed enviado com sucesso!'
                except Exception as e:
                        print(f"[PAINEL] Erro ao enviar: {e}")
                        feedback = 'Erro ao enviar mensagem. (Verifique permissões do bot)'
        else:
                print(f"[PAINEL] Canal {channel_id} não encontrado!")
                feedback = 'Canal não encontrado.'
        return redirect(url_for('index', feedback=feedback))


# Função para rodar o Flask em thread separada
def run_flask():
    # Usa a variável de ambiente 'PORT' do Replit, se não encontrar, usa 5002
    port = int(os.environ.get('PORT', 5002)) 
    # Roda o servidor em 0.0.0.0 para aceitar conexões externas
    app.run(host='0.0.0.0', port=port) 

# Evento de novo membro entrando no servidor
@bot.event
async def on_member_join(member):
    # Ignora se o membro que entrou é outro bot
    if member.bot:
        return

    # Tenta obter o canal de boas-vindas usando o ID definido
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if welcome_channel:
        # Cria a mensagem de boas-vindas
        welcome_message = f"🎉 Olá **{member.mention}**! Bem-vindo(a) ao servidor **{member.guild.name}**! Sinta-se à vontade para explorar e dizer um 'oi' no chat! 🎉"
        
        # Criar um Embed (Mensagem mais bonita)
        embed = discord.Embed(
            title="Boas-vindas!",
            description=welcome_message,
            color=0x3a7bd5 # A cor do seu tema
        )
        # Define o avatar do usuário como thumbnail
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        # Adiciona a contagem de membros no rodapé
        embed.set_footer(text=f"Temos agora {len(member.guild.members)} membros!")

        try:
            # Envia a mensagem no canal de boas-vindas
            await welcome_channel.send(embed=embed)
        except discord.Forbidden:
            print(f"❌ Erro: Não tenho permissão para enviar mensagens no canal {welcome_channel.name}.")
        except Exception as e:
            print(f"❌ Erro ao enviar boas-vindas: {e}")
    else:
        print(f"❌ Aviso: O canal de boas-vindas com ID {WELCOME_CHANNEL_ID} não foi encontrado.")

# Comando tradicional (!oi)
@bot.command() 
async def oi(ctx, membro: discord.Member = None): 
        if membro:
                await ctx.send(f'Olá, {membro.mention}! Eu sou o bot da sasa.') 
        else:
                await ctx.send('Olá! Eu sou o bot da sasa.') 

# Comando Slash /help
@bot.tree.command(name="help", description="Mostra a lista de comandos e funcionalidades do Sweetheart.")
async def slash_help(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    
    # Definindo a cor e o ícone do bot para o Embed
    cor_lavanda = 0x8A2BE2  # Roxo Lavanda
    
    embed = discord.Embed(
        title="💖 Central Sweetheart | Ajuda Inevitável",
        description="Eu sou a sua ferramenta de gerenciamento e conexão. Use os comandos abaixo para interagir e moderar!",
        color=cor_lavanda
    )
    
    # --- Interação e Magia ---
    embed.add_field(
        name="✨ Interação e Magia",
        value=(
            "**/ship:** Calcule o destino e afinidade de dois usuários.\n"
            "**/genio:** Resposta mística para qualquer pergunta (sim ou não).\n"
            "**/abracar:** Dê um abraço aconchegante em alguém.\n"
            "**/bater:** Dê um tapa em alguém."
        ),
        inline=False
    )
    
    # --- Utilidade e Informação ---
    embed.add_field(
        name="🛠️ Utilidades (Em Breve)",
        value=(
            "**/dados:** Role dados (D6, D20, etc.) e descubra sua sorte.\n"
            "**/userinfo:** Veja informações de um membro (em desenvolvimento).\n"
            "**/tempo:** Veja o clima em qualquer cidade (em desenvolvimento)."
        ),
        inline=False
    )
    
    # --- Moderação e Gerenciamento ---
    embed.add_field(
        name="🛡️ Moderação Essencial",
        value=(
            "**/kick [membro]:** Expulsa temporariamente um membro.\n"
            "**/ban [membro]:** Bane permanentemente um membro.\n"
            "**/lock:** Tranca o canal atual para todos.\n"
            "**/unlock:** Destranca o canal atual.\n"
            "**/role [membro, cargo]:** *[Em Breve]* Gerencia cargos (Adicionar/Remover)."
        ),
        inline=False
    )
    
    embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
    embed.set_footer(text="Use '/' para ver todos os comandos disponíveis.")
    
    await interaction.followup.send(embed=embed)

# Slash command /oi
@bot.tree.command(name="oi", description="Diga oi para alguém!")
@app_commands.describe(
        mensagem="Mensagem a ser enviada",
        membro="Mencione um usuário (opcional)"
)
async def slash_oi(interaction: discord.Interaction, mensagem: str, membro: discord.Member = None):
        if membro is not None:
                await interaction.response.send_message(f'{mensagem} {membro.mention}')
        else:
                await interaction.response.send_message(mensagem)

# Slash command /avatar
@bot.tree.command(name="avatar", description="Mostra o avatar de um usuário!")
@app_commands.describe(
        membro="Mencione um usuário para ver o avatar"
)
async def slash_avatar(interaction: discord.Interaction, membro: discord.Member = None): 
        user = membro or interaction.user # Usa o autor se nenhum membro for mencionado
        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url # Pega o avatar ou o padrão
        embed = discord.Embed(title=f"Avatar de {user.display_name}", color=0x3a7bd5) # Cria embed
        embed.set_image(url=avatar_url) # Define a imagem do embed
        await interaction.response.send_message(embed=embed) # Envia o embed

# Slash command /apagar
@bot.tree.command(name="apagar", description="Apaga mensagens do chat")
@app_commands.describe(
    quantidade="Quantidade de mensagens a serem apagadas (até 100)"
)
async def slash_apagar(interaction: discord.Interaction, quantidade: int):
    # Verifica se o usuário tem permissão
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Você não tem permissão para apagar mensagens.", ephemeral=True)
        return
        # Verifica se a quantidade é válida    
    if quantidade < 1 or quantidade > 100:
        await interaction.response.send_message("⚠️ A quantidade deve ser entre 1 e 100.", ephemeral=True)
        return

    # Responde imediatamente para evitar timeout
    await interaction.response.defer(ephemeral=True)

    try: 
        apagadas = await interaction.channel.purge(limit=quantidade) 
        await interaction.followup.send(f"✅ Foram apagadas {len(apagadas)} mensagens.", ephemeral=True) 
    except Exception as e: 
        await interaction.followup.send(f"❌ Erro ao tentar apagar: {e}", ephemeral=True) 

# Slash command restrito a administradores para desconectar usuários da call /disconnect
@bot.tree.command(name="disconnect", description="Desconecta um usuário da call (somente admins)") 
@app_commands.describe(user="Usuário que será desconectado")
async def disconnect(interaction: discord.Interaction, user: discord.Member):
    # Verifica se quem usou o comando é administrador
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
        return

    if not user.voice:
        await interaction.response.send_message(f"{user.mention} não está em um canal de voz.", ephemeral=True)
        return

    try:
        await user.move_to(None)  # desconecta o usuário
        await interaction.response.send_message(
            f"{user.mention} foi desconectado da call por {interaction.user.mention}."
        )
    except discord.Forbidden:
        await interaction.response.send_message("Eu não tenho permissão para desconectar este usuário.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Ocorreu um erro: {e}", ephemeral=True)

# Slash command /info
@bot.tree.command(name="info", description="Exibe informações detalhadas sobre um membro.")
@app_commands.describe(membro="O membro sobre quem você deseja informações.")
async def slash_info(interaction: discord.Interaction, membro: discord.Member):
    # Responde imediatamente para evitar o tempo limite, já que a operação é rápida
    await interaction.response.defer()
    
    # Formata as datas no padrão brasileiro
    def format_date(dt):
        return dt.strftime("%d/%m/%Y, %H:%M:%S")

    # 1. Definir a cor do Embed e o status
    status_cores = {
        discord.Status.online: 0x43b581, # Verde
        discord.Status.idle: 0xfaa61a,   # Laranja
        discord.Status.dnd: 0xf04747,    # Vermelho
        discord.Status.offline: 0x747f8d, # Cinza
    }
    
    cor_embed = status_cores.get(membro.status, 0x747f8d)
    
    # 2. Construir o Embed
    embed = discord.Embed(
        title=f"Informações de {membro.display_name}",
        color=cor_embed
    )
    
    # Adiciona a imagem de perfil
    embed.set_thumbnail(url=membro.avatar.url if membro.avatar else membro.default_avatar.url)
    
    # Adiciona campos essenciais
    embed.add_field(name="<:ID:942484050215905330> ID do Usuário", value=membro.id, inline=False)
    
    # 3. Informações da Conta
    embed.add_field(
        name="Conta Criada em",
        value=format_date(membro.created_at),
        inline=True
    )
    
    # 4. Informações no Servidor
    embed.add_field(
        name="Entrou no Servidor em",
        value=format_date(membro.joined_at),
        inline=True
    )
    
    # 5. Cargos (Roles)
    # Pega todos os cargos, exceto o @everyone, e os lista
    cargos = [role.mention for role in membro.roles if role.id != membro.guild.id]
    
    if cargos:
        # Limita a exibição para que a mensagem não fique muito longa
        cargos_list = ' '.join(cargos[:10]) + (f' e mais {len(cargos) - 10}...' if len(cargos) > 10 else '')
        embed.add_field(name=f"Cargos ({len(cargos)})", value=cargos_list, inline=False)
    else:
        embed.add_field(name="Cargos", value="Nenhum cargo.", inline=False)
        
    # 6. Status e Menção
    embed.set_footer(text=f"Menção: {membro.mention}")

    # Envia o Embed como resposta
    await interaction.followup.send(embed=embed)

# Slash command /abracar
@bot.tree.command(name="abracar", description="Dê um abraço caloroso em alguém! ❤️")
@app_commands.describe(membro="O membro que você deseja abraçar (opcional).")
async def slash_abracar(interaction: discord.Interaction, membro: Optional[discord.Member]):
    await interaction.response.defer()
    
    autor = interaction.user
    
    # Lista de GIFs/Imagens de abraço (Com seus GIFs personalizados)
    gifs_abraco = [
       "https://i.pinimg.com/originals/ab/58/a8/ab58a8f3ad91fd62911f84bf3d54127c.gif",
        "https://i.pinimg.com/originals/16/f4/ef/16f4ef8659534c88264670265e2a1626.gif",
        "https://i.pinimg.com/originals/dd/d4/2c/ddd42c994d225d87c0c635ca7cb2c10b.gif",
        "https://media.tenor.com/kCZjTqCKiggAAAAM/hug.gif",
        "https://i.pinimg.com/originals/c8/67/f6/c867f6e32eb7bc81760015dfc08f4d05.gif",
    ]
    
    import random
    gif_selecionado = random.choice(gifs_abraco)
    cor_embed = 0xffa500 # Cor laranja padrão

    # Verifica se um membro foi mencionado
    if membro:
        # Menção explícita no título e descrição.
        if membro.id == autor.id:
            # Caso 1: O usuário abraça a si mesmo
            titulo = f"🤗 Auto-Abraço de {autor.display_name}! 🤗"
            descricao = f"{autor.mention} está demonstrando carinho por si mesmo! Às vezes, é necessário."
            
        elif membro.bot:
            # Caso 2: O usuário tenta abraçar um bot
            titulo = f"🤖 {autor.display_name} abraçou o Bot! 🤖"
            descricao = f"{autor.mention}, meus circuitos de afeto estão ativados. Obrigado pelo carinho! (beep boop)"
            
        else:
            # Caso 3: O usuário abraça outro membro - USANDO MENÇÃO AQUI!
            titulo = f"🥰 Um Abraço Caloroso! 🥰"
            # Aqui garantimos que os dois membros são mencionados
            descricao = f"{autor.mention} deu um abraço em {membro.mention}!"
            
            if isinstance(membro, discord.Member):
                 cor_embed = membro.color if membro.color != discord.Color.default() else 0xffa500

    else:
        # Caso 4: Ninguém foi mencionado (Abraço geral)
        titulo = f"💖 {autor.display_name} está a distribuir abraços! 💖"
        descricao = "Um abraço para todos no servidor!"
        cor_embed = 0x3a7bd5 # Cor azul

    # 2. Construir o Embed
    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=cor_embed
    )
    
    # Adiciona o GIF selecionado
    embed.set_image(url=gif_selecionado)
    
    # 3. Envia o Embed como resposta
    await interaction.followup.send(embed=embed)

# Slash command /cara-ou-coroa
@bot.tree.command(name="cara-ou-coroa", description="Lança uma moeda virtualmente para Cara ou Coroa.")
async def slash_moeda(interaction: discord.Interaction):
    await interaction.response.defer()
    
    import random
    
    # As opções de resultado
    resultado = random.choice(["Cara", "Coroa"])
    
    # Define o emoji e a cor do Embed baseado no resultado
    if resultado == "Cara":
        emoji = "👑"
        cor = 0xf1c40f  # Amarelo
    else:
        emoji = "🪙"
        cor = 0x3498db  # Azul

    embed = discord.Embed(
        title=f"{emoji} Resultado do Lançamento: {resultado}!",
        # AQUI ESTÁ A CORREÇÃO: Usando interaction.user.mention
        description=f"{interaction.user.mention} lançou a moeda e o resultado foi **{resultado}**.",
        color=cor
    )
    
    # Opcional: Adiciona uma imagem divertida da moeda (apenas para referência visual)
    embed.set_thumbnail(url="https://art.pixilart.com/3f841d559803173.gif") 

    await interaction.followup.send(embed=embed)

# Slash command /roleta-russa
@bot.tree.command(name="roleta-russa", description="Você está com sorte? Jogue a roleta...")
async def slash_roleta(interaction: discord.Interaction):
    await interaction.response.defer()
    
    import random
    
    # Define os GIFs temáticos
    GIF_ACERTO = "https://dinopixel.com/preload/0424/gun-gifgif_1713646262.gif" # Exemplo de GIF de "acerto" (tiro, explosão, etc.)
    GIF_FALHA = "https://media.tenor.com/MkyiUsAp8t8AAAAM/tom-and-jerry-tom-the-cat.gif"  # Exemplo de GIF de "falha" (alívio, carinha feliz)

    # Sete câmaras (0 a 6). A 'bala' é aleatória de 1 a 6.
    bala_posicao = random.randint(1, 6)
    tiro = random.randint(1, 6)
    
    autor_mention = interaction.user.mention

    if tiro == bala_posicao:
        # Posição com a bala (ACERTO)
        cor = 0xc0392b # Vermelho (Drama)
        titulo = "💀 **BOOM!**"
        descricao = f"O tambor girou, o gatilho foi apertado, e na câmara **{tiro}**... Tinha uma bala.\n**{autor_mention}** não teve sorte desta vez! 😵"
        gif_final = GIF_ACERTO
    else:
        # Posição vazia (FALHA / ALÍVIO)
        cor = 0x2ecc71 # Verde (Alívio)
        titulo = "🥳 **CLIC!**"
        descricao = f"O tambor girou e parou na câmara **{tiro}**. Vazia.\n**{autor_mention}** sobreviveu por pouco! A bala estava na câmara {bala_posicao}."
        gif_final = GIF_FALHA

    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=cor
    )
    
    # Adiciona o GIF escolhido como thumbnail
    embed.set_thumbnail(url=gif_final)
    
    embed.set_footer(text="Câmaras do Tambor: 6 | Balas: 1")
    
    await interaction.followup.send(embed=embed)

# Slash command /escolher
@bot.tree.command(name="escolher", description="Ajuda você a decidir, sorteando uma opção de uma lista.")
@app_commands.describe(
    opcoes="As opções para escolher, separadas por vírgulas (ex: pizza, hambúrguer, sushi)."
)
async def slash_escolher(interaction: discord.Interaction, opcoes: str):
    await interaction.response.defer()
    
    # 1. Separar as opções
    # Remove espaços em branco antes e depois de cada opção
    lista_opcoes = [opcao.strip() for opcao in opcoes.split(',') if opcao.strip()]
    
    # 2. Verificar se há opções suficientes
    if len(lista_opcoes) < 2:
        await interaction.followup.send("❌ Você precisa fornecer pelo menos duas opções separadas por vírgulas (ex: opção 1, opção 2).", ephemeral=True)
        return

    # 3. Escolher aleatoriamente
    import random
    escolha = random.choice(lista_opcoes)

    # 4. Construir o Embed
    embed = discord.Embed(
        title="🤔 Decisão Tomada!",
        description=f"A dúvida é grande, mas a resposta é simples:",
        color=0x9b59b6 # Roxo
    )
    
    # Monta a lista de opções para exibição
    opcoes_formatadas = "\n".join([f"• {item}" for item in lista_opcoes])
    
    embed.add_field(name="Opções Consideradas:", value=opcoes_formatadas, inline=False)
    embed.add_field(name="✨ A Escolha Final é:", value=f"**{escolha.upper()}**", inline=False)
    
    embed.set_footer(text=f"Pedido por: {interaction.user.display_name}")

    # 5. Enviar a resposta
    await interaction.followup.send(embed=embed)

# Slash command /ship
@bot.tree.command(name="ship", description="Calcula a compatibilidade entre dois membros. 💕")
@app_commands.describe(
    membro_1="O primeiro membro.",
    membro_2="O segundo membro."
)
async def slash_ship(interaction: discord.Interaction, membro_1: discord.Member, membro_2: discord.Member):
    await interaction.response.defer()
    
    # --- DEFINIÇÃO DOS GIFS ESTÉTICOS ---
    GIF_EPIC = "https://i.pinimg.com/originals/30/50/d3/3050d3b5ea671bab86f6b6bc2b3f090b.gif"   # Abraço intenso (80%+)
    GIF_FORTE = "https://i.pinimg.com/originals/6a/71/c8/6a71c8522afd22f20c4e78f96cf0b150.gif"  # Corações estéticos (50-79%)
    GIF_AMIGOS = "https://media1.giphy.com/media/v1.Y2lkPTZjMDliOTUycTdsd2txdWd5bDMzMWQ0MDE5dHd6Y2tmaGlqNWpmdHZrYm82bWQ1YyZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/23D8NR89IoZUC9jgsO/giphy.gif" # Vibe de amizade/soft (0-49%)

    # 1. Base Fixa (Hash dos IDs - 80% da pontuação)
    import hashlib
    id_menor = min(membro_1.id, membro_2.id)
    id_maior = max(membro_1.id, membro_2.id)
    semente = f"{id_menor}{id_maior}seu_segredo_amoroso" 
    
    hash_valor = hashlib.md5(semente.encode()).hexdigest()
    numero_base = int(hash_valor[:2], 16)
    base_compatibilidade = round((numero_base / 255) * 80)

    # 2. Bônus de Cargos Compartilhados (20% da pontuação)
    roles_m1 = set([r.id for r in membro_1.roles if r.name != '@everyone'])
    roles_m2 = set([r.id for r in membro_2.roles if r.name != '@everyone'])
    shared_roles = len(roles_m1.intersection(roles_m2))
    min_roles = min(len(roles_m1), len(roles_m2))
    
    bonus = 0
    if min_roles > 0:
        bonus_bruto = (shared_roles / min_roles) * 20
        bonus = int(min(bonus_bruto, 20))
        
    # 3. Pontuação Final
    compatibilidade = base_compatibilidade + bonus
    if compatibilidade > 100:
        compatibilidade = 100

    # 4. Determinar a COR, FRASE e GIF (Aesthetic)
    if compatibilidade >= 80:
        cor = 0xff69b4 # Pink (Hot Pink)
        emoji = "✨💖✨"
        frase = "É um amor épico! Vocês são a combinação perfeita do universo. A conexão de vocês brilha!"
        gif_final = GIF_EPIC
    elif compatibilidade >= 50:
        cor = 0xffa07a # Salmão Claro
        emoji = "💕"
        frase = "Existe uma forte sintonia aqui. Muita fofura e potenciais momentos românticos à frente!"
        gif_final = GIF_FORTE
    else:
        cor = 0xadd8e6 # Azul Claro (Lavanda)
        emoji = "💜"
        frase = "A energia é suave! Talvez o destino reserve vocês para serem ótimos amigos ou para tentarem de novo no futuro."
        gif_final = GIF_AMIGOS

    # 5. Construir o Embed
    embed = discord.Embed(
        title=f"🌸 {emoji} Compatibilidade Astral {emoji} 🌸",
        # Usa .mention para marcar os usuários
        description=f"O destino de **{membro_1.mention}** e **{membro_2.mention}** foi revelado:",
        color=cor
    )
    
    # AQUI ESTÁ A CORREÇÃO: Usa o GIF final escolhido
    embed.set_thumbnail(url=gif_final)
    
    embed.add_field(name="Porcentagem Mágica", value=f"## {compatibilidade}%", inline=False)
    embed.add_field(name="✨ Veredito do Bot ✨", value=frase, inline=False)
    
    if shared_roles > 0:
        embed.add_field(name="Conexão do Servidor", value=f"Eles compartilham **{shared_roles}** cargos! (Isso conta!)", inline=False)

    embed.set_footer(text=f"Teste de amor solicitado por: {interaction.user.display_name}")
    
    await interaction.followup.send(embed=embed)


# Slash command /genio
@bot.tree.command(name="genio", description="Pergunte qualquer coisa ao gênio, e ele responderá.")
@app_commands.describe(pergunta="Sua pergunta de vida (sim/não ou aberta).")
async def slash_genio(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()

    import random

    # Lista de respostas
    respostas = [
        "Sim, Juro migs.", "É certo.", "Sem dúvida.", 
        "Você pode confiar nisso.", "Clarinho que sim. 💅", "Provavelmente, diva(o).", 
        "Talvez Sim.", "Sinais apontam que sim, meu amor", 
        "Resposta vaga, tente novamente.", "Pergunte novamente mais tarde.", 
        "É melhor não te dizer agora.", "Não posso prever agora.",
        "Nem sonha com com isso, best.", "Minhas fontes dizem não.", 
        "Acho que não em, love.", "JUROU KKKKKK 🙂‍↔️", "Absolutamente não."
    ]
    
    resposta_genio = random.choice(respostas)
    
    embed = discord.Embed(
        title="🔮 O Gênio Responde",
        description=f"**Você:** {pergunta}\n\n**Gênio:** {resposta_genio}",
        color=0x8e44ad
    )
    
    await interaction.followup.send(embed=embed)        

# Slash command /dados
@bot.tree.command(name="dados", description="Rola um dado com a quantidade de lados que você escolher.")
@app_commands.describe(lados="O número de lados do dado (ex: 6, 20, 100).")
async def slash_dados(interaction: discord.Interaction, lados: int):
    await interaction.response.defer()
    
    if lados < 2:
        await interaction.followup.send("❌ Um dado deve ter pelo menos 2 lados!", ephemeral=True)
        return

    import random
    
    resultado = random.randint(1, lados)
    
    # Define cores e títulos especiais para D20 (usado em RPG)
    if lados >= 20:
        cor = 0x27ae60 if resultado == lados else 0xe74c3c if resultado == 1 else 0x3498db
        emoji = "🎲"
        titulo = "Rolagem Crítica!" if resultado == lados or resultado == 1 else "Rolagem de Dado"
    else:
        cor = 0x3498db 
        emoji = "🎲"
        titulo = "Rolagem de Dado"

    embed = discord.Embed(
        title=titulo,
        description=f"{interaction.user.mention} rolou um D{lados} e o resultado foi:",
        color=cor
    )
    
    embed.add_field(name="Resultado Final", value=f"## {emoji} {resultado}", inline=False)
    
    await interaction.followup.send(embed=embed)

# Slash command /bater (Bater/Tapa)
@bot.tree.command(name="bater", description="Dê um tapinha de brincadeira em alguém! 💥")
@app_commands.describe(
    membro="O membro que receberá o tapinha."
)
async def slash_bater(interaction: discord.Interaction, membro: discord.Member):
    await interaction.response.defer()
    
    import random

    # Lista de GIFs de Tapa (Brincadeira)
    GIFS_BATER = [
        "https://i.pinimg.com/originals/67/a4/a6/67a4a69d924f76f7ee150f6099913212.gif",
        "https://i.pinimg.com/originals/e7/b4/28/e7b42852733763a11f26634ae7447534.gif", 
        "https://i.gifer.com/9KyA.gif", 
        "https://pa1.aminoapps.com/6524/a3a7f2e42e5543e579683729e08dc275c1de7333_hq.gif",  
        "https://i.gifer.com/Bopq.gif"   
    ]

    # Mensagens de Tapa (Brincadeira)
    mensagens = [
        "dá um tapa",
        "mostra quem manda",
        "solta uma mãozada",
        "acerta um tapa surpreendente"
        "dá um tapinha",
        "dá um tapa com estilo"
    ]
    
    # Lógica para o usuário interagir consigo mesmo
    if membro == interaction.user:
        titulo = "Tapa em Si Mesmo? 😅"
        descricao = f"**{interaction.user.mention}** se deu um tapinha para acordar."
        cor = 0x95a5a6 # Cinza
    else:
        titulo = "💥 SOCOU A CARA!"
        acao = random.choice(mensagens)
        descricao = f"**{interaction.user.mention}** {acao} em **{membro.mention}**!"
        cor = 0xe67e22 # Laranja (Cor de impacto)

    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=cor
    )
    
    # Adiciona o GIF aleatório
    embed.set_image(url=random.choice(GIFS_BATER))
    
    await interaction.followup.send(embed=embed)

# Comando Slash /kick
@bot.tree.command(name="kick", description="Remove (expulsa) um membro do servidor.")
@app_commands.checks.has_permissions(kick_members=True)
@app_commands.describe(
    membro="O membro a ser expulso.",
    motivo="O motivo da expulsão (aparecerá no log)."
)
async def slash_kick(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo especificado."):
    await interaction.response.defer(ephemeral=True) # Responde de forma privada

    if membro.top_role >= interaction.user.top_role:
        await interaction.followup.send(f"❌ Você não pode expulsar **{membro.display_name}**. O cargo dele é igual ou superior ao seu.")
        return

    try:
        await membro.kick(reason=motivo)
        
        embed = discord.Embed(
            title="👢 Membro Expulso!",
            description=f"**Usuário:** {membro.mention}\n**Moderador:** {interaction.user.mention}\n**Motivo:** {motivo}",
            color=0xf1c40f # Amarelo - Aviso
        )
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Ocorreu um erro ao tentar expulsar o membro: {e}")

# Comando Slash /ban
@bot.tree.command(name="ban", description="Bane (proíbe permanentemente) um membro do servidor.")
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.describe(
    membro="O membro a ser banido.",
    motivo="O motivo do banimento (aparecerá no log)."
)
async def slash_ban(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo especificado."):
    await interaction.response.defer(ephemeral=True) # Responde de forma privada

    if membro.top_role >= interaction.user.top_role:
        await interaction.followup.send(f"❌ Você não pode banir **{membro.display_name}**. O cargo dele é igual ou superior ao seu.")
        return

    try:
        await membro.ban(reason=motivo)
        
        embed = discord.Embed(
            title="🔨 Membro Banido!",
            description=f"**Usuário:** {membro.mention}\n**Moderador:** {interaction.user.mention}\n**Motivo:** {motivo}",
            color=0xe74c3c # Vermelho - Perigo
        )
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Ocorreu um erro ao tentar banir o membro: {e}")

# Comando Slash /lock e /unlock
@bot.tree.command(name="lock", description="Tranca o canal atual, impedindo que membros enviem mensagens.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_lock(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True) # Responde de forma privada
    
    canal = interaction.channel
    # Encontra a permissão padrão (@everyone)
    permissao_everyone = canal.overwrites_for(interaction.guild.default_role)

    if permissao_everyone.send_messages is False:
        await interaction.followup.send("❌ O canal já está trancado!")
        return

    # Define a permissão de envio de mensagens para FALSO para @everyone
    permissao_everyone.send_messages = False
    
    try:
        await canal.set_permissions(interaction.guild.default_role, overwrite=permissao_everyone)
        
        embed = discord.Embed(
            title="🔒 Canal Trancado!",
            description=f"Canal **{canal.mention}** foi trancado por {interaction.user.mention}.",
            color=0x2ecc71 # Verde - Sucesso
        )
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Erro ao trancar o canal: {e}")


@bot.tree.command(name="unlock", description="Destranca o canal atual, permitindo o envio de mensagens.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_unlock(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True) # Responde de forma privada
    
    canal = interaction.channel
    permissao_everyone = canal.overwrites_for(interaction.guild.default_role)
    
    if permissao_everyone.send_messages is True:
        await interaction.followup.send("❌ O canal já está destrancado!")
        return

    # Define a permissão de envio de mensagens para VERDADEIRO para @everyone
    permissao_everyone.send_messages = True
    
    try:
        await canal.set_permissions(interaction.guild.default_role, overwrite=permissao_everyone)
        
        embed = discord.Embed(
            title="🔓 Canal Destrancado!",
            description=f"Canal **{canal.mention}** foi destrancado por {interaction.user.mention}.",
            color=0x3498db # Azul - Info
        )
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Erro ao destrancar o canal: {e}")

# Sincroniza os comandos de barra ao iniciar
@bot.event
async def on_ready():

    # Define o status Rich Presence do Bot
    atividade = discord.Game(name="/help com o Destino Inevitável.")
    await bot.change_presence(activity=atividade)
    
    print(f'Bot conectado como {bot.user}') # Mostra o nome do bot no console
    try:
        # Sincroniza todos os comandos
        synced = await bot.tree.sync()
        print(f"Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Erro ao sincronizar slash commands: {e}")
# Inicia o Flask em uma thread separada
threading.Thread(target=run_flask, daemon=True).start()

bot.run(TOKEN) 
