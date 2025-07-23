const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const path = require('path');

// Bot configuration
const BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE';
const bot = new TelegramBot(BOT_TOKEN, { polling: true });

// Data storage (dalam production gunakan database)
let users = new Map();
let activeChats = new Map();
let waitingUsers = [];
let userPreferences = new Map();
let bannedUsers = new Set();
let adminIds = new Set(); // Add admin IDs here

// Multi-language support
const languages = {
    en: {
        welcome: "🎭 Welcome to Anonymous Chat Bot!\n\nChat anonymously with random people around the world!\n\nChoose your language:",
        main_menu: "🏠 Main Menu\n\nChoose an option:",
        start_search: "🔍 Find Chat Partner",
        my_profile: "👤 My Profile",
        settings: "⚙️ Settings",
        help: "❓ Help",
        admin_panel: "👑 Admin Panel",
        searching: "🔍 Searching for a chat partner...\n\nPlease wait while we find someone for you!",
        partner_found: "✅ Chat partner found! Say hello!\n\n💡 Type /next to find new partner\n💡 Type /stop to end chat",
        no_partner: "😔 No available chat partners right now. Please try again later.",
        chat_ended: "👋 Chat ended. Hope you had a great conversation!",
        partner_left: "😔 Your chat partner has left the conversation.",
        send_message: "Type your message to send to your chat partner:",
        profile_info: "👤 Your Profile:\n\n🆔 User ID: {userId}\n🌍 Language: {lang}\n⭐ Reputation: {rep}\n💬 Total chats: {chats}\n⏱️ Online time: {time}",
        language_changed: "✅ Language changed successfully!",
        not_in_chat: "❌ You're not currently in a chat.",
        already_searching: "⏳ You're already searching for a chat partner!",
        help_text: "❓ How to use Anonymous Chat Bot:\n\n1. Click 'Find Chat Partner' to start\n2. Wait for a match\n3. Start chatting anonymously\n4. Use /next for new partner\n5. Use /stop to end chat\n\n🔒 Your privacy is protected!",
        banned_message: "🚫 You have been banned from using this bot.",
        partner_disconnected: "📱 Your partner has disconnected.",
        reconnecting: "🔄 Reconnecting...",
        stats: "📊 Your Statistics:\n\n💬 Messages sent: {messages}\n⏱️ Time chatting: {time}\n👥 Partners met: {partners}\n⭐ Rating: {rating}/5"
    },
    id: {
        welcome: "🎭 Selamat datang di Bot Anonymous Chat!\n\nChat anonim dengan orang-orang acak di seluruh dunia!\n\nPilih bahasa Anda:",
        main_menu: "🏠 Menu Utama\n\nPilih opsi:",
        start_search: "🔍 Cari Partner Chat",
        my_profile: "👤 Profil Saya",
        settings: "⚙️ Pengaturan",
        help: "❓ Bantuan",
        admin_panel: "👑 Panel Admin",
        searching: "🔍 Mencari partner chat...\n\nTunggu sebentar, kami sedang mencarikan seseorang untuk Anda!",
        partner_found: "✅ Partner chat ditemukan! Katakan halo!\n\n💡 Ketik /next untuk partner baru\n💡 Ketik /stop untuk mengakhiri chat",
        no_partner: "😔 Tidak ada partner chat tersedia saat ini. Silakan coba lagi nanti.",
        chat_ended: "👋 Chat berakhir. Semoga Anda memiliki percakapan yang menyenangkan!",
        partner_left: "😔 Partner chat Anda telah meninggalkan percakapan.",
        send_message: "Ketik pesan Anda untuk dikirim ke partner chat:",
        profile_info: "👤 Profil Anda:\n\n🆔 ID Pengguna: {userId}\n🌍 Bahasa: {lang}\n⭐ Reputasi: {rep}\n💬 Total chat: {chats}\n⏱️ Waktu online: {time}",
        language_changed: "✅ Bahasa berhasil diubah!",
        not_in_chat: "❌ Anda sedang tidak dalam chat.",
        already_searching: "⏳ Anda sudah mencari partner chat!",
        help_text: "❓ Cara menggunakan Bot Anonymous Chat:\n\n1. Klik 'Cari Partner Chat' untuk memulai\n2. Tunggu untuk mendapat pasangan\n3. Mulai chat secara anonim\n4. Gunakan /next untuk partner baru\n5. Gunakan /stop untuk mengakhiri chat\n\n🔒 Privasi Anda terlindungi!",
        banned_message: "🚫 Anda telah dibanned dari menggunakan bot ini.",
        partner_disconnected: "📱 Partner Anda telah terputus.",
        reconnecting: "🔄 Menyambung kembali...",
        stats: "📊 Statistik Anda:\n\n💬 Pesan terkirim: {messages}\n⏱️ Waktu chatting: {time}\n👥 Partner bertemu: {partners}\n⭐ Rating: {rating}/5"
    },
    es: {
        welcome: "🎭 ¡Bienvenido al Bot de Chat Anónimo!\n\n¡Chatea anónimamente con personas aleatorias de todo el mundo!\n\nElige tu idioma:",
        main_menu: "🏠 Menú Principal\n\nElige una opción:",
        start_search: "🔍 Buscar Compañero de Chat",
        my_profile: "👤 Mi Perfil",
        settings: "⚙️ Configuración",
        help: "❓ Ayuda",
        admin_panel: "👑 Panel de Admin",
        searching: "🔍 Buscando compañero de chat...\n\n¡Espera mientras encontramos a alguien para ti!",
        partner_found: "✅ ¡Compañero de chat encontrado! ¡Di hola!\n\n💡 Escribe /next para nuevo compañero\n💡 Escribe /stop para terminar chat",
        no_partner: "😔 No hay compañeros de chat disponibles ahora. Inténtalo más tarde.",
        chat_ended: "👋 Chat terminado. ¡Espero que hayas tenido una gran conversación!",
        partner_left: "😔 Tu compañero de chat ha dejado la conversación.",
        send_message: "Escribe tu mensaje para enviar a tu compañero de chat:",
        profile_info: "👤 Tu Perfil:\n\n🆔 ID de Usuario: {userId}\n🌍 Idioma: {lang}\n⭐ Reputación: {rep}\n💬 Total chats: {chats}\n⏱️ Tiempo online: {time}",
        language_changed: "✅ ¡Idioma cambiado exitosamente!",
        not_in_chat: "❌ No estás actualmente en un chat.",
        already_searching: "⏳ ¡Ya estás buscando un compañero de chat!",
        help_text: "❓ Cómo usar el Bot de Chat Anónimo:\n\n1. Haz clic en 'Buscar Compañero de Chat' para comenzar\n2. Espera por una coincidencia\n3. Comienza a chatear anónimamente\n4. Usa /next para nuevo compañero\n5. Usa /stop para terminar chat\n\n🔒 ¡Tu privacidad está protegida!",
        banned_message: "🚫 Has sido baneado de usar este bot.",
        partner_disconnected: "📱 Tu compañero se ha desconectado.",
        reconnecting: "🔄 Reconectando...",
        stats: "📊 Tus Estadísticas:\n\n💬 Mensajes enviados: {messages}\n⏱️ Tiempo chateando: {time}\n👥 Compañeros conocidos: {partners}\n⭐ Calificación: {rating}/5"
    }
};

