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
BOT_TOKEN = "8137029943:AAHBKhjI42Rk6AAJMd0nJ7JzDsez9TZQbKg"

# ID Admin (ganti dengan user ID admin)
ADMIN_IDS = [7466357779]  # Tambahkan ID admin di sini

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

# Main function
async def main():
    logger.info("🚀 Starting Anonymous Chat Bot...")
    
    # Set bot commands
    await set_bot_commands()
    
    # Start bot
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
