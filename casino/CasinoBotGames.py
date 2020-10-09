import random
import discord
from casino.CasinoBotUtils import validate_play
from casino.CasinoBotDB import set_player_plays, add_funds, remove_funds, update_money_won, update_money_lost, \
    update_jackpot
from casino.BlackjackUtils import blackjack_start, blackjack_hit, check_ace
from database.DBHelper import create_connection, get_prefix

SLOT_PATTERN = [':eggplant:', ':poop:', ':heart:', ':thumbsdown:', ':grin:']
DATABASE = "../database/UserData.db"


async def slot_machine(message, bot):
    amount = await validate_play(message, bot)
    if amount < 0:
        return

    conn = create_connection(DATABASE)
    set_player_plays(conn, int(message.author.id), "slots")
    slotbed = discord.Embed(title=message.author.name, colour=0x00FFFF)

    col1 = random.randint(0, 4)
    col2 = random.randint(0, 4)
    col3 = random.randint(0, 4)

    if col1 == col2 == col3:
        amount *= 10
        add_funds(conn, int(message.author.id), amount)
        update_money_won(conn, int(message.author.id), amount)
        slotbed.add_field(name='JACKPOT WIN!', value='```xl\nYOU WIN ${}```'.format(amount))
        slotbed.set_image(url='https://bpsh2.hs.llnwd.net/e1/contenthub-cdn-origin/media/casinoeuro/casinoeuro_blog/'
                              'Blog_1140x400_Top_5_Jackpots_1000.jpg')
    elif col1 == col2 or col2 == col3:
        if (col1 == 2 and col2 == 2) or (col2 == 2 and col3 == 2):
            amount *= 2
            add_funds(conn, int(message.author.id), amount)
            update_money_won(conn, int(message.author.id), amount)
            slotbed.add_field(name='HEARTS WIN!', value='```xl\nYou win ${}```'.format(amount))
            slotbed.set_thumbnail(url='http://www.imagefully.com/wp-content/uploads/2015/07/Cute-Two-Heart-Picture-'
                                      'Share-On-Whats-App-1024x768.jpg')
        else:
            slotbed.add_field(name='MONEY BACK!', value='```xl\nMoney back```'.format(amount))
            slotbed.set_thumbnail(url='http://www.netentstalker.com/wp-content/uploads/2015/08/Spin-Party-Slot-Bar-'
                                      'Symbol.jpg')
    else:
        remove_funds(conn, int(message.author.id), amount)
        update_money_lost(conn, int(message.author.id), amount)
        update_jackpot(conn, int(message.server.id), int(amount / 4))
        slotbed.add_field(name='LOSS, TRY AGAIN!', value='```xl\nYou lose ${}```'.format(amount))

    slotbed.add_field(name='SLOT MACHINE', value="[ {} | {} | {} ]".format(SLOT_PATTERN[col1], SLOT_PATTERN[col2],
                                                                           SLOT_PATTERN[col3]), inline=False)
    await bot.send_message(message.channel, embed=slotbed)


async def dice_roll(message, bot):
    amount = await validate_play(message, bot)
    if amount < 0:
        return

    conn = create_connection(DATABASE)
    set_player_plays(conn, int(message.author.id), "dice")

    prefix = get_prefix(conn, int(message.server.id))[0]
    multiplier = 1.0

    await bot.send_message(message.channel, '```xl\n{0}: Guess if the roll is \'{1}even\' or \'{1}odd\' '
                                            '(Current Multiplier \'x{2}\')\n```'
                           .format(message.author.name, prefix, multiplier))
    while True:
        def check(msg):
            return msg.content.startswith(prefix)
        guess = await bot.wait_for_message(timeout=20, author=message.author, channel=message.channel, check=check)
        if guess is None:
            await bot.send_message(message.channel, '```xl\n{} timed out and loses bet of ${}\n```'
                                   .format(message.author.name, amount))
            remove_funds(conn, int(message.author.id), amount)
            update_money_lost(conn, int(message.author.id), amount)
            update_jackpot(conn, int(message.server.id), int(amount / 4))
            return
        if guess.content == '{}even'.format(prefix):
            pick = 0
            break
        if guess.content == '{}odd'.format(prefix):
            pick = 1
            break
        else:
            await bot.send_message(message.channel, '```xl\nTo guess use \'{0}even\' or \'{0}odd\'\n```'.format(prefix))

    while True:
        roll = random.randint(1, 6)
        chosenPic = '../pics/dice/Die{}.jpg'.format(roll)
        evenOdd = roll % 2

        with open(chosenPic, 'rb') as die:
            await bot.send_file(message.channel, die)
        if pick == evenOdd:
            multiplier += 0.2
            await bot.send_message(message.channel, '```xl\n{0} ROLL: {1}\nGuess again to increase your winnings '
                                                    'multiplier or cash out (Current Multiplier \'x{2}\')\nUse \''
                                                    '{3}even\' or \'{3}odd\' to go again or \'{3}quit\' to cash out\n```'
                                   .format(message.author.name, roll, float(multiplier), prefix))

            def check(msg):
                return msg.content.startswith(prefix)

            guess = await bot.wait_for_message(timeout=20, author=message.author, channel=message.channel,
                                               check=check)
            if guess is None:
                await bot.send_message(message.channel, '```xl\n{} timed out and loses bet of ${}\n```'
                                       .format(message.author.name, amount))
                remove_funds(conn, int(message.author.id), amount)
                update_money_lost(conn, int(message.author.id), amount)
                update_jackpot(conn, int(message.server.id), int(amount / 4))
                return
            if guess.content == '{}even'.format(prefix):
                pick = 0
            elif guess.content == '{}odd'.format(prefix):
                pick = 1
            elif guess.content == '{}quit'.format(prefix):
                await bot.send_message(message.channel, '```xl\n{} wins ${}\n```'
                                       .format(message.author.name, int(amount * multiplier)))
                add_funds(conn, int(message.author.id), int(amount * multiplier))
                update_money_won(conn, int(message.author.id), amount)
                return
            else:
                await bot.send_message(message.channel, '```xl\nTo guess use \'{0}even\' or \'{0}odd\'\n```'
                                       .format(prefix))
        else:
            await bot.send_message(message.channel, '```xl\n{} loses bet of ${}\n```'
                                   .format(message.author.name, amount))
            remove_funds(conn, int(message.author.id), amount)
            update_money_lost(conn, int(message.author.id), amount)
            update_jackpot(conn, int(message.server.id), int(amount / 4))
            return


