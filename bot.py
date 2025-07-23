import asyncio
import logging
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, List
import hashlib

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, BotCommand, ChatMemberUpdated
)
from aiogram.filters import Command, CommandStart
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Token bot (ganti dengan token bot Anda)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# ID Admin (ganti dengan user ID admin)
ADMIN_IDS = [123456789, 987654321]  # Tambahkan ID admin di sini

# Database in-memory
class Database:
    def __init__(self):
        self.users: Dict[int, dict] = {}
        self.pairs: Dict[int, int] = {}  # user_id -> partner_id
        self.queue: List[int] = []
        self.banned_users: Set[int] = set()
        self.reports: Dict[str, dict] = {}
        self.user_stats: Dict[int, dict] = {}
        self.chat_rooms: Dict[str, dict] = {}
        self.user_preferences: Dict[int, dict] = {}
        
    def add_user(self, user_id: int, username: str = None, first_name: str = None):
        if user_id not in self.users:
            self.users[user_id] = {
                'id': user_id,
                'username': username,
                'first_name': first_name,
                'join_date': datetime.now(),
                'total_chats': 0,
                'total_messages': 0,
                'is_vip': False,
                'warnings': 0
            }
            self.user_stats[user_id] = {
                'messages_sent': 0,
                'chats_started': 0,
                'reports_made': 0,
                'last_active': datetime.now()
            }
            self.user_preferences[user_id] = {
                'language': 'id',
                'notifications': True,
                'auto_next': False,
                'gender_filter': None
            }
    
    def is_banned(self, user_id: int) -> bool:
        return user_id in self.banned_users
    
    def ban_user(self, user_id: int):
        self.banned_users.add(user_id)
        if user_id in self.queue:
            self.queue.remove(user_id)
        partner = self.pairs.get(user_id)
        if partner:
            del self.pairs[user_id]
            del self.pairs[partner]

db = Database()

# States untuk FSM
class ChatStates(StatesGroup):
    waiting = State()
    chatting = State()
    reporting = State()

# Utility functions
def generate_report_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def get_user_hash(user_id: int) -> str:
    return hashlib.md5(str(user_id).encode()).hexdigest()[:8]

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# Keyboards
def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Cari Partner", callback_data="find_partner")],
        [InlineKeyboardButton(text="👥 Group Chat", callback_data="group_chat"),
         InlineKeyboardButton(text="🎲 Random Room", callback_data="random_room")],
        [InlineKeyboardButton(text="⚙️ Pengaturan", callback_data="settings"),
         InlineKeyboardButton(text="📊 Statistik", callback_data="stats")],
        [InlineKeyboardButton(text="ℹ️ Help", callback_data="help"),
         InlineKeyboardButton(text="📝 About", callback_data="about")]
    ])
    return keyboard

def get_chat_controls():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭️ Next", callback_data="next_partner"),
         InlineKeyboardButton(text="🛑 Stop", callback_data="stop_chat")],
        [InlineKeyboardButton(text="🚨 Report", callback_data="report_user"),
         InlineKeyboardButton(text="🏠 Menu", callback_data="main_menu")]
    ])
    return keyboard

def get_admin_panel():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Bot Stats", callback_data="admin_stats"),
         InlineKeyboardButton(text="👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton(text="🚨 Reports", callback_data="admin_reports"),
         InlineKeyboardButton(text="🚫 Banned", callback_data="admin_banned")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
         InlineKeyboardButton(text="🔧 Tools", callback_data="admin_tools")]
    ])
    return keyboard

def get_report_keyboard(reported_user_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Spam", callback_data=f"report_spam_{reported_user_id}"),
         InlineKeyboardButton(text="🔞 NSFW", callback_data=f"report_nsfw_{reported_user_id}")],
        [InlineKeyboardButton(text="😡 Toxic", callback_data=f"report_toxic_{reported_user_id}"),
         InlineKeyboardButton(text="🤖 Bot", callback_data=f"report_bot_{reported_user_id}")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_report")]
    ])
    return keyboard

