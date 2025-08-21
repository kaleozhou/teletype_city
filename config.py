#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏配置文件
"""

# 服务器配置
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 2323

# 游戏配置
GAME_TICK_RATE = 10  # Hz
MAX_PLAYERS = 100
MAX_MESSAGE_LENGTH = 500

# 数据库配置
DATABASE_FILE = 'data/game.db'
BACKUP_INTERVAL = 300  # 5分钟

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = 'game_server.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 安全配置
MAX_COMMANDS_PER_SECOND = 10
CHAT_COOLDOWN = 1.0  # 秒

# 世界配置
STARTING_ROOM = 'dock'
STARTING_MONEY = 0
STARTING_HP = 100
STARTING_EP = 100

# 经济配置
CURRENCY_NAME = '铆钉'
INITIAL_MONEY = 0

# 任务配置
MAX_ACTIVE_QUESTS = 10
QUEST_EXPIRY_DAYS = 7

# 战斗配置
COMBAT_ENABLED = True
ATTACK_COOLDOWN = 2.0  # 秒
SKILL_COOLDOWN = 5.0  # 秒

# 社交配置
MAX_CHAT_HISTORY = 1000
MAX_CHANNELS = 20
MAX_CHANNEL_MEMBERS = 50
