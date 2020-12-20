import asyncio
import json
import os
import sys
import logging

from discord.ext import commands
import discord
import nest_asyncio

ADMIN_CHANNEL = int(os.getenv('ADMIN_CHANNEL'))
MEMBER_CHANNEL = int(os.getenv('MEMBER_CHANNEL'))
ADMIN_ROLE = int(os.getenv('ADMIN_ROLE'))
IT_ROLE = int(os.getenv('IT_ROLE'))
MEMBER_ROLE = int(os.getenv('MEMBER_ROLE'))
SERVER = int(os.getenv('SERVER_ID'))
ANNOUNCEMENTS = int(os.getenv('ANNOUNCEMENTS'))
RECRUIT_ROLE = int(os.getenv('RECRUIT_ROLE'))
RECRUIT_CHANNEL = int(os.getenv("RECRUIT_CHANNEL"))


class Roles():
    def __init__(self, bot, auth_token=None, refresh_token=None):
        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        self.log.addHandler(handler)
        self.server = bot.get_guild(SERVER)
        self.log.info(self.server)
        self.admin_channel = bot.get_channel(ADMIN_CHANNEL)
        self.log.info(self.admin_channel)
        self.member_channel = bot.get_channel(MEMBER_CHANNEL)
        self.log.info(self.member_channel)
        self.member_role = self.server.get_role(MEMBER_ROLE)
        self.log.info(self.member_role)
        self.it_role = self.server.get_role(IT_ROLE)
        self.log.info(self.it_role)
        self.admin_role = self.server.get_role(ADMIN_ROLE)
        self.log.info(self.admin_role)
        self.recruit_role = self.server.get_role(RECRUIT_ROLE)
        self.log.info(self.recruit_role)
        self.recruit_channel = self.server.get_channel(RECRUIT_CHANNEL)
        self.log.info(self.recruit_channel)
        self.announcements = self.server.get_channel(ANNOUNCEMENTS)
        self.log.info(self.announcements)
        self.TOKEN = os.getenv('DISCORD_TOKEN')
        self.BOT_PASSWORD = os.getenv('BOT_PASSWORD')
        self.BASE_URL = os.getenv('BASE_URL')
        self.SITE_TOKEN = os.getenv('SITE_TOKEN')
        self.VERIFY_SSL = bool(int(os.getenv('VERIFY_SSL')))
        self.auth_token = auth_token
        self.refresh_token = refresh_token
        self.subscribable = [self.server.get_role(int(role)) for role in os.getenv('SUBSCRIBABLE').split(',')]
        self.log.info(self.subscribable)