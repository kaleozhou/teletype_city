#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏演示脚本
展示《终端·回响》的主要功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_banner():
    """打印游戏横幅"""
    print("""\x1b[36m
  ____  _   _  ____    ____                  _           _
 |  _ \| \ | |/ ___|  / ___|_ __ ___  __ _  __| | ___  ___| |
 | |_) |  \| | |  _  | |  _| '__/ _ \/ _` |/ _` |/ _ \/ __| |
 |  __/| |\  | |_| | | |_| | | |  __/ (_| | (_| |  __/\__ \_|
 |_|   |_| \_|\____|  \____|_|  \___|\__,_|\__,_|\___||___(_)
\x1b[0m""")
    print("《终端·回响》游戏演示")
    print("=" * 50)

def show_world_info():
    """显示世界信息"""
    print("\n🌍 游戏世界信息:")
    print("   • 9个精心设计的房间")
    print("   • 5个有趣的NPC")
    print("   • 17种不同的物品")
    print("   • 10个精彩的任务")
    
    print("\n🗺️  世界地图:")
    print("        [灯塔下] [海滩]")
    print("           |        |")
    print("        [老码头] [电传机房]")
    print("           |        |")
    print("        [暗巷] [集市] [公告板]")
    print("           |        |")
    print("        [地下水道] [杂货店]")

def show_features():
    """显示游戏特性"""
    print("\n🎮 游戏特性:")
    print("   • 纯文本界面，支持ANSI颜色")
    print("   • 多人在线社交")
    print("   • 任务系统与成长")
    print("   • 经济系统与交易")
    print("   • 回合制战斗（开发中）")
    print("   • 零门槛接入（telnet即可）")

def show_commands():
    """显示主要命令"""
    print("\n⌨️  主要命令:")
    print("   • LOGIN <昵称> - 登录游戏")
    print("   • LOOK - 查看当前房间")
    print("   • GO N/S/E/W - 移动方向")
    print("   • SAY <内容> - 房间内发言")
    print("   • WHO - 查看在线玩家")
    print("   • HELP - 获取帮助")
    print("   • QUIT - 退出游戏")

def show_quick_start():
    """显示快速开始指南"""
    print("\n🚀 快速开始:")
    print("1. 启动服务器:")
    print("   source venv/bin/activate")
    print("   python3 start_server.py")
    print("")
    print("2. 连接游戏:")
    print("   telnet localhost 2323")
    print("")
    print("3. 新手任务:")
    print("   • 在老码头寻找【纸带】")
    print("   • 将纸带带到【电传机房】")
    print("   • 获得新手称号【报童】和20铆钉")

def show_development_status():
    """显示开发状态"""
    print("\n🔧 开发状态:")
    print("   ✓ 项目架构设计")
    print("   ✓ 核心服务器框架")
    print("   ✓ 世界系统")
    print("   ✓ 玩家系统")
    print("   ✓ 基础命令系统")
    print("   ✓ 聊天系统框架")
    print("   ⚠️  任务系统（基础框架）")
    print("   ⚠️  战斗系统（待开发）")
    print("   ⚠️  数据持久化（基础框架）")

def main():
    """主函数"""
    print_banner()
    show_world_info()
    show_features()
    show_commands()
    show_quick_start()
    show_development_status()
    
    print("\n" + "=" * 50)
    print("🎉 恭喜！《终端·回响》游戏服务器已经准备就绪！")
    print("   按照上面的指南开始你的电传之城冒险吧！")
    print("=" * 50)

if __name__ == "__main__":
    main()
