from PIL import Image, ImageFont, ImageDraw
import random


async def blackjack_start(message, bot, deck):
    deal = {'dealer_cards': [], 'player_cards': []}
    deal_hand = {'dealer_cards': [], 'player_cards': []}
    score = {'dealer_score': 0, 'player_score': 0}
    background = Image.open('../pics/blackjack/felt_table.jpg')

    x = 0
    while x != 4:
        card = random.randint(1, 52)
        if deck[card]:
            deck[card] = 0
            x += 1

            value = card_value(card)

            if x % 2:
                deal_hand['dealer_cards'].append(value)
                if value == 1:
                    value = 11
                deal['dealer_cards'].append(Image.open('../pics/deck/{}.jpg'.format(card)))
                score['dealer_score'] += value
            else:
                deal_hand['player_cards'].append(value)
                deal['player_cards'].append(Image.open('../pics/deck/{}.jpg'.format(card)))
                score['player_score'] += value
        else:
            continue

    textOverlay = ImageDraw.Draw(background)
    font = ImageFont.truetype('impact.ttf', 36)
    textOverlay.text((520, 250), message.author.name, (0, 0, 0), font=font)

    background.paste(deal['dealer_cards'][0], (43, 50))
    background.paste(deal['dealer_cards'][1], (143, 50))
    background.paste(deal['player_cards'][0], (43, 305))
    background.paste(deal['player_cards'][1], (143, 305))

    background.save('../pics/blackjack/game{}.jpg'.format(message.author.id))
    background.close()

    deal['dealer_cards'][0].close()
    deal['player_cards'][1].close()
    deal['dealer_cards'][0].close()
    deal['player_cards'][1].close()

    with open('../pics/blackjack/game{}.jpg'.format(message.author.id), 'rb') as show:
        await bot.send_file(message.channel, show)

    return score, deal_hand


async def blackjack_hit(message, bot, deck, deal_hand, score, player, turn):
    deal = {'dealer_cards': [], 'player_cards': []}
    background = Image.open('../pics/blackjack/game{}.jpg'.format(message.author.id))

    card = random.randint(1, 52)
    while True:
        if deck[card]:
            deck[card] = 0
            break
        else:
            continue

    value = card_value(card)
    deal_hand[player].append(value)
    deal[player].append(Image.open('../pics/deck/{}.jpg'.format(card)))

    if player == 'player_cards':
        score['player_score'] += value
        background.paste(deal['player_cards'][-1], ((turn + 43), 305))
        deal['player_cards'][-1].close()
    elif player == 'dealer_cards':
        score['dealer_score'] += value
        background.paste(deal['dealer_cards'][-1], ((turn + 43), 50))
        deal['dealer_cards'][-1].close()

    background.save('../pics/blackjack/game{}.jpg'.format(message.author.id))
    background.close()

    with open('../pics/blackjack/game{}.jpg'.format(message.author.id), 'rb') as show:
        await bot.send_file(message.channel, show)

    return score, deal_hand


def card_value(number):
    if number > 39:
        number -= 39
    elif number > 26:
        number -= 26
    elif number > 13:
        number -= 13
    if 10 < number < 14:
        return 10
    else:
        return number


async def check_ace(message, bot, hand, score, prefix):
    if 1 in hand['player_cards']:
        await bot.send_message(message.channel, '```xl\nAce \'{0}high\' or \'{0}low\'?\n```'.format(prefix))
        while 1:
            def check(msg):
                if msg.content.startswith('{}high'.format(prefix)):
                    return msg.content.startswith('{}high'.format(prefix))
                if msg.content.startswith('{}low'.format(prefix)):
                    return msg.content.startswith('{}low'.format(prefix))

            message = await bot.wait_for_message(author=message.author, check=check, timeout=15.0,
                                                 channel=message.channel)
            if message.content == '{}high'.format(prefix):
                hand['player_cards'][hand['player_cards'].index(1)] = 11
                score['player_score'] += 10
                break
            if message.content == '{}low'.format(prefix):
                break
            else:
                await bot.send_message(message.channel, '```xl\nPlease enter if Ace is \'{0}high\' or \'{0}low\'\n```'
                                       .format(prefix))
    return
