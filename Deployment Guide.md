# 🚀 Complete Deployment Guide - Anonymous Chat Bot

Panduan lengkap untuk deploy bot Telegram Anonymous Chat dengan berbagai platform hosting.

## 📋 Daftar Isi

1. [Persiapan](#persiapan)
2. [VPS/Dedicated Server](#vpsdedicated-server)
3. [Heroku Deployment](#heroku-deployment)
4. [Railway Deployment](#railway-deployment)
5. [DigitalOcean App Platform](#digitalocean-app-platform)
6. [Docker Deployment](#docker-deployment)
7. [AWS EC2](#aws-ec2)
8. [Google Cloud Platform](#google-cloud-platform)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

## 🛠️ Persiapan

### 1. Buat Bot Telegram
```
1. Chat dengan @BotFather di Telegram
2. Ketik /newbot
3. Berikan nama bot (contoh: "My Anonymous Chat Bot")
4. Berikan username bot (contoh: "my_anon_chat_bot")
5. Simpan token yang diberikan
```

### 2. Dapatkan Telegram ID Anda
```
1. Chat dengan @userinfobot di Telegram
2. Bot akan memberikan Telegram ID Anda
3. Catat ID ini untuk dijadikan admin
```

### 3. Persiapkan File
```bash
# Clone atau download source code
git clone https://github.com/your-username/anonymous-chat-bot.git
cd anonymous-chat-bot

# Edit konfigurasi
nano bot.js
# Ganti BOT_TOKEN dengan token bot Anda
# Tambahkan Telegram ID Anda ke adminIds
```

## 🖥️ VPS/Dedicated Server

### Ubuntu/Debian

#### 1. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2
sudo npm install -g pm2

# Install nginx (optional, for reverse proxy)
sudo apt install nginx -y
```

#### 2. Setup Bot
```bash
# Create user for bot
sudo adduser botuser
sudo usermod -aG sudo botuser
su - botuser

# Upload bot files
git clone https://github.com/your-username/anonymous-chat-bot.git
cd anonymous-chat-bot

# Install dependencies
npm install

# Make scripts executable
chmod +x *.sh

# Start bot
./start.sh
```

#### 3. Setup Auto-start
```bash
# Setup PM2 startup
pm2 startup
# Copy and run the command shown

# Save PM2 configuration
pm2 save
```

#### 4. Setup Nginx (Optional)
```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/bot

# Add configuration (see nginx.conf in files)

# Enable site
sudo ln -s /etc/nginx/sites-available/bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### CentOS/RHEL/Rocky Linux

#### 1. Install Dependencies
```bash
# Update system
sudo dnf update -y

# Install Node.js
sudo dnf module install nodejs:
