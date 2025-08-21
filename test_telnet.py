#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telnet客户端测试脚本
模拟真实的telnet连接体验
"""

import asyncio
import sys
import time

async def telnet_client():
    """模拟telnet客户端"""
    try:
        # 连接到服务器
        reader, writer = await asyncio.open_connection('localhost', 2323)
        print("已连接到游戏服务器！")
        print("=" * 50)
        
        # 读取欢迎消息
        while True:
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=1.0)
                if not data:
                    break
                
                message = data.decode('utf-8', errors='ignore').strip()
                if message:
                    print(f"服务器: {message}")
                    
                    # 如果收到完整的欢迎消息，开始交互
                    if "新手任务" in message:
                        break
                        
            except asyncio.TimeoutError:
                break
        
        print("\n" + "=" * 50)
        print("开始游戏交互测试...")
        
        # 测试登录
        print("\n1. 测试登录...")
        login_cmd = "LOGIN 海风\n".encode()
        writer.write(login_cmd)
        await writer.drain()
        print("发送: LOGIN 海风")
        
        # 读取登录响应
        await asyncio.sleep(0.5)
        for _ in range(5):
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=0.5)
                if data:
                    response = data.decode('utf-8', errors='ignore').strip()
                    if response:
                        print(f"响应: {response}")
            except asyncio.TimeoutError:
                break
        
        # 测试查看房间
        print("\n2. 测试查看房间...")
        look_cmd = "LOOK\n".encode()
        writer.write(look_cmd)
        await writer.drain()
        print("发送: LOOK")
        
        # 读取响应
        await asyncio.sleep(0.5)
        for _ in range(3):
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=0.5)
                if data:
                    response = data.decode('utf-8', errors='ignore').strip()
                    if response:
                        print(f"响应: {response}")
            except asyncio.TimeoutError:
                break
        
        # 测试移动
        print("\n3. 测试移动...")
        go_cmd = "GO E\n".encode()
        writer.write(go_cmd)
        await writer.drain()
        print("发送: GO E")
        
        # 读取响应
        await asyncio.sleep(0.5)
        for _ in range(3):
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=0.5)
                if data:
                    response = data.decode('utf-8', errors='ignore').strip()
                    if response:
                        print(f"响应: {response}")
            except asyncio.TimeoutError:
                break
        
        # 测试聊天
        print("\n4. 测试聊天...")
        say_cmd = 'SAY 大家好，我是新来的！\n'.encode()
        writer.write(say_cmd)
        await writer.drain()
        print("发送: SAY 大家好，我是新来的！")
        
        # 读取响应
        await asyncio.sleep(0.5)
        for _ in range(2):
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=0.5)
                if data:
                    response = data.decode('utf-8', errors='ignore').strip()
                    if response:
                        print(f"响应: {response}")
            except asyncio.TimeoutError:
                break
        
        # 测试帮助
        print("\n5. 测试帮助...")
        help_cmd = "HELP\n".encode()
        writer.write(help_cmd)
        await writer.drain()
        print("发送: HELP")
        
        # 读取响应
        await asyncio.sleep(0.5)
        for _ in range(10):
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=0.5)
                if data:
                    response = data.decode('utf-8', errors='ignore').strip()
                    if response:
                        print(f"响应: {response}")
            except asyncio.TimeoutError:
                break
        
        # 退出
        print("\n6. 退出游戏...")
        quit_cmd = "QUIT\n".encode()
        writer.write(quit_cmd)
        await writer.drain()
        print("发送: QUIT")
        
        # 关闭连接
        writer.close()
        await writer.wait_closed()
        
        print("\n" + "=" * 50)
        print("测试完成！游戏服务器运行正常！")
        print("=" * 50)
        
    except ConnectionRefusedError:
        print("无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    print("《终端·回响》游戏服务器 - Telnet客户端测试")
    print("正在连接到 localhost:2323...")
    asyncio.run(telnet_client())
