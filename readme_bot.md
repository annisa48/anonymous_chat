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
git clone https://github.com/your-username/anonymous-chat-bot.git
cd anonymous-chat-bot
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

- **Issues**: [GitHub Issues](https://github.com/your-username/anonymous-chat-bot/issues)
- **Telegram**: @yourusername
- **Email**: your.email@example.com

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

---

**Made with ❤️ for the Telegram community**

> ⚠️ **Disclaimer**: Bot ini untuk tujuan edukasi. Pastikan mematuhi Terms of Service Telegram dan hukum setempat.
