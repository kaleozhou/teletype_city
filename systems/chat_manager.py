#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天管理器
负责管理游戏内的聊天、频道和消息系统
"""

import asyncio
import logging
import time
from typing import Dict, List, Set, Optional

logger = logging.getLogger(__name__)

class ChatManager:
    def __init__(self, server):
        self.server = server
        logger.info(f"ChatManager初始化，server: {server}")
        logger.info(f"server类型: {type(server)}")
        logger.info(f"server属性: {dir(server) if server else 'None'}")
        
        self.channels = {}  # 频道名称 -> Channel对象
        self.chat_cooldown_time = 1.0  # 聊天冷却时间（秒）
        self.chat_cooldowns = {}  # 玩家名 -> 下次可聊天时间
        self.max_history = 100  # 最大历史记录数量
        self.message_history: List[Message] = []
    
    async def tick(self):
        """聊天系统tick更新"""
        current_time = time.time()
        
        # 清理过期的聊天冷却
        expired_cooldowns = [
            player_id for player_id, cooldown_time in self.chat_cooldowns.items()
            if current_time > cooldown_time
        ]
        for player_id in expired_cooldowns:
            del self.chat_cooldowns[player_id]
    
    async def send_room_message(self, player, message: str):
        """发送房间消息"""
        if not player:
            return False
        
        # 检查聊天冷却
        if not self._check_chat_cooldown(player.name):
            return False
        
        # 创建消息对象
        chat_message = Message(
            sender=player.name,
            content=message,
            type="room",
            target=player.current_room
        )
        
        # 添加到历史记录
        self._add_to_history(chat_message)
        
        # 广播到房间
        await self._broadcast_to_room(player.current_room, chat_message, exclude=player.name)
        
        logger.info(f"房间消息 [{player.current_room}] {player.name}: {message}")
        return True
    
    async def send_global_message(self, player, message: str):
        """发送全服消息"""
        if not player:
            return False
        
        # 检查聊天冷却
        if not self._check_chat_cooldown(player.name):
            return False
        
        # 创建消息对象
        chat_message = Message(
            sender=player.name,
            content=message,
            type="global",
            target="global"
        )
        
        # 添加到历史记录
        self._add_to_history(chat_message)
        
        # 广播到全服
        await self._broadcast_to_global(chat_message, exclude=player.name)
        
        logger.info(f"全服消息 {player.name}: {message}")
        return True
    
    async def send_private_message(self, sender, target_name: str, message: str):
        """发送私聊消息"""
        if not sender:
            return False
        
        # 检查聊天冷却
        if not self._check_chat_cooldown(sender.name):
            return False
        
        # 查找目标玩家
        target_player = self._find_player_by_name(target_name)
        if not target_player:
            return False
        
        # 创建消息对象
        chat_message = Message(
            sender=sender.name,
            content=message,
            type="private",
            target=target_name
        )
        
        # 添加到历史记录
        self._add_to_history(chat_message)
        
        # 发送给目标玩家
        try:
            await target_player.protocol.send_message("SEEN", f"私聊: {sender.name}: {message}")
            await sender.protocol.send_message("OK", f"私聊发送给 {target_name}")
        except Exception as e:
            logger.error(f"发送私聊失败: {e}")
            return False
        
        logger.info(f"私聊 {sender.name} -> {target_name}: {message}")
        return True
    
    async def join_channel(self, player, channel_name: str):
        """加入频道"""
        if not player:
            return False
        
        # 创建频道（如果不存在）
        if channel_name not in self.channels:
            self.channels[channel_name] = Channel(channel_name, f"频道 {channel_name}")
        
        channel = self.channels[channel_name]
        channel.add_member(player)
        
        await player.protocol.send_message("OK", f"已加入频道 {channel_name}")
        logger.info(f"玩家 {player.name} 加入频道 {channel_name}")
        return True
    
    async def leave_channel(self, player, channel_name: str):
        """离开频道"""
        if not player:
            return False
        
        if channel_name not in self.channels:
            await player.protocol.send_message("ERR", f"频道 {channel_name} 不存在")
            return False
        
        channel = self.channels[channel_name]
        if player not in channel.members:
            await player.protocol.send_message("ERR", f"你不在频道 {channel_name} 中")
            return False
        
        channel.remove_member(player)
        await player.protocol.send_message("OK", f"已离开频道 {channel_name}")
        logger.info(f"玩家 {player.name} 离开频道 {channel_name}")
        return True
    
    async def send_channel_message(self, player, channel_name: str, message: str):
        """发送频道消息"""
        if not player or channel_name not in self.channels:
            return False
        
        # 检查聊天冷却
        if not self._check_chat_cooldown(player.name):
            return False
        
        channel = self.channels[channel_name]
        if player not in channel.members:
            await player.protocol.send_message("ERR", f"你不在频道 {channel_name} 中")
            return False
        
        # 创建消息对象
        chat_message = Message(
            sender=player.name,
            content=message,
            type="channel",
            target=channel_name
        )
        
        # 添加到历史记录
        self._add_to_history(chat_message)
        
        # 广播到频道
        await self._broadcast_to_channel(channel_name, chat_message, exclude=player.name)
        
        logger.info(f"频道消息 [{channel_name}] {player.name}: {message}")
        return True
    
    def _check_chat_cooldown(self, player_name: str) -> bool:
        """检查聊天冷却"""
        current_time = time.time()
        if player_name in self.chat_cooldowns:
            if current_time < self.chat_cooldowns[player_name]:
                return False
        
        self.chat_cooldowns[player_name] = current_time + self.chat_cooldown_time
        return True
    
    def _add_to_history(self, message: 'Message'):
        """添加消息到历史记录"""
        self.message_history.append(message)
        
        # 限制历史记录数量
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
    
    async def _broadcast_to_room(self, room_name: str, message: 'Message', exclude: str = None):
        """广播消息到房间"""
        try:
            logger.debug(f"开始广播房间消息到 {room_name}")
            
            # 直接访问player_manager
            if not hasattr(self.server, 'players'):
                logger.error("服务器没有players属性")
                return
            
            # 获取房间内的所有玩家
            online_players = self.server.players.get_online_players()
            logger.debug(f"在线玩家数量: {len(online_players)}")
            
            room_players = [p for p in online_players if p.current_room == room_name and p.name != exclude]
            logger.debug(f"房间 {room_name} 中的玩家: {[p.name for p in room_players]}")
            
            if not room_players:
                logger.warning(f"房间 {room_name} 中没有其他玩家")
                return
            
            # 广播给房间内的所有玩家
            for player in room_players:
                try:
                    await player.protocol.send_message("SEEN", f"{message.sender}: {message.content}")
                    logger.debug(f"房间消息已发送给 {player.name}")
                except Exception as e:
                    logger.error(f"房间广播失败: {e}")
            
            logger.info(f"房间 {room_name} 消息已广播给 {len(room_players)} 个玩家")
            
        except Exception as e:
            logger.error(f"房间广播过程中发生异常: {e}")
            import traceback
            logger.error(f"异常堆栈: {traceback.format_exc()}")
    
    async def _broadcast_to_global(self, message: 'Message', exclude: str = None):
        """广播消息到全服"""
        if not hasattr(self.server, 'player_manager'):
            return
        
        # 获取所有在线玩家
        online_players = self.server.player_manager.get_online_players()
        for player in online_players:
            if player.name != exclude:
                try:
                    await player.protocol.send_message("SEEN", f"[全服] {message.sender}: {message.content}")
                except Exception as e:
                    logger.error(f"全服广播失败: {e}")
    
    async def _broadcast_to_channel(self, channel_name: str, message: 'Message', exclude: str = None):
        """广播消息到频道"""
        if channel_name in self.channels:
            channel = self.channels[channel_name]
            for member in channel.members:
                if exclude and member.name == exclude:
                    continue
                
                try:
                    await member.protocol.send_message("SEEN", f"[{channel_name}] {message.sender}: {message.content}")
                except Exception as e:
                    logger.error(f"频道广播失败: {e}")
    
    def _find_player_by_name(self, name: str):
        """根据名字查找玩家"""
        if not hasattr(self.server, 'players'):
            return None
        
        # 从玩家管理器查找玩家
        return self.server.players.get_player(name)

class Channel:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.members: Set = set()
        self.created_at = time.time()
    
    def add_member(self, player):
        """添加成员"""
        self.members.add(player)
    
    def remove_member(self, player):
        """移除成员"""
        self.members.discard(player)
    
    def get_member_count(self) -> int:
        """获取成员数量"""
        return len(self.members)

class Message:
    def __init__(self, sender: str, content: str, type: str, target: str):
        self.sender = sender
        self.content = content
        self.type = type  # room, global, private, channel
        self.target = target
        self.timestamp = time.time()
