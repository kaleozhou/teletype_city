#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器启动脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import GameServer

async def main():
    print("正在启动《终端·回响》游戏服务器...")
    
    # 创建服务器实例
    server = GameServer(host='0.0.0.0', port=2323)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n收到中断信号，正在关闭服务器...")
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)
    finally:
        await server.stop()
        print("服务器已关闭")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务器已退出")
    except Exception as e:
        print(f"服务器异常退出: {e}")
        sys.exit(1)
