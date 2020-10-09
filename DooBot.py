import discord
import time
import random
import urllib.request
import requests
from lxml import html
from bs4 import BeautifulSoup
from DooBotAdmin import set_twitch_channel, set_schedule
from DooBotDBHelper import make_data, create_connection, fetch_user_data, add_users, add_channel, add_server, get_owner
from TwitchScraper import streamer_data
# from DataTools import get_users, get_channels


bot = discord.Client()

INSULT_1 = ['lazy ', 'stupid ', 'slimy ', 'slutty ', 'smelly ', 'pompous ', 'communist ', 'dicknose ', 'pie-eating ',
            'racist ', 'white trash ', 'drug-loving ', 'butterface ', 'tone deaf ', 'creepy ', 'insecure ', 'idiotic ',
            'elitist ', 'ugly ']
INSULT_2 = ['douche ', 'ass ', 'turd ', 'rectum ', 'butt ', 'cock ', 'shit ', 'crotch ', 'bitch ', 'turd ', 'prick ',
            'slut ', 'taint ', 'fuck ', 'dick ', 'boner ', 'shart ', 'nut ', 'sphincter']
INSULT_3 = ['pilot', ' canoe', 'captain', 'pirate', 'hammer', 'knob', 'box', 'jockey', 'nazi', 'waffle', 'goblin',
            'blossum', 'biscuit', 'clown', 'socket', 'monster', 'hound', 'dragon', 'balloon']


async def bot_welcome(server):
    database = 'database/UserData.db'
    conn = create_connection(database)
    serverID = int(server.id)
    serverIcon = 'https://cdn.discordapp.com/icons/' + str(serverID) + '/' + server.icon + '.png'

    add_server(conn, serverID, server.name, int(server.owner.id), server.owner.name, serverIcon)

    server = bot.get_server(str(serverID))
    for member in server.members:
        add_users(conn, serverID, member.name, int(member.id))

    server = bot.get_server(str(serverID))
    for channel in server.channels:
        if str(channel.type) == "text":
            add_channel(conn, serverID, channel.name, int(channel.id))

    # with conn:
    #     userData = (serverID, ownerID)
    #     make_data(conn, "INSERT INTO Settings VALUES(?,?)", userData)
    #     make_data(conn, "INSERT INTO Moderators VALUES(?,?,?)", (serverID, "null", "null"))
    #     make_data(conn, "INSERT INTO Streamers VALUES(?,?,?)", (serverID, ownerID, "null"))
    conn.commit()
    conn.close()

    # TODO: Update welcome commands/ admin commands
    welcomeLine1 = "Use !help to see Doo Bot commands"
    adminCommands1 = "Thanks for using Doo Bot! Below are some admin commands and configurations. " \
                     "(You can use these command here in this private message)"
    adminCommands2 = "```css\n\'!twitch <discord text channel>\' - //The text channel you'd like to have your " \
                     "stream notifications posted to here on you Discord server" + \
                     "\n\'!setschedule\' - //Upload an image and add the comment !setschedule to set a schedule " \
                     "image for users to see\n```"

    await bot.send_message(server.owner, adminCommands1 + "\n\nAdmin Commands: \n" + adminCommands2)
    setBed = discord.Embed(title="Doo Bot", description="Version 3.0.0", color=0x00FFFF)
    setBed.add_field(name="Thanks for choosing Doo Bot:", value=welcomeLine1)
    setBed.set_footer(text=" Website coming soon | Github coming soon ")
    setBed.set_thumbnail(url="http://www3.pictures.zimbio.com/mp/OLESKRmZW6Al.jpg")

    for channel in server.channels:
        if str(channel.type) == 'text':
            await bot.send_message(channel, embed=setBed)
            break


async def dispatch(message):
    text = str(message.content)[1:].split()[0].lower()

    if text == 'help':
        await help_me(message)
        return
    if text == 'meme':
        await meme_pic(message)
        return
    if text == 'weird':
        await cursed_pic(message)
        return
    if text == 'youtube':
        await youtube_search(message)
        return
    if text == 'wouldyou':
        await rather(message)
        return
    if text == 'either':
        await either_or(message)
        return
    if text == 'insult':
        await insult_me(message)
        return
    if text == 'schedule':
        await get_schedule(message)
        return

    if text == 'tet':
        await tetting(message)
        return

    database = 'database/UserData.db'
    conn = create_connection(database)
    # loc = message.server.id
    # boss = fetch_user_data(database, "SELECT OwnerID FROM Settings WHERE ServerID=?", (loc,))
    # if int(message.server.owner.id) == int(boss):

    # Admin commands
    # if fetch_user_data(database, "SELECT OwnerID FROM Settings WHERE OwnerID=?", (message.author.id,)):
    if get_owner(conn, int(message.author.id), int(message.server.id)):
        if text.lower() == 'twitch':
            await set_twitch_channel(message, bot)
            return
        if text.lower() == 'setschedule':
            await set_schedule(message, bot)
            return