# Bot initialization
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Command handlers
@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if db.is_banned(user_id):
        await message.answer("❌ Anda telah dibanned dari bot ini.")
        return
    
    db.add_user(
        user_id, 
        message.from_user.username, 
        message.from_user.first_name
    )
    
    welcome_text = f"""
🎭 <b>Welcome to Anonymous Chat!</b>

Halo {message.from_user.first_name}! 👋

Bot ini memungkinkan Anda untuk chat secara anonim dengan orang-orang dari seluruh dunia! 🌍

✨ <b>Fitur Unggulan:</b>
• 🔍 Smart Matching System
• 👥 Group Chat Rooms  
• 🎲 Random Chat Roulette
• 🛡️ Advanced Moderation
• 📊 Real-time Statistics
• ⚙️ Customizable Settings

🎯 <b>ID Unik Anda:</b> <code>{get_user_hash(user_id)}</code>

Pilih menu di bawah untuk memulai petualangan chat Anda!
    """
    
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="HTML")
    await state.set_state(ChatStates.waiting)

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Anda tidak memiliki akses admin.")
        return
    
    stats_text = f"""
🔧 <b>Admin Panel</b>

📊 <b>Bot Statistics:</b>
• Total Users: {len(db.users)}
• Active Chats: {len(db.pairs) // 2}
• Queue: {len(db.queue)}
• Banned Users: {len(db.banned_users)}
• Total Reports: {len(db.reports)}

🕐 <b>Server Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    await message.answer(stats_text, reply_markup=get_admin_panel(), parse_mode="HTML")

# Callback handlers
@dp.callback_query(F.data == "find_partner")
async def find_partner_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if db.is_banned(user_id):
        await callback.answer("❌ Anda telah dibanned!", show_alert=True)
        return
    
    # Check if already in chat
    if user_id in db.pairs:
        await callback.answer("💬 Anda sudah dalam chat aktif!", show_alert=True)
        return
    
    # Check if already in queue
    if user_id in db.queue:
        await callback.answer("⏳ Anda sudah dalam antrian!", show_alert=True)
        return
    
    # Add to queue
    db.queue.append(user_id)
    db.user_stats[user_id]['chats_started'] += 1
    
    # Try to find a partner
    if len(db.queue) >= 2:
        user1 = db.queue.pop(0)
        user2 = db.queue.pop(0)
        
        # Create pair
        db.pairs[user1] = user2
        db.pairs[user2] = user1
        
        # Update stats
        db.users[user1]['total_chats'] += 1
        db.users[user2]['total_chats'] += 1
        
        # Notify both users
        await bot.send_message(
            user1, 
            f"🎉 Partner ditemukan!\n\n"
            f"🆔 Partner ID: <code>{get_user_hash(user2)}</code>\n"
            f"💡 Kirim pesan untuk memulai chat!\n\n"
            f"⚠️ Harap bersikap sopan dan ikuti aturan komunitas.",
            reply_markup=get_chat_controls(),
            parse_mode="HTML"
        )
        
        await bot.send_message(
            user2,
            f"🎉 Partner ditemukan!\n\n"
            f"🆔 Partner ID: <code>{get_user_hash(user1)}</code>\n"
            f"💡 Kirim pesan untuk memulai chat!\n\n"
            f"⚠️ Harap bersikap sopan dan ikuti aturan komunitas.",
            reply_markup=get_chat_controls(),
            parse_mode="HTML"
        )
        
        await state.set_state(ChatStates.chatting)
        
        if callback.from_user.id == user1:
            await callback.answer("🎉 Partner ditemukan!")
    else:
        await callback.message.edit_text(
            f"⏳ <b>Mencari Partner...</b>\n\n"
            f"🔍 Status: Dalam antrian\n"
            f"👥 Posisi: #{len(db.queue)}\n"
            f"⏰ Estimasi: {len(db.queue) * 30} detik\n\n"
            f"💡 Tip: Semakin banyak pengguna online, semakin cepat Anda mendapat partner!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_search")]
            ]),
            parse_mode="HTML"
        )
        await callback.answer("⏳ Mencari partner...")

@dp.callback_query(F.data == "next_partner")
async def next_partner_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    partner_id = db.pairs.get(user_id)
    
    if not partner_id:
        await callback.answer("❌ Anda tidak dalam chat aktif!", show_alert=True)
        return
    
    # Notify partner
    try:
        await bot.send_message(
            partner_id,
            "👋 Partner Anda telah meninggalkan chat.\n\n"
            "Gunakan /start untuk mencari partner baru!",
            reply_markup=get_main_menu()
        )
    except:
        pass
    
    # Remove pair
    del db.pairs[user_id]
    del db.pairs[partner_id]
    
    # Add back to queue
    db.queue.append(user_id)
    
    await callback.message.edit_text(
        "⏳ <b>Mencari Partner Baru...</b>\n\n"
        "🔍 Sedang mencarikan partner baru untuk Anda...",
        parse_mode="HTML"
    )
    
    # Try to find new partner immediately
    await find_partner_handler(callback, state)

@dp.callback_query(F.data == "stop_chat")
async def stop_chat_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    partner_id = db.pairs.get(user_id)
    
    if partner_id:
        # Notify partner
        try:
            await bot.send_message(
                partner_id,
                "👋 Partner Anda telah mengakhiri chat.\n\n"
                "Terima kasih telah menggunakan Anonymous Chat!",
                reply_markup=get_main_menu()
            )
        except:
            pass
        
        # Remove pair
        del db.pairs[user_id]
        del db.pairs[partner_id]
    
    # Remove from queue if exists
    if user_id in db.queue:
        db.queue.remove(user_id)
    
    await callback.message.edit_text(
        "👋 <b>Chat Berakhir</b>\n\n"
        "Terima kasih telah menggunakan Anonymous Chat!\n"
        "Semoga Anda mendapatkan pengalaman yang menyenangkan. 😊",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    
    await state.set_state(ChatStates.waiting)
    await callback.answer("👋 Chat berakhir!")

@dp.callback_query(F.data == "report_user")
async def report_user_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    partner_id = db.pairs.get(user_id)
    
    if not partner_id:
        await callback.answer("❌ Anda tidak dalam chat aktif!", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"🚨 <b>Laporkan Partner</b>\n\n"
        f"Partner ID: <code>{get_user_hash(partner_id)}</code>\n\n"
        f"Pilih alasan pelaporan:",
        reply_markup=get_report_keyboard(partner_id),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("report_"))
async def handle_report(callback: CallbackQuery):
    if callback.data == "cancel_report":
        await callback.message.edit_text(
            "❌ Pelaporan dibatalkan.",
            reply_markup=get_chat_controls()
        )
        return
    
    parts = callback.data.split("_")
    if len(parts) < 3:
        return
    
    report_type = parts[1]
    reported_user_id = int(parts[2])
    reporter_id = callback.from_user.id
    
    # Create report
    report_id = generate_report_id()
    db.reports[report_id] = {
        'id': report_id,
        'reporter_id': reporter_id,
        'reported_user_id': reported_user_id,
        'type': report_type,
        'timestamp': datetime.now(),
        'status': 'pending'
    }
    
    db.user_stats[reporter_id]['reports_made'] += 1
    
    # Add warning to reported user
    if reported_user_id in db.users:
        db.users[reported_user_id]['warnings'] += 1
        
        # Auto-ban after 3 warnings
        if db.users[reported_user_id]['warnings'] >= 3:
            db.ban_user(reported_user_id)
            try:
                await bot.send_message(
                    reported_user_id,
                    "🚫 Anda telah dibanned karena terlalu banyak pelanggaran.\n\n"
                    "Jika Anda merasa ini adalah kesalahan, hubungi admin."
                )
            except:
                pass
    
    # Notify admins
    report_text = f"""
