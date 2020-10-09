from database.DBHelper import add_channel_permission, get_channel_permission, remove_channel_permission, set_prefix, \
    add_blacklist_user, get_blacklist_users, remove_blacklist_user, add_stream_channel, add_casino_channel, \
    get_stream_channel, get_casino_channel, remove_stream_channel, remove_casino_channel, add_streamer, get_streamer, \
    remove_streamer
from discord import utils, ChannelType
from discord.errors import Forbidden

CURRENT_GAMES = []


async def set_server_prefix(conn, message, bot):
    if len(message.content.split()) != 2:
        await bot.send_message(message.channel, "Invalid input")
        return
    prefix = message.content.split()[1]
    if len(prefix) != 1:
        await bot.send_message(message.channel, "Only single symbols are allowed")
        return

    set_prefix(conn, prefix, int(message.server.id))
    await bot.send_message(message.channel, "@everyone Prefix changed to {0} \n(e.g. {0}meme)".format(prefix))
    return


async def set_channels(conn, message, bot, mod, chan_type="permission"):
    channelsNotPresent = []
    allowedChannels = []
    channels = message.content.split()
    if len(channels) < 2:
        await bot.send_message(message.channel, "You didn't enter any channels")
        return

    if mod == "add":
        for name in channels[1:]:
            try:
                channel = utils.get(message.server.channels, name=name, type=ChannelType.text)
                if chan_type == 'permission':
                    add_channel_permission(conn, int(channel.server.id), int(channel.id), channel.name)
                elif chan_type == 'stream':
                    add_stream_channel(conn, int(channel.server.id), int(channel.id), channel.name)
                elif chan_type == 'casino':
                    add_casino_channel(conn, int(channel.server.id), int(channel.id), channel.name)
            except AttributeError:
                channelsNotPresent.append(name)
    elif mod == "remove":
        for name in channels[1:]:
            try:
                channel = utils.get(message.server.channels, name=name, type=ChannelType.text)
                if chan_type == 'permission':
                    remove_channel_permission(conn, int(channel.id))
                elif chan_type == 'stream':
                    remove_stream_channel(conn, int(channel.id))
                elif chan_type == 'casino':
                    remove_casino_channel(conn, int(channel.id))
            except AttributeError:
                channelsNotPresent.append(name)

    if chan_type == 'permission':
        allowedChannels = get_channel_permission(conn, int(message.server.id))
        if len(allowedChannels) == 0:
            await bot.send_message(message.channel, "@everyone")
            await bot.send_message(message.channel, "Doo Bot callable in all channels")
            if len(channelsNotPresent) != 0:
                await bot.send_message(message.channel,
                                       "Channel(s) `{}` not found".format(', '.join(channelsNotPresent)))
            return
    elif chan_type == 'stream':
        allowedChannels = get_stream_channel(conn, int(message.server.id))
        if len(allowedChannels) == 0:
            await bot.send_message(message.channel, "No stream channel set")
            if len(channelsNotPresent) != 0:
                await bot.send_message(message.channel,
                                       "Channel(s) `{}` not found".format(', '.join(channelsNotPresent)))
            return
    elif chan_type == 'casino':
        allowedChannels = get_casino_channel(conn, int(message.server.id))
        if len(allowedChannels) == 0:
            await bot.send_message(message.channel, "@everyone")
            await bot.send_message(message.channel, "Casino callable in all channels")
            if len(channelsNotPresent) != 0:
                await bot.send_message(message.channel,
                                       "Channel(s) `{}` not found".format(', '.join(channelsNotPresent)))
            return

    allowedChannels = [x[1] for x in allowedChannels]
    allowedChannels = "\n".join(allowedChannels)

    await bot.send_message(message.channel, "@everyone")
    if chan_type == 'permission':
        await bot.send_message(message.channel, "```css\n[Allowed Channels]\n{}```".format(allowedChannels))
    if chan_type == 'stream':
        await bot.send_message(message.channel, "```css\n[Stream Channels]\n{}```".format(allowedChannels))
    if chan_type == 'casino':
        await bot.send_message(message.channel, "```css\n[Casino Channels]\n{}```".format(allowedChannels))

    if len(channelsNotPresent) != 0:
        await bot.send_message(message.channel, "Channel(s) `{}` not found".format(', '.join(channelsNotPresent)))
    return


async def get_channels(conn, message, bot):
    callableChannels = get_channel_permission(conn, int(message.server.id))
    streamChannel = get_stream_channel(conn, int(message.server.id))
    casinoChannels = get_casino_channel(conn, int(message.server.id))

    if callableChannels:
        callableChannels = [x[1] for x in callableChannels]
        callableChannels = "\n".join(callableChannels)
    else:
        callableChannels = 'Doo Bot is callable in all channels'

    if streamChannel:
        streamChannel = [x[1] for x in streamChannel]
        streamChannel = "\n".join(streamChannel)
    else:
        streamChannel = 'No stream channel set'

    if casinoChannels:
        casinoChannels = [x[1] for x in casinoChannels]
        casinoChannels = "\n".join(casinoChannels)
    else:
        casinoChannels = 'Casino functions in all channels'

    await bot.send_message(message.channel, "```css\n[Allowed Channels]\n{}```".format(callableChannels))
    await bot.send_message(message.channel, "```css\n[Stream Channel]\n{}```".format(streamChannel))
    await bot.send_message(message.channel, "```css\n[Casino Channels]\n{}```".format(casinoChannels))
    return


async def set_blacklist(conn, message, bot, mod):
    try:
        name = message.content.split(' ', 1)[1]
    except IndexError:
        await bot.send_message(message.channel, "You need to enter a name (Only one)")
        return

    user = utils.get(message.server.members, name=name)
    if user is None:
        await bot.send_message(message.channel, "User `{}` not found (check spelling?)".format(name))
        return

    if mod == "add":
        if int(message.server.owner.id) == int(user.id):
            await bot.send_message(message.channel, "You cannot blacklist yourself")
            return

        add_blacklist_user(conn, int(message.server.id), int(user.id), user.name)
        await bot.send_message(message.channel, "User `{}` added to blacklist".format(user.name))
        try:
            await bot.send_message(user, "You have been blacklisted from `{}` by `{}`"
                                   .format(message.server.name, message.server.owner.name))
        except Forbidden:
            return
    elif mod == "remove":
        remove_blacklist_user(conn, int(message.server.id), int(user.id))
        await bot.send_message(message.channel, "User `{}` removed from blacklist".format(user.name))


async def get_blacklist(conn, message, bot):
    blacklistData = get_blacklist_users(conn, int(message.server.id))
    if not blacklistData:
        await bot.send_message(message.channel, "No Users blacklisted")
        return

    blacklistData = [x[1] for x in blacklistData]
    blacklistUsers = "\n".join(blacklistData)

    await bot.send_message(message.channel, "```css\n[Blacklisted Users]\n{}```".format(blacklistUsers))
    return


async def set_streamer_user(conn, message, bot, mod):
    usersNotPresent = []
    allowedStreamers = []
    users = message.content.split()
    if len(users) < 2:
        await bot.send_message(message.channel, "You need to enter a user")
        return

    if mod == 'add':
        name = message.content.replace('!addstreamer ', '')
        try:
            user = utils.get(message.server.members, name=name)
            add_streamer(conn, int(message.server.id), int(user.id), user.name)
        except AttributeError:
            usersNotPresent.append(name)
    if mod == 'remove':
        name = message.content.replace('!removestreamer ', '')
        try:
            user = utils.get(message.server.members, name=name)
            remove_streamer(conn, int(message.server.id), int(user.id))
        except AttributeError:
            usersNotPresent.append(name)

    allowedStreamers = get_streamer(conn, int(message.server.id))

    if len(allowedStreamers) == 0:
        await bot.send_message(message.channel, "No streamers")
        if len(usersNotPresent) != 0:
            await bot.send_message(message.channel,
                                   "User `{}` not found".format(', '.join(usersNotPresent)))
        return

    allowedStreamers = [x[1] for x in allowedStreamers]
    allowedStreamers = "\n".join(allowedStreamers)

    await bot.send_message(message.channel, "```css\n[Streaming Users]\n{}```".format(allowedStreamers))
    if len(usersNotPresent) != 0:
        await bot.send_message(message.channel, "User `{}` not found".format(', '.join(usersNotPresent)))
    return


async def get_streamer_user(conn, message, bot):
    streamerData = get_streamer(conn, int(message.server.id))
    if not streamerData:
        await bot.send_message(message.channel, "No users streaming")
        return

    streamerData = [x[1] for x in streamerData]
    streamUsers = "\n".join(streamerData)

    await bot.send_message(message.channel, "```css\n[Streaming Users]\n{}```".format(streamUsers))
    return


def begin_game(serverID):
    if serverID in CURRENT_GAMES:
        return False
    else:
        CURRENT_GAMES.append(serverID)
        return True


def end_game(serverID):
    CURRENT_GAMES.remove(serverID)
