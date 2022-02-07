#!/usr/bin/env python
# coding: utf-8

from telegram.ext import Updater
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    # Criação do método Updater - Fornece um frontend para o bot, além de passar a chave de autenticação 
    updater = Updater(token='1950541172:AAH9IVUn_Q9y2Y1100ntNB7Zdbpp_1M_vAE', use_context=True)
    # Iniciamos o bot
    updater.start_polling()
    # Paramos o mesmo
    updater.idle()

# Função padrão, para início do script em Python
if __name__ == '__main__':
    main()