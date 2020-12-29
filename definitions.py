import asyncio
import json
import os
import sys
import logging

from discord.ext import commands
import discord
import nest_asyncio

SERVER = int(os.getenv('SERVER_ID'))
ANNOUNCEMENTS = int(os.getenv('ANNOUNCEMENTS'))
ADMIN_ROLE = int(os.getenv('ADMIN_ROLE'))
ADMIN_CHANNEL = int(os.getenv('ADMIN_CHANNEL'))
IT_ROLE = int(os.getenv('IT_ROLE'))
IT_CHANNEL = int(os.getenv('IT_CHANNEL'))
MEMBER_ROLE = int(os.getenv('MEMBER_ROLE'))
MEMBER_CHANNEL = int(os.getenv('MEMBER_CHANNEL'))
RECRUIT_ROLE = int(os.getenv('RECRUIT_ROLE'))
RECRUIT_CHANNEL = int(os.getenv("RECRUIT_CHANNEL"))
DIPLO_ROLE = int(os.getenv("DIPLO_ROLE"))
DIPLO_CHANNEL = int(os.getenv("DIPLO_CHANNEL"))
ALLIANCE_ROLE = int(os.getenv("ALLIANCE_ROLE"))


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
        self.it_channel = self.server.get_channel(IT_CHANNEL)
        self.log.info(self.it_channel)
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
        self.diplo_role = self.server.get_role(DIPLO_ROLE)
        self.log.info(self.diplo_role)
        self.diplo_channel = self.server.get_channel(DIPLO_CHANNEL)
        self.log.info(self.diplo_channel)
        self.alliance_role = self.server.get_role(ALLIANCE_ROLE)
        self.log.info(self.alliance_role)