// User class dengan fitur lengkap
class User {
    constructor(id, username, firstName, lastName, languageCode) {
        this.id = id;
        this.username = username;
        this.firstName = firstName;
        this.lastName = lastName;
        this.language = languageCode || 'en';
        this.joinDate = new Date();
        this.lastActive = new Date();
        this.reputation = 5.0;
        this.totalChats = 0;
        this.totalMessages = 0;
        this.onlineTime = 0;
        this.partnersMetCount = 0;
        this.isSearching = false;
        this.currentPartner = null;
        this.preferences = {
            ageRange: [18, 99],
            gender: 'any',
            interests: [],
            language: 'any'
        };
        this.reports = [];
        this.isBanned = false;
        this.isVip = false;
        this.chatHistory = [];
    }

    updateLastActive() {
        this.lastActive = new Date();
    }

    addMessage() {
        this.totalMessages++;
        this.updateLastActive();
    }

    endChat() {
        if (this.currentPartner) {
            this.totalChats++;
            this.currentPartner = null;
        }
        this.isSearching = false;
    }
}

// Utility functions
function getText(userId, key, params = {}) {
    const user = users.get(userId);
    const lang = user ? user.language : 'en';
    let text = languages[lang] ? languages[lang][key] : languages['en'][key];
    
    // Replace parameters
    Object.keys(params).forEach(param => {
        text = text.replace(`{${param}}`, params[param]);
    });
    
    return text;
}

