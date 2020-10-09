import discord
from DooBotDBHelper import set_data, fetch_user_data
import os
import requests
import shutil


async def add_mod(message):
    print("poop")


async def set_twitch_channel(message, bot):
    database = "database/UserData.db"
    loc = fetch_user_data(database, "SELECT ServerID FROM Streamers WHERE UserID=?", (message.author.id,))
    userServer = bot.get_server(str(loc))
    for channel in userServer.channels:
        if str(message.content[8:]) == str(channel) and str(channel.type) == 'text':
            set_data(database, "UPDATE Streamers SET UserID=? WHERE ServerID=?",
                     (message.author.id, userServer.id))
            set_data(database, "UPDATE Streamers SET Channel=? WHERE ServerID=?",
                     (channel.id, userServer.id))
            await bot.send_message(message.channel, "Notification channel set to " + message.content[8:])
            return
    await bot.send_message(message.channel, "Channel not found!")


async def set_schedule(message, bot):
    try:
        os.makedirs("bin/" + str(message.server.id))
    except FileExistsError:
        pass
    try:
        r = requests.get(message.attachments[0]['url'], stream=True)
        if r.status_code == 200:
            with open("bin/" + str(message.server.id) + "/schedule.jpg", 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
    except Exception:
        bot.send_message(message.channel, "There was an error uploading file, please try again")
