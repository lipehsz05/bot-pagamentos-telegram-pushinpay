import telebot
import sqlite3
import time
import uuid
import requests
import logging
import base64
from io import BytesIO
from PIL import Image
import pytz
from datetime import datetime, timedelta
import calendar
from senhas import (
    TELEGRAM_BOT_TOKEN, GRUPO_ID, PUSHINPAY_TOKEN, PLANOS, ID_DONO, LINK_SUPORTE
)

# Configurar logging para depuração
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicializar o bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Definindo o fuso horário de Brasília
timezone_br = pytz.timezone('America/Sao_Paulo')

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('usuarios.db', check_same_thread=False)
cursor = conn.cursor()

# Criar tabela de usuários se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    user_id INTEGER PRIMARY KEY,
    primeiro_nome TEXT,
    data_pagamento TEXT,
    data_expiracao TEXT,
    plano TEXT
)
''')
conn.commit()

# Dicionário para armazenar códigos PIX e pagamentos pendentes
codigos_pix = {}
pagamentos_pendentes = {}

# Dicionário para armazenar links de convite e IDs de usuários correspondentes
links_convite = {}

# Dicionário para armazenar links de usuários
links_usuarios = {}

# Função para gerar um link único para um usuário
def gerar_link_unico():
    base_url = "https://seu_dominio.com/link/"  # Substitua pelo seu domínio real
    link_unico = str(uuid.uuid4())
    return base_url + link_unico

# Função para revogar o link de um usuário
def revogar_link(usuario):
    if usuario in links_usuarios:
        del links_usuarios[usuario]
        print(f"Link revogado para o usuário: {usuario}")
    else:
        print(f"Usuário {usuario} não encontrado.")

# Função para animar os pontos
def animar_pontos(chat_id, message_id, texto_inicial, duracao=3):
    pontos = ["", ".", "..", "..."]
    for i in range(duracao):
        for ponto in pontos:
            try:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"{texto_inicial}{ponto}"
                )
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Erro ao animar pontos: {e}")
                return

# Função para enviar as três mensagens iniciais
def enviar_mensagem_inicial(chat_id, primeiro_nome):
    try:
        # 1. Enviar a imagem inicio.png
        with open("inicio.png", "rb") as img:
            bot.send_photo(chat_id, img)

        # 2. Enviar a mensagem de saudação
        bot.send_message(chat_id, f"👋 Olá, {primeiro_nome}! que tal ter acesso aos melhores conteúdos de vendas e marketing do telegram?")

        # 3. Enviar a mensagem com a descrição do serviço e os botões
        descricao_servico = ("💎<b><i><u>CONTEÚDOS EXCLUSIVOS NO VIP</u></i></b>💎\n"
"\n"
"🎥 <i>OS MELHORES <b><i><u>CONTEÚDOS</u></i></b> DIRETO NO TELEGRAM</i>\n"
"\n"
"🔥 <b><i>PLANOS ACESSÍVEIS:</i></b>\n"
"   - 💵 <b><u>VITALÍCIO</u></b>\n"
"   - 💵 <b><u>MENSAL</u></b>\n"
"   - 💵 <b><u>SEMANAL</u></b>\n"
"\n"
"🔒 <b><i>ENTRADA 100% SEGURA.</i></b>\n"
"🎟️ <b><i>ACESSE E SAIA QUANDO QUISER.</i></b>\n"
"\n"
"📂 <i>Conteúdo exclusivo para empreendedores e vendedores:</i>\n"
"<blockquote>"
"<b><i>🔔 Novidades diárias sobre vendas</i></b>\n"
"<b><i>🎬 Estratégias de marketing</i></b>\n"
"<b><i>💬 Dicas de negociação e fechamento</i></b>\n"
"<b><i>📈 Casos de sucesso e insights do mercado</i></b>\n"
"</blockquote>"
"<del>--------------------------</del>\n"
"<i>Assine já e tenha acesso a <u>conteúdos atualizados diariamente!</u></i>\n"
"<del>-------------------------</del>\n"
"<b><i>FAÇA PARTE DO VIP ⤵️</i></b>\n"
"<del>-------------------------</del>\n")
 

        # Criar os botões (um abaixo do outro)
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn_conteudos = telebot.types.InlineKeyboardButton(text="👥 Entrar no grupo", callback_data="acessar_conteudos")
        btn_suporte = telebot.types.InlineKeyboardButton(text="🛠 Suporte", callback_data="suporte")
        markup.add(btn_conteudos, btn_suporte)

        # Enviar a mensagem com a descrição e os botões
        bot.send_message(chat_id, descricao_servico, reply_markup=markup, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Erro ao enviar a mensagem inicial: {e}")

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    primeiro_nome = message.from_user.first_name
    enviar_mensagem_inicial(message.chat.id, primeiro_nome)

# Comando /suporte
@bot.message_handler(commands=['suporte'])
def comando_suporte(message):
    # Mensagem de suporte com botão
    mensagem = ("🆘 Suporte SnapLives 🆘\n\n"
                "Para agilizar o atendimento, por favor:\n\n"
                "1. Vá direto ao ponto.\n"  
                "2. Se for problema com pagamento, envie o comprovante.\n"
                "3. Se for problema técnico, envie um print do problema.\n\n"  
                "⚠️ **Atenção**: Não realizamos reembolso.\n"  
                "Clique no botão abaixo para falar com o suporte.")
    
    # Criar botão com link de suporte
    markup = telebot.types.InlineKeyboardMarkup()
    btn_suporte = telebot.types.InlineKeyboardButton(text="Falar com Suporte", url=LINK_SUPORTE)
    markup.add(btn_suporte)
    
    # Enviar mensagem com botão
    bot.send_message(message.chat.id, mensagem, reply_markup=markup)

# Comando /status
@bot.message_handler(commands=['status'])
def comando_status(message):
    user_id = message.from_user.id
    # Lógica para verificar se o usuário fez o pagamento
    cursor.execute('SELECT primeiro_nome, plano, data_pagamento, data_expiracao FROM usuarios WHERE user_id = ?', (user_id,))
    usuario = cursor.fetchone()
    
    if usuario:
        primeiro_nome, plano, data_pagamento, data_expiracao = usuario
        # Mensagem de boas-vindas
        if plano == 'vitalicio':
            mensagem = f"👋 Bem-vindo de volta, {primeiro_nome}!\n\n🔥 *Plano:* {plano.capitalize()}\n📅 *Data de Pagamento:* {data_pagamento}\n💎 *Duração:* Para sempre!"
        else:
            mensagem = f"👋 Bem-vindo de volta, {primeiro_nome}!\n\n🔥 *Plano:* {plano.capitalize()}\n📅 *Data de Pagamento:* {data_pagamento}\n⏳ *Expira em:* {data_expiracao}"
        
        # Gerar um link de convite para o grupo
        try:
            link_convite = obter_link_grupo(user_id)
            markup = telebot.types.InlineKeyboardMarkup()
            btn_acessar_grupo = telebot.types.InlineKeyboardButton(text="Acessar Grupo", url=link_convite)
            markup.add(btn_acessar_grupo)
            bot.send_message(message.chat.id, mensagem, reply_markup=markup, parse_mode='Markdown')
        except Exception as e:
            bot.send_message(message.chat.id, "Erro ao gerar o link de convite. Por favor, tente novamente mais tarde.")
            logger.error(f"Erro ao gerar o link de convite: {e}")
    else:
        # Usuário não está no banco de dados (não é VIP)
        bot.send_message(message.chat.id, "Você ainda não é VIP. Assine agora para ter acesso exclusivo!")

# Comando /planos
@bot.message_handler(commands=['planos'])
def comando_planos(message):
    # Mensagem com os planos disponíveis
    mensagem = "🔥 Escolha um dos planos abaixo:\n\n"
    
    # Adicionar detalhes de cada plano
    for plano, valor in PLANOS.items():
        duracao = {
            'semanal': "1 semana",
            'mensal': "1 mês",
            'vitalicio': "Vitalício"
        }.get(plano, "Desconhecido")
        
        mensagem += f"📌 *Plano {plano.capitalize()}*\n"
        mensagem += f"💵 Valor: R${valor:.2f}\n"
        mensagem += f"⏳ Duração: {duracao}\n\n"
    
    # Criar botões para cada plano
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for plano, valor in PLANOS.items():
        btn_plano = telebot.types.InlineKeyboardButton(text=f"🔥 Plano {plano.capitalize()} - R${valor:.2f}", callback_data=f"escolher_{plano}")
        markup.add(btn_plano)
    
    # Enviar mensagem com os planos e botões
    bot.send_message(message.chat.id, mensagem, reply_markup=markup, parse_mode="Markdown")

# Callback para os botões
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    logger.info(f"Callback recebido: {call.data}")

    if call.data == "acessar_conteudos":
        # Enviar os planos com um botão "Voltar"
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        for plano, valor in PLANOS.items():
            markup.add(telebot.types.InlineKeyboardButton(text=f"🔥 Plano {plano.capitalize()} - R${valor:.2f}", callback_data=f"escolher_{plano}"))
        btn_voltar = telebot.types.InlineKeyboardButton(text="🔙 Voltar", callback_data="voltar_inicio")
        markup.add(btn_voltar)

        # Editar a mensagem de texto (não a imagem)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Escolha um dos planos abaixo:",
            reply_markup=markup
        )
    elif call.data == "suporte":
        # Enviar a mensagem de suporte com um botão "Voltar"
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn_link_suporte = telebot.types.InlineKeyboardButton(text="🛠 Falar com suporte", url=LINK_SUPORTE)
        btn_voltar = telebot.types.InlineKeyboardButton(text="🔙 Voltar", callback_data="voltar_inicio")
        markup.add(btn_link_suporte, btn_voltar)

        # Editar a mensagem de texto (não a imagem)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=("🆘 Suporte SnapLives 🆘\n\n"
                "Para agilizar o atendimento, por favor:\n\n"
                "1. Vá direto ao ponto.\n"  
                "2. Se for problema com pagamento, envie o comprovante.\n"
                "3. Se for problema técnico, envie um print do problema.\n\n"  
                "⚠️ **Atenção**: Não realizamos reembolso.\n"  
                "Clique no botão abaixo para falar com o suporte."),
            reply_markup=markup
        )
    elif call.data == "voltar_inicio":
        # Voltar para a mensagem inicial (editando a mensagem anterior)
        descricao_servico = ("💎<b><i><u>CONTEÚDOS EXCLUSIVOS NO VIP</u></i></b>💎\n"
"\n"
"🎥 <i>OS MELHORES <b><i><u>CONTEÚDOS</u></i></b> DIRETO NO TELEGRAM</i>\n"
"\n"
"🔥 <b><i>PLANOS ACESSÍVEIS:</i></b>\n"
"   - 💵 <b><u>VITALÍCIO</u></b>\n"
"   - 💵 <b><u>MENSAL</u></b>\n"
"   - 💵 <b><u>SEMANAL</u></b>\n"
"\n"
"🔒 <b><i>ENTRADA 100% SEGURA.</i></b>\n"
"🎟️ <b><i>ACESSE E SAIA QUANDO QUISER.</i></b>\n"
"\n"
"📂 <i>Conteúdo exclusivo para empreendedores e vendedores:</i>\n"
"<blockquote>"
"<b><i>🔔 Novidades diárias sobre vendas</i></b>\n"
"<b><i>🎬 Estratégias de marketing</i></b>\n"
"<b><i>💬 Dicas de negociação e fechamento</i></b>\n"
"<b><i>📈 Casos de sucesso e insights do mercado</i></b>\n"
"</blockquote>"
"<del>--------------------------</del>\n"
"<i>Assine já e tenha acesso a <u>conteúdos atualizados diariamente!</u></i>\n"
"<del>-------------------------</del>\n"
"<b><i>FAÇA PARTE DO VIP ⤵️</i></b>\n"
"<del>-------------------------</del>\n")

        # Criar os botões (um abaixo do outro)
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn_conteudos = telebot.types.InlineKeyboardButton(text="👥 Entrar no grupo", callback_data="acessar_conteudos")
        btn_suporte = telebot.types.InlineKeyboardButton(text="🛠 Suporte", callback_data="suporte")
        markup.add(btn_conteudos, btn_suporte)

        # Editar a mensagem anterior
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=descricao_servico,
            reply_markup=markup,
            parse_mode='HTML'
        )
    elif call.data.startswith("escolher_"):
        # Lógica para escolher o plano
        plano = call.data.split("_")[1]
        valor = PLANOS.get(plano)
        if valor:
            # Definir a duração do plano
            duracao = {
                'semanal': "1 semana",
                'mensal': "1 mês",
                'vitalicio': "Vitalício"
            }.get(plano)
            
            # Enviar um resumo do plano com emojis
            resumo_plano = (
                "🎉 *Resumo do Plano* 🎉\n\n"
                f"🔥 *Nome do Plano:* {plano.capitalize()}\n"
                f"💵 *Valor:* R${valor:.2f}\n"  # Valor corrigido
                f"⏳ *Duração:* {duracao}"
            )

            # Criar botões para o resumo
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)
            btn_confirmar = telebot.types.InlineKeyboardButton(text="✅ Confirmar Plano", callback_data=f"confirmar_{plano}")
            btn_voltar = telebot.types.InlineKeyboardButton(text="🔙 Voltar", callback_data="voltar_planos")
            markup.add(btn_confirmar, btn_voltar)

            # Enviar o resumo do plano
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=resumo_plano,
                reply_markup=markup,
                parse_mode="Markdown"
            )
        else:
            bot.send_message(chat_id, "Plano inválido.")
    elif call.data == "voltar_planos":
        # Voltar para a lista de planos (editando a mensagem anterior)
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        for plano, valor in PLANOS.items():
            markup.add(telebot.types.InlineKeyboardButton(text=f"🔥 Plano {plano.capitalize()} - R${valor:.2f}", callback_data=f"escolher_{plano}"))
        btn_voltar = telebot.types.InlineKeyboardButton(text="🔙 Voltar", callback_data="voltar_inicio")
        markup.add(btn_voltar)

        # Editar a mensagem de texto (não a imagem)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Escolha um dos planos abaixo:",
            reply_markup=markup
        )
    elif call.data.startswith("confirmar_"):
        # Lógica para confirmar o plano
        plano = call.data.split("_")[1]
        valor = PLANOS.get(plano)
        if valor:
            # Enviar mensagem de "Gerando pagamento..."
            mensagem = bot.send_message(chat_id, "🔄 Gerando pagamento...")

            # Animar os pontos por 1 segundo
            animar_pontos(chat_id, mensagem.message_id, "🔄 Gerando pagamento", duracao=1)

            # Gerar código PIX via API Pushin Pay
            qr_code, qr_code_base64, payment_id = gerar_codigo_pix(valor)
            if qr_code and qr_code_base64 and payment_id:
                codigos_pix[payment_id] = qr_code  # Armazena o código PIX

                if ',' in qr_code_base64:
                    qr_code_base64 = qr_code_base64.split(",")[1]
                else:
                    logger.error("Formato inesperado para qr_code_base64: %s", qr_code_base64)
                    raise ValueError("Formato inesperado para qr_code_base64")

                # Decodificar o Base64 para bytes
                try:
                    qr_code_bytes = base64.b64decode(qr_code_base64)
                except Exception as e:
                    logger.error(f"Erro ao decodificar o QR Code: {e}")
                    bot.send_message(chat_id, "Erro ao processar o QR Code. Tente novamente.")
                    return

                # Redimensionar a imagem do QR Code
                qr_code_redimensionado = redimensionar_qr_code(qr_code_bytes)
                if not qr_code_redimensionado:
                    bot.send_message(chat_id, "Erro ao redimensionar o QR Code. Tente novamente.")
                    return

                # Enviar a mensagem de instrução de pagamento
                bot.send_message(chat_id, "Para efetuar o pagamento, utilize a opção 'Pagar' -> 'PIX Copia e Cola' no aplicativo do seu banco. (Não usar a opção chave aleatória)\n\nCopie o código abaixo:")

                # Enviar a imagem do QR code
                bot.send_photo(chat_id, BytesIO(qr_code_redimensionado))

                # Enviar o código PIX sozinho
                bot.send_message(chat_id, f"<code>{qr_code}</code>", parse_mode='HTML')

                # Enviar a mensagem final com o botão para verificar pagamento
                mensagem_verificar_pagamento = "<b>Após efetuar o pagamento, clique no botão abaixo ⤵️</b>"
                markup = telebot.types.InlineKeyboardMarkup(row_width=1)
                btn_confirmar = telebot.types.InlineKeyboardButton(text="❖EFETUEI O PAGAMENTO❖", callback_data=f"pago_{plano}_{call.from_user.id}_{payment_id}")
                markup.add(btn_confirmar)
                bot.send_message(chat_id, mensagem_verificar_pagamento, reply_markup=markup, parse_mode='HTML')
            else:
                bot.send_message(chat_id, "Erro ao gerar o código PIX. Tente novamente.")
        else:
            bot.send_message(chat_id, "Plano inválido.")
    elif call.data.startswith("pago_"):
        plano = call.data.split("_")[1]
        user_id = int(call.data.split("_")[2])
        payment_id = call.data.split("_")[3]

        # Verificar se o pagamento foi aprovado
        pagamento_aprovado, mensagem = verificar_pagamento(payment_id)
        
        if pagamento_aprovado:
            # Adicionar ou atualizar o usuário no banco de dados
            data_pagamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dias_plano = {'semanal': 7, 'mensal': 30, 'vitalicio': 0}.get(plano.lower(), 0)
            valor_plano = PLANOS.get(plano.lower(), 0)
            adicionar_usuario(user_id, call.from_user.first_name, data_pagamento, dias_plano, plano)

            # Enviar notificação de venda ao dono
            enviar_notificacao_venda(user_id, call.from_user.first_name, plano, valor_plano, f'{dias_plano} dias')

            bot.send_message(call.message.chat.id, 'Seu pagamento foi aprovado! Clique no botão abaixo para acessar o grupo:', 
                             reply_markup=telebot.types.InlineKeyboardMarkup([[telebot.types.InlineKeyboardButton('Acessar Grupo', url=obter_link_grupo(user_id))]]))
        else:
            bot.answer_callback_query(call.id, "Pagamento ainda não aprovado. Por favor, aguarde um momento e tente novamente.")
            # Enviar mensagem ao usuário informando que o pagamento não foi aprovado
            bot.send_message(call.from_user.id, "⚠️ Seu pagamento ainda não foi aprovado. Por favor, tente novamente mais tarde.")

# Função para obter o link de convite do grupo
def obter_link_grupo(user_id):
    try:
        link_convite = bot.export_chat_invite_link(GRUPO_ID)
        links_usuarios[user_id] = link_convite  # Armazenar o link gerado
        return link_convite
    except Exception as e:
        logger.error(f"Erro ao gerar link de convite para o grupo: {e}")
        return None

# Função para verificar se o usuário que entrou no grupo é o mesmo do pagamento
@bot.chat_member_handler()
def verificar_usuario_grupo(message):
    if message.chat.id == GRUPO_ID and message.new_chat_members:
        for member in message.new_chat_members:
            # Verificar se o usuário que entrou é o mesmo que fez o pagamento
            cursor.execute('SELECT * FROM usuarios WHERE user_id = ?', (member.id,))
            usuario = cursor.fetchone()
            if not usuario:
                # Remover usuário que não é o mesmo do pagamento
                bot.kick_chat_member(GRUPO_ID, member.id)
                logger.info(f"Usuário {member.id} removido do grupo por não corresponder ao pagamento.")

@bot.callback_query_handler(func=lambda call: call.data == 'efetuei_pagamento')
def handle_efetuei_pagamento(call):
    user_id = call.from_user.id
    # Verificar se o usuário fez o pagamento
    cursor.execute('SELECT * FROM usuarios WHERE user_id = ?', (user_id,))
    usuario = cursor.fetchone()

    if usuario:
        # Gerar um link de convite para o grupo
        try:
            link_convite = bot.export_chat_invite_link(GRUPO_ID)
            bot.send_message(call.message.chat.id, f'Seu link de acesso ao grupo é: {link_convite}')
        except Exception as e:
            bot.send_message(call.message.chat.id, "Erro ao gerar o link de convite. Por favor, tente novamente mais tarde.")
            logger.error(f"Erro ao gerar o link de convite: {e}")

# Função para verificar o status do pagamento via API Pushin Pay
def verificar_pagamento(payment_id, user_id=None, message_id=None):
    if not payment_id:
        logger.error("Payment ID inválido.")
        return False, "Erro: Payment ID inválido. Tente novamente."

    # Endpoint correto para consultar o status do pagamento PIX
    url = f"https://api.pushinpay.com.br/api/transactions/{payment_id}"  # Atualize conforme a documentação
    headers = {
        "Authorization": f"Bearer {PUSHINPAY_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Verifica se o pagamento foi aprovado
        if data.get("status") == "paid":  # Status correto para pagamento aprovado
            return True, "Pagamento aprovado! 🎉"
        else:
            logger.info(f"Pagamento ainda não aprovado. Status: {data.get('status')}")
            return False, "Pagamento ainda não aprovado. Aguarde e tente novamente."

    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro na requisição à API Pushin Pay: {e}")
        logger.error(f"Resposta da API: {e.response.text}")
        return False, "Erro ao verificar o pagamento. Tente novamente mais tarde."
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição à API Pushin Pay: {e}")
        return False, "Erro de conexão. Tente novamente mais tarde."

# Função para gerar código PIX via API Pushin Pay
def gerar_codigo_pix(valor):
    url = "https://api.pushinpay.com.br/api/pix/cashIn"
    headers = {
        "Authorization": f"Bearer {PUSHINPAY_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Converter o valor de reais para centavos
    valor_em_centavos = int(valor * 100)

    payload = {
        "value": valor_em_centavos,
        "webhook_url": "https://telegram.discloud.app"  # Substitua pelo seu webhook
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Verifica se a resposta contém os campos esperados
        if "qr_code" in data and "qr_code_base64" in data and "id" in data:
            logger.info(f"Código PIX gerado com sucesso. Payment ID: {data.get('id')}")
            return data["qr_code"], data["qr_code_base64"], data["id"]  # Retorna o payment_id
        else:
            logger.error("Resposta da API não contém os campos esperados.")
            return None, None, None

    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro na requisição à API Pushin Pay: {e}")
        logger.error(f"Resposta da API: {e.response.text}")
        return None, None, None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição à API Pushin Pay: {e}")
        return None, None, None

# Função para redimensionar a imagem do QR Code
def redimensionar_qr_code(qr_code_bytes, tamanho=(300, 300)):
    try:
        # Abrir a imagem do QR Code
        qr_code_img = Image.open(BytesIO(qr_code_bytes)).convert("RGBA")

        # Criar uma nova imagem com fundo branco
        fundo_branco = Image.new("RGB", tamanho, "white")

        # Redimensionar o QR Code para caber na nova imagem
        qr_code_img = qr_code_img.resize(tamanho, Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)

        # Colar o QR Code na imagem de fundo branco
        fundo_branco.paste(qr_code_img, (0, 0), qr_code_img)

        # Salvar a imagem resultante em um buffer
        output = BytesIO()
        fundo_branco.save(output, format="PNG")
        return output.getvalue()
    except Exception as e:
        logger.error(f"Erro ao redimensionar o QR Code: {e}")
        return None

# Função para enviar notificação de venda ao dono
def enviar_notificacao_venda(user_id, primeiro_nome, plano, valor, duracao):
    # Obter a data e hora atual
    data_hora_compra = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Montar a mensagem com emojis
    mensagem = (
        "🎉 Pagamento Aprovado 🎉\n\n"
        f"💵 Valor: R${valor:.2f}\n"
        f"🆔 ID do Usuário: {user_id}\n"
        f"👤 Primeiro Nome: {primeiro_nome}\n"
        f"🔥 Plano: {plano.capitalize()}\n"
        f"⏳ Duração: {duracao}\n"
        f"📅 Data e Hora da Compra: {data_hora_compra}"
    )

    # Enviar a mensagem ao dono
    bot.send_message(ID_DONO, mensagem, parse_mode="Markdown")

def adicionar_usuario(user_id, primeiro_nome, data_pagamento, dias_plano, plano):
    try:
        # Converter data_pagamento para um objeto datetime no horário de Brasília
        data_pagamento_dt = datetime.strptime(data_pagamento, '%Y-%m-%d %H:%M:%S')
        data_pagamento_dt = timezone_br.localize(data_pagamento_dt)

        # Verificar se o usuário já existe no banco de dados
        cursor.execute('SELECT data_expiracao FROM usuarios WHERE user_id = ?', (user_id,))
        resultado = cursor.fetchone()

        if resultado:
            # Usuário já existe, atualizar a data de expiração
            data_expiracao_atual = resultado[0]
            if data_expiracao_atual:
                data_expiracao_dt = datetime.strptime(data_expiracao_atual, '%Y-%m-%d %H:%M:%S')
                data_expiracao_dt = timezone_br.localize(data_expiracao_dt)
                if plano.lower() == 'vitalicio':
                    data_expiracao_dt = None
                else:
                    data_expiracao_dt += timedelta(days=dias_plano)
            else:
                # Caso de plano vitalício
                data_expiracao_dt = None
        else:
            # Novo usuário, calcular a data de expiração
            if plano.lower() == 'vitalicio':
                data_expiracao_dt = None
            else:
                data_expiracao_dt = data_pagamento_dt + timedelta(days=dias_plano)

        # Formatar data_expiracao no formato legível antes de inserir no banco de dados
        data_expiracao_formatada = data_expiracao_dt.strftime('%Y-%m-%d %H:%M:%S') if data_expiracao_dt else None

        # Inserir ou atualizar os dados no banco
        cursor.execute('''
            INSERT OR REPLACE INTO usuarios (user_id, primeiro_nome, data_pagamento, data_expiracao, plano)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, primeiro_nome, data_pagamento, data_expiracao_formatada, plano))

        conn.commit()
        logger.info(f"Usuário {user_id} adicionado ou atualizado no banco de dados com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao adicionar usuário ao banco de dados: {e}")
        return False
    return True