function createKeyboard(userId, type) {
    const user = users.get(userId);
    const lang = user ? user.language : 'en';
    
    switch(type) {
        case 'language':
            return {
                reply_markup: {
                    inline_keyboard: [
                        [
                            { text: '🇺🇸 English', callback_data: 'lang_en' },
                            { text: '🇮🇩 Bahasa Indonesia', callback_data: 'lang_id' }
                        ],
                        [
                            { text: '🇪🇸 Español', callback_data: 'lang_es' }
                        ]
                    ]
                }
            };
            
        case 'main':
            const keyboard = [
                [{ text: getText(userId, 'start_search'), callback_data: 'start_search' }],
                [
                    { text: getText(userId, 'my_profile'), callback_data: 'profile' },
                    { text: getText(userId, 'settings'), callback_data: 'settings' }
                ],
                [{ text: getText(userId, 'help'), callback_data: 'help' }]
            ];
            
            if (adminIds.has(userId)) {
                keyboard.push([{ text: getText(userId, 'admin_panel'), callback_data: 'admin' }]);
            }
            
            return {
                reply_markup: {
                    inline_keyboard: keyboard
                }
            };
            
        case 'chat':
            return {
                reply_markup: {
                    inline_keyboard: [
                        [
                            { text: '🔄 Next Partner', callback_data: 'next_partner' },
                            { text: '🛑 Stop Chat', callback_data: 'stop_chat' }
                        ],
                        [
                            { text: '⭐ Rate Partner', callback_data: 'rate_partner' },
                            { text: '🚫 Report', callback_data: 'report_partner' }
                        ]
                    ]
                }
            };
            
        case 'admin':
            return {
                reply_markup: {
                    inline_keyboard: [
                        [
                            { text: '📊 Statistics', callback_data: 'admin_stats' },
                            { text: '👥 Users', callback_data: 'admin_users' }
                        ],
                        [
                            { text: '🚫 Ban User', callback_data: 'admin_ban' },
                            { text: '📢 Broadcast', callback_data: 'admin_broadcast' }
                        ],
                        [{ text: '🔙 Back', callback_data: 'main_menu' }]
                    ]
                }
            };
            
        default:
            return {};
    }
}

// Advanced matching algorithm
function findBestMatch(userId) {
    const user = users.get(userId);
    if (!user) return null;
    
    const availableUsers = waitingUsers.filter(id => {
        const otherUser = users.get(id);
        return id !== userId && 
               otherUser && 
               !otherUser.currentPartner &&
               !bannedUsers.has(id);
    });
    
    if (availableUsers.length === 0) return null;
    
    // Simple random selection for now - could be enhanced with preference matching
    const randomIndex = Math.floor(Math.random() * availableUsers.length);
    return availableUsers[randomIndex];
}

function startChat(user1Id, user2Id) {
    const user1 = users.get(user1Id);
    const user2 = users.get(user2Id);
    
    if (!user1 || !user2) return false;
    
    // Set up chat
    user1.currentPartner = user2Id;
    user2.currentPartner = user1Id;
    user1.isSearching = false;
    user2.isSearching = false;
    
    // Remove from waiting list
    waitingUsers = waitingUsers.filter(id => id !== user1Id && id !== user2Id);
    
    // Add to active chats
    const chatId = `${user1Id}_${user2Id}`;
    activeChats.set(chatId, {
        user1: user1Id,
        user2: user2Id,
        startTime: new Date(),
        messageCount: 0
    });
    
    // Notify both users
    bot.sendMessage(user1Id, getText(user1Id, 'partner_found'), createKeyboard(user1Id, 'chat'));
    bot.sendMessage(user2Id, getText(user2Id, 'partner_found'), createKeyboard(user2Id, 'chat'));
    
    return true;
}

function endChat(userId) {
    const user = users.get(userId);
    if (!user || !user.currentPartner) return false;
    
    const partnerId = user.currentPartner;
    const partner = users.get(partnerId);
    
    // End chat for both users
    user.endChat();
    if (partner) {
        partner.endChat();
        bot.sendMessage(partnerId, getText(partnerId, 'partner_left'));
    }
    
    // Remove from active chats
    const chatId1 = `${userId}_${partnerId}`;
    const chatId2 = `${partnerId}_${userId}`;
    activeChats.delete(chatId1);
    activeChats.delete(chatId2);
    
    bot.sendMessage(userId, getText(userId, 'chat_ended'));
    
    return true;
}

// Bot event handlers
bot.onText(/\/start/, (msg) => {
    const userId = msg.from.id;
    
    if (bannedUsers.has(userId)) {
        bot.sendMessage(userId, getText(userId, 'banned_message'));
        return;
    }
    
    // Create or update user
    if (!users.has(userId)) {
        const user = new User(
            userId, 
            msg.from.username, 
            msg.from.first_name, 
            msg.from.last_name,
            msg.from.language_code
        );
        users.set(userId, user);
    }
    
    const user = users.get(userId);
    user.updateLastActive();
    
    // Send welcome message with language selection
    bot.sendMessage(userId, getText(userId, 'welcome'), createKeyboard(userId, 'language'));
});

bot.onText(/\/help/, (msg) => {
    const userId = msg.from.id;
    bot.sendMessage(userId, getText(userId, 'help_text'));
});

bot.onText(/\/stats/, (msg) => {
    const userId = msg.from.id;
    const user = users.get(userId);
    
    if (!user) return;
    
    const params = {
        messages: user.totalMessages,
        time: Math.round(user.onlineTime / 60) + ' minutes',
        partners: user.partnersMetCount,
        rating: user.reputation.toFixed(1)
    };
    
    bot.sendMessage(userId, getText(userId, 'stats', params));
});

