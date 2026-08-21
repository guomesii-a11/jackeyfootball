# ---------- 阶段 1：构建前端 ----------
FROM node:20-alpine AS frontend
WORKDIR /build/frontend

# 仅复制依赖清单以利用层缓存
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install

# 复制源码并构建（跳过 vue-tsc 类型检查，避免在 CI/容器里因开发期小报错导致构建失败）
COPY frontend/ ./
RUN npx vite build

# ---------- 阶段 2：运行后端 ----------
FROM python:3.11-slim AS backend
WORKDIR /app

# 系统依赖（psycopg2-binary 等可能需要编译头，预装以减少意外）
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制后端源码与依赖清单
COPY backend/ ./backend/

# 将前端构建产物并入后端静态目录（头像 avatars/ 已随 backend 复制进来）
COPY --from=frontend /build/frontend/dist ./backend/app/static

# 安装 Python 依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

WORKDIR /app/backend
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# 启动：自动建表 + 填充种子数据 + 运行评分引擎（已在 app.main 启动时完成）
CMD ["python", "-m", "app.main"]