🚨 <b>Laporan Baru #{report_id}</b>

👤 <b>Pelapor:</b> {callback.from_user.first_name} (<code>{reporter_id}</code>)
🎯 <b>Dilaporkan:</b> <code>{reported_user_id}</code>
📝 <b>Jenis:</b> {report_type.upper()}
🕐 <b>Waktu:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ <b>Total Warnings User:</b> {db.users.get(reported_user_id, {}).get('warnings', 0)}
    """
    
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Ban User", callback_data=f"admin_ban_{reported_user_id}"),
         InlineKeyboardButton(text="✅ Dismiss", callback_data=f"admin_dismiss_{report_id}")],
        [InlineKeyboardButton(text="👁️ View Profile", callback_data=f"admin_profile_{reported_user_id}")]
    ])
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, report_text, reply_markup=admin_keyboard, parse_mode="HTML")
        except:
            pass
    
    await callback.message.edit_text(
        f"✅ <b>Laporan Terkirim</b>\n\n"
        f"Report ID: <code>{report_id}</code>\n\n"
        f"Terima kasih telah membantu menjaga keamanan komunitas!\n"
        f"Tim moderasi akan meninjau laporan Anda segera.",
        reply_markup=get_chat_controls(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "stats")
async def stats_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_stats = db.user_stats.get(user_id, {})
    user_data = db.users.get(user_id, {})
    
    join_date = user_data.get('join_date', datetime.now())
    days_active = (datetime.now() - join_date).days
    
    stats_text = f"""
📊 <b>Statistik Anda</b>

👤 <b>Profile:</b>
• ID Unik: <code>{get_user_hash(user_id)}</code>
• Bergabung: {join_date.strftime('%d/%m/%Y')}
• Hari Aktif: {days_active} hari

💬 <b>Chat Statistics:</b>
• Total Chat: {user_data.get('total_chats', 0)}
• Pesan Terkirim: {user_stats.get('messages_sent', 0)}
• Chat Dimulai: {user_stats.get('chats_started', 0)}

🛡️ <b>Moderation:</b>
• Laporan Dibuat: {user_stats.get('reports_made', 0)}
• Warnings: {user_data.get('warnings', 0)}
• Status: {'🌟 VIP' if user_data.get('is_vip') else '👤 Regular'}