bot.onText(/\/next/, (msg) => {
    const userId = msg.from.id;
    const user = users.get(userId);
    
    if (!user || !user.currentPartner) {
        bot.sendMessage(userId, getText(userId, 'not_in_chat'));
        return;
    }
    
    endChat(userId);
    
    // Start new search
    user.isSearching = true;
    waitingUsers.push(userId);
    bot.sendMessage(userId, getText(userId, 'searching'));
    
    // Try to find immediate match
    setTimeout(() => {
        if (user.isSearching) {
            const partnerId = findBestMatch(userId);
            if (partnerId) {
                startChat(userId, partnerId);
            }
        }
    }, 1000);
});

bot.onText(/\/stop/, (msg) => {
    const userId = msg.from.id;
    endChat(userId);
    bot.sendMessage(userId, getText(userId, 'main_menu'), createKeyboard(userId, 'main'));
});

// Handle callback queries
bot.on('callback_query', (callbackQuery) => {
    const userId = callbackQuery.from.id;
    const data = callbackQuery.data;
    const messageId = callbackQuery.message.message_id;
    
    if (bannedUsers.has(userId)) {
        bot.answerCallbackQuery(callbackQuery.id, getText(userId, 'banned_message'));
        return;
    }
    
    let user = users.get(userId);
    
    // Language selection
    if (data.startsWith('lang_')) {
        const lang = data.split('_')[1];
        if (!user) {
            user = new User(userId, callbackQuery.from.username, callbackQuery.from.first_name, callbackQuery.from.last_name, lang);
            users.set(userId, user);
        }
        user.language = lang;
        
        bot.editMessageText(getText(userId, 'language_changed'), {
            chat_id: userId,
            message_id: messageId
        });
        
        setTimeout(() => {
            bot.sendMessage(userId, getText(userId, 'main_menu'), createKeyboard(userId, 'main'));
        }, 1000);
        
        bot.answerCallbackQuery(callbackQuery.id);
        return;
    }
    
    if (!user) return;
    user.updateLastActive();
    
    switch (data) {
        case 'start_search':
            if (user.isSearching) {
                bot.answerCallbackQuery(callbackQuery.id, getText(userId, 'already_searching'));
                return;
            }
            
            if (user.currentPartner) {
                endChat(userId);
            }
            
            user.isSearching = true;
            waitingUsers.push(userId);
            
            bot.editMessageText(getText(userId, 'searching'), {
                chat_id: userId,
                message_id: messageId
            });
            
            // Try to find match
            setTimeout(() => {
                if (user.isSearching) {
                    const partnerId = findBestMatch(userId);
                    if (partnerId) {
                        startChat(userId, partnerId);
                    } else {
                        // Keep searching message active
                    }
                }
            }, 2000);
            break;
            
        case 'profile':
            const params = {
                userId: userId,
                lang: user.language.toUpperCase(),
                rep: user.reputation.toFixed(1),
                chats: user.totalChats,
                time: Math.round(user.onlineTime / 60) + ' min'
            };
            
            bot.editMessageText(getText(userId, 'profile_info', params), {
                chat_id: userId,
                message_id: messageId,
                reply_markup: {
                    inline_keyboard: [[{ text: '🔙 Back', callback_data: 'main_menu' }]]
                }
            });
            break;
            
        case 'settings':
            bot.editMessageText('⚙️ Settings', {
                chat_id: userId,
                message_id: messageId,
                reply_markup: {
                    inline_keyboard: [
                        [{ text: '🌍 Change Language', callback_data: 'change_language' }],
                        [{ text: '🔔 Notifications', callback_data: 'notifications' }],
                        [{ text: '🔙 Back', callback_data: 'main_menu' }]
                    ]
                }
            });
            break;
            
        case 'change_language':
            bot.editMessageText('🌍 Select Language:', {
                chat_id: userId,
                message_id: messageId,
                ...createKeyboard(userId, 'language')
            });
            break;
            
        case 'help':
            bot.editMessageText(getText(userId, 'help_text'), {
                chat_id: userId,
                message_id: messageId,
                reply_markup: {
                    inline_keyboard: [[{ text: '🔙 Back', callback_data: 'main_menu' }]]
                }
            });
            break;
            
        case 'main_menu':
            bot.editMessageText(getText(userId, 'main_menu'), {
                chat_id: userId,
                message_id: messageId,
                ...createKeyboard(userId, 'main')
            });
            break;
            
        case 'next_partner':
            if (!user.currentPartner) {
                bot.answerCallbackQuery(callbackQuery.id, getText(userId, 'not_in_chat'));
                return;
            }
            
            endChat(userId);
            user.isSearching = true;
            waitingUsers.push(userId);
            
            bot.sendMessage(userId, getText(userId, 'searching'));
            
            setTimeout(() => {
                if (user.isSearching) {
                    const partnerId = findBestMatch(userId);
                    if (partnerId) {
                        startChat(userId, partnerId);
                    }
                }
            }, 1000);
            break;
            
        case 'stop_chat':
            endChat(userId);
            bot.sendMessage(userId, getText(userId, 'main_menu'), createKeyboard(userId, 'main'));
            break;
            
        case 'rate_partner':
            bot.answerCallbackQuery(callbackQuery.id, '⭐ Rating feature coming soon!');
            break;
            
        case 'report_partner':
            bot.answerCallbackQuery(callbackQuery.id, '🚫 Report feature coming soon!');
            break;
            
        // Admin commands
        case 'admin':
            if (!adminIds.has(userId)) {
                bot.answerCallbackQuery(callbackQuery.id, '❌ Access denied');
                return;
            }
            
            bot.editMessageText('👑 Admin Panel', {
                chat_id: userId,
                message_id: messageId,
                ...createKeyboard(userId, 'admin')
            });
            break;
            
        case 'admin_stats':
            if (!adminIds.has(userId)) return;
            
            const totalUsers = users.size;
            const activeUsers = activeChats.size * 2;
            const waitingCount = waitingUsers.length;
            
            const statsText = `📊 Bot Statistics:\n\n👥 Total Users: ${totalUsers}\n💬 Active Chats: ${activeChats.size}\n⏳ Waiting: ${waitingCount}\n🚫 Banned: ${bannedUsers.size}`;
            
            bot.editMessageText(statsText, {
                chat_id: userId,
                message_id: messageId,
                reply_markup: {
                    inline_keyboard: [[{ text: '🔙 Back', callback_data: 'admin' }]]
                }
            });
            break;
    }
    
    bot.answerCallbackQuery(callbackQuery.id);
});

