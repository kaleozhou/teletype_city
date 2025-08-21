#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令处理系统
负责解析和执行游戏命令
"""

import asyncio
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class CommandHandler:
    def __init__(self, server):
        self.server = server
        self.commands = {}
        self._register_commands()
    
    def _register_commands(self):
        """注册所有命令"""
        self.commands = {
            'LOGIN': self.cmd_login,
            'LOOK': self.cmd_look,
            'GO': self.cmd_go,
            'SAY': self.cmd_say,
            'WHO': self.cmd_who,
            'TELL': self.cmd_tell,
            'JOIN': self.cmd_join,
            'LEAVE': self.cmd_leave,
            'INV': self.cmd_inventory,
            'USE': self.cmd_use,
            'GIVE': self.cmd_give,
            'EQUIP': self.cmd_equip,
            'STATS': self.cmd_stats,
            'QUESTS': self.cmd_quests,
            'TRACK': self.cmd_track,
            'TURNIN': self.cmd_turnin,
            'ATTACK': self.cmd_attack,
            'SKILL': self.cmd_skill,
            'FLEE': self.cmd_flee,
            'HELP': self.cmd_help,
            'QUIT': self.cmd_quit,
            'MAP': self.cmd_map,
            'EMOTE': self.cmd_emote,
            'BOARD': self.cmd_board,
            'MAIL': self.cmd_mail
        }
    
    async def handle_command(self, protocol, command: str, args: List[str]):
        """处理命令"""
        try:
            if command in self.commands:
                await self.commands[command](protocol, args)
            else:
                await protocol.send_message("ERR", f"未知命令: {command}")
                
        except Exception as e:
            logger.error(f"命令执行错误: {e}")
            await protocol.send_message("ERR", "命令执行出错，请重试")
    
    async def cmd_login(self, protocol, args: List[str]):
        """登录命令"""
        if len(args) < 1:
            await protocol.send_message("ERR", "用法: LOGIN <昵称>")
            return
        
        nickname = args[0]
        
        # 检查昵称长度
        if len(nickname) < 2 or len(nickname) > 20:
            await protocol.send_message("ERR", "昵称长度必须在2-20个字符之间")
            return
        
        # 检查昵称格式
        if not nickname.replace('_', '').replace('-', '').isalnum():
            await protocol.send_message("ERR", "昵称只能包含字母、数字、下划线和连字符")
            return
        
        try:
            # 创建或加载玩家
            player = await self.server.players.create_player(nickname, protocol)
            protocol.set_player(player)
            
            await protocol.send_message("OK", f"登录成功！欢迎来到电传之城，{nickname}")
            
            # 显示当前房间信息
            await self.cmd_look(protocol, [])
            
        except ValueError as e:
            await protocol.send_message("ERR", str(e))
        except Exception as e:
            logger.error(f"登录失败: {e}")
            await protocol.send_message("ERR", "登录失败，请重试")
    
    async def cmd_look(self, protocol, args: List[str]):
        """查看房间命令"""
        if not protocol.is_authenticated():
            await protocol.send_message("ERR", "请先登录")
            return
        
        player = protocol.get_player()
        room_id = player.current_room
        
        # 获取房间信息
        room = self.server.world.get_room(room_id)
        if not room:
            await protocol.send_message("ERR", "房间不存在")
            return
        
        # 发送房间信息
        await protocol.send_message("ROOM", room.title)
        await protocol.send_message("DESC", room.desc)
        
        # 显示出口
        if room.exits:
            exits = ", ".join([f"{dir} -> {room_id}" for dir, room_id in room.exits.items()])
            await protocol.send_message("SYS", f"出口: {exits}")
        
        # 显示房间内的其他玩家
        room_players = [p for p in room.get_players() if p != player]
        if room_players:
            player_names = ", ".join([p.name for p in room_players])
            await protocol.send_message("SYS", f"房间内的其他玩家: {player_names}")
    
    async def cmd_go(self, protocol, args: List[str]):
        """移动命令"""
        if not protocol.is_authenticated():
            await protocol.send_message("ERR", "请先登录")
            return
        
        if len(args) < 1:
            await protocol.send_message("ERR", "用法: GO <方向> (N/S/E/W)")
            return
        
        direction = args[0].upper()
        if direction not in ['N', 'S', 'E', 'W']:
            await protocol.send_message("ERR", "无效方向，请使用 N/S/E/W")
            return
        
        player = protocol.get_player()
        current_room = self.server.world.get_room(player.current_room)
        
        if not current_room:
            await protocol.send_message("ERR", "当前房间不存在")
            return
        
        # 检查出口
        target_room_id = current_room.get_exit_room(direction)
        if not target_room_id:
            await protocol.send_message("ERR", f"那个方向没有出口")
            return
        
        target_room = self.server.world.get_room(target_room_id)
        if not target_room:
            await protocol.send_message("ERR", "目标房间不存在")
            return
        
        # 移动玩家
        old_room = player.current_room
        player.current_room = target_room_id
        
        # 通知其他玩家
        await protocol.broadcast_to_room(f"离开了房间")
        
        # 进入新房间
        await protocol.send_message("OK", f"你向{direction}方向移动")
        await protocol.send_message("ROOM", target_room.title)
        await protocol.send_message("DESC", target_room.desc)
        
        # 通知新房间的玩家
        await protocol.broadcast_to_room(f"进入了房间")
        
        logger.info(f"玩家 {player.name} 从 {old_room} 移动到 {target_room_id}")
    
    async def cmd_say(self, protocol, args: List[str]):
        """说话命令"""
        if not protocol.is_authenticated():
            await protocol.send_message("ERR", "请先登录")
            return
        
        if len(args) < 1:
            await protocol.send_message("ERR", "用法: SAY <内容>")
            return
        
        message = " ".join(args)
        player = protocol.get_player()
        
        # 发送房间消息
        success = await self.server.chat.send_room_message(player, message)
        if success:
            await protocol.send_message("OK", f"你说: {message}")
        else:
            await protocol.send_message("ERR", "消息发送失败")
    
    async def cmd_who(self, protocol, args: List[str]):
        """查看在线玩家命令"""
        online_players = self.server.players.get_online_players()
        
        if not online_players:
            await protocol.send_message("SYS", "当前没有在线玩家")
            return
        
        player_list = []
        for player in online_players:
            status = f"{player.name}"
            if player.title:
                status += f" [{player.title}]"
            status += f" (Lv.{player.level})"
            player_list.append(status)
        
        await protocol.send_message("SYS", f"在线玩家 ({len(online_players)}):")
        for player_info in player_list:
            await protocol.send_message("SYS", f"  {player_info}")
    
    async def cmd_tell(self, protocol, args: List[str]):
        """私聊命令"""
        if not protocol.is_authenticated():
            await protocol.send_message("ERR", "请先登录")
            return
        
        if len(args) < 2:
            await protocol.send_message("ERR", "用法: TELL <玩家名> <内容>")
            return
        
        target_name = args[0]
        message = " ".join(args[1:])
        sender = protocol.get_player()
        
        # 发送私聊
        success = await self.server.chat.send_private_message(sender, target_name, message)
        if not success:
            await protocol.send_message("ERR", "私聊发送失败")
    
    async def cmd_join(self, protocol, args: List[str]):
        """加入频道命令"""
        if not protocol.is_authenticated():
            await protocol.send_message("ERR", "请先登录")
            return
        
        if len(args) < 1:
            await protocol.send_message("ERR", "用法: JOIN <频道名>")
            return
        
        channel_name = args[0]
        if not channel_name.startswith('#'):
            channel_name = '#' + channel_name
        
        player = protocol.get_player()
        success = await self.server.chat.join_channel(player, channel_name)
        if not success:
            await protocol.send_message("ERR", "加入频道失败")
    
    async def cmd_leave(self, protocol, args: List[str]):
        """离开频道命令"""
        if not protocol.is_authenticated():
            await protocol.send_message("ERR", "请先登录")
            return
        
        if len(args) < 1:
            await protocol.send_message("ERR", "用法: LEAVE <频道名>")
            return
        
        channel_name = args[0]
        if not channel_name.startswith('#'):
            channel_name = '#' + channel_name
        
        player = protocol.get_player()
        success = await self.server.chat.leave_channel(player, channel_name)
        if not success:
            await protocol.send_message("ERR", "离开频道失败")
    
    async def cmd_inventory(self, protocol, args: List[str]):
        """查看背包命令"""
        if not protocol.is_authenticated():
            await protocol.send_message("ERR", "请先登录")
            return
        
        player = protocol.get_player()
        inventory = player.get_inventory()
        
        if not inventory:
            await protocol.send_message("SYS", "你的背包是空的")
            return
        
        await protocol.send_message("SYS", "背包内容:")
        for item_id, count in inventory.items():
            item = self.server.world.get_item(item_id)
            if item:
                await protocol.send_message("SYS", f"  {item.name} x{count}")
            else:
                await protocol.send_message("SYS", f"  {item_id} x{count}")
    
    async def cmd_stats(self, protocol, args: List[str]):
        """查看状态命令"""
        if not protocol.is_authenticated():
            await protocol.send_message("ERR", "请先登录")
            return
        
        player = protocol.get_player()
        
        await protocol.send_message("SYS", f"角色状态 - {player.name}")
        if player.title:
            await protocol.send_message("SYS", f"称号: {player.title}")
        await protocol.send_message("SYS", f"等级: {player.level}")
        await protocol.send_message("SYS", f"经验: {player.exp}/{player.level * 100}")
        await protocol.send_message("SYS", f"生命值: {player.hp}/{player.max_hp}")
        await protocol.send_message("SYS", f"精力: {player.ep}/{player.max_ep}")
        await protocol.send_message("SYS", f"金钱: {player.money} 铆钉")
        await protocol.send_message("SYS", f"属性: 力量{player.stats['str']} 敏捷{player.stats['agi']} 智力{player.stats['int']} 魅力{player.stats['cha']}")
    
    async def cmd_help(self, protocol, args: List[str]):
        """帮助命令"""
        help_text = """可用命令:
