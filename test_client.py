#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试客户端脚本
用于测试游戏服务器的基本功能
"""

import asyncio
import sys

async def test_client():
    """测试客户端连接"""
    try:
        # 连接到服务器
        reader, writer = await asyncio.open_connection('localhost', 2323)
        print("已连接到服务器")
        
        # 读取欢迎消息
        data = await reader.readline()
        print(f"服务器消息: {data.decode().strip()}")
        
        # 发送登录命令
        login_cmd = "LOGIN 测试玩家\n".encode()
        writer.write(login_cmd)
        await writer.drain()
        print("已发送登录命令")
        
        # 读取响应
        for _ in range(5):  # 读取多条响应
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=2.0)
                if data:
                    print(f"服务器响应: {data.decode().strip()}")
                else:
                    break
            except asyncio.TimeoutError:
                break
        
        # 发送帮助命令
        help_cmd = "HELP\n".encode()
        writer.write(help_cmd)
        await writer.drain()
        print("已发送帮助命令")
        
        # 读取帮助响应
        for _ in range(3):
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=2.0)
                if data:
                    print(f"帮助信息: {data.decode().strip()}")
                else:
                    break
            except asyncio.TimeoutError:
                break
        
        # 关闭连接
        writer.close()
        await writer.wait_closed()
        print("测试完成，连接已关闭")
        
    except ConnectionRefusedError:
        print("无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    print("开始测试游戏服务器...")
    asyncio.run(test_client())
