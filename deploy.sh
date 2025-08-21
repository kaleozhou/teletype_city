#!/bin/bash
# 部署脚本

echo "开始部署《终端·回响》游戏服务器..."

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "检测到Python版本: $python_version"

# 安装依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p data backups logs

# 设置权限
echo "设置文件权限..."
chmod +x start_server.py
chmod +x test_client.py

# 创建systemd服务文件
echo "创建systemd服务文件..."
sudo tee /etc/systemd/system/teletype-city.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=终端回响游戏服务器
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 start_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# 重新加载systemd
echo "重新加载systemd配置..."
sudo systemctl daemon-reload

# 启用服务
echo "启用服务..."
sudo systemctl enable teletype-city.service

echo "部署完成！"
echo ""
echo "使用方法："
echo "  启动服务: sudo systemctl start teletype-city"
echo "  停止服务: sudo systemctl stop teletype-city"
echo "  查看状态: sudo systemctl status teletype-city"
echo "  查看日志: sudo journalctl -u teletype-city -f"
echo ""
echo "玩家可以通过以下命令连接："
echo "  telnet localhost 2323"