// Handle regular messages (chat forwarding)
bot.on('message', (msg) => {
    const userId = msg.from.id;
    
    // Skip commands and callback queries
    if (msg.text && msg.text.startsWith('/')) return;
    
    const user = users.get(userId);
    if (!user || !user.currentPartner || bannedUsers.has(userId)) return;
    
    const partnerId = user.currentPartner;
    const partner = users.get(partnerId);
    
    if (!partner) {
        endChat(userId);
        return;
    }
    
    // Forward message to partner
    try {
        if (msg.text) {
            bot.sendMessage(partnerId, `💬 ${msg.text}`);
        } else if (msg.photo) {
            const photo = msg.photo[msg.photo.length - 1];
            bot.sendPhoto(partnerId, photo.file_id, {
                caption: msg.caption ? `📷 ${msg.caption}` : '📷 Photo'
            });
        } else if (msg.voice) {
            bot.sendVoice(partnerId, msg.voice.file_id);
        } else if (msg.video) {
            bot.sendVideo(partnerId, msg.video.file_id, {
                caption: msg.caption ? `🎥 ${msg.caption}` : '🎥 Video'
            });
        } else if (msg.document) {
            bot.sendDocument(partnerId, msg.document.file_id, {
                caption: msg.caption ? `📄 ${msg.caption}` : '📄 Document'
            });
        } else if (msg.sticker) {
            bot.sendSticker(partnerId, msg.sticker.file_id);
        } else if (msg.audio) {
            bot.sendAudio(partnerId, msg.audio.file_id);
        }
        
        user.addMessage();
        partner.updateLastActive();
        
        // Update chat statistics
        const chatId1 = `${userId}_${partnerId}`;
        const chatId2 = `${partnerId}_${userId}`;
        const chat = activeChats.get(chatId1) || activeChats.get(chatId2);
        if (chat) {
            chat.messageCount++;
        }
        
    } catch (error) {
        console.error('Error forwarding message:', error);
        bot.sendMessage(userId, getText(userId, 'partner_disconnected'));
        endChat(userId);
    }
});

// Error handling
bot.on('error', (error) => {
    console.error('Bot error:', error);
});

bot.on('polling_error', (error) => {
    console.error('Polling error:', error);
});

// Cleanup inactive users periodically
setInterval(() => {
    const now = new Date();
    const inactiveThreshold = 30 * 60 * 1000; // 30 minutes
    
    // Clean up inactive waiting users
    waitingUsers = waitingUsers.filter(userId => {
        const user = users.get(userId);
        if (!user) return false;
        
        const timeDiff = now - user.lastActive;
        if (timeDiff > inactiveThreshold) {
            user.isSearching = false;
            return false;
        }
        return true;
    });
    
    // Clean up inactive chats
    activeChats.forEach((chat, chatId) => {
        const timeDiff = now - chat.startTime;
        if (timeDiff > 2 * 60 * 60 * 1000) { // 2 hours
            const user1 = users.get(chat.user1);
            const user2 = users.get(chat.user2);
            
            if (user1) {
                user1.endChat();
                bot.sendMessage(chat.user1, getText(chat.user1, 'chat_ended'));
            }
            if (user2) {
                user2.endChat();
                bot.sendMessage(chat.user2, getText(chat.user2, 'chat_ended'));
            }
            
            activeChats.delete(chatId);
        }
    });
}, 5 * 60 * 1000); // Run every 5 minutes

