import discord
import time

from database.DBHelper import create_connection, add_user, add_channel, add_server, remove_channel,\
    get_channel_permission, update_channel, remove_user, get_prefix, get_blacklist_users, get_casino_channel, \
    get_stream_channel
from support.SettingsHandler import set_server_prefix, set_channels, begin_game, end_game, set_blacklist, get_blacklist,\
    get_channels, set_streamer_user, get_streamer_user
from support.ActivityFunctions import help_me, meme_pic, imgur_meme, insult_me, either_or, rather, ow_stats, \
    google_trends, cursed_pic, youtube_search, price_is_right
from support.TwitchScraper import streamer_data
from casino.CasinoBotGames import slot_machine, black_jack, dice_roll
from casino.CasinoBotUtils import player_bank, show_pot, my_stats, lotto
from casino.CasinoBotDB import add_casino


bot = discord.Client()
DATABASE = '../database/UserData.db'
GAMES = ['slots', 'blackjack', 'dice', 'bank', 'jackpot', 'mystats', 'lotto']


async def bot_welcome(server):
    conn = create_connection(DATABASE)
    serverID = int(server.id)
    try:
        serverIcon = 'https://cdn.discordapp.com/icons/' + str(serverID) + '/' + server.icon + '.png'
    except TypeError:
        serverIcon = 0

    add_server(conn, serverID, server.name, int(server.owner.id), server.owner.name, serverIcon)

    prefix = get_prefix(conn, serverID)[0]

    server = bot.get_server(str(serverID))
    for member in server.members:
        add_user(conn, serverID, int(member.id), member.name)
        add_casino(conn, int(member.id))

    server = bot.get_server(str(serverID))
    for channel in server.channels:
        if str(channel.type) == "text":
            add_channel(conn, serverID, int(channel.id), channel.name)

    conn.commit()
    conn.close()

    welcomeLine1 = "Use {}help to see Doo Bot commands".format(prefix)

    adminBed = discord.Embed(colour=0xFF00FF)
    adminBed.set_author(name="Doo Bot", icon_url="http://www3.pictures.zimbio.com/mp/OLESKRmZW6Al.jpg")
    adminBed.set_footer(text=" Website coming soon | Github coming soon ")
    adminBed.set_thumbnail(url="https://www.mydish.com/filestream.ashx?ID=17612")
    adminBed.add_field(name="Thanks for using Doo Bot! Below are some admin commands and configurations.",
                       value="Here are some admin commands that only you are able to use")
    adminBed.add_field(name="{}prefix".format(prefix), value="This changes the prefixes Doo Bot will listen for. "
                                                             "By default the prefix is {}.".format(prefix))
    adminBed.add_field(name="{}addchannels".format(prefix), value="Add channels that Doo Bot will listen too. "
                                                                  "By default, it is all channels.")
    adminBed.add_field(name="{}removechannels".format(prefix), value="Remove channels that Doo Bot will listen too. "
                                                                     "If all channels are removed, Doo Bot will listen"
                                                                     "too all channels.")
    await bot.send_message(server.owner, embed=adminBed)

    welcomeBed = discord.Embed(title="Doo Bot", description="Version 4.0.0", color=0x00FFFF)
    welcomeBed.add_field(name="Thanks for choosing Doo Bot:", value=welcomeLine1)
    welcomeBed.set_footer(text=" Website coming soon | Github coming soon ")
    welcomeBed.set_thumbnail(url="http://www3.pictures.zimbio.com/mp/OLESKRmZW6Al.jpg")

    for channel in server.channels:
        if str(channel.type) == 'text':
            await bot.send_message(channel, embed=welcomeBed)
            break


async def twitch_poster(after):
    conn = create_connection(DATABASE)
    streamerInfo = streamer_data(str(after.game.url))
    streamChannels = get_stream_channel(conn, int(after.server.id))
    streamChannels = [x[0] for x in streamChannels]

    if len(streamChannels) == 0:
        return

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

    if len(streamChannels) == 1:
        channel = bot.get_channel(str(streamChannels[0]))
        await bot.send_message(channel, "@here, {} is now live on Twitch, don't miss them!".format(after.name))
        await bot.send_message(channel, embed=twitchbed)
    else:
        for channelId in streamChannels:
            channel = bot.get_channel(str(channelId))
            await bot.send_message(channel, "@here, {} is now live on Twitch, don't miss them!".format(after.name))
            await bot.send_message(channel, embed=twitchbed)


async def dispatch(message):
    try:
        text = str(message.content)[1:].split()[0].lower()
    except IndexError:
        return

    if text in GAMES:
        await dispatch_casino(message, text)
        return

    conn = create_connection(DATABASE)

    if not message.server.owner.id == message.author.id:
        allowedChannels = get_channel_permission(conn, int(message.server.id))
        allowedChannels = [x[0] for x in allowedChannels]
        if int(message.channel.id) not in allowedChannels:
            if len(allowedChannels):
                return

    blacklist = get_blacklist_users(conn, int(message.server.id))
    if int(message.author.id) in blacklist:
        return

    # User Commands
    if text == 'help':
        await help_me(message, bot)
        return
    if text == 'meme':
        await meme_pic(message, bot)
        return
    if text == 'weird':
        await cursed_pic(message, bot)
        return
    if text == 'youtube':
        await youtube_search(message, bot)
        return
    if text == 'wouldyou':
        await rather(message, bot)
        return
    if text == 'either':
        await either_or(message, bot)
        return
    if text == 'insult':
        await insult_me(message, bot)
        return
    if text == 'imgur':
        await imgur_meme(message, bot)
        return
    if text == 'overwatch':
        await ow_stats(message, bot)
        return

    # Game Commands
    if text == 'comeondown':
        if begin_game(message.server.id):
            await price_is_right(message, bot)
            end_game(message.server.id)
        return
    if text == 'trends':
        if begin_game(message.server.id):
            await google_trends(message, bot)
            end_game(message.server.id)
        return

    # Admin Commands
    if message.server.owner.id == message.author.id:
        if text == 'prefix':
            conn = create_connection(DATABASE)
            await set_server_prefix(conn, message, bot)
            return
        if text == 'addchannels':
            conn = create_connection(DATABASE)
            await set_channels(conn, message, bot, "add")
            return
        if text == 'removechannels':
            conn = create_connection(DATABASE)
            await set_channels(conn, message, bot, "remove")
            return
        if text == 'addstreamer':
            conn = create_connection(DATABASE)
            await set_streamer_user(conn, message, bot, "add")
            return
        if text == 'removestreamer':
            conn = create_connection(DATABASE)
            await set_streamer_user(conn, message, bot, "remove")
            return
        if text == 'streamer':
            conn = create_connection(DATABASE)
            await get_streamer_user(conn, message, bot)
            return
        if text == 'addstream':
            conn = create_connection(DATABASE)
            await set_channels(conn, message, bot, "add", chan_type='stream')
            return
        if text == 'removestream':
            conn = create_connection(DATABASE)
            await set_channels(conn, message, bot, "remove", chan_type='stream')
            return
        if text == 'addcasino':
            conn = create_connection(DATABASE)
            await set_channels(conn, message, bot, "add", chan_type='casino')
            return
        if text == 'removecasino':
            conn = create_connection(DATABASE)
            await set_channels(conn, message, bot, "remove", chan_type='casino')
            return
        if text == 'channels':
            conn = create_connection(DATABASE)
            await get_channels(conn, message, bot)
            return
        if text == 'addblacklist':
            conn = create_connection(DATABASE)
            await set_blacklist(conn, message, bot, "add")
            return
        if text == 'removeblacklist':
            conn = create_connection(DATABASE)
            await set_blacklist(conn, message, bot, "remove")
            return
        if text == 'blacklist':
            conn = create_connection(DATABASE)
            await get_blacklist(conn, message, bot)
            return


async def dispatch_casino(message, text):
    conn = create_connection(DATABASE)
    if not message.server.owner.id == message.author.id:
        casinoChannels = get_casino_channel(conn, int(message.server.id))
        casinoChannels = [x[0] for x in casinoChannels]
        if int(message.channel.id) not in casinoChannels:
            if len(casinoChannels):
                return

    if text == 'bank':
        await player_bank(message, bot)
        return
    if text == 'slots':
        await slot_machine(message, bot)
        return
    if text == 'dice':
        await dice_roll(message, bot)
        return
    if text == 'blackjack':
        await black_jack(message, bot)
        return
    if text == 'jackpot':
        await show_pot(message, bot)
        return
    if text == 'mystats':
        await my_stats(message, bot)
        return

    if message.server.owner.id == message.author.id:
        if text == 'lotto':
            await lotto(message, bot)
            return


@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='Skittlely\'s Fun House', type=0))


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    conn = create_connection(DATABASE)

    if message.content.startswith(get_prefix(conn, int(message.server.id))[0]):
        await dispatch(message)
        return


@bot.event
async def on_member_join(member):
    conn = create_connection(DATABASE)
    add_user(conn, int(member.server.id), int(member.id), member.name)
    return


@bot.event
async def on_member_remove(member):
    conn = create_connection(DATABASE)
    remove_user(conn, int(member.server.id), int(member.id))
    return


@bot.event
async def on_channel_delete(channel):
    conn = create_connection(DATABASE)
    remove_channel(conn, int(channel.id))
    return


@bot.event
async def on_channel_create(channel):
    conn = create_connection(DATABASE)
    try:
        add_channel(conn, int(channel.server.id), int(channel.id), channel.name)
    except AttributeError:
        pass
    return


@bot.event
async def on_channel_update(before, after):
    if str(after.type) == "text":
        conn = create_connection(DATABASE)
        update_channel(conn, int(after.id), after.name)
    return


@bot.event
async def on_server_join(server):
    await bot_welcome(server)


@bot.event
async def on_server_update(before, after):
    conn = create_connection(DATABASE)
    prefix = get_prefix(conn, int(after.id))
    try:
        serverIcon = 'https://cdn.discordapp.com/icons/{}/{}.png'.format(after.id, after.icon)
    except TypeError:
        serverIcon = 0
    add_server(conn, int(after.id), after.name, int(after.owner.id), after.owner.name, serverIcon, prefix=prefix[0])
    return


@bot.event
async def on_member_update(before, after):
    try:
        if after.game.type == 1:
            await twitch_poster(after)
    except AttributeError:
        return


bot.run("Mzk0MTc3NDYxMzcxNTM1Mzcz.DSAiBA.UL5bgEO3ulxhfFgaHvLiKWTt03o")
