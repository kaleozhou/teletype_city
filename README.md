# 《终端·回响》——纯终端网络游戏

一个基于Telnet的纯文本MUD游戏，重现BBS时代的网络游戏体验。

## 特性

- 🎮 纯文本界面，支持ANSI颜色
- 🌍 复古码头城市世界观
- 👥 多人在线社交
- 🎯 任务系统与成长
- ⚔️ 回合制战斗
- 💰 经济系统与交易
- 📱 零门槛接入（telnet 或 nc 即可  ）

## 快速开始

### 服务器端
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器
python start_server.py
```

### 客户端连接
```bash
telnet teletype.kaleo.vip 2323
或
nc  teletype.kaleo.vip 2323
```

## 游戏命令

- `LOGIN <昵称>` - 登录游戏
- `LOOK` - 查看当前房间
- `GO N/S/E/W` - 移动方向
- `SAY <内容>` - 房间内发言
- `TELL <玩家名> <内容>` - 私聊
- `JOIN <频道名>` - 加入频道
- `WHO` - 查看在线玩家
- `HELP` - 获取帮助

## 项目结构

```
teletype_city/
├── server.py          # 主服务器
├── protocol.py        # 协议处理
├── commands.py        # 命令系统
├── world/             # 游戏世界
├── systems/           # 游戏系统
├── data/              # 游戏数据
├── persist/           # 数据持久化
├── start_server.py    # 服务器启动脚本
├── test_*.py          # 测试脚本
├── Dockerfile         # Docker容器配置
├── docker-compose.yml # Docker编排配置
└── Makefile           # 自动化构建脚本
```

## 开发状态

### ✅ 已完成
- [x] 项目架构设计
- [x] 核心服务器框架
- [x] 世界系统（9个房间，5个NPC，17件物品，10个任务）
- [x] 玩家系统（登录、移动、状态管理）
- [x] 聊天系统（房间聊天、私聊、频道聊天）
- [x] 基础命令系统（LOOK、GO、SAY、TELL、WHO、HELP等）
- [x] 数据持久化（玩家数据保存/加载）
- [x] Docker容器化部署
- [x] 测试框架和脚本

### 🔄 进行中
- [ ] 任务系统完善
- [ ] 战斗系统开发
- [ ] 经济系统实现

### 📋 待开发
- [ ] 物品使用和装备系统
- [ ] 技能系统
- [ ] 公会/组织系统
- [ ] 排行榜系统
- [ ] 管理员工具
- [ ] 客户端优化

## Docker部署

```bash
# 构建镜像
make build

# 运行容器
make run

# 查看日志
make logs

# 停止服务
make stop
```

## 测试

```bash
# 基础功能测试
python3 test_basic.py

# 聊天功能测试
python3 test_all_chat.py

# Telnet客户端测试
python3 test_telnet.py
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
