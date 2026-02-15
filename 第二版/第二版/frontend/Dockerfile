# 多階段構建
# 階段 1: 構建階段
FROM node:18-alpine AS builder

WORKDIR /app

# 複製 package.json
COPY package*.json ./

# 安裝依賴
RUN npm install

# 複製源代碼
COPY . .

# 構建生產版本
RUN npm run build

# 階段 2: 生產階段
FROM nginx:alpine

# 複製構建產物到 nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 複製 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 啟動 nginx
CMD ["nginx", "-g", "daemon off;"]