导航与观察:
  LOOK                  - 查看当前房间
  GO N|S|E|W           - 朝方向移动
  MAP                   - 查看地图

社交:
  SAY <内容>            - 房间内发言
  WHO                   - 查看在线玩家
  TELL <玩家名> <内容>  - 私聊
  JOIN #频道名          - 加入频道
  LEAVE #频道名         - 离开频道
  EMOTE <动作>          - 做动作

角色与物品:
  INV                   - 查看背包
  USE <物品>            - 使用物品
  GIVE <玩家名> <物品>  - 给予物品
  EQUIP <物品>          - 装备物品
  STATS                 - 查看状态

任务:
  QUESTS                - 查看任务
  TRACK <任务ID>        - 追踪任务
  TURNIN <任务ID>       - 交付任务

战斗:
  ATTACK <目标>         - 攻击
  SKILL <技能名> <目标> - 使用技能
  FLEE                  - 逃跑

系统:
  HELP [主题]           - 获取帮助
  QUIT                  - 退出游戏

别名: N=GO N, S=GO S, E=GO E, W=GO W, "内容"=SAY 内容"""
        
        await protocol.send_message("SYS", help_text)
    
    async def cmd_quit(self, protocol, args: List[str]):
        """退出命令"""
        await protocol.send_message("SYS", "再见！欢迎再次来到电传之城！")
        protocol.writer.close()
    
    async def cmd_map(self, protocol, args: List[str]):
        """地图命令"""
        if not protocol.is_authenticated():
            await protocol.send_message("ERR", "请先登录")
            return
        
        map_text = """电传之城地图:
        
        [灯塔下] [海滩]
           |        |
        [老码头] [电传机房]
           |        |
        [暗巷] [集市] [公告板]
           |        |
        [地下水道] [杂货店]
        
        你当前在: [老码头]"""
        
        await protocol.send_message("SYS", map_text)
    
    async def cmd_emote(self, protocol, args: List[str]):
        """动作命令"""
        if not protocol.is_authenticated():
            await protocol.send_message("ERR", "请先登录")
            return
        
        if len(args) < 1:
            await protocol.send_message("ERR", "用法: EMOTE <动作>")
            return
        
        action = " ".join(args)
        player = protocol.get_player()
        
        # 广播动作到房间
        await protocol.broadcast_to_room(f"{action}")
        await protocol.send_message("OK", f"你{action}")
    
    # 其他命令的占位符实现
    async def cmd_use(self, protocol, args: List[str]):
        await protocol.send_message("SYS", "此功能正在开发中")
    
    async def cmd_give(self, protocol, args: List[str]):
        await protocol.send_message("SYS", "此功能正在开发中")
    
    async def cmd_equip(self, protocol, args: List[str]):
        await protocol.send_message("SYS", "此功能正在开发中")
    
    async def cmd_quests(self, protocol, args: List[str]):
        await protocol.send_message("SYS", "此功能正在开发中")
    
    async def cmd_track(self, protocol, args: List[str]):
        await protocol.send_message("SYS", "此功能正在开发中")
    
    async def cmd_turnin(self, protocol, args: List[str]):
        await protocol.send_message("SYS", "此功能正在开发中")
    
    async def cmd_attack(self, protocol, args: List[str]):
        await protocol.send_message("SYS", "此功能正在开发中")
    
    async def cmd_skill(self, protocol, args: List[str]):
        await protocol.send_message("SYS", "此功能正在开发中")
    
    async def cmd_flee(self, protocol, args: List[str]):
        await protocol.send_message("SYS", "此功能正在开发中")
    
    async def cmd_board(self, protocol, args: List[str]):
        await protocol.send_message("SYS", "此功能正在开发中")
    
    async def cmd_mail(self, protocol, args: List[str]):
        await protocol.send_message("SYS", "此功能正在开发中")
