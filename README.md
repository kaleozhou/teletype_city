# 《终端·回响》——纯终端网络游戏

一个基于Telnet的纯文本MUD游戏，重现BBS时代的网络游戏体验。

## 特性

- 🎮 纯文本界面，支持ANSI颜色
- 🌍 复古码头城市世界观
- 👥 多人在线社交
- 🎯 任务系统与成长
- ⚔️ 回合制战斗
- 💰 经济系统与交易
- 📱 零门槛接入（telnet即可）

## 快速开始

### 服务器端
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器
python server.py
```

### 客户端连接
```bash
telnet localhost 2323
```

## 游戏命令

- `LOGIN <昵称>` - 登录游戏
- `LOOK` - 查看当前房间
- `GO N/S/E/W` - 移动方向
- `SAY <内容>` - 房间内发言
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
└── persist/           # 数据持久化
```

## 开发状态

- [x] 项目架构设计
- [ ] 核心服务器框架
- [ ] 世界系统
- [ ] 玩家系统
- [ ] 任务系统
- [ ] 战斗系统
- [ ] 社交系统
- [ ] 数据持久化
- [ ] 客户端优化
