#!/usr/bin/env python
# coding: utf-8

## As bibliotecas necessárias foram importadas no requirements.txt
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Função de início do robô, que deverá rodar após /start
def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Um novo acesso foi reconhecido!")


def main():
    # Criação do método Updater - Fornece um frontend para o bot, além de passar a chave de autenticação 
    updater = Updater(token='1950541172:AAH9IVUn_Q9y2Y1100ntNB7Zdbpp_1M_vAE', use_context=True)
    # Chamamos o método dispatcher para gerencimento dos eventos (handlers)
    dispatcher = updater.dispatcher
    # Comandos ao qual o robô reage
    dispatcher.add_handler(CommandHandler('start', start))
    # Iniciamos o bot
    updater.start_polling()
    # Paramos o mesmo
    updater.idle()

# Função padrão, para início do script em Python
if __name__ == '__main__':
    main()