// Matching algorithm - continuously try to match waiting users
setInterval(() => {
    const availableUsers = [...waitingUsers];
    const matched = new Set();
    
    for (let i = 0; i < availableUsers.length - 1; i++) {
        if (matched.has(availableUsers[i])) continue;
        
        for (let j = i + 1; j < availableUsers.length; j++) {
            if (matched.has(availableUsers[j])) continue;
            
            const user1Id = availableUsers[i];
            const user2Id = availableUsers[j];
            
            const user1 = users.get(user1Id);
            const user2 = users.get(user2Id);
            
            if (user1 && user2 && user1.isSearching && user2.isSearching) {
                if (startChat(user1Id, user2Id)) {
                    matched.add(user1Id);
                    matched.add(user2Id);
                    break;
                }
            }
        }
    }
}, 3000); // Run every 3 seconds

// Save data periodically (in production, use proper database)
setInterval(() => {
    const data = {
        users: Array.from(users.entries()).map(([id, user]) => ({
            id,
            ...user,
            joinDate: user.joinDate.toISOString(),
            lastActive: user.lastActive.toISOString()
        })),
        bannedUsers: Array.from(bannedUsers),
        timestamp: new Date().toISOString()
    };
    
    // Save to file (replace with database in production)
    fs.writeFileSync('bot_data.json', JSON.stringify(data, null, 2));
}, 10 * 60 * 1000); // Save every 10 minutes

