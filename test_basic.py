#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本功能测试脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from world.world_manager import WorldManager
        print("✓ WorldManager 导入成功")
    except Exception as e:
        print(f"✗ WorldManager 导入失败: {e}")
    
    try:
        from systems.player_manager import PlayerManager
        print("✓ PlayerManager 导入成功")
    except Exception as e:
        print(f"✗ PlayerManager 导入失败: {e}")
    
    try:
        from systems.chat_manager import ChatManager
        print("✓ ChatManager 导入成功")
    except Exception as e:
        print(f"✗ ChatManager 导入失败: {e}")
    
    try:
        from persist.storage import StorageManager
        print("✓ StorageManager 导入成功")
    except Exception as e:
        print(f"✗ StorageManager 导入失败: {e}")
    
    try:
        from commands import CommandHandler
        print("✓ CommandHandler 导入成功")
    except Exception as e:
        print(f"✗ CommandHandler 导入失败: {e}")

def test_data_files():
    """测试数据文件"""
    print("\n测试数据文件...")
    
    data_files = [
        'data/rooms.yml',
        'data/npcs.yml',
        'data/items.yml',
        'data/quests.yml'
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} 存在")
        else:
            print(f"✗ {file_path} 不存在")

def test_yaml_parsing():
    """测试YAML解析"""
    print("\n测试YAML解析...")
    
    try:
        import yaml
        
        # 测试房间数据
        with open('data/rooms.yml', 'r', encoding='utf-8') as f:
            rooms_data = yaml.safe_load(f)
            print(f"✓ 房间数据解析成功，共 {len(rooms_data)} 个房间")
        
        # 测试NPC数据
        with open('data/npcs.yml', 'r', encoding='utf-8') as f:
            npcs_data = yaml.safe_load(f)
            print(f"✓ NPC数据解析成功，共 {len(npcs_data)} 个NPC")
        
        # 测试物品数据
        with open('data/items.yml', 'r', encoding='utf-8') as f:
            items_data = yaml.safe_load(f)
            print(f"✓ 物品数据解析成功，共 {len(items_data)} 件物品")
        
        # 测试任务数据
        with open('data/quests.yml', 'r', encoding='utf-8') as f:
            quests_data = yaml.safe_load(f)
            print(f"✓ 任务数据解析成功，共 {len(quests_data)} 个任务")
            
    except Exception as e:
        print(f"✗ YAML解析失败: {e}")

def test_world_creation():
    """测试世界创建"""
    print("\n测试世界创建...")
    
    try:
        from world.world_manager import WorldManager
        
        world = WorldManager()
        print("✓ WorldManager 创建成功")
        
        # 注意：这里不实际加载数据，因为可能没有完整的实现
        
    except Exception as e:
        print(f"✗ 世界创建失败: {e}")

def main():
    """主测试函数"""
    print("《终端·回响》基本功能测试")
    print("=" * 40)
    
    test_imports()
    test_data_files()
    test_yaml_parsing()
    test_world_creation()
    
    print("\n测试完成！")
    print("\n如果所有测试都通过，你可以尝试启动服务器：")
    print("  python3 start_server.py")
    print("\n然后在另一个终端测试客户端：")
    print("  python3 test_client.py")

if __name__ == "__main__":
    main()
