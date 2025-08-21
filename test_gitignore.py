#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 .gitignore 文件是否正常工作
"""

import os
import subprocess
import sys

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_gitignore():
    """测试 .gitignore 文件"""
    print("🔍 测试 .gitignore 文件...")
    print("=" * 50)
    
    # 检查是否在Git仓库中
    success, stdout, stderr = run_command("git status")
    if not success:
        print("❌ 错误: 当前目录不是Git仓库")
        return False
    
    print("✅ 当前目录是Git仓库")
    
    # 检查被忽略的文件
    success, stdout, stderr = run_command("git status --ignored")
    if not success:
        print("❌ 错误: 无法获取忽略文件列表")
        return False
    
    print("\n📋 被忽略的文件:")
    ignored_files = []
    for line in stdout.split('\n'):
        if line.strip() and not line.startswith('On branch') and not line.startswith('Your branch'):
            if 'Ignored files:' in line:
                continue
            if line.strip():
                ignored_files.append(line.strip())
    
    if ignored_files:
        for file in ignored_files:
            print(f"  🚫 {file}")
    else:
        print("  📭 没有文件被忽略")
    
    # 检查特定文件是否被忽略
    test_files = [
        'venv/',
        '__pycache__/',
        'game_server.log',
        'data/players.json',
        'backups/',
        '*.pyc'
    ]
    
    print(f"\n🧪 测试特定文件:")
    for test_file in test_files:
        success, stdout, stderr = run_command(f"git check-ignore {test_file}")
        if success and stdout.strip():
            print(f"  ✅ {test_file} 被正确忽略")
        else:
            print(f"  ❌ {test_file} 未被忽略")
    
    # 检查应该被跟踪的文件
    should_track = [
        'server.py',
        'commands.py',
        'data/rooms.yml',
        'README.md'
    ]
    
    print(f"\n📁 检查应该被跟踪的文件:")
    for file in should_track:
        if os.path.exists(file):
            success, stdout, stderr = run_command(f"git check-ignore {file}")
            if success and stdout.strip():
                print(f"  ⚠️  {file} 被意外忽略")
            else:
                print(f"  ✅ {file} 可以正常跟踪")
        else:
            print(f"  ❓ {file} 文件不存在")
    
    print("\n" + "=" * 50)
    print("🎯 .gitignore 测试完成！")
    
    return True

def show_usage():
    """显示使用说明"""
    print("🔧 .gitignore 测试工具")
    print("使用方法:")
    print("  python3 test_gitignore.py")
    print("")
    print("这个工具会测试:")
    print("  - Git仓库状态")
    print("  - 被忽略的文件")
    print("  - 特定文件的忽略状态")
    print("  - 应该被跟踪的文件")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        show_usage()
    else:
        test_gitignore()
