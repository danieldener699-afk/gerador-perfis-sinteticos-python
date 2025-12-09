import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from gerador_perfis import gerar_perfil

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# O token do bot deve ser lido de uma variável de ambiente por segurança
# Para fins de demonstração, usaremos o token fornecido, mas o código final
# usará a variável de ambiente.
# TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context):
    """Envia uma mensagem quando o comando /start é emitido."""
    await update.message.reply_text(
        "Olá! Eu sou o Bot Gerador de Perfis Sintéticos.\n"
        "Use o comando /gerar seguido de um identificador (ex: /gerar +5511999999999) para gerar um perfil."
    )

async def help_command(update: Update, context):
    """Envia uma mensagem quando o comando /help é emitido."""
    await update.message.reply_text(
        "Comandos disponíveis:\n"
        "/start - Inicia o bot e mostra a mensagem de boas-vindas.\n"
        "/gerar <identificador> - Gera um perfil sintético para o identificador fornecido."
    )

async def gerar(update: Update, context):
    """Gera um perfil sintético com base no identificador fornecido."""
    if not context.args:
        await update.message.reply_text(
            "Por favor, forneça um identificador após o comando /gerar. "
            "Exemplo: /gerar +5511999999999"
        )
        return

    identifier = " ".join(context.args)
    
    try:
        # Chama a função de geração de perfil do módulo importado
        perfil = gerar_perfil(identifier)
        
        # Formata o perfil em JSON para envio
        perfil_json = json.dumps(perfil, ensure_ascii=False, indent=2)
        
        # Envia a resposta. O Telegram tem um limite de caracteres,
        # então é melhor enviar como um arquivo se for muito longo, mas
        # para este caso, o texto deve ser suficiente.
        await update.message.reply_text(
            f"Perfil Sintético para '{identifier}':\n\n"
            f"```json\n{perfil_json}\n```",
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        logger.error(f"Erro ao gerar perfil para {identifier}: {e}")
        await update.message.reply_text(
            f"Ocorreu um erro ao gerar o perfil para '{identifier}'. Por favor, tente novamente."
        )

def main():
    """Inicia o bot."""
    if not TOKEN:
        logger.error("O token do bot do Telegram não foi encontrado.")
        return

    # Cria o Application e passa o token do bot
    application = Application.builder().token(TOKEN).build()

    # Adiciona handlers para comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("gerar", gerar))

    # Inicia o bot
    logger.info("Bot iniciado. Pressione Ctrl-C para parar.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
