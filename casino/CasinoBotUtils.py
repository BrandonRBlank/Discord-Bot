import discord
import random
from casino.CasinoBotDB import get_player_bank, get_jackpot, get_player_stats, update_jackpot, add_funds
from database.DBHelper import create_connection
from database.DBHelper import get_users

SERVER_ROLES = ['Peasant', 'Tourist', 'Rich Boi', 'High Roller', 'VIP Club', 'VIP Elite', 'Kingpin']
DATABASE = "../database/UserData.db"


# USER COMMANDS---------------------------------------------------------------------------------------------------------
# 'bank' -Shows Player Bank
async def player_bank(message, bot):
    conn = create_connection(DATABASE)
    bank = get_player_bank(conn, int(message.author.id))
    await bot.send_message(message.channel, '```xl\n{}: ${}\n```'.format(message.author.name, bank))


# 'jackpot' -Shows Current Jackpot Amount
async def show_pot(message, bot):
    conn = create_connection(DATABASE)
    pot = get_jackpot(conn, int(message.server.id))
    await bot.send_message(message.channel, 'Current Jackpot is at ${}'.format(pot))


# 'mystats' -Shows player's stats for the casino
async def my_stats(message, bot):
    conn = create_connection(DATABASE)
    stats = get_player_stats(conn, int(message.author.id))

    statbed = discord.Embed(colour=0x00FFFF)
    statbed.set_author(name='{}\'s Casino Stats'.format(message.author.name), icon_url=message.author.avatar_url)
    statbed.set_thumbnail(url='https://pbs.twimg.com/profile_images/518176678384648192/h9VHq2Y2_400x400.png')
    statbed.add_field(name='Blackjack Plays', value=stats[1], inline=False)
    statbed.add_field(name='Dice Plays', value=stats[2], inline=False)
    statbed.add_field(name='Slots Plays', value=stats[3], inline=False)
    statbed.add_field(name='Money Won', value='${}'.format(stats[4]))
    statbed.add_field(name='Money Lost', value='${}'.format(stats[5]))
    await bot.send_message(message.channel, embed=statbed)


# ADMIN FUNCTIONS ------------------------------------------------------------------------------------------------------
async def lotto(message, bot):
    winner = ""
    conn = create_connection(DATABASE)
    jackpot = get_jackpot(conn, int(message.server.id))
    if not jackpot:
        await bot.send_message(message.channel, 'The current Jackpot is at $0')
        return

    users = get_users(conn, int(message.server.id))

    while True:
        try:
            winner = random.choice(users)
            winnerObj = await bot.get_user_info(str(winner[1]))
            if winnerObj.bot:
                raise AttributeError
            break
        except AttributeError:
            users.remove(winner)
            pass

    lottobed = discord.Embed(title='{} IS THE LOTTO WINNER!'.format(winner[0]), color=0x00FFFF)
    lottobed.add_field(name='Today\'s Winnings', value='${}'.format(jackpot))
    lottobed.set_thumbnail(url=winnerObj.avatar_url)
    lottobed.set_image(url='https://localtvktvi.files.wordpress.com/2011/12/lotto-winner.jpg?quality=85&strip=all&w=770')

    add_funds(conn, winner[1], jackpot)
    update_jackpot(conn, int(message.server.id), 0, empty=True)

    mentionName = '<@{}>'.format(winner[1])
    await bot.send_message(message.channel, mentionName)
    await bot.send_message(message.channel, embed=lottobed)


# UTILITY FUNCTIONS-----------------------------------------------------------------------------------------------------
async def validate_play(message, bot):
    conn = create_connection(DATABASE)
    try:
        money = message.content.split()[1]
        money = int(money)
    except ValueError:
        await bot.send_message(message.channel, 'You need to enter an integer amount')
        return -1
    except IndexError:
        await bot.send_message(message.channel, 'You need to enter an amount')
        return -1
    if money < 1:
        await bot.send_message(message.channel, 'You need to enter a positive amount')
        return -1

    bank = get_player_bank(conn, int(message.author.id))
    if bank < money:
        await bot.send_message(message.channel, 'You don\'t have enough money')
        return -1
    return money


"""
async def check_tier(author, bot, database):
    adminRoleName = "Cool Kids Club"
    if '374700251610873856' != str(author.server.id):  # TODO: this is 'botopia, need to change to Kettlecorn when ready
        return
    cash = fetch_user_data(database, "SELECT bank FROM UserData WHERE ident=? AND server=?",
                           (author.id, author.server.id))  # TODO: Change server here too
    roleName = list(inside.name for inside in author.server.roles)
    roles = list(inside for inside in author.server.roles)
    adminRoleRole = roleName.index(adminRoleName)

    if cash < 1000:
        newTier = roleName.index(SERVER_ROLES[0])
        if adminRoleName in roleName:
            await bot.replace_roles(author, roles[adminRoleRole], roles[newTier])
        else:
            await bot.replace_roles(author, roles[newTier])
        return
    if cash < 10000:
        newTier = roleName.index(SERVER_ROLES[1])
        if adminRoleName in roleName:
            await bot.replace_roles(author, roles[adminRoleRole], roles[newTier])
        else:
            await bot.replace_roles(author, roles[newTier])
        return
    if cash < 20000:
        newTier = roleName.index(SERVER_ROLES[2])
        if adminRoleName in roleName:
            await bot.replace_roles(author, roles[adminRoleRole], roles[newTier])
        else:
            await bot.replace_roles(author, roles[newTier])
        return
    if cash < 50000:
        newTier = roleName.index(SERVER_ROLES[3])
        if adminRoleName in roleName:
            await bot.replace_roles(author, roles[adminRoleRole], roles[newTier])
        else:
            await bot.replace_roles(author, roles[newTier])
        return
    if cash < 100000:
        newTier = roleName.index(SERVER_ROLES[4])
        if adminRoleName in roleName:
            await bot.replace_roles(author, roles[adminRoleRole], roles[newTier])
        else:
            await bot.replace_roles(author, roles[newTier])
        return
    if cash < 250000:
        newTier = roleName.index(SERVER_ROLES[5])
        if adminRoleName in roleName:
            await bot.replace_roles(author, roles[adminRoleRole], roles[newTier])
        else:
            await bot.replace_roles(author, roles[newTier])
        return
    if cash < 1000000:
        newTier = roleName.index(SERVER_ROLES[6])
        if adminRoleName in roleName:
            await bot.replace_roles(author, roles[adminRoleRole], roles[newTier])
        else:
            await bot.replace_roles(author, roles[newTier])
        return
"""