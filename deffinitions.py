import asyncio
import json
import os
import sys
import logging

from discord.ext import commands
import discord
import nest_asyncio

_ADMIN_CHANNEL = int(os.getenv('ADMIN_CHANNEL'))
_MEMBER_CHANNEL = int(os.getenv('MEMBER_CHANNEL'))
_ADMIN_ROLE = int(os.getenv('ADMIN_ROLE'))
_IT_ROLE = int(os.getenv('IT_ROLE'))
_MEMBER_ROLE = int(os.getenv('MEMBER_ROLE'))
_SERVER = int(os.getenv('SERVER_ID'))
_ANOUNCEMENTS = int(os.getenv('ANOUNCEMENTS'))
RECRUTE_ROLE = int(os.getenv('RECRUTE_ROLE'))
RECRUTE_CHANNEL = int(os.getenv("RECRUTE_CHANNEL"))


class Roles():
    def __init__(self, bot, auth_token=None, refresh_token=None):
        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        self.log.addHandler(handler)
        self.server = bot.get_guild(_SERVER)
        self.log.info(self.server)
        self.admin_channel = bot.get_channel(_ADMIN_CHANNEL)
        self.log.info(self.admin_channel)
        self.member_channel = bot.get_channel(_MEMBER_CHANNEL)
        self.log.info(self.member_channel)
        self.member_role = self.server.get_role(_MEMBER_ROLE)
        self.log.info(self.member_role)
        self.it_role = self.server.get_role(_IT_ROLE)
        self.log.info(self.it_role)
        self.admin_role = self.server.get_role(_ADMIN_ROLE)
        self.log.info(self.admin_role)
        self.recrute_role = self.server.get_role(RECRUTE_ROLE)
        self.log.info(self.recrute_role)
        self.recrute_channel = self.server.get_channel(RECRUTE_CHANNEL)
        self.log.info(self.recrute_channel)
        self.anouncements = self.server.get_channel(_ANOUNCEMENTS)
        self.log.info(self.anouncements)
        self.TOKEN = os.getenv('DISCORD_TOKEN')
        self.BOT_PASSWORD = os.getenv('BOT_PASSWORD')
        self.BASE_URL = os.getenv('BASE_URL')
        self.SITE_TOKEN = os.getenv('SITE_TOKEN')
        self.VERIFY_SSL = bool(int(os.getenv('VERIFY_SSL')))
        self.auth_token = auth_token
        self.refresh_token = refresh_token
        self.subscribable = [self.server.get_role(int(role)) for role in os.getenv('SUBSCRIBABLE').split(',')]
        self.log.info(self.subscribable)