# REMOVE -> USED FOR TESTING
async def tetting(message):
    print(message.channel.type)


async def help_me(message):
    await bot.send_message(message.channel,
                           '\'!youtube <Search Term>\' to post a relevant video\n\n' +
                           '\'!meme\' for a dank meme\n\n' +
                           '\'!weird\' for some weird shit\n\n' +
                           '\'!overwatch\' to check Overwatch stats (Implemented soon)\n\n' +
                           '\'!wouldyou\' for a would-you-rather question\n\n' +
                           '\'!either\' for an either-or quandary\n\n' +
                           '\'!insult <Name>\' to insult someone\n\n' +
                           '\'!schedule\' to see streaming schedule')


async def meme_pic(message):
    picRoll = random.randint(1, 8)
    chosenPic = 'pics/meme/spicy'
    chosenPic += str(picRoll) + '.jpg'
    try:
        with open(chosenPic, 'rb') as f:
            await bot.send_file(message.channel, f)
    except FileNotFoundError:
        await bot.send_message(message.channel, 'Some dumb shit happened. Try again lol \n' +
                                                'Error Code: #100' + str(picRoll))


async def cursed_pic(message):
    picRoll = random.randint(1, 8)
    chosenPic = 'pics/cursed/cursed'
    chosenPic += str(picRoll) + '.jpg'
    try:
        with open(chosenPic, 'rb') as f:
            await bot.send_file(message.channel, f)
    except FileNotFoundError:
        await bot.send_message(message.channel, 'Some dumb shit happened. Try again lol \n' +
                               'Error Code: #200' + str(picRoll))


async def youtube_search(message):
    linkList = []
    textToSearch = message.content.replace('!youtube', '')
    await bot.send_message(message.channel, 'Searching YouTube for: ' + textToSearch)
    query = urllib.request.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html_s = response.read()
    soup = BeautifulSoup(html_s, "lxml")
    for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
        linkList.append('https://www.youtube.com' + vid['href'])
    # noinspection PyBroadException
    try:
        random_num = random.randint(0, len(linkList) - 1)
    except Exception:
        await bot.send_message(message.channel, 'There was an error. Try another search term')
        return


async def rather(message):
    page = requests.get('http://www.willyoupressthebutton.com/')
    tree = html.fromstring(page.content)
    WYRbed = discord.Embed(title='Would You?', colour=0x00FFFF)
    this = tree.xpath('/html/body/div[2]/div/div/div[2]/div/div[2]/div[1]/text()')
    that = tree.xpath('/html/body/div[2]/div/div/div[2]/div/div[2]/div[3]/text()')
    WYRbed.add_field(name='This:', value=this[0])
    WYRbed.add_field(name='But: ', value=that[0], inline=False)
    await bot.send_message(message.channel, embed=WYRbed)


async def either_or(message):
    page = requests.get('http://either.io/')
    pageView = page.text
    EObed = discord.Embed(title='Would You Rather:', colour=0x00FFFF)
    soup = BeautifulSoup(pageView, 'lxml')
    results = soup.find_all('span', {'class': 'option-text'})
    this = str(results[0])
    that = str(results[1])
    EObed.add_field(name='This:', value=this[26:-7])
    EObed.add_field(name='Or: ', value=that[26:-7], inline=False)
    await bot.send_message(message.channel, embed=EObed)


async def insult_me(message):
    randInsult1 = random.randint(0, 18)
    randInsult2 = random.randint(0, 18)
    randInsult3 = random.randint(0, 18)
    person = message.content[8:]

    if len(person) < 2:
        await bot.send_message(message.channel, 'You need to enter a person\'s name')
        return
    if str(person.lower()) == 'doobot' or str(person.lower()) == 'doo bot':
        await bot.send_message(message.channel, 'Nice try dummy!')
        return
    elif randInsult1 < 15:
        await bot.send_message(message.channel, person + ' you\'re a ' + INSULT_1[randInsult1] +
                               INSULT_2[randInsult2] + INSULT_3[randInsult3])
    else:
        await bot.send_message(message.channel, person + ' you\'re an ' + INSULT_1[randInsult1] +
                               INSULT_2[randInsult2] + INSULT_3[randInsult3])


async def twitch_poster(before, after):
    check = False
    try:
        if after.game.type == 1:
            check = True
    except AttributeError:
        pass
    try:
        if before.game.type == 1:
            check = True
    except AttributeError:
        pass

    if not check:
        return
    database = "database/UserData.db"
    try:
        loc = fetch_user_data(database, "SELECT Channel FROM Streamers WHERE ServerID=?", (after.server.id,))
        streamerInfo = streamer_data(str(after.game.url))
        channel = after.server.get_channel(str(loc))
        streamer = str(after)

        twitchbed = discord.Embed(title="↓ Watch them now! ↓", description=after.game.url, color=0xEE00EE)
        twitchbed.set_author(name=after.name + " is now streaming!", url=after.game.url,
                             icon_url="https://cdn.discordapp.com/attachments/395303394547466241/395754894096597002"
                                      "/287637883022737418.png")
        twitchbed.set_thumbnail(url=streamerInfo['logo'])
        twitchbed.add_field(name="Now Playing", value=streamerInfo['game'], inline=False)
        twitchbed.add_field(name="Stream Title", value=after.game, inline=False)
        twitchbed.add_field(name="Followers", value=streamerInfo['followers'], inline=True)
        twitchbed.add_field(name="Total Views", value=streamerInfo['views'], inline=True)
        if str(streamerInfo['banner']) != 'None':
            twitchbed.set_image(url=streamerInfo['banner'])
        twitchbed.set_footer(text="Website coming soon | Github coming soon | " +
                             str(time.strftime("%a %b %dth, %Y at %I:%M %p", time.localtime(time.time()))))

        await bot.send_message(channel, "@here, " + streamer + " is now live on Twitch, don't miss them!")
        await bot.send_message(channel, embed=twitchbed)
    except AttributeError:
        loc = fetch_user_data(database, "SELECT Channel FROM Streamers WHERE ServerID=?", (before.server.id,))
        channel = before.server.get_channel(str(loc))
        count = 0
        async for message in bot.logs_from(channel):
            if message.author == bot.user and count < 2:
                await bot.delete_message(message)
                count += 1

        streamerInfo = streamer_data(str(before.game.url))
        streamer = str(before)

        twitchbed = discord.Embed(title="↓ You can still follow! ↓", description=before.game.url, color=0xEE00EE)
        twitchbed.set_author(name=before.name + " is no longer streaming!", url=before.game.url,
                             icon_url="https://cdn.discordapp.com/attachments/395303394547466241/395754894096597002"
                                      "/287637883022737418.png")
        twitchbed.set_thumbnail(url=streamerInfo['logo'])
        twitchbed.add_field(name="Was Playing", value=streamerInfo['game'], inline=False)
        twitchbed.add_field(name="Stream Title", value=before.game, inline=False)
        twitchbed.add_field(name="Followers", value=streamerInfo['followers'], inline=True)
        twitchbed.add_field(name="Total Views", value=streamerInfo['views'], inline=True)
        if str(streamerInfo['banner']) != 'None':
            twitchbed.set_image(url=streamerInfo['banner'])
        twitchbed.set_footer(text="Website coming soon | Github coming soon | " +
                                  str(time.strftime("%a %b %dth, %Y at %I:%M %p", time.localtime(time.time()))))

        await bot.send_message(channel, streamer + " is now offline")
        await bot.send_message(channel, embed=twitchbed)


async def get_schedule(message):
    database = "database/UserData.db"
    user = fetch_user_data(database, "SELECT UserID FROM Streamers WHERE ServerID=?", (message.server.id,))
    await bot.send_message(message.channel, str(message.server.get_member(str(user))) + "'s current schedule:")
    try:
        with open("bin/" + str(message.server.id) + "/schedule.jpg", "rb") as f:
            await bot.send_file(message.channel, f)
    except FileNotFoundError:
        await bot.send_message(message.channel, "``` \n Currently no schedule posted \n ```")


@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='Skittlely\'s Fun House', type=0))


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.startswith('!'):
        await dispatch(message)
        return


# @bot.event
# async def on_member_join(member):
#     new_member(member)


@bot.event
async def on_server_join(server):
    await bot_welcome(server)


@bot.event
async def on_member_update(before, after):
    database = "database/UserData.db"
    loc = fetch_user_data(database, "SELECT ServerID FROM Streamers WHERE UserID=?", (before.id,))
    if str(loc) == str(before.server.id):
        await twitch_poster(before, after)

bot.run("Mzk0MTc3NDYxMzcxNTM1Mzcz.DSAiBA.UL5bgEO3ulxhfFgaHvLiKWTt03o")
