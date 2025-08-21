#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试私聊功能
"""

import asyncio

async def test_private_chat():
    """测试私聊功能"""
    print("《终端·回响》私聊功能测试")
    print("=" * 50)
    
    # 创建两个客户端连接
    client1 = await create_client("私聊测试1")
    client2 = await create_client("私聊测试2")
    
    if not client1 or not client2:
        print("❌ 客户端连接失败")
        return
    
    print("✅ 两个客户端连接成功")
    
    # 测试私聊
    print("\n测试私聊...")
    print(f"  {client1['name']} 向 {client2['name']} 发送私聊...")
    
    # 客户端1发送私聊
    client1['writer'].write("TELL 私聊测试2 你好，这是私聊消息！\n".encode('utf-8'))
    await client1['writer'].drain()
    
    # 等待消息传播
    await asyncio.sleep(2)
    
    # 检查客户端2是否收到私聊
    responses = await read_responses(client2['reader'])
    print(f"  客户端2收到的消息: {responses}")
    
    # 检查是否有私聊消息
    private_message_received = any("私聊:" in resp for resp in responses)
    
    if private_message_received:
        print("  ✅ 私聊功能正常")
    else:
        print("  ❌ 私聊功能异常")
    
    # 清理
    await cleanup_clients([client1, client2])
    print("\n✅ 私聊功能测试完成")

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
        while True:
            data = await asyncio.wait_for(reader.readline(), timeout=0.1)
            if data:
                response = data.decode('utf-8', errors='ignore').strip()
                if response:
                    responses.append(response)
            else:
                break
    except asyncio.TimeoutError:
        pass
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
    asyncio.run(test_private_chat())