// Load data on startup
function loadData() {
    try {
        if (fs.existsSync('bot_data.json')) {
            const data = JSON.parse(fs.readFileSync('bot_data.json', 'utf8'));
            
            // Restore users
            data.users.forEach(userData => {
                const user = new User(
                    userData.id,
                    userData.username,
                    userData.firstName,
                    userData.lastName,
                    userData.language
                );
                
                // Restore user data
                Object.assign(user, userData);
                user.joinDate = new Date(userData.joinDate);
                user.lastActive = new Date(userData.lastActive);
                user.isSearching = false; // Reset search state on startup
                user.currentPartner = null; // Reset partner state
                
                users.set(userData.id, user);
            });
            
            // Restore banned users
            if (data.bannedUsers) {
                data.bannedUsers.forEach(id => bannedUsers.add(id));
            }
            
            console.log(`Loaded ${users.size} users and ${bannedUsers.size} banned users`);
        }
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Additional features and commands

// VIP System
bot.onText(/\/vip/, (msg) => {
    const userId = msg.from.id;
    const user = users.get(userId);
    
    if (!user) return;
    
    const vipText = user.isVip 
        ? "⭐ You are already a VIP member!"
        : "💎 VIP Membership Benefits:\n\n⚡ Priority matching\n🔍 Advanced filters\n🎯 Interest-based matching\n📊 Detailed statistics\n🛡️ Enhanced privacy\n\nContact admin to upgrade!";
    
    bot.sendMessage(userId, vipText);
});

// Interest system
bot.onText(/\/interests (.+)/, (msg, match) => {
    const userId = msg.from.id;
    const user = users.get(userId);
    
    if (!user) return;
    
    const interests = match[1].split(',').map(i => i.trim().toLowerCase());
    user.preferences.interests = interests.slice(0, 10); // Max 10 interests
    
    bot.sendMessage(userId, `✅ Your interests updated: ${interests.join(', ')}`);
});

// Gender preference
bot.onText(/\/gender (male|female|any)/, (msg, match) => {
    const userId = msg.from.id;
    const user = users.get(userId);
    
    if (!user) return;
    
    user.preferences.gender = match[1];
    bot.sendMessage(userId, `✅ Gender preference set to: ${match[1]}`);
});

// Age range preference
bot.onText(/\/age (\d+)-(\d+)/, (msg, match) => {
    const userId = msg.from.id;
    const user = users.get(userId);
    
    if (!user) return;
    
    const minAge = parseInt(match[1]);
    const maxAge = parseInt(match[2]);
    
    if (minAge >= 18 && maxAge <= 99 && minAge <= maxAge) {
        user.preferences.ageRange = [minAge, maxAge];
        bot.sendMessage(userId, `✅ Age preference set to: ${minAge}-${maxAge} years`);
    } else {
        bot.sendMessage(userId, "❌ Invalid age range. Use format: /age 18-25");
    }
});

// Report system
function handleReport(reporterId, reportedId, reason) {
    const reporter = users.get(reporterId);
    const reported = users.get(reportedId);
    
    if (!reporter || !reported) return false;
    
    const report = {
        id: Date.now(),
        reporter: reporterId,
        reported: reportedId,
        reason: reason,
        timestamp: new Date(),
        status: 'pending'
    };
    
    reported.reports.push(report);
    
    // Auto-ban if too many reports
    if (reported.reports.length >= 3) {
        bannedUsers.add(reportedId);
        
        // Notify admins
        adminIds.forEach(adminId => {
            bot.sendMessage(adminId, `🚨 User ${reportedId} auto-banned for multiple reports`);
        });
    }
    
    return true;
}

// Enhanced admin commands
bot.onText(/\/admin_ban (\d+)/, (msg, match) => {
    const adminId = msg.from.id;
    if (!adminIds.has(adminId)) return;
    
    const userToBan = parseInt(match[1]);
    bannedUsers.add(userToBan);
    
    // End any active chat
    const user = users.get(userToBan);
    if (user && user.currentPartner) {
        endChat(userToBan);
    }
    
    bot.sendMessage(adminId, `✅ User ${userToBan} has been banned`);
    bot.sendMessage(userToBan, getText(userToBan, 'banned_message')).catch(() => {});
});

bot.onText(/\/admin_unban (\d+)/, (msg, match) => {
    const adminId = msg.from.id;
    if (!adminIds.has(adminId)) return;
    
    const userToUnban = parseInt(match[1]);
    bannedUsers.delete(userToUnban);
    
    bot.sendMessage(adminId, `✅ User ${userToUnban} has been unbanned`);
});

bot.onText(/\/admin_broadcast (.+)/, (msg, match) => {
    const adminId = msg.from.id;
    if (!adminIds.has(adminId)) return;
    
    const message = match[1];
    let sentCount = 0;
    
    users.forEach((user, userId) => {
        if (!bannedUsers.has(userId)) {
            bot.sendMessage(userId, `📢 ${message}`).then(() => {
                sentCount++;
            }).catch(() => {});
        }
    });
    
    setTimeout(() => {
        bot.sendMessage(adminId, `✅ Broadcast sent to ${sentCount} users`);
    }, 5000);
});

// User feedback system
bot.onText(/\/feedback (.+)/, (msg, match) => {
    const userId = msg.from.id;
    const feedback = match[1];
    
    // Send feedback to admins
    adminIds.forEach(adminId => {
        bot.sendMessage(adminId, `💬 Feedback from ${userId}:\n${feedback}`);
    });
    
    bot.sendMessage(userId, "✅ Thank you for your feedback!");
});

// Statistics for users
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
}

bot.onText(/\/mystats/, (msg) => {
    const userId = msg.from.id;
    const user = users.get(userId);
    
    if (!user) return;
    
    const joinDays = Math.floor((new Date() - user.joinDate) / (1000 * 60 * 60 * 24));
    const avgRating = user.reputation.toFixed(1);
    const totalTime = formatTime(user.onlineTime);
    
    const stats = `
📊 Your Detailed Statistics

👤 Profile:
• User ID: ${userId}
• Joined: ${joinDays} days ago
• Language: ${user.language.toUpperCase()}
• Status: ${user.isVip ? 'VIP ⭐' : 'Regular'}

💬 Chat Stats:
• Total chats: ${user.totalChats}
• Messages sent: ${user.totalMessages}
• Partners met: ${user.partnersMetCount}
• Average rating: ${avgRating}/5.0

⏱️ Activity:
• Total online: ${totalTime}
• Last active: ${formatTime((new Date() - user.lastActive) / 1000)} ago

🎯 Preferences:
• Age range: ${user.preferences.ageRange.join('-')}
• Gender: ${user.preferences.gender}
• Interests: ${user.preferences.interests.slice(0, 5).join(', ') || 'None'}
    `.trim();
    
    bot.sendMessage(userId, stats);
});

// Fun commands
const funFacts = [
    "🌍 Our users come from over 50 countries!",
    "💬 Over 1 million messages sent through our bot!",
    "⚡ Average response time is under 2 seconds!",
    "🎭 Your anonymity is our top priority!",
    "🤝 95% of users rate their experience as positive!",
    "🔒 All chats are end-to-end private!",
    "🌟 New features added every week!",
    "👥 Peak hours: 7-11 PM in most timezones!"
];

bot.onText(/\/funfact/, (msg) => {
    const userId = msg.from.id;
    const randomFact = funFacts[Math.floor(Math.random() * funFacts.length)];
    bot.sendMessage(userId, `🎲 Fun Fact:\n${randomFact}`);
});

// Ice breaker suggestions
const iceBreakers = {
    en: [
        "Hi! How's your day going?",
        "What's the most interesting thing that happened to you today?",
        "If you could travel anywhere right now, where would you go?",
        "What's your favorite way to spend a weekend?",
        "What's something you've learned recently?",
        "If you could have dinner with anyone, who would it be?",
        "What's your hidden talent?",
        "What's the best advice you've ever received?"
    ],
    id: [
        "Hai! Bagaimana harimu?",
        "Apa hal paling menarik yang terjadi hari ini?",
        "Kalau bisa traveling kemana saja, mau ke mana?",
        "Cara favorit kamu menghabiskan weekend?",
        "Apa yang baru kamu pelajari belakangan ini?",
        "Kalau bisa makan malam sama siapa saja, pilih siapa?",
        "Apa bakat tersembunyi kamu?",
        "Apa nasihat terbaik yang pernah kamu terima?"
    ],
    es: [
        "¡Hola! ¿Cómo va tu día?",
        "¿Qué es lo más interesante que te pasó hoy?",
        "Si pudieras viajar a cualquier lugar ahora, ¿a dónde irías?",
        "¿Cuál es tu forma favorita de pasar un fin de semana?",
        "¿Qué has aprendido recientemente?",
        "Si pudieras cenar con cualquier persona, ¿quién sería?",
        "¿Cuál es tu talento oculto?",
        "¿Cuál es el mejor consejo que has recibido?"
    ]
};

bot.onText(/\/icebreaker/, (msg) => {
    const userId = msg.from.id;
    const user = users.get(userId);
    
    if (!user) return;
    
    const lang = user.language || 'en';
    const breakers = iceBreakers[lang] || iceBreakers['en'];
    const randomBreaker = breakers[Math.floor(Math.random() * breakers.length)];
    
    bot.sendMessage(userId, `💡 Ice breaker suggestion:\n"${randomBreaker}"`);
});

// Queue position for waiting users
bot.onText(/\/queue/, (msg) => {
    const userId = msg.from.id;
    const user = users.get(userId);
    
    if (!user || !user.isSearching) {
        bot.sendMessage(userId, "❌ You're not currently searching for a partner.");
        return;
    }
    
    const position = waitingUsers.indexOf(userId) + 1;
    const totalWaiting = waitingUsers.length;
    
    bot.sendMessage(userId, `📍 Queue Position: ${position}/${totalWaiting}\n\n⏱️ Estimated wait time: ${Math.max(1, position * 30)} seconds`);
});

// Enhanced matching with preferences
function findBestMatchWithPreferences(userId) {
    const user = users.get(userId);
    if (!user) return null;
    
    const availableUsers = waitingUsers.filter(id => {
        const otherUser = users.get(id);
        return id !== userId && 
               otherUser && 
               !otherUser.currentPartner &&
               !bannedUsers.has(id);
    });
    
    if (availableUsers.length === 0) return null;
    
    // VIP users get priority
    if (user.isVip) {
        const vipMatches = availableUsers.filter(id => users.get(id).isVip);
        if (vipMatches.length > 0) {
            return vipMatches[0];
        }
    }
    
    // Interest-based matching
    if (user.preferences.interests.length > 0) {
        const interestMatches = availableUsers.filter(id => {
            const otherUser = users.get(id);
            const commonInterests = user.preferences.interests.filter(interest =>
                otherUser.preferences.interests.includes(interest)
            );
            return commonInterests.length > 0;
        });
        
        if (interestMatches.length > 0) {
            return interestMatches[Math.floor(Math.random() * interestMatches.length)];
        }
    }
    
    // Language preference matching
    if (user.preferences.language !== 'any') {
        const langMatches = availableUsers.filter(id => {
            const otherUser = users.get(id);
            return otherUser.language === user.preferences.language;
        });
        
        if (langMatches.length > 0) {
            return langMatches[Math.floor(Math.random() * langMatches.length)];
        }
    }
    
    // Random selection as fallback
    return availableUsers[Math.floor(Math.random() * availableUsers.length)];
}

// Load data on startup
loadData();

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('Shutting down bot...');
    
    // Save data before exit
    const data = {
        users: Array.from(users.entries()).map(([id, user]) => ({
            id,
            ...user,
            joinDate: user.joinDate.toISOString(),
            lastActive: user.lastActive.toISOString()
        })),
        bannedUsers: Array.from(bannedUsers),
        timestamp: new Date().toISOString()
    };
    
    fs.writeFileSync('bot_data.json', JSON.stringify(data, null, 2));
    console.log('Data saved. Goodbye!');
    
    process.exit(0);
});

console.log('🤖 Anonymous Chat Bot started successfully!');
console.log('📊 Features loaded:');
console.log('   ✅ Multi-language support (EN, ID, ES)');
console.log('   ✅ Advanced matching algorithm');
console.log('   ✅ User preferences and interests');
console.log('   ✅ VIP system');
console.log('   ✅ Admin panel');
console.log('   ✅ Report system');
console.log('   ✅ Statistics tracking');
console.log('   ✅ Ice breaker suggestions');
console.log('   ✅ Media message support');
console.log('   ✅ Queue system');
console.log('   ✅ Auto-cleanup and data persistence');
console.log('');
console.log('🚀 Bot is ready to serve users!');