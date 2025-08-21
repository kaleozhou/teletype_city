#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的聊天功能测试
"""

import asyncio
import time

async def simple_chat_test():
    """简单的聊天测试"""
    print("《终端·回响》简单聊天测试")
    print("=" * 40)
    
    # 创建两个客户端
    client1 = await create_client("简单测试1")
    client2 = await create_client("简单测试2")
    
    if not client1 or not client2:
        print("❌ 客户端连接失败")
        return
    
    print("✅ 两个客户端连接成功")
    
    # 等待一下确保连接稳定
    await asyncio.sleep(2)
    
    # 测试房间聊天
    print("\n测试房间聊天...")
    print(f"  {client1['name']} 发送: SAY 测试消息")
    
    client1['writer'].write("SAY 测试消息\n".encode('utf-8'))
    await client1['writer'].drain()
    
    # 等待消息传播
    await asyncio.sleep(3)
    
    # 读取客户端2的响应
    print(f"  读取 {client2['name']} 的响应...")
    responses = await read_all_responses(client2['reader'])
    print(f"  响应数量: {len(responses)}")
    print(f"  响应内容: {responses}")
    
    # 检查是否有SEEN消息
    seen_messages = [r for r in responses if "SEEN" in r]
    if seen_messages:
        print(f"  ✅ 收到 {len(seen_messages)} 条SEEN消息")
        for msg in seen_messages:
            print(f"    {msg}")
    else:
        print("  ❌ 没有收到SEEN消息")
    
    # 清理
    await cleanup_clients([client1, client2])
    print("\n✅ 测试完成")

async def create_client(name):
    """创建客户端连接"""
    try:
        reader, writer = await asyncio.open_connection('localhost', 2323)
        
        # 等待欢迎消息
        await asyncio.sleep(1)
        
        # 登录
        writer.write(f"LOGIN {name}\n".encode('utf-8'))
        await writer.drain()
        
        # 等待登录响应
        await asyncio.sleep(1)
        
        return {
            'name': name,
            'reader': reader,
            'writer': writer
        }
    except Exception as e:
        print(f"❌ 创建客户端 {name} 失败: {e}")
        return None

async def read_all_responses(reader):
    """读取所有响应"""
    responses = []
    try:
        # 多次尝试读取
        for _ in range(10):
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=0.3)
                if data:
                    response = data.decode('utf-8', errors='ignore').strip()
                    if response and response not in responses:
                        responses.append(response)
                else:
                    break
            except asyncio.TimeoutError:
                break
    except Exception as e:
        print(f"读取响应时出错: {e}")
    return responses

async def cleanup_clients(clients):
    """清理客户端连接"""
    for client in clients:
        try:
            client['writer'].write("QUIT\n".encode('utf-8'))
            await client['writer'].drain()
            client['writer'].close()
            await client['writer'].wait_closed()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(simple_chat_test())
