#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存储管理器
负责游戏数据的持久化存储
"""

import json
import logging
import os
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self):
        self.data_dir = "data"
        self.backup_dir = "backups"
        self.ensure_directories()
        
    def ensure_directories(self):
        """确保必要的目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def save_data(self, filename: str, data: Any):
        """保存数据到文件"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            
            # 创建备份
            if os.path.exists(filepath):
                backup_name = f"{filename}.{int(time.time())}.bak"
                backup_path = os.path.join(self.backup_dir, backup_name)
                os.rename(filepath, backup_path)
            
            # 保存新数据
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"数据已保存到 {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            return False
    
    def load_data(self, filename: str) -> Optional[Any]:
        """从文件加载数据"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            
            if not os.path.exists(filepath):
                logger.debug(f"文件不存在: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.debug(f"数据已从 {filepath} 加载")
            return data
            
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return None
    
    def save_player_data(self, player_data: Dict[str, Any]):
        """保存玩家数据"""
        filename = f"player_{player_data['name']}.json"
        return self.save_data(filename, player_data)
    
    def load_player_data(self, player_name: str) -> Optional[Dict[str, Any]]:
        """加载玩家数据"""
        filename = f"player_{player_name}.json"
        return self.load_data(filename)
    
    def save_world_data(self, world_data: Dict[str, Any]):
        """保存世界数据"""
        return self.save_data("world_state.json", world_data)
    
    def load_world_data(self) -> Optional[Dict[str, Any]]:
        """加载世界数据"""
        return self.load_data("world_state.json")
    
    def save_game_stats(self, stats: Dict[str, Any]):
        """保存游戏统计"""
        return self.save_data("game_stats.json", stats)
    
    def load_game_stats(self) -> Optional[Dict[str, Any]]:
        """加载游戏统计"""
        return self.load_data("game_stats.json")
    
    def create_backup(self, filename: str):
        """创建数据备份"""
        try:
            source_path = os.path.join(self.data_dir, filename)
            if not os.path.exists(source_path):
                return False
            
            timestamp = int(time.time())
            backup_name = f"{filename}.{timestamp}.bak"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            with open(source_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            logger.info(f"备份已创建: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return False
    
    def cleanup_old_backups(self, max_backups: int = 10):
        """清理旧的备份文件"""
        try:
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.bak'):
                    filepath = os.path.join(self.backup_dir, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))
            
            # 按修改时间排序
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # 删除多余的备份
            for filepath, _ in backup_files[max_backups:]:
                os.remove(filepath)
                logger.debug(f"删除旧备份: {filepath}")
            
            logger.info(f"备份清理完成，保留 {min(len(backup_files), max_backups)} 个备份")
            
        except Exception as e:
            logger.error(f"清理备份失败: {e}")
    
    def get_data_size(self, filename: str) -> int:
        """获取数据文件大小（字节）"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                return os.path.getsize(filepath)
            return 0
        except Exception:
            return 0
    
    def get_total_data_size(self) -> int:
        """获取总数据大小（字节）"""
        total_size = 0
        try:
            for filename in os.listdir(self.data_dir):
                total_size += self.get_data_size(filename)
        except Exception:
            pass
        return total_size
