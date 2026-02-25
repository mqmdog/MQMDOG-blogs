#!/bin/bash
# Django 项目部署脚本
# 使用方法: bash deploy.sh

echo "=========================================="
echo "  Django 项目自动化部署脚本"
echo "=========================================="

# 1. 更新系统
echo "[1/12] 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装 Python 和 pip
echo "[2/12] 安装 Python 和相关工具..."
sudo apt install -y python3 python3-pip python3-venv git

# 3. 安装 MySQL
echo "[3/12] 安装 MySQL..."
sudo apt install -y mysql-server

# 4. 启动 MySQL
echo "[4/12] 启动 MySQL 服务..."
sudo service mysql start

# 5. 创建数据库
echo "[5/12] 创建数据库..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS xhc_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'xhc_user'@'localhost' IDENTIFIED BY 'your-strong-password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON xhc_db.* TO 'xhc_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# 6. 创建项目目录
echo "[6/12] 创建项目目录..."
sudo mkdir -p /var/www/django_project
cd /var/www/django_project

# 7. 上传项目（需要手动或使用 git）
echo "[7/12] 请将项目文件上传到 /var/www/django_project/"
echo "可以使用: scp -r ./DjangoProject_xhc_blog/* user@server:/var/www/django_project/"

# 8. 创建虚拟环境
echo "[8/12] 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 9. 安装依赖
echo "[9/12] 安装 Python 依赖..."
pip install django mysqlclient gunicorn

# 10. 配置环境变量
echo "[10/12] 配置环境变量..."
cp .env.example .env
# 编辑 .env 文件设置正确的值

# 11. 收集静态文件
echo "[11/12] 收集静态文件..."
export DJANGO_SETTINGS_MODULE=DjangoProject_xhc_blog.settings_production
python manage.py collectstatic --noinput

# 12. 执行数据库迁移
echo "[12/12] 执行数据库迁移..."
python manage.py migrate

# 13. 配置 Gunicorn
echo "配置 Gunicorn..."
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon for Django project
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/django_project
Environment="PATH=/var/www/django_project/venv/bin"
ExecStart=/var/www/django_project/venv/bin/gunicorn --workers 3 --bind unix:/var/www/django_project/gunicorn.sock DjangoProject_xhc_blog.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# 14. 配置 Nginx
sudo tee /etc/nginx/sites-available/django_project > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /var/www/django_project/staticfiles/;
    }

    location /media/ {
        alias /var/www/django_project/media/;
    }

    location / {
        proxy_pass http://unix:/var/www/django_project/gunicorn.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启用站点
sudo ln -s /etc/nginx/sites-available/django_project /etc/nginx/sites-enabled/
sudo nginx -t

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl restart nginx

echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo "访问 http://your-domain.com 查看网站"