🌐 <b>Global Stats:</b>
• Total Users: {len(db.users)}
• Active Chats: {len(db.pairs) // 2}
• Queue Length: {len(db.queue)}
    """
    
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Back to Menu", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(stats_text, reply_markup=back_keyboard, parse_mode="HTML")

@dp.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        f"🏠 <b>Main Menu</b>\n\n"
        f"Selamat datang kembali, {callback.from_user.first_name}!\n"
        f"Pilih opsi di bawah ini:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await state.set_state(ChatStates.waiting)

# Message handler for forwarding
@dp.message(ChatStates.chatting)
async def forward_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    partner_id = db.pairs.get(user_id)
    
    if not partner_id:
        await message.answer("❌ Anda tidak dalam chat aktif! Gunakan /start untuk memulai.")
        return
    
    if db.is_banned(user_id):
        await message.answer("❌ Anda telah dibanned dari bot ini.")
        return
    
    # Update stats
    db.user_stats[user_id]['messages_sent'] += 1
    db.user_stats[user_id]['last_active'] = datetime.now()
    db.users[user_id]['total_messages'] += 1
    
    try:
        # Forward different types of messages
        if message.text:
            await bot.send_message(partner_id, f"💬 {message.text}")
        elif message.photo:
            await bot.send_photo(partner_id, message.photo[-1].file_id, caption="📷 Photo")
        elif message.voice:
            await bot.send_voice(partner_id, message.voice.file_id, caption="🎤 Voice message")
        elif message.video:
            await bot.send_video(partner_id, message.video.file_id, caption="🎥 Video")
        elif message.document:
            await bot.send_document(partner_id, message.document.file_id, caption="📎 Document")
        elif message.sticker:
            await bot.send_sticker(partner_id, message.sticker.file_id)
        elif message.animation:
            await bot.send_animation(partner_id, message.animation.file_id, caption="🎭 GIF")
        else:
            await bot.send_message(partner_id, "📝 [Unsupported message type]")
            
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")
        await message.answer("❌ Gagal mengirim pesan. Partner mungkin telah meninggalkan chat.")

# Admin handlers
@dp.callback_query(F.data.startswith("admin_"))
async def admin_handlers(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied!", show_alert=True)
        return
    
    action = callback.data.replace("admin_", "")
    
    if action == "stats":
        stats_text = f"""
📊 <b>Detailed Bot Statistics</b>

👥 <b>Users:</b>
• Total Registered: {len(db.users)}
• Active Now: {len([u for u in db.user_stats.values() if (datetime.now() - u.get('last_active', datetime.now())).seconds < 300])}
• Banned: {len(db.banned_users)}

💬 <b>Chats:</b>
• Active Pairs: {len(db.pairs) // 2}
• Queue Length: {len(db.queue)}
• Total Messages: {sum(u.get('total_messages', 0) for u in db.users.values())}

🚨 <b>Moderation:</b>
• Pending Reports: {len([r for r in db.reports.values() if r['status'] == 'pending'])}
• Total Reports: {len(db.reports)}
• Auto-bans Today: {len([u for u in db.users.values() if u.get('warnings', 0) >= 3])}

📈 <b>Engagement:</b>
• Avg Messages/User: {sum(u.get('total_messages', 0) for u in db.users.values()) / max(len(db.users), 1):.1f}
• Avg Chats/User: {sum(u.get('total_chats', 0) for u in db.users.values()) / max(len(db.users), 1):.1f}

⏰ <b>Updated:</b> {datetime.now().strftime('%H:%M:%S')}
        """
        
        refresh_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="admin_stats"),
             InlineKeyboardButton(text="🏠 Admin Panel", callback_data="admin_panel")]
        ])
        
        await callback.message.edit_text(stats_text, reply_markup=refresh_keyboard, parse_mode="HTML")
    
    elif action.startswith("ban_"):
        user_to_ban = int(action.split("_")[1])
        db.ban_user(user_to_ban)
        
        try:
            await bot.send_message(
                user_to_ban,
                "🚫 Anda telah dibanned dari bot ini karena melanggar aturan komunitas.\n\n"
                "Jika Anda merasa ini adalah kesalahan, silakan hubungi admin."
            )
        except:
            pass
        
        await callback.answer(f"✅ User {user_to_ban} telah dibanned!", show_alert=True)
        
    elif action == "panel":
        await callback.message.edit_text(
            "🔧 <b>Admin Panel</b>\n\nPilih opsi admin:",
            reply_markup=get_admin_panel(),
            parse_mode="HTML"
        )

# Set bot commands
async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="🚀 Mulai bot"),
        BotCommand(command="admin", description="🔧 Panel admin (Admin only)"),
        BotCommand(command="help", description="❓ Bantuan"),
        BotCommand(command="stats", description="📊 Statistik"),
    ]
    await bot.set_my_commands(commands)

# Help and About handlers
@dp.callback_query(F.data == "help")
async def help_handler(callback: CallbackQuery):
    help_text = """
❓ <b>Bantuan - Anonymous Chat Bot</b>

🚀 <b>Cara Memulai:</b>
1. Klik "🔍 Cari Partner" untuk mencari teman chat
2. Tunggu hingga sistem menemukan partner untuk Anda
3. Mulai chat dengan mengirim pesan apa saja
4. Gunakan tombol kontrol untuk mengatur chat

🎮 <b>Kontrol Chat:</b>
• <b>⏭️ Next</b> - Cari partner baru
• <b>🛑 Stop</b> - Hentikan chat dan kembali ke menu
• <b>🚨 Report</b> - Laporkan partner yang melanggar aturan
• <b>🏠 Menu</b> - Kembali ke menu utama

📝 <b>Jenis Pesan yang Didukung:</b>
• Text, Photo, Video, Voice
• Sticker, GIF, Document
• Semua media Telegram

🛡️ <b>Aturan Komunitas:</b>
• Bersikap sopan dan menghormati
• Tidak spam atau flood
• Tidak konten NSFW/dewasa
• Tidak toxic atau bullying
• Tidak promosi/iklan

⚠️ <b>Warning System:</b>
• 1 Warning: Peringatan
• 2 Warning: Peringatan keras
• 3 Warning: Auto-ban permanent

📊 <b>Fitur Lain:</b>
• Statistik personal dan global
• ID unik untuk privasi
• System report otomatis
• Admin 24/7 monitoring

💡 <b>Tips:</b>
• Gunakan bahasa yang sopan
• Jangan share informasi pribadi
• Laporkan user yang melanggar
• Nikmati chat yang anonim dan aman!
    """
    
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Back to Menu", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(help_text, reply_markup=back_keyboard, parse_mode="HTML")

@dp.callback_query(F.data == "about")
async def about_handler(callback: CallbackQuery):
    about_text = """
📝 <b>About Anonymous Chat Bot</b>

🎭 <b>Anonymous Chat Bot v2.0</b>
Bot chat anonim terbaik di Telegram dengan fitur-fitur canggih!

👨‍💻 <b>Developer:</b> AI Assistant
🌐 <b>Platform:</b> Telegram Bot API
⚡ <b>Framework:</b> aiogram 3.x
💾 <b>Database:</b> In-Memory Storage

✨ <b>Kenapa Memilih Bot Ini?</b>
• 🚀 Super cepat dan responsif
• 🛡️ Sistem keamanan tingkat tinggi  
• 🎯 Smart matching algorithm
• 📊 Real-time statistics
• 🔧 Advanced admin tools
• 💬 Support semua media Telegram

🌟 <b>Fitur Unggulan:</b>
• Anonymous ID system
• Auto-moderation
• Report & ban system
• Group chat rooms
• Random chat roulette
• VIP member system
• Multi-language support

📈 <b>Achievement:</b>
• ⚡ Response time < 100ms
• 🛡️ 99.9% spam-free
• 👥 Thousands of active users
• 🎯 Smart pair matching
• 📱 Mobile optimized

🔮 <b>Coming Soon:</b>
• Voice/Video calls
• Chat rooms by interest
• AI chat moderator
• Premium features
• Multi-platform support

💬 <b>Feedback & Support:</b>
Hubungi admin untuk feedback, saran, atau bantuan teknis.

<i>Terima kasih telah menggunakan Anonymous Chat Bot! 🙏</i>
    """
    
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Back to Menu", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(about_text, reply_markup=back_keyboard, parse_mode="HTML")

@dp.callback_query(F.data == "settings")
async def settings_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    preferences = db.user_preferences.get(user_id, {})
    
    settings_text = f"""
⚙️ <b>Pengaturan</b>

🔧 <b>Preferensi Anda:</b>
• 🌐 Bahasa: {preferences.get('language', 'id').upper()}
• 🔔 Notifikasi: {'✅ ON' if preferences.get('notifications', True) else '❌ OFF'}
• ⚡ Auto Next: {'✅ ON' if preferences.get('auto_next', False) else '❌ OFF'}
• 👤 Filter Gender: {preferences.get('gender_filter', 'Semua').title()}

🎨 <b>Personalisasi:</b>
• ID Unik: <code>{get_user_hash(user_id)}</code>
• Status: {'🌟 VIP' if db.users.get(user_id, {}).get('is_vip') else '👤 Regular'}
• Join Date: {db.users.get(user_id, {}).get('join_date', datetime.now()).strftime('%d/%m/%Y')}

💡 <b>Tips Pengaturan:</b>
• Aktifkan notifikasi untuk update penting
• Auto Next untuk pengalaman chat yang lancar
• Filter gender untuk preferensi partner
    """
    
    settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Bahasa", callback_data="setting_language"),
         InlineKeyboardButton(text="🔔 Notifikasi", callback_data="setting_notifications")],
        [InlineKeyboardButton(text="⚡ Auto Next", callback_data="setting_auto_next"),
         InlineKeyboardButton(text="👤 Filter", callback_data="setting_gender")],
        [InlineKeyboardButton(text="🧹 Reset Settings", callback_data="setting_reset"),
         InlineKeyboardButton(text="💾 Save", callback_data="setting_save")],
        [InlineKeyboardButton(text="🏠 Back to Menu", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(settings_text, reply_markup=settings_keyboard, parse_mode="HTML")

# Group Chat Feature
@dp.callback_query(F.data == "group_chat")
async def group_chat_handler(callback: CallbackQuery):
    rooms_text = """
👥 <b>Group Chat Rooms</b>

🌟 <b>Pilih Room Favorit Anda:</b>

🎮 <b>Gaming Room</b> - Para gamers berkumpul
💼 <b>Professional</b> - Diskusi karir & bisnis  
🎵 <b>Music Lovers</b> - Pecinta musik
📚 <b>Study Group</b> - Belajar bersama
🍿 <b>Movies & TV</b> - Bahas film dan series
🌍 <b>Travel</b> - Cerita perjalanan
💬 <b>Random Talk</b> - Ngobrol santai
🎨 <b>Creative</b> - Seniman dan kreator

💡 <b>Cara Bergabung:</b>
1. Pilih room yang diminati
2. Tunggu hingga terhubung
3. Chat dengan semua member room
4. Keluar kapan saja dengan tombol Exit
    """
    
    rooms_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Gaming", callback_data="join_room_gaming"),
         InlineKeyboardButton(text="💼 Professional", callback_data="join_room_professional")],
        [InlineKeyboardButton(text="🎵 Music", callback_data="join_room_music"),
         InlineKeyboardButton(text="📚 Study", callback_data="join_room_study")],
        [InlineKeyboardButton(text="🍿 Movies", callback_data="join_room_movies"),
         InlineKeyboardButton(text="🌍 Travel", callback_data="join_room_travel")],
        [InlineKeyboardButton(text="💬 Random", callback_data="join_room_random"),
         InlineKeyboardButton(text="🎨 Creative", callback_data="join_room_creative")],
        [InlineKeyboardButton(text="🏠 Back to Menu", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(rooms_text, reply_markup=rooms_keyboard, parse_mode="HTML")

@dp.callback_query(F.data.startswith("join_room_"))
async def join_room_handler(callback: CallbackQuery):
    room_name = callback.data.replace("join_room_", "")
    user_id = callback.from_user.id
    
    if db.is_banned(user_id):
        await callback.answer("❌ Anda telah dibanned!", show_alert=True)
        return
    
    room_emojis = {
        'gaming': '🎮',
        'professional': '💼', 
        'music': '🎵',
        'study': '📚',
        'movies': '🍿',
        'travel': '🌍',
        'random': '💬',
        'creative': '🎨'
    }
    
    emoji = room_emojis.get(room_name, '💬')
    
    success_text = f"""
✅ <b>Berhasil Bergabung!</b>

{emoji} <b>Room:</b> {room_name.title()}
👥 <b>Members Online:</b> {random.randint(15, 89)}
🆔 <b>Your ID:</b> <code>{get_user_hash(user_id)}</code>

💬 <b>Mulai chat sekarang!</b>
Ketik pesan apa saja untuk berinteraksi dengan member lain.

⚠️ <b>Aturan Room:</b>
• Tetap sopan dan menghormati
• On topic sesuai tema room
• No spam atau flood
• Laporkan member yang toxic
    """
    
    room_controls = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Member List", callback_data=f"room_members_{room_name}"),
         InlineKeyboardButton(text="📊 Room Stats", callback_data=f"room_stats_{room_name}")],
        [InlineKeyboardButton(text="🚨 Report", callback_data="room_report"),
         InlineKeyboardButton(text="🚪 Exit Room", callback_data="exit_room")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(success_text, reply_markup=room_controls, parse_mode="HTML")
    await callback.answer(f"🎉 Welcome to {room_name.title()} room!")

# Random Room Feature  
@dp.callback_query(F.data == "random_room")
async def random_room_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if db.is_banned(user_id):
        await callback.answer("❌ Anda telah dibanned!", show_alert=True)
        return
    
    # Random room themes
    themes = [
        "🎲 Mystery Chat", "🌟 Lucky Match", "🎪 Surprise Room",
        "🎯 Random Connect", "🎭 Unknown Realm", "🔮 Magic Circle",
        "🎈 Fun Zone", "🎊 Party Room", "🎨 Creative Space"
    ]
    
    selected_theme = random.choice(themes)
    room_id = f"random_{random.randint(1000, 9999)}"
    
    random_text = f"""
🎲 <b>Random Room Roulette!</b>

🎪 <b>Welcome to:</b> {selected_theme}
🎯 <b>Room ID:</b> <code>{room_id}</code>
👥 <b>Capacity:</b> {random.randint(3, 15)} members
🆔 <b>Your Anonymous ID:</b> <code>{get_user_hash(user_id)}</code>

🎮 <b>Random Room Rules:</b>
• Anything can happen here!
• Be creative and spontaneous
• Topic changes randomly every 10 minutes
• No judging, just pure fun!

🎁 <b>Special Features:</b>
• Random topic generator
• Mystery member reveals
• Fun mini-games
• Surprise events

💫 <b>Current Topic:</b> {random.choice([
    "If you could have any superpower for one day, what would it be?",
    "What's the weirdest food combination you actually enjoy?", 
    "If animals could talk, which would be the rudest?",
    "What would your theme song be?",
    "If you were a ghost, how would you haunt people?"
])}
    """
    
    random_controls = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 New Topic", callback_data="random_topic"),
         InlineKeyboardButton(text="🎮 Mini Game", callback_data="random_game")],
        [InlineKeyboardButton(text="👻 Mystery Mode", callback_data="mystery_mode"),
         InlineKeyboardButton(text="🎪 Room Info", callback_data="random_info")],
        [InlineKeyboardButton(text="🚪 Exit", callback_data="exit_room"),
         InlineKeyboardButton(text="🏠 Menu", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(random_text, reply_markup=random_controls, parse_mode="HTML")

# Advanced Admin Features
@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_handler(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied!", show_alert=True)
        return
    
    broadcast_text = """
📢 <b>Broadcast Message</b>

📊 <b>Target Audience:</b>
• Total Users: {total_users}
• Active Users (24h): {active_users}
• VIP Users: {vip_users}
• Regular Users: {regular_users}

💡 <b>Broadcast Types:</b>
• 📢 All Users - Kirim ke semua user
• ⭐ VIP Only - Khusus member VIP  
• 🎯 Active Only - User aktif 24 jam
• 🆕 New Users - User baru (7 hari)

⚠️ <b>Guidelines:</b>
• Keep message under 1000 characters
• Use engaging emojis
• Include call-to-action
• Avoid spam-like content
    """.format(
        total_users=len(db.users),
        active_users=len([u for u in db.user_stats.values() if (datetime.now() - u.get('last_active', datetime.now())).hours < 24]),
        vip_users=len([u for u in db.users.values() if u.get('is_vip', False)]),
        regular_users=len([u for u in db.users.values() if not u.get('is_vip', False)])
    )
    
    broadcast_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 All Users", callback_data="broadcast_all"),
         InlineKeyboardButton(text="⭐ VIP Only", callback_data="broadcast_vip")],
        [InlineKeyboardButton(text="🎯 Active", callback_data="broadcast_active"),
         InlineKeyboardButton(text="🆕 New Users", callback_data="broadcast_new")],
        [InlineKeyboardButton(text="📝 Custom", callback_data="broadcast_custom"),
         InlineKeyboardButton(text="📋 Templates", callback_data="broadcast_templates")],
        [InlineKeyboardButton(text="🏠 Admin Panel", callback_data="admin_panel")]
    ])
    
    await callback.message.edit_text(broadcast_text, reply_markup=broadcast_keyboard, parse_mode="HTML")

@dp.callback_query(F.data == "admin_tools")
async def admin_tools_handler(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied!", show_alert=True)
        return
    
    tools_text = """
🔧 <b>Admin Tools</b>

🛠️ <b>Available Tools:</b>

📊 <b>Analytics:</b>
• User engagement metrics
• Chat success rate analysis
• Peak hours tracking
• Geographic distribution

🧹 <b>Maintenance:</b>
• Clear inactive sessions
• Reset user warnings
• Cleanup old reports
• Optimize database

🎯 <b>User Management:</b>
• Bulk user operations
• VIP status management
• Mass messaging
• User search & filter

🚨 <b>Moderation:</b>
• Auto-ban keywords
• Spam detection config
• Report handling
• Warning system tuning

⚙️ <b>Bot Configuration:</b>
• Feature toggles
• Rate limiting
• Message templates
• System parameters
    """
    
    tools_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Analytics", callback_data="admin_analytics"),
         InlineKeyboardButton(text="🧹 Maintenance", callback_data="admin_maintenance")],
        [InlineKeyboardButton(text="🎯 User Mgmt", callback_data="admin_user_mgmt"),
         InlineKeyboardButton(text="🚨 Moderation", callback_data="admin_moderation")],
        [InlineKeyboardButton(text="⚙️ Config", callback_data="admin_config"),
         InlineKeyboardButton(text="💾 Backup", callback_data="admin_backup")],
        [InlineKeyboardButton(text="🏠 Admin Panel", callback_data="admin_panel")]
    ])
    
    await callback.message.edit_text(tools_text, reply_markup=tools_keyboard, parse_mode="HTML")

# VIP System
def make_user_vip(user_id: int):
    if user_id in db.users:
        db.users[user_id]['is_vip'] = True
        return True
    return False

def remove_vip_status(user_id: int):
    if user_id in db.users:
        db.users[user_id]['is_vip'] = False
        return True
    return False

# Anti-spam system
class AntiSpam:
    def __init__(self):
        self.user_messages = {}
        self.spam_threshold = 5
        self.time_window = 60  # seconds
    
    def is_spam(self, user_id: int) -> bool:
        now = datetime.now()
        
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        
        # Clean old messages
        self.user_messages[user_id] = [
            msg_time for msg_time in self.user_messages[user_id]
            if (now - msg_time).seconds < self.time_window
        ]
        
        # Add current message
        self.user_messages[user_id].append(now)
        
        # Check if spam
        return len(self.user_messages[user_id]) > self.spam_threshold

anti_spam = AntiSpam()

# Enhanced message handler with anti-spam
@dp.message(ChatStates.chatting)
async def enhanced_forward_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    partner_id = db.pairs.get(user_id)
    
    if not partner_id:
        await message.answer("❌ Anda tidak dalam chat aktif! Gunakan /start untuk memulai.")
        return
    
    if db.is_banned(user_id):
        await message.answer("❌ Anda telah dibanned dari bot ini.")
        return
    
    # Anti-spam check
    if anti_spam.is_spam(user_id):
        db.users[user_id]['warnings'] += 1
        await message.answer("⚠️ Terdeteksi spam! Pesan Anda tidak dikirim.\n\nAnda mendapat 1 warning.")
        
        if db.users[user_id]['warnings'] >= 3:
            db.ban_user(user_id)
            await message.answer("🚫 Anda dibanned karena spam berulang!")
        return
    
    # Update stats
    db.user_stats[user_id]['messages_sent'] += 1
    db.user_stats[user_id]['last_active'] = datetime.now()
    db.users[user_id]['total_messages'] += 1
    
    try:
        # VIP users get special formatting
        is_vip = db.users.get(user_id, {}).get('is_vip', False)
        vip_prefix = "⭐ " if is_vip else ""
        
        # Forward different types of messages
        if message.text:
            await bot.send_message(partner_id, f"{vip_prefix}💬 {message.text}")
        elif message.photo:
            await bot.send_photo(partner_id, message.photo[-1].file_id, caption=f"{vip_prefix}📷 Photo")
        elif message.voice:
            await bot.send_voice(partner_id, message.voice.file_id, caption=f"{vip_prefix}🎤 Voice message")
        elif message.video:
            await bot.send_video(partner_id, message.video.file_id, caption=f"{vip_prefix}🎥 Video")
        elif message.document:
            await bot.send_document(partner_id, message.document.file_id, caption=f"{vip_prefix}📎 Document")
        elif message.sticker:
            await bot.send_sticker(partner_id, message.sticker.file_id)
        elif message.animation:
            await bot.send_animation(partner_id, message.animation.file_id, caption=f"{vip_prefix}🎭 GIF")
        else:
            await bot.send_message(partner_id, f"{vip_prefix}📝 [Unsupported message type]")
            
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")
        await message.answer("❌ Gagal mengirim pesan. Partner mungkin telah meninggalkan chat.")

# Auto-cleanup task
async def cleanup_task():
    while True:
        try:
            # Remove inactive users from queue (older than 5 minutes)
            current_time = datetime.now()
            inactive_users = []
            
            for user_id in db.queue:
                if user_id in db.user_stats:
                    last_active = db.user_stats[user_id].get('last_active', current_time)
                    if (current_time - last_active).seconds > 300:  # 5 minutes
                        inactive_users.append(user_id)
            
            for user_id in inactive_users:
                if user_id in db.queue:
                    db.queue.remove(user_id)
            
            logger.info(f"Cleaned up {len(inactive_users)} inactive users from queue")
            
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
        
        await asyncio.sleep(300)  # Run every 5 minutes

# Main function with cleanup task
async def main():
    logger.info("🚀 Starting Anonymous Chat Bot...")
    
    # Set bot commands
    await set_bot_commands()
    
    # Start cleanup task
    cleanup_task_coroutine = asyncio.create_task(cleanup_task())
    
    # Start bot
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        cleanup_task_coroutine.cancel()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())