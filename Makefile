# 《终端·回响》游戏服务器 Docker 构建脚本
# 使用方法: make <target>

# 变量定义
IMAGE_NAME = teletype-city
IMAGE_TAG = latest
CONTAINER_NAME = teletype-city-server
REGISTRY = localhost:5000
FULL_IMAGE_NAME = $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

# 默认目标
.DEFAULT_GOAL := help

# 帮助信息
.PHONY: help
help:
	@echo "《终端·回响》游戏服务器 Docker 构建脚本"
	@echo "=========================================="
	@echo ""
	@echo "可用命令:"
	@echo "  make build          - 构建Docker镜像"
	@echo "  make run            - 运行Docker容器"
	@echo "  make stop           - 停止Docker容器"
	@echo "  make restart        - 重启Docker容器"
	@echo "  make logs           - 查看容器日志"
	@echo "  make shell          - 进入容器shell"
	@echo "  make clean          - 清理容器和镜像"
	@echo "  make push           - 推送到本地镜像仓库"
	@echo "  make pull           - 从本地镜像仓库拉取"
	@echo "  make test           - 测试Docker容器"
	@echo "  make backup         - 备份游戏数据"
	@echo "  make restore        - 恢复游戏数据"
	@echo "  make deploy         - 部署到生产环境"
	@echo "  make monitor        - 监控容器状态"
	@echo ""

# 构建Docker镜像
.PHONY: build
build:
	@echo "正在构建Docker镜像..."
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "镜像构建完成: $(IMAGE_NAME):$(IMAGE_TAG)"

# 运行Docker容器
.PHONY: run
run:
	@echo "正在启动Docker容器..."
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p 2323:2323 \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/logs:/app/logs \
		-v $(PWD)/backups:/app/backups \
		--restart unless-stopped \
		$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "容器启动完成，游戏服务器运行在端口 2323"

# 停止Docker容器
.PHONY: stop
stop:
	@echo "正在停止Docker容器..."
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	@echo "容器已停止并删除"

# 重启Docker容器
.PHONY: restart
restart: stop run
	@echo "容器重启完成"

# 查看容器日志
.PHONY: logs
logs:
	@echo "查看容器日志 (Ctrl+C 退出):"
	docker logs -f $(CONTAINER_NAME)

# 进入容器shell
.PHONY: shell
shell:
	@echo "进入容器shell..."
	docker exec -it $(CONTAINER_NAME) /bin/bash

# 清理容器和镜像
.PHONY: clean
clean:
	@echo "正在清理..."
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) || true
	docker system prune -f
	@echo "清理完成"

# 推送到本地镜像仓库
.PHONY: push
push:
	@echo "正在推送到本地镜像仓库..."
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(FULL_IMAGE_NAME)
	docker push $(FULL_IMAGE_NAME)
	@echo "推送完成: $(FULL_IMAGE_NAME)"

# 从本地镜像仓库拉取
.PHONY: pull
pull:
	@echo "正在从本地镜像仓库拉取..."
	docker pull $(FULL_IMAGE_NAME)
	docker tag $(FULL_IMAGE_NAME) $(IMAGE_NAME):$(IMAGE_TAG)
	@echo "拉取完成"

# 测试Docker容器
.PHONY: test
test:
	@echo "正在测试Docker容器..."
	@echo "1. 构建镜像..."
	$(MAKE) build
	@echo "2. 启动容器..."
	$(MAKE) run
	@echo "3. 等待服务启动..."
	sleep 10
	@echo "4. 测试连接..."
	python3 test_telnet.py || echo "测试失败，请检查容器状态"
	@echo "5. 清理测试环境..."
	$(MAKE) stop
	@echo "测试完成"

# 备份游戏数据
.PHONY: backup
backup:
	@echo "正在备份游戏数据..."
	mkdir -p backups
	tar -czf backups/game_data_$(shell date +%Y%m%d_%H%M%S).tar.gz data/ logs/
	@echo "备份完成"

# 恢复游戏数据
.PHONY: restore
restore:
	@echo "请选择要恢复的备份文件:"
	@ls -la backups/
	@echo "使用方法: make restore-backup BACKUP_FILE=backups/filename.tar.gz"
	@echo "注意: 恢复前请先停止容器"

# 恢复指定的备份文件
.PHONY: restore-backup
restore-backup:
ifndef BACKUP_FILE
	@echo "错误: 请指定备份文件"
	@echo "使用方法: make restore-backup BACKUP_FILE=backups/filename.tar.gz"
	@exit 1
endif
	@echo "正在恢复备份: $(BACKUP_FILE)"
	tar -xzf $(BACKUP_FILE)
	@echo "恢复完成"

# 部署到生产环境
.PHONY: deploy
deploy:
	@echo "正在部署到生产环境..."
	@echo "1. 构建生产镜像..."
	$(MAKE) build
	@echo "2. 停止现有容器..."
	$(MAKE) stop
	@echo "3. 启动新容器..."
	$(MAKE) run
	@echo "4. 等待服务启动..."
	sleep 10
	@echo "5. 检查服务状态..."
	docker ps | grep $(CONTAINER_NAME)
	@echo "部署完成！"

