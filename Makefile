# 《终端·回响》游戏服务器 Docker 构建脚本

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
	@echo "  make test           - 测试Docker容器"
	@echo "  make backup         - 备份游戏数据"
	@echo "  make info           - 显示容器信息"

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

# 显示使用说明
.PHONY: usage
usage:
	@echo "《终端·回响》Docker 使用说明"
	@echo "============================"
	@echo ""
	@echo "快速开始:"
	@echo "  make build && make run    # 构建并运行"
	@echo "  make test                 # 完整测试流程"
	@echo ""
	@echo "日常操作:"
	@echo "  make logs                 # 查看日志"
	@echo "  make restart              # 重启服务"
	@echo "  make backup               # 备份数据"
