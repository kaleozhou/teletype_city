#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
玩家管理器
负责管理所有在线玩家、数据持久化和玩家状态
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional
import hashlib

logger = logging.getLogger(__name__)

class PlayerManager:
    def __init__(self):
        self.online_players: Dict[str, 'Player'] = {}
        self.player_data_file = 'data/players.json'
        
    async def create_player(self, name: str, protocol) -> 'Player':
        """创建新玩家"""
        try:
            # 检查玩家名是否已存在
            if name in self.online_players:
                raise ValueError("玩家名已存在")
            
            # 创建新玩家
            player = Player(name, protocol)
            
            # 添加到在线玩家列表
            self.online_players[name] = player
            
            # 设置出生点
            await self.spawn_player(player)
            
            logger.info(f"新玩家创建: {name}")
            return player
            
        except Exception as e:
            logger.error(f"创建玩家失败: {e}")
            raise
    
    async def spawn_player(self, player: 'Player'):
        """设置玩家出生点"""
        # 设置到老码头（出生点）
        player.current_room = "dock"
        player.position = [0, 0]
        
        # 给予初始物品
        player.add_item("paper_tape", 1)
        
        # 设置初始属性
        player.hp = 100
        player.max_hp = 100
        player.ep = 100
        player.max_ep = 100
        player.money = 0
        player.exp = 0
        player.level = 1
        
        logger.info(f"玩家 {player.name} 出生在 {player.current_room}")
    
    def get_player(self, name: str) -> Optional['Player']:
        """获取在线玩家"""
        return self.online_players.get(name)
    
    def get_online_players(self) -> List['Player']:
        """获取所有在线玩家"""
        return list(self.online_players.values())
    
    def remove_player(self, player: 'Player'):
        """移除在线玩家"""
        if player.name in self.online_players:
            del self.online_players[player.name]
            logger.info(f"玩家 {player.name} 已离线")
    
    async def save_player(self, player: 'Player'):
        """保存玩家数据"""
        try:
            # 读取现有数据
            players_data = {}
            try:
                with open(self.player_data_file, 'r', encoding='utf-8') as f:
                    players_data = json.load(f)
            except FileNotFoundError:
                pass
            
            # 更新玩家数据
            players_data[player.name] = player.to_dict()
            
            # 保存到文件
            with open(self.player_data_file, 'w', encoding='utf-8') as f:
                json.dump(players_data, f, ensure_ascii=False, indent=2)
                
            logger.debug(f"玩家 {player.name} 数据已保存")
            
        except Exception as e:
            logger.error(f"保存玩家数据失败: {e}")
    
    async def save_all_players(self):
        """保存所有玩家数据"""
        logger.info("正在保存所有玩家数据...")
        for player in self.get_online_players():
            await self.save_player(player)
        logger.info("所有玩家数据保存完成")
    
    async def load_player(self, name: str) -> Optional['Player']:
        """加载玩家数据"""
        try:
            with open(self.player_data_file, 'r', encoding='utf-8') as f:
                players_data = json.load(f)
                
            if name in players_data:
                player_data = players_data[name]
                player = Player.from_dict(player_data)
                return player
                
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.error(f"加载玩家数据失败: {e}")
        
        return None
    
    async def tick(self):
        """玩家管理器tick更新"""
        current_time = time.time()
        
        # 定期保存玩家数据
        if int(current_time) % 300 == 0:  # 每5分钟
            await self.save_all_players()
        
        # 更新所有在线玩家状态
        for player in self.get_online_players():
            await player.tick()

class Player:
    def __init__(self, name: str, protocol):
        self.name = name
        self.protocol = protocol
        self.title = ""
        self.level = 1
        self.exp = 0
        self.hp = 100
        self.max_hp = 100
        self.ep = 100
        self.max_ep = 100
        self.money = 0
        self.position = [0, 0]
        self.current_room = "dock"
        self.inventory = {}
        self.equipment = {}
        self.quests = {}
        self.stats = {
            'str': 10,
            'agi': 10,
            'int': 10,
            'cha': 10
        }
        self.created_at = time.time()
        self.last_login = time.time()
        
    def add_item(self, item_id: str, count: int = 1):
        """添加物品到背包"""
        if item_id in self.inventory:
            self.inventory[item_id] += count
        else:
            self.inventory[item_id] = count
        
        logger.debug(f"玩家 {self.name} 获得物品: {item_id} x{count}")
    
    def remove_item(self, item_id: str, count: int = 1) -> bool:
        """从背包移除物品"""
        if item_id in self.inventory and self.inventory[item_id] >= count:
            self.inventory[item_id] -= count
            if self.inventory[item_id] <= 0:
                del self.inventory[item_id]
            return True
        return False
    
    def has_item(self, item_id: str, count: int = 1) -> bool:
        """检查是否有指定物品"""
        return item_id in self.inventory and self.inventory[item_id] >= count
    
    def get_inventory(self) -> Dict[str, int]:
        """获取背包内容"""
        return self.inventory.copy()
    
    def add_money(self, amount: int):
        """添加金钱"""
        self.money += amount
        logger.debug(f"玩家 {self.name} 获得金钱: {amount}")
    
    def remove_money(self, amount: int) -> bool:
        """移除金钱"""
        if self.money >= amount:
            self.money -= amount
            return True
        return False
    
    def add_exp(self, amount: int):
        """添加经验值"""
        self.exp += amount
        
        # 检查升级
        required_exp = self.level * 100
        while self.exp >= required_exp:
            self.exp -= required_exp
            self.level += 1
            self.max_hp += 10
            self.max_ep += 5
            self.hp = self.max_hp
            self.ep = self.max_ep
            
            logger.info(f"玩家 {self.name} 升级到 {self.level} 级")
    
    def heal(self, amount: int):
        """治疗玩家"""
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            logger.info(f"玩家 {self.name} 死亡")
            return True
        return False
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'name': self.name,
            'title': self.title,
            'level': self.level,
            'exp': self.exp,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'ep': self.ep,
            'max_ep': self.max_ep,
            'money': self.money,
            'position': self.position,
            'current_room': self.current_room,
            'inventory': self.inventory,
            'equipment': self.equipment,
            'quests': self.quests,
            'stats': self.stats,
            'created_at': self.created_at,
            'last_login': time.time()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """从字典创建玩家"""
        player = cls(data['name'], None)
        player.title = data.get('title', '')
        player.level = data.get('level', 1)
        player.exp = data.get('exp', 0)
        player.hp = data.get('hp', 100)
        player.max_hp = data.get('max_hp', 100)
        player.ep = data.get('ep', 100)
        player.max_ep = data.get('max_ep', 100)
        player.money = data.get('money', 0)
        player.position = data.get('position', [0, 0])
        player.current_room = data.get('current_room', 'dock')
        player.inventory = data.get('inventory', {})
        player.equipment = data.get('equipment', {})
        player.quests = data.get('quests', {})
        player.stats = data.get('stats', {'str': 10, 'agi': 10, 'int': 10, 'cha': 10})
        player.created_at = data.get('created_at', time.time())
        player.last_login = data.get('last_login', time.time())
        return player
    
    async def tick(self):
        """玩家tick更新"""
        # 恢复精力
        if self.ep < self.max_ep:
            self.ep = min(self.max_ep, self.ep + 1)
        
        # 恢复生命值（较慢）
        if self.hp < self.max_hp and time.time() % 10 == 0:
            self.hp = min(self.max_hp, self.hp + 1)