# 监控容器状态
.PHONY: monitor
monitor:
	@echo "容器状态监控 (每5秒刷新，Ctrl+C 退出):"
	@while true; do \
		echo "=== $(shell date) ==="; \
		docker ps | grep $(CONTAINER_NAME) || echo "容器未运行"; \
		docker stats --no-stream $(CONTAINER_NAME) 2>/dev/null || echo "无法获取容器统计信息"; \
		echo "端口检查:"; \
		netstat -tlnp 2>/dev/null | grep :2323 || echo "端口2323未监听"; \
		echo "=================="; \
		sleep 5; \
	done

# 开发环境快速构建
.PHONY: dev
dev:
	@echo "开发环境快速构建..."
	docker build -t $(IMAGE_NAME):dev .
	docker run -d \
		--name $(CONTAINER_NAME)-dev \
		-p 2324:2323 \
		-v $(PWD):/app \
		--restart unless-stopped \
		$(IMAGE_NAME):dev
	@echo "开发容器启动完成，端口 2324"

# 生产环境构建
.PHONY: prod
prod:
	@echo "生产环境构建..."
	docker build \
		--build-arg BUILD_ENV=production \
		--build-arg VERSION=$(shell git describe --tags --always 2>/dev/null || echo "dev") \
		-t $(IMAGE_NAME):prod .
	@echo "生产镜像构建完成"

# 多架构构建
.PHONY: multiarch
multiarch:
	@echo "多架构构建 (需要启用buildx)..."
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-t $(IMAGE_NAME):$(IMAGE_TAG) \
		--push .
	@echo "多架构镜像构建完成"

# 安全扫描
.PHONY: scan
scan:
	@echo "正在扫描镜像安全漏洞..."
	docker run --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PWD):/workspace \
		--workdir /workspace \
		-aquasec/trivy image $(IMAGE_NAME):$(IMAGE_TAG)
	@echo "安全扫描完成"

# 性能测试
.PHONY: benchmark
benchmark:
	@echo "正在运行性能测试..."
	@echo "1. 启动测试容器..."
	$(MAKE) run
	@echo "2. 等待服务启动..."
	sleep 10
	@echo "3. 运行负载测试..."
	python3 -c "
import asyncio
import time
import socket

async def test_connection():
    start_time = time.time()
    try:
        reader, writer = await asyncio.open_connection('localhost', 2323)
        writer.write(b'LOGIN testuser\n')
        await writer.drain()
        data = await reader.readline()
        writer.close()
        await writer.wait_closed()
        return time.time() - start_time
    except Exception as e:
        return None

async def run_benchmark():
    times = []
    for i in range(10):
        t = await test_connection()
        if t:
            times.append(t)
            print(f'连接 {i+1}: {t:.3f}s')
        else:
            print(f'连接 {i+1}: 失败')
    
    if times:
        avg_time = sum(times) / len(times)
        print(f'平均响应时间: {avg_time:.3f}s')
        print(f'最快响应时间: {min(times):.3f}s')
        print(f'最慢响应时间: {max(times):.3f}s')

asyncio.run(run_benchmark())
"
	@echo "4. 清理测试环境..."
	$(MAKE) stop
	@echo "性能测试完成"

# 显示容器信息
.PHONY: info
info:
	@echo "容器信息:"
	@echo "镜像: $(IMAGE_NAME):$(IMAGE_TAG)"
	@echo "容器名: $(CONTAINER_NAME)"
	@echo "端口: 2323"
	@echo ""
	@echo "当前状态:"
	docker ps -a | grep $(CONTAINER_NAME) || echo "容器不存在"
	@echo ""
	@echo "镜像信息:"
	docker images | grep $(IMAGE_NAME) || echo "镜像不存在"

# 清理所有相关资源
.PHONY: clean-all
clean-all:
	@echo "正在清理所有相关资源..."
	docker stop $(CONTAINER_NAME) $(CONTAINER_NAME)-dev || true
	docker rm $(CONTAINER_NAME) $(CONTAINER_NAME)-dev || true
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) $(IMAGE_NAME):dev $(IMAGE_NAME):prod || true
	docker system prune -af
	@echo "所有资源清理完成"

# 显示使用说明
.PHONY: usage
usage:
	@echo "《终端·回响》Docker 使用说明"
	@echo "============================"
	@echo ""
	@echo "快速开始:"
	@echo "  make build && make run    # 构建并运行"
	@echo "  make test                 # 完整测试流程"
	@echo "  make deploy               # 生产环境部署"
	@echo ""
	@echo "日常操作:"
	@echo "  make logs                 # 查看日志"
	@echo "  make restart              # 重启服务"
	@echo "  make backup               # 备份数据"
	@echo ""
	@echo "开发调试:"
	@echo "  make dev                  # 开发环境"
	@echo "  make shell                # 进入容器"
	@echo "  make monitor              # 监控状态"