def verificar_assinaturas_expiradas():
    while True:
        try:
            time.sleep(60)  # Verificar a cada minuto
            agora = int(time.time())
            cursor.execute('SELECT user_id, data_pagamento, plano, data_expiracao FROM usuarios WHERE data_expiracao IS NOT NULL')
            expirados = cursor.fetchall()
            for user_id, data_pagamento, plano, data_expiracao in expirados:
                if data_expiracao is None:
                    continue  # Ignorar usuários vitalícios
                try:
                    # Converter data_expiracao de texto para timestamp
                    data_expiracao_timestamp = int(time.mktime(time.strptime(data_expiracao, '%Y-%m-%d %H:%M:%S')))
                    if data_expiracao_timestamp < agora:
                        try:
                            # Remove o usuário do grupo e do banco de dados
                            bot.kick_chat_member(GRUPO_ID, user_id)
                            bot.unban_chat_member(GRUPO_ID, user_id)
                            cursor.execute('DELETE FROM usuarios WHERE user_id = ?', (user_id,))
                            conn.commit()
                            logger.info(f"Usuário {user_id} removido do grupo e do banco de dados por expiração de assinatura.")

                            # Enviar mensagem privada ao usuário
                            try:
                                bot.send_message(user_id, "Sua assinatura expirou. Você pode renovar usando o comando /status.")
                            except telebot.apihelper.ApiTelegramException as e:
                                if 'bot was blocked by the user' in str(e):
                                    logger.info(f"Usuário {user_id} bloqueou o bot.")
                                else:
                                    logger.error(f"Erro ao enviar mensagem para usuário {user_id}: {e}")
                        except Exception as e:
                            logger.error(f"Erro ao remover usuário {user_id} do grupo ou banco de dados: {e}")
                except ValueError as e:
                    # Recalcular data de expiração correta
                    nova_data_expiracao = calcular_data_expiracao(plano, data_pagamento)
                    cursor.execute('UPDATE usuarios SET data_expiracao = ? WHERE user_id = ?', (nova_data_expiracao, user_id))
                    conn.commit()
                    logger.info(f"Data de expiração corrigida para usuário {user_id}. Nova data: {nova_data_expiracao}")
        except Exception as e:
            logger.error(f"Erro ao verificar assinaturas expiradas: {e}")

