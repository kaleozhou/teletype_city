#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏协议处理
负责客户端通信、消息编码解码和命令路由
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
import re

logger = logging.getLogger(__name__)

class GameProtocol:
    """游戏协议处理器"""
    
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, server):
        self.reader = reader
        self.writer = writer
        self.server = server
        self.player = None
        self.authenticated = False
        
        # 连接信息
        self.addr = writer.get_extra_info('peername')
        self.connected_at = asyncio.get_event_loop().time()
        
        # 消息缓冲
        self.input_buffer = ""
        self.last_command_time = 0
        self.command_cooldown = 0.1  # 100ms冷却时间
    
    async def send_welcome(self):
        """发送欢迎信息"""
        welcome_msg = self._format_welcome()
        await self.send_message("SYS", welcome_msg)
        await self.send_message("SYS", "输入 'LOGIN <昵称>' 开始游戏，或输入 'HELP' 获取帮助。")
    
    def _format_welcome(self):
        """格式化欢迎信息"""
        return """\x1b[36m
  ____  _   _  ____    ____                  _           _
 |  _ \| \ | |/ ___|  / ___|_ __ ___  __ _  __| | ___  ___| |
 | |_) |  \| | |  _  | |  _| '__/ _ \/ _` |/ _` |/ _ \/ __| |
 |  __/| |\  | |_| | | |_| | | |  __/ (_| | (_| |  __/\__ \_|
 |_|   |_| \_|\____|  \____|_|  \___|\__,_|\__,_|\___||___(_)
\x1b[0m

欢迎来到【终端·回响】！
一座复古码头城，以键盘敲下每一道命令，结识远方的旅人、完成小小的冒险。
听见电传机与灯塔在文本中回响。

新手任务：在老码头寻找【纸带】并带到【电传机房】！"""
    
    async def handle_communication(self):
        """处理客户端通信"""
        try:
            while not self.reader.at_eof():
                # 读取一行数据
                data = await self.reader.readline()
                if not data:
                    break
                
                # 解码并处理命令
                message = data.decode('utf-8', errors='ignore').strip()
                if message:
                    await self.process_message(message)
                
        except asyncio.CancelledError:
            logger.info(f"客户端 {self.addr} 连接被取消")
        except Exception as e:
            logger.error(f"客户端 {self.addr} 通信错误: {e}")
        finally:
            await self.handle_disconnect()
    
    async def process_message(self, message: str):
        """处理客户端消息"""
        try:
            current_time = asyncio.get_event_loop().time()
            
            # 检查命令冷却时间
            if current_time - self.last_command_time < self.command_cooldown:
                await self.send_message("ERR", "命令执行过快，请稍等片刻。")
                return
            
            self.last_command_time = current_time
            
            # 解析命令
            command, args = self._parse_command(message)
            
            if not command:
                await self.send_message("ERR", "无效命令。输入 'HELP' 获取帮助。")
                return
            
            # 处理命令
            await self.server.command_handler.handle_command(self, command, args)
            
        except Exception as e:
            logger.error(f"处理消息错误: {e}")
            await self.send_message("ERR", "命令执行出错，请重试。")
    
    def _parse_command(self, message: str) -> tuple:
        """解析命令和参数"""
        # 处理引号内的内容（SAY命令）
        if message.startswith('"') and message.endswith('"'):
            return "SAY", [message[1:-1]]
        
        # 分割命令和参数
        parts = message.split()
        if not parts:
            return None, []
        
        command = parts[0].upper()
        args = parts[1:] if len(parts) > 1 else []
        
        return command, args
    
    async def send_message(self, msg_type: str, content: str, **kwargs):
        """发送消息到客户端"""
        try:
            # 格式化消息
            if msg_type == "ROOM":
                message = f"ROOM {content}"
            elif msg_type == "DESC":
                message = f"DESC {content}"
            elif msg_type == "SYS":
                message = f"SYS {content}"
            elif msg_type == "ERR":
                message = f"ERR {content}"
            elif msg_type == "OK":
                message = f"OK {content}"
            elif msg_type == "SEEN":
                player_name = kwargs.get('player_name', '')
                action = kwargs.get('action', '')
                message = f"SEEN {player_name} {action}"
            elif msg_type == "LIST":
                items = kwargs.get('items', [])
                message = f"LIST {' '.join(items)}"
            elif msg_type == "ITEM":
                item_data = kwargs.get('item_data', {})
                message = f"ITEM {json.dumps(item_data, ensure_ascii=False)}"
            elif msg_type == "QUEST":
                quest_data = kwargs.get('quest_data', {})
                message = f"QUEST {json.dumps(quest_data, ensure_ascii=False)}"
            else:
                message = f"{msg_type} {content}"
            
            # 添加换行符
            message += "\n"
            
            # 发送消息
            self.writer.write(message.encode('utf-8'))
            await self.writer.drain()
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
    
    async def send_multiline_desc(self, lines: list):
        """发送多行描述"""
        for line in lines:
            await self.send_message("DESC", line)
    
    async def broadcast_to_room(self, message: str, exclude_self: bool = False):
        """向房间内所有玩家广播消息"""
        if not self.player or not self.player.current_room:
            return
        
        room = self.server.world.get_room(self.player.current_room)
        if room:
            for player in room.get_players():
                if exclude_self and player == self.player:
                    continue
                
                try:
                    await player.protocol.send_message("SEEN", message, 
                                                     player_name=self.player.name,
                                                     action=message)
                except Exception as e:
                    logger.error(f"广播消息失败: {e}")
    
    async def handle_disconnect(self):
        """处理客户端断开连接"""
        if self.player:
            # 保存玩家数据
            await self.server.players.save_player(self.player)
            
            # 通知房间内其他玩家
            if self.player.current_room:
                await self.broadcast_to_room(f"离开了房间")
            
            # 从在线玩家列表中移除
            self.server.players.remove_player(self.player)
            
            logger.info(f"玩家 {self.player.name} 断开连接")
        
        # 关闭连接
        if not self.writer.is_closing():
            self.writer.close()
            await self.writer.wait_closed()
    
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self.authenticated and self.player is not None
    
    def get_player(self) -> Optional['Player']:
        """获取玩家对象"""
        return self.player
    
    def set_player(self, player: 'Player'):
        """设置玩家对象"""
        self.player = player
        self.authenticated = True
    
    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        return {
            'addr': self.addr,
            'connected_at': self.connected_at,
            'authenticated': self.authenticated,
            'player_name': self.player.name if self.player else None
        }
