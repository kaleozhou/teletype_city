# 《终端·回响》Docker 部署指南

## 🐳 快速开始

### 1. 构建镜像
```bash
make build
```

### 2. 运行容器
```bash
make run
```

### 3. 测试连接
```bash
telnet localhost 2323
```

## 📋 可用命令

### 基础操作
- `make build` - 构建Docker镜像
- `make run` - 运行Docker容器
- `make stop` - 停止Docker容器
- `make restart` - 重启Docker容器
- `make logs` - 查看容器日志
- `make shell` - 进入容器shell

### 高级操作
- `make test` - 完整测试流程
- `make deploy` - 生产环境部署
- `make backup` - 备份游戏数据
- `make restore` - 恢复游戏数据
- `make monitor` - 监控容器状态
- `make clean` - 清理资源

### 开发环境
- `make dev` - 开发环境容器
- `make prod` - 生产环境构建
- `make multiarch` - 多架构构建

## 🚀 使用Docker Compose

### 启动服务
```bash
# 启动生产环境
docker-compose up -d

# 启动开发环境
docker-compose --profile dev up -d

# 启动监控服务
docker-compose --profile monitoring up -d
```

### 停止服务
```bash
docker-compose down
```

### 查看日志
```bash
docker-compose logs -f teletype-city
```

## 🔧 配置说明

### 环境变量
- `GAME_PORT` - 游戏服务器端口 (默认: 2323)
- `PYTHONUNBUFFERED` - Python输出缓冲 (默认: 1)
- `ENVIRONMENT` - 运行环境 (development/production)

### 端口映射
- 2323 - 游戏服务器端口
- 2324 - 开发环境端口
- 3000 - 监控服务端口 (可选)

### 数据卷挂载
- `./data` → `/app/data` - 游戏数据
- `./logs` → `/app/logs` - 日志文件
- `./backups` → `/app/backups` - 备份文件

## 📊 监控和维护

### 健康检查
容器包含健康检查，每30秒检查一次服务状态。

### 日志管理
```bash
# 查看实时日志
make logs

# 查看历史日志
docker logs teletype-city-server

# 导出日志
docker logs teletype-city-server > game_server.log
```

### 数据备份
```bash
# 创建备份
make backup

# 恢复备份
make restore-backup BACKUP_FILE=backups/filename.tar.gz
```

## 🛠️ 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   lsof -i :2323
   
   # 停止占用进程
   sudo lsof -ti:2323 | xargs kill -9
   ```

2. **容器启动失败**
   ```bash
   # 查看容器状态
   docker ps -a
   
   # 查看启动日志
   docker logs teletype-city-server
   ```

3. **权限问题**
   ```bash
   # 修复数据目录权限
   sudo chown -R $USER:$USER data/ logs/ backups/
   ```

### 调试命令
```bash
# 进入容器调试
make shell

# 查看容器资源使用
docker stats teletype-city-server

# 检查网络连接
docker exec teletype-city-server netstat -tlnp
```

## 🔒 安全考虑

### 生产环境
- 使用非root用户运行
- 限制容器资源使用
- 定期更新基础镜像
- 启用安全扫描

### 网络安全
- 只暴露必要端口
- 使用内部网络通信
- 配置防火墙规则

## 📈 性能优化

### 资源限制
```bash
docker run -d \
  --name teletype-city \
  --memory=512m \
  --cpus=1.0 \
  -p 2323:2323 \
  teletype-city:latest
```

### 监控指标
- CPU使用率
- 内存使用量
- 网络I/O
- 磁盘I/O

## 🚀 部署流程

### 开发环境
1. `make build` - 构建镜像
2. `make dev` - 启动开发容器
3. `make test` - 运行测试
4. `make stop` - 停止容器

### 生产环境
1. `make build` - 构建镜像
2. `make deploy` - 部署服务
3. `make monitor` - 监控状态
4. `make backup` - 定期备份

### 持续集成
```bash
# 自动化测试
make test

# 安全扫描
make scan

# 性能测试
make benchmark
```

## 📚 更多资源

- [Docker官方文档](https://docs.docker.com/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [Python Docker最佳实践](https://docs.docker.com/language/python/)

---

**现在您可以使用Docker轻松部署《终端·回响》游戏服务器了！** 🎮🐳
