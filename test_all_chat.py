#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《终端·回响》完整聊天功能测试
"""

import asyncio
import time

async def test_all_chat():
    """测试所有聊天功能"""
    print("《终端·回响》完整聊天功能测试")
    print("=" * 60)
    
    # 创建三个客户端连接
    client1 = await create_client("聊天测试1")
    client2 = await create_client("聊天测试2")
    client3 = await create_client("聊天测试3")
    
    if not all([client1, client2, client3]):
        print("❌ 客户端连接失败")
        return
    
    print("✅ 三个客户端连接成功")
    
    # 测试1: 房间聊天
    print("\n1. 测试房间聊天...")
    await test_room_chat(client1, client2, client3)
    
    # 测试2: 私聊
    print("\n2. 测试私聊...")
    await test_private_chat(client1, client2)
    
    # 测试3: 频道聊天
    print("\n3. 测试频道聊天...")
    await test_channel_chat(client1, client2, client3)
    
    # 清理
    await cleanup_clients([client1, client2, client3])
    print("\n🎉 所有聊天功能测试完成！")

async def test_room_chat(client1, client2, client3):
    """测试房间聊天"""
    print(f"  {client1['name']} 发送房间消息...")
    
    # 客户端1发送房间消息
    client1['writer'].write("SAY 大家好，我是新来的！\n".encode('utf-8'))
    await client1['writer'].drain()
    
    # 等待消息传播
    await asyncio.sleep(2)
    
    # 检查其他客户端是否收到消息
    responses2 = await read_responses(client2['reader'])
    responses3 = await read_responses(client3['reader'])
    
    # 检测SEEN消息格式
    room_message_received2 = any("SEEN" in resp for resp in responses2)
    room_message_received3 = any("SEEN" in resp for resp in responses3)
    
    print(f"    客户端2响应: {responses2}")
    print(f"    客户端3响应: {responses3}")
    
    if room_message_received2 and room_message_received3:
        print("  ✅ 房间聊天功能正常 - 所有玩家都收到了SEEN消息")
    else:
        print("  ❌ 房间聊天功能异常")
        if not room_message_received2:
            print(f"    客户端2未收到SEEN消息")
        if not room_message_received3:
            print(f"    客户端3未收到SEEN消息")

async def test_private_chat(client1, client2):
    """测试私聊"""
    print(f"  {client1['name']} 向 {client2['name']} 发送私聊...")
    
    # 客户端1发送私聊
    client1['writer'].write("TELL 聊天测试2 你好，这是私聊消息！\n".encode('utf-8'))
    await client1['writer'].drain()
    
    # 等待消息传播
    await asyncio.sleep(2)
    
    # 检查客户端2是否收到私聊
    responses = await read_responses(client2['reader'])
    private_message_received = any("SEEN" in resp and "私聊:" in resp for resp in responses)
    
    print(f"    客户端2收到的消息: {responses}")
    
    if private_message_received:
        print("  ✅ 私聊功能正常 - 收到SEEN私聊消息")
    else:
        print("  ❌ 私聊功能异常")

async def test_channel_chat(client1, client2, client3):
    """测试频道聊天"""
    print(f"  测试频道 #test 聊天...")
    
    # 所有客户端加入频道
    for client in [client1, client2, client3]:
        client['writer'].write("JOIN test\n".encode('utf-8'))
        await client['writer'].drain()
        await asyncio.sleep(0.5)
    
    # 等待加入完成
    await asyncio.sleep(1)
    
    # 客户端1发送频道消息
    client1['writer'].write("SAY #test 大家好，这是频道消息！\n".encode('utf-8'))
    await client1['writer'].drain()
    
    # 等待消息传播
    await asyncio.sleep(2)
    
    # 检查其他客户端是否收到频道消息
    responses2 = await read_responses(client2['reader'])
    responses3 = await read_responses(client3['reader'])
    
    channel_message_received2 = any("SEEN" in resp and "[test]" in resp for resp in responses2)
    channel_message_received3 = any("SEEN" in resp and "[test]" in resp for resp in responses3)
    
    print(f"    客户端2响应: {responses2}")
    print(f"    客户端3响应: {responses3}")
    
    if channel_message_received2 and channel_message_received3:
        print("  ✅ 频道聊天功能正常 - 所有频道成员都收到了SEEN消息")
    else:
        print("  ❌ 频道聊天功能异常")
        if not channel_message_received2:
            print(f"    客户端2未收到SEEN频道消息")
        if not channel_message_received3:
            print(f"    客户端3未收到SEEN频道消息")

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
            'writer': writer,
            'responses': []
        }
    except Exception as e:
        print(f"❌ 创建客户端 {name} 失败: {e}")
        return None

async def read_responses(reader):
    """读取响应"""
    responses = []
    try:
        # 多次尝试读取，确保获取所有响应
        for _ in range(5):
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=0.2)
                if data:
                    response = data.decode('utf-8', errors='ignore').strip()
                    if response and response not in responses:
                        responses.append(response)
                else:
                    break
            except asyncio.TimeoutError:
                break
    except Exception as e:
        print(f"    读取响应时出错: {e}")
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
    asyncio.run(test_all_chat())