# Função para calcular a data de expiração do plano com base no tipo de plano escolhido
def calcular_data_expiracao(tipo_plano, data_pagamento):
    tipo_plano = tipo_plano.lower()  # Tornar o tipo de plano case-insensitive
    data_pagamento_dt = datetime.strptime(data_pagamento, '%Y-%m-%d %H:%M:%S')
    if tipo_plano == 'semanal':
        data_expiracao_dt = data_pagamento_dt + timedelta(weeks=1)
    elif tipo_plano == 'mensal':
        data_expiracao_dt = data_pagamento_dt + timedelta(days=30)
    elif tipo_plano == 'vitalicio':
        return None  # Vitalício não expira
    else:
        logger.error(f"Tipo de plano inválido: {tipo_plano} para usuário com data de pagamento {data_pagamento}")
        raise ValueError('Tipo de plano inválido')

    # Ajustar para anos não bissextos
    if data_expiracao_dt.month == 2 and data_expiracao_dt.day == 29 and not calendar.isleap(data_expiracao_dt.year):
        data_expiracao_dt = data_expiracao_dt.replace(day=28)

    return data_expiracao_dt.strftime('%Y-%m-%d %H:%M:%S')

@bot.callback_query_handler(func=lambda call: call.data == 'efetuei_pagamento')
def handle_efetuei_pagamento(call):
    user_id = call.from_user.id
    # Verificar se o usuário fez o pagamento
    cursor.execute('SELECT * FROM usuarios WHERE user_id = ?', (user_id,))
    usuario = cursor.fetchone()

    if usuario:
        # Gerar um link de convite para o grupo
        try:
            link_convite = bot.export_chat_invite_link(GRUPO_ID)
            bot.send_message(call.message.chat.id, f'Seu link de acesso ao grupo é: {link_convite}')
        except Exception as e:
            bot.send_message(call.message.chat.id, "Erro ao gerar o link de convite. Por favor, tente novamente mais tarde.")
            logger.error(f"Erro ao gerar o link de convite: {e}")

# Iniciar o bot e a verificação de assinaturas expiradas
import threading
threading.Thread(target=verificar_assinaturas_expiradas, daemon=True).start()

# Loop para manter o bot sempre online
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Erro crítico no bot: {e}")
        logger.info("Reiniciando o bot em 5 segundos...")
        time.sleep(5)