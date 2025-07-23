# 🎭 Anonymous Chat Telegram Bot

Bot Telegram canggih untuk chat anonim dengan fitur lengkap, multi-bahasa, dan sistem matching yang sophisticated.

## ✨ Fitur Utama

### 🌟 Core Features
- **Chat Anonim**: Chat dengan stranger secara anonim dan aman
- **Multi-Language**: Mendukung bahasa Indonesia, English, dan Español
- **Smart Matching**: Algoritma matching berdasarkan preferensi dan interest
- **Media Support**: Kirim foto, video, voice notes, sticker, dan dokumen
- **Real-time**: Pesan langsung diteruskan tanpa delay

### 👑 VIP System
- **Priority Matching**: VIP users mendapat prioritas dalam matching
- **Advanced Filters**: Filter berdasarkan age, gender, interests
- **Enhanced Privacy**: Fitur privasi tambahan untuk VIP
- **Detailed Stats**: Statistik lengkap aktivitas chat

### 🛡️ Safety & Moderation
- **Report System**: User bisa report partner yang tidak pantas
- **Auto-ban**: Sistem otomatis ban user dengan banyak report
- **Admin Panel**: Panel admin lengkap untuk moderasi
- **Blacklist**: Sistem banned users yang persistent

### 📊 Advanced Features
- **Queue System**: Lihat posisi antrian saat mencari partner
- **Ice Breakers**: Saran pembuka percakapan
- **Statistics**: Tracking lengkap aktivitas user
- **Preferences**: Set preferensi age, gender, interests
- **Activity Tracking**: Monitor waktu online dan statistik chat

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ 
- NPM atau Yarn
- Bot Token dari BotFather

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/annisa48/anonymous_chat.git
cd anonymous-chat
```

2. **Install Dependencies**
```bash
npm install
```

3. **Configuration**
```javascript
// Edit bot.js
const BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE';  // Ganti dengan token bot Anda
const adminIds = new Set([123456789]);    // Ganti dengan Telegram ID admin
```

4. **Start Bot**
```bash
npm start
```

## 📋 Commands

### User Commands
```
/start - Mulai menggunakan bot
/help - Bantuan dan panduan
/next - Cari partner baru (saat chat)
/stop - Berhenti chat
/stats - Lihat statistik personal
/mystats - Statistik detail
/queue - Lihat posisi antrian
/icebreaker - Saran pembuka percakapan
/funfact - Fun facts random
/vip - Info membership VIP
/interests tag1,tag2,tag3 - Set interests
/gender male/female/any - Set preferensi gender  
/age 18-25 - Set preferensi umur
/feedback pesan - Kirim feedback ke admin
```

### Admin Commands
```
/admin_ban [user_id] - Ban user
/admin_unban [user_id] - Unban user
/admin_broadcast [message] - Broadcast ke semua user
```

## 🌍 Multi-Language Support

Bot mendukung 3 bahasa:
- 🇺🇸 **English** (en)
- 🇮🇩 **Bahasa Indonesia** (id) 
- 🇪🇸 **Español** (es)

User bisa ganti bahasa kapan saja melalui menu settings.

## ⚙️ Configuration

### Environment Variables (Opsional)
```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321
DEBUG=true
PORT=3000
```

### Bot Settings
```javascript
// Kustomisasi di bot.js
const inactiveThreshold = 30 * 60 * 1000;  // 30 menit
const chatTimeout = 2 * 60 * 60 * 1000;    // 2 jam
const maxReports = 3;                       // Max reports sebelum auto-ban
const maxInterests = 10;                    // Max interests per user
```

## 🏗️ Architecture

```
bot.js (Main file)
├── User Class - Manajemen data user
├── Language System - Multi-language support
├── Matching Algorithm - Smart partner matching
├── Admin Panel - Moderasi dan statistik
├── Safety System - Report dan ban system
├── VIP System - Premium features
└── Data Persistence - Auto-save ke JSON
```

## 📊 Database Structure

Data disimpan dalam file JSON (untuk production gunakan database):
```javascript
{
  "users": [
    {
      "id": 123456789,
      "username": "user123",
      "language": "id",
      "reputation": 4.5,
      "totalChats": 15,
      "isVip": false,
      "preferences": {
        "ageRange": [20, 30],
        "gender": "any",
        "interests": ["musik", "film"]
      }
    }
  ],
  "bannedUsers": [987654321]
}
```

## 🔧 Hosting Options

### 1. **VPS/Dedicated Server**
```bash
# Install PM2 untuk production
npm install -g pm2
pm2 start bot.js --name "anonymous-bot"
pm2 startup
pm2 save
```

### 2. **Heroku**
```bash
# Procfile
web: node bot.js

# Deploy
heroku create your-bot-name
git push heroku main
```

### 3. **Railway**
```bash
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "node bot.js"
  }
}
```

### 4. **DigitalOcean App Platform**
- Upload source code
- Set environment variables
- Deploy dengan 1-click

## 📈 Monitoring

### Built-in Stats
- Total users registered
- Active chats
- Waiting queue length
- Banned users count
- Messages sent
- Average session time

### Logging
Bot mencatat semua aktivitas penting:
```javascript
// Custom logging bisa ditambahkan
console.log(`User ${userId} started chat with ${partnerId}`);
console.log(`Total active chats: ${activeChats.size}`);
```

## 🛡️ Security Features

1. **Input Validation**: Semua input user divalidasi
2. **Rate Limiting**: Mencegah spam dan abuse
3. **Report System**: User bisa report behavior tidak pantas
4. **Auto-ban**: Sistem otomatis ban berdasarkan reports
5. **Admin Monitoring**: Panel admin untuk monitoring

## 🔄 Updates & Maintenance

### Auto-cleanup System
- Inactive users dihapus dari queue setiap 5 menit
- Chat timeout otomatis setelah 2 jam
- Data auto-save setiap 10 menit

### Backup
```bash
# Auto backup data (tambahkan ke crontab)
0 2 * * * cp /path/to/bot_data.json /path/to/backup/bot_data_$(date +\%Y\%m\%d).json
```

## 🐛 Troubleshooting

### Common Issues

**Bot tidak respond:**
```bash
# Check process
pm2 status
# Check logs  
pm2 logs anonymous-bot
```

**Database issues:**
```bash
# Reset data (WARNING: akan hapus semua data)
rm bot_data.json
# Restart bot
pm2 restart anonymous-bot
```

**Memory issues:**
```bash
# Monitor memory
pm2 monit
# Set memory limit
pm2 start bot.js --max-memory-restart 500M
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

Distributed under MIT License. See `LICENSE` for more information.

## 🙋‍♂️ Support

- **Issues**: [GitHub Issues](https://github.com/annisa48/anonymous_chat/issues)
- **Telegram**: @annisa401
- **Email**: annisa48@gmail.com

## 🎯 Roadmap

### V2.1 (Coming Soon)
- [ ] Voice/Video call support
- [ ] Group chat rooms  
- [ ] Games integration
- [ ] AI chatbot integration
- [ ] Cryptocurrency payments

### V2.2 (Future)
- [ ] Mobile app
- [ ] Web dashboard
- [ ] Advanced analytics
- [ ] Machine learning recommendations

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
git clone https://github.com/annisa48/anonymous_chat.git
cd anonymous-chat

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
git clone https://github.com/annisa48/anonymous_chat.git
cd anonymous-chat

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
---
