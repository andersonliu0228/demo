#!/bin/bash
set -e

echo "等待 PostgreSQL 啟動..."
while ! pg_isready -h $POSTGRES_HOST -p 5432 -U $POSTGRES_USER; do
  sleep 1
done

echo "PostgreSQL 已就緒"

echo "執行資料庫遷移..."
alembic upgrade head

echo "啟動應用程式..."
exec "$@"
