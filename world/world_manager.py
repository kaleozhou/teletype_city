#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界管理器
负责管理游戏世界、房间、NPC和事件
"""

import asyncio
import yaml
import logging
from typing import Dict, List, Optional
import time

logger = logging.getLogger(__name__)

class WorldManager:
    def __init__(self):
        self.rooms = {}
        self.npcs = {}
        self.items = {}
        self.quests = {}
        self.events = []
        self.last_hourly_event = 0
        self.last_daily_event = 0
        
    async def load_world(self):
        """加载游戏世界数据"""
        try:
            # 加载房间数据
            with open('data/rooms.yml', 'r', encoding='utf-8') as f:
                rooms_data = yaml.safe_load(f)
                for room_data in rooms_data:
                    room = Room(room_data)
                    self.rooms[room.id] = room
            
            # 加载NPC数据
            with open('data/npcs.yml', 'r', encoding='utf-8') as f:
                npcs_data = yaml.safe_load(f)
                for npc_data in npcs_data:
                    npc = NPC(npc_data)
                    self.npcs[npc.id] = npc
            
            # 加载物品数据
            with open('data/items.yml', 'r', encoding='utf-8') as f:
                items_data = yaml.safe_load(f)
                for item_data in items_data:
                    item = Item(item_data)
                    self.items[item.id] = item
            
            # 加载任务数据
            with open('data/quests.yml', 'r', encoding='utf-8') as f:
                quests_data = yaml.safe_load(f)
                for quest_data in quests_data:
                    quest = Quest(quest_data)
                    self.quests[quest.id] = quest
            
            logger.info(f"世界加载完成: {len(self.rooms)} 房间, {len(self.npcs)} NPC, {len(self.items)} 物品, {len(self.quests)} 任务")
            
        except Exception as e:
            logger.error(f"加载世界数据失败: {e}")
            raise
    
    async def tick(self):
        """世界tick更新"""
        current_time = time.time()
        
        # 检查整点事件
        if int(current_time) % 3600 == 0 and int(current_time) != self.last_hourly_event:
            await self.trigger_hourly_event()
            self.last_hourly_event = int(current_time)
        
        # 检查每日事件
        if int(current_time // 86400) != self.last_daily_event:
            await self.trigger_daily_event()
            self.last_daily_event = int(current_time // 86400)
    
    async def trigger_hourly_event(self):
        """触发整点事件"""
        logger.info("触发整点事件：灯塔鸣笛")
        # 这里可以添加具体的整点事件逻辑
        
    async def trigger_daily_event(self):
        """触发每日事件"""
        logger.info("触发每日事件：新的一天开始")
        # 这里可以添加具体的每日事件逻辑
    
    def get_room(self, room_id: str) -> Optional['Room']:
        """获取房间"""
        return self.rooms.get(room_id)
    
    def get_npc(self, npc_id: str) -> Optional['NPC']:
        """获取NPC"""
        return self.npcs.get(npc_id)
    
    def get_item(self, item_id: str) -> Optional['Item']:
        """获取物品"""
        return self.items.get(item_id)
    
    def get_quest(self, quest_id: str) -> Optional['Quest']:
        """获取任务"""
        return self.quests.get(quest_id)

class Room:
    def __init__(self, data: dict):
        self.id = data['id']
        self.title = data['title']
        self.desc = data['desc']
        self.pos = data.get('pos', [0, 0])
        self.exits = data.get('exits', {})
        self.npcs = data.get('npcs', [])
        self.monsters = data.get('monsters', [])
        self.items = data.get('items', [])
        self.features = data.get('features', [])
        self.on_enter = data.get('on_enter', [])
        self.players = []
    
    def add_player(self, player):
        """添加玩家到房间"""
        if player not in self.players:
            self.players.append(player)
            player.current_room = self
    
    def remove_player(self, player):
        """从房间移除玩家"""
        if player in self.players:
            self.players.remove(player)
    
    def get_players(self):
        """获取房间内的玩家"""
        return self.players
    
    def get_exit_room(self, direction: str):
        """获取出口房间"""
        room_id = self.exits.get(direction.upper())
        return room_id

class NPC:
    def __init__(self, data: dict):
        self.id = data['id']
        self.name = data['name']
        self.title = data.get('title', '')
        self.room = data.get('room', '')
        self.dialog = data.get('dialog', {})
        self.trade = data.get('trade', {})
        self.quests = data.get('quests', [])
        self.inventory = data.get('inventory', [])

class Item:
    def __init__(self, data: dict):
        self.id = data['id']
        self.name = data['name']
        self.type = data['type']
        self.desc = data['desc']
        self.value = data.get('value', 0)
        self.weight = data.get('weight', 0.0)
        self.stackable = data.get('stackable', False)
        self.max_stack = data.get('max_stack', 1)
        self.durability = data.get('durability', 100)
        self.damage = data.get('damage', 0)
        self.defense = data.get('defense', 0)
        self.effect = data.get('effect', '')

class Quest:
    def __init__(self, data: dict):
        self.id = data['id']
        self.name = data['name']
        self.desc = data['desc']
        self.type = data.get('type', 'side')
        self.steps = data.get('steps', [])
        self.reward = data.get('reward', {})
        self.repeatable = data.get('repeatable', False)
        self.completed = False
