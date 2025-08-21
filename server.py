#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《终端·回响》游戏服务器
主服务器文件，负责TCP连接、玩家管理和游戏循环
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Set
import time

from protocol import GameProtocol
from world.world_manager import WorldManager
from systems.player_manager import PlayerManager
from systems.chat_manager import ChatManager
from persist.storage import StorageManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GameServer:
    def __init__(self, host='0.0.0.0', port=2323):
        self.host = host
        self.port = port
        self.server = None
        self.running = False
        
        # 初始化各个管理器
        self.storage = StorageManager()
        self.world = WorldManager()
        self.players = PlayerManager()
        self.chat = ChatManager()
        
        # 初始化命令处理器
        from commands import CommandHandler
        self.command_handler = CommandHandler(self)
        
        # 游戏状态
        self.tick_rate = 10  # 10Hz tick
        self.tick_interval = 1.0 / self.tick_rate
        
        # 统计信息
        self.stats = {
            'start_time': time.time(),
            'total_connections': 0,
            'peak_players': 0,
            'current_players': 0
        }
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理系统信号"""
        logger.info(f"收到信号 {signum}，正在关闭服务器...")
        self.running = False
        if self.server:
            self.server.close()
    
    async def start(self):
        """启动游戏服务器"""
        try:
            # 加载游戏数据
            logger.info("正在加载游戏世界...")
            await self.world.load_world()
            
            # 启动TCP服务器
            logger.info(f"正在启动服务器 {self.host}:{self.port}...")
            self.server = await asyncio.start_server(
                self.handle_client,
                self.host,
                self.port,
                reuse_address=True
            )
            
            logger.info(f"服务器启动成功！端口: {self.port}")
            logger.info("玩家可以通过以下命令连接:")
            logger.info(f"  telnet {self.host} {self.port}")
            
            # 启动游戏循环
            self.running = True
            await self.game_loop()
            
        except Exception as e:
            logger.error(f"服务器启动失败: {e}")
            sys.exit(1)
    
    async def handle_client(self, reader, writer):
        """处理新的客户端连接"""
        addr = writer.get_extra_info('peername')
        logger.info(f"新连接: {addr}")
        
        self.stats['total_connections'] += 1
        
        try:
            # 创建游戏协议处理器
            protocol = GameProtocol(reader, writer, self)
            
            # 发送欢迎信息
            await protocol.send_welcome()
            
            # 处理客户端通信
            await protocol.handle_communication()
            
        except Exception as e:
            logger.error(f"客户端 {addr} 处理错误: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"连接关闭: {addr}")
    
    async def game_loop(self):
        """游戏主循环"""
        logger.info("游戏循环启动")
        last_tick = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # 执行游戏tick
                if current_time - last_tick >= self.tick_interval:
                    await self.tick()
                    last_tick = current_time
                
                # 更新统计信息
                current_players = len(self.players.get_online_players())
                self.stats['current_players'] = current_players
                if current_players > self.stats['peak_players']:
                    self.stats['peak_players'] = current_players
                
                # 短暂休眠避免CPU占用过高
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"游戏循环错误: {e}")
                await asyncio.sleep(1)
        
        logger.info("游戏循环结束")
    
    async def tick(self):
        """执行一个游戏tick"""
        try:
            # 更新世界状态
            await self.world.tick()
            
            # 更新玩家状态
            await self.players.tick()
            
            # 处理聊天系统
            await self.chat.tick()
            
            # 处理定时事件
            await self.handle_timed_events()
            
        except Exception as e:
            logger.error(f"Tick执行错误: {e}")
    
    async def handle_timed_events(self):
        """处理定时事件"""
        current_time = time.time()
        
        # 整点事件（灯塔鸣笛）
        if int(current_time) % 3600 == 0:  # 每小时
            await self.world.trigger_hourly_event()
        
        # 每日事件
        if int(current_time // 86400) != int(self.stats['start_time'] // 86400):
            await self.world.trigger_daily_event()
            self.stats['start_time'] = current_time
    
    async def stop(self):
        """停止服务器"""
        logger.info("正在停止服务器...")
        self.running = False
        
        # 保存所有玩家数据
        await self.players.save_all_players()
        
        # 关闭服务器
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        logger.info("服务器已停止")

async def main():
    """主函数"""
    server = GameServer()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    finally:
        await server.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务器已退出")
    except Exception as e:
        logger.error(f"服务器异常退出: {e}")
        sys.exit(1)