# '!blackjack' -Plays Blackjack Game
async def black_jack(message, bot):
    amount = await validate_play(message, bot)
    if amount < 0:
        return

    conn = create_connection(DATABASE)
    set_player_plays(conn, int(message.author.id), "blackjack")

    prefix = get_prefix(conn, int(message.server.id))[0]
    deck = [1] * 54
    player_turn = 200
    dealer_turn = 200

    score = await blackjack_start(message, bot, deck)
    hand = score[1]
    score = score[0]

    await check_ace(message, bot, hand, score, prefix)

    if score['player_score'] == 21:
        amount *= 2
        add_funds(conn, int(message.author.id), amount)
        update_money_won(conn, int(message.author.id), amount)

    await bot.send_message(message.channel, '```xl\n\'{0}hit\'  : or :  \'{0}stay\'\n```'.format(prefix))
    while True:
        def check(msg):
            if msg.content.startswith('{}hit'.format(prefix)):
                return msg.content.startswith('{}hit'.format(prefix))
            if msg.content.startswith('{}stay'.format(prefix)):
                return msg.content.startswith('{}stay'.format(prefix))

        hit = await bot.wait_for_message(author=message.author, check=check, channel=message.channel)

        if hit is None:
            await bot.send_message(message.channel, '```xl\n{} timed out and loses bet of ${}\n```'
                                   .format(message.author.name, amount))
            remove_funds(conn, int(message.author.id), amount)
            update_money_lost(conn, int(message.author.id), amount)
            update_jackpot(conn, int(message.server.id), int(amount / 4))
            return
        if hit.content == '{}hit'.format(prefix):
            score = await blackjack_hit(message, bot, deck, hand, score, 'player_cards', player_turn)
            player_turn += 100
            hand = score[1]
            score = score[0]

            await check_ace(message, bot, hand, score, prefix)

            if score['player_score'] > 21:
                remove_funds(conn, int(message.author.id), amount)
                update_money_lost(conn, int(message.author.id), amount)
                update_jackpot(conn, int(message.server.id), int(amount / 4))
                await bot.send_message(message.channel, '```xl\n{} busts, and loses ${}\n```'
                                       .format(message.author.name, amount))
                return

        if hit.content == '{}stay'.format(prefix):
            break
        else:
            await bot.send_message(message.channel, '```xl\nPlease choose \'{0}hit\'  : or :  \'{0}stay\'\n```'
                                   .format(prefix))

    while True:
        if score['dealer_score'] < score['player_score']:
            score = await blackjack_hit(message, bot, deck, hand, score, 'dealer_cards', dealer_turn)
            dealer_turn += 100
            hand = score[1]
            score = score[0]
        elif score['dealer_score'] == score['player_score']:
            await bot.send_message(message.channel, 'Draw, {}: Money back!'.format(message.author.name))
            return
        elif score['dealer_score'] < 22:
            remove_funds(conn, int(message.author.id), amount)
            update_money_lost(conn, int(message.author.id), amount)
            update_jackpot(conn, int(message.server.id), int(amount / 4))
            await bot.send_message(message.channel, '```xl\n{} you lose ${}!\n```'.format(message.author.name, amount))
            return
        elif score['dealer_score'] > 21:
            add_funds(conn, int(message.author.id), amount)
            update_money_won(conn, int(message.author.id), amount)
            await bot.send_message(message.channel, '```xl\n{} you win ${}!\n```'.format(message.author.name, amount))
            return
