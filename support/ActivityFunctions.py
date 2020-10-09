import random
import urllib.request
import requests
import discord
from urllib.error import HTTPError
from lxml import html
from bs4 import BeautifulSoup
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError
import json
from json.decoder import JSONDecodeError
from concurrent.futures import CancelledError, TimeoutError
from scratch.OWLevel import get_level
from scratch.TrendTerms import trendTerms
from scratch.Insults import INSULT_1, INSULT_2, INSULT_3
from database.DBHelper import create_connection, get_ow_rank, get_prefix

DATABASE = '../database/UserData.db'


async def help_me(message, bot):
    conn = create_connection(DATABASE)
    prefix = get_prefix(conn, int(message.server.id))[0]

    helpBed = discord.Embed(colour=0xFF00FF)
    helpBed.set_author(name="Doo Bot", icon_url="http://www3.pictures.zimbio.com/mp/OLESKRmZW6Al.jpg")
    helpBed.set_footer(text=" Website coming soon | Github coming soon ")
    helpBed.set_thumbnail(url="https://www.mydish.com/filestream.ashx?ID=17612")
    helpBed.add_field(name="{}overwatch <BattleTag>".format(prefix), value="```fix\nGets Overwatch stats for entered player```")
    helpBed.add_field(name="{}youtube <Search Term>".format(prefix), value="```fix\nSearches Youtube and posts relevant video```")
    helpBed.add_field(name="{}insult <Name>".format(prefix), value="```fix\nInsults entered person```", inline=False)
    helpBed.add_field(name="{}imgur".format(prefix), value="```fix\nRandom image from Imgur's hot page```")
    helpBed.add_field(name="{}wouldyou".format(prefix), value="```fix\nAsks a would-you-rather question```")
    helpBed.add_field(name="{}either".format(prefix), value="```fix\nAsks an either-or quandary```", inline=False)
    helpBed.add_field(name="{}weird".format(prefix), value="```fix\nPosts some weird shit```", inline=False)
    helpBed.add_field(name="{}meme".format(prefix), value="```fix\nPosts a dank meme```")
    helpBed.add_field(name="{}comeondown".format(prefix), value="```fix\nStarts a Price is right game for up to 4 people```")
    helpBed.add_field(name="{}trends".format(prefix), value="```fix\nStarts a Google Trends game for up to 5 people```")

    await bot.send_message(message.channel, embed=helpBed)


async def meme_pic(message, bot):
    picRoll = random.randint(1, 8)
    chosenPic = '../pics/meme/spicy{}.jpg'.format(picRoll)
    try:
        with open(chosenPic, 'rb') as f:
            await bot.send_file(message.channel, f)
    except FileNotFoundError:
        await bot.send_message(message.channel, 'Image not found. Try again \nError Code: #100{}'.format(picRoll))


async def cursed_pic(message, bot):
    picRoll = random.randint(1, 8)
    chosenPic = '../pics/cursed/cursed{}.jpg'.format(picRoll)
    try:
        with open(chosenPic, 'rb') as f:
            await bot.send_file(message.channel, f)
    except FileNotFoundError:
        await bot.send_message(message.channel, 'Image not found. Try again \nError Code: #200{}'.format(picRoll))


async def youtube_search(message, bot):
    if len(message.content.split()) < 2:
        return

    conn = create_connection(DATABASE)
    linkList = []
    textToSearch = message.content.replace('{}youtube'.format(get_prefix(conn, int(message.server.id))[0]), '')
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
        random.randint(0, len(linkList) - 1)
    except Exception:
        await bot.send_message(message.channel, 'There was an error. Try another search term')
        return

    random_num = random.randint(0, 3)
    await bot.send_message(message.channel, linkList[random_num])


async def rather(message, bot):
    page = requests.get('http://www.willyoupressthebutton.com/')
    tree = html.fromstring(page.content)
    WYRbed = discord.Embed(title='Would You?', colour=0x00FFFF)
    this = tree.xpath('/html/body/div[2]/div/div/div[2]/div/div[2]/div[1]/text()')
    that = tree.xpath('/html/body/div[2]/div/div/div[2]/div/div[2]/div[3]/text()')
    WYRbed.add_field(name='This:', value=this[0])
    WYRbed.add_field(name='But: ', value=that[0], inline=False)
    await bot.send_message(message.channel, embed=WYRbed)


async def either_or(message, bot):
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


async def insult_me(message, bot):
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


async def imgur_meme(message, bot):
    clientId = 'b49ec8d9045f4ff'
    clientSecret = 'ff33b374c6c0faf7c591020cf621afdd963d1ea4'

    try:
        imager = ImgurClient(clientId, clientSecret)

        randPage = random.randint(0, 10)
        await bot.send_message(message.channel, "Fetching a spicy one...")
        items = imager.gallery(page=randPage)
        while True:
            randImage = random.randint(0, len(items))
            try:
                if str(items[randImage].images[0]['link'])[-4:] == '.gif':
                    continue
                await bot.send_message(message.channel, "```" + items[randImage].title + "```")
                await bot.send_message(message.channel, items[randImage].images[0]['link'])
                return
            except AttributeError:
                if str(items[randImage].link)[-4:] == '.gif':
                    continue
                await bot.send_message(message.channel, "```" + items[randImage].title + "```")
                await bot.send_message(message.channel, items[randImage].link)
                return
            except JSONDecodeError:
                continue
            except ImgurClientError:
                continue
    except CancelledError as e:
        await bot.send_message(message.channel, "Imgur Cancelled Error: let Skittlely know")
        print(e)
    except TimeoutError as e:
        await bot.send_message(message.channel, "Imgur Timeout Error: let Skittlely know")
        print(e)


async def ow_stats(message, bot):
    database = '../database/OW_Ranks.db'
    conn = create_connection(database)

    QPtop5NameList = []
    QPtop5TimeList = []
    CPtop5NameList = []
    CPtop5TimeList = []
    QPElims = 0
    QPDeaths = 0
    QPTime = 0
    CPElims = 0
    CPDeaths = 0
    CPTime = 0

    player = message.content[11:].replace("#", "-")
    stat_page = "https://playoverwatch.com/career/pc/" + player

    if len(message.content.split()) == 1:
        return

    try:
        page = urllib.request.urlopen(stat_page).read()
    except HTTPError:
        await bot.send_message(message.channel, message.content[11:] + " not found. You need to include the # and "
                                                                       "numbers after their name, and proper "
                                                                       "capitalization matters too")
        return

    soup = BeautifulSoup(page, 'html.parser')

    # User Icon
    try:
        icon = soup.find("img", {'class': 'player-portrait'}).get('src')
    except AttributeError:
        await bot.send_message(message.channel, message.content[11:] + " not found. You need to include the # and "
                                                                       "numbers after their name, and proper "
                                                                       "capitalization matters too")
        return

    # User level (not competitive rank)
    prestigeLevel = soup.find("div", {'class': 'player-level'})['style'].split("url(")
    partialLevel = soup.find("div", {'class': 'u-vertical-center'}).text
    playerLevel = get_level(prestigeLevel[1][:-1].split("rewards/")[1].split("_Border")[0]) + int(partialLevel)

    emblem = get_ow_rank(conn, playerLevel)

    # QP stats
    for top5 in soup.find_all("div", {'id': 'quickplay'}):
        for item in top5.find_all("div", {'class': 'bar-text'})[:5]:
            QPtop5NameList.append(item.find("div", {'class': 'title'}).text)
            QPtop5TimeList.append(item.find("div", {'class': 'description'}).text)
            try:
                QPElims = top5.find("td", string="Eliminations").find_next_sibling("td").text
            except AttributeError:
                pass
            try:
                QPDeaths = top5.find("td", string="Deaths").find_next_sibling("td").text
            except AttributeError:
                pass
            try:
                QPTime = top5.find("td", string="Time Played").find_next_sibling("td").text
            except AttributeError:
                pass

    # CP stats
    for top5 in soup.find_all("div", {'id': 'competitive'}):
        for item in top5.find_all("div", {'class': 'bar-text'})[:5]:
            CPtop5NameList.append(item.find("div", {'class': 'title'}).text)
            CPtop5TimeList.append(item.find("div", {'class': 'description'}).text)
            try:
                CPElims = top5.find("td", string="Eliminations").find_next_sibling("td").text
            except AttributeError:
                pass
            try:
                CPDeaths = top5.find("td", string="Deaths").find_next_sibling("td").text
            except AttributeError:
                pass
            try:
                CPTime = top5.find("td", string="Time Played").find_next_sibling("td").text
            except AttributeError:
                pass

    OWBed = discord.Embed(title=message.content[11:] + "'s Overwatch stats", color=0x00FFFF, url=stat_page)
    OWBed.set_thumbnail(url=emblem)
    OWBed.set_image(url=icon)

    formattedData = ""
    for i in range(5):
        formattedData += "`{}  ::  {} `\n".format(QPtop5NameList[i].ljust(15, " "), QPtop5TimeList[i].rjust(11), " ")
    OWBed.add_field(name="__Top 5 Quick Play Characters Played__", value=formattedData, inline=False)

    formattedData = ""
    try:
        formattedData += "`{}  ::  {} `\n".format("Eliminations".ljust(15, " "), QPElims.rjust(11, " "))
    except AttributeError:
        formattedData += "`{}  ::  {} `\n".format("Eliminations".ljust(15, " "), "0".rjust(11, " "))
    try:
        formattedData += "`{}  ::  {} `\n".format("Deaths".ljust(15, " "), QPDeaths.rjust(11, " "))
    except AttributeError:
        formattedData += "`{}  ::  {} `\n".format("Deaths".ljust(15, " "), "0".rjust(11, " "))
    try:
        formattedData += "`{}  ::  {} `\n".format("Time Played".ljust(15, " "), QPTime.rjust(11, " "))
    except AttributeError:
        formattedData += "`{}  ::  {} `\n".format("Time Played".ljust(15, " "), "0".rjust(11, " "))
    OWBed.add_field(name="__Quick Play Stats__", value=formattedData, inline=False)

    OWBed.add_field(name="-----------------------------------------", value="----------------------------------------",
                    inline=False)

    formattedData = ""
    for i in range(5):
        formattedData += "`{}  ::  {} `\n".format(CPtop5NameList[i].ljust(15, " "), CPtop5TimeList[i].rjust(11), " ")
    OWBed.add_field(name="__Top 5 Comp Play Characters Played__", value=formattedData, inline=False)

    formattedData = ""
    try:
        formattedData += "`{}  ::  {} `\n".format("Eliminations".ljust(15, " "), CPElims.rjust(11, " "))
    except AttributeError:
        formattedData += "`{}  ::  {} `\n".format("Eliminations".ljust(15, " "), "0".rjust(11, " "))
    try:
        formattedData += "`{}  ::  {} `\n".format("Deaths".ljust(15, " "), CPDeaths.rjust(11, " "))
    except AttributeError:
        formattedData += "`{}  ::  {} `\n".format("Deaths".ljust(15, " "), "0".rjust(11, " "))
    try:
        formattedData += "`{}  ::  {} `\n".format("Time Played".ljust(15, " "), CPTime.rjust(11, " "))
    except AttributeError:
        formattedData += "`{}  ::  {} `\n".format("Time Played".ljust(15, " "), "0".rjust(11, " "))
    OWBed.add_field(name="__Comp Play Stats__", value=formattedData, inline=False)

    await bot.send_message(message.channel, embed=OWBed)


# TODO: Make sure to get fresh items (multiple requests without killing rate limit)
async def price_is_right(message, bot):
    randItem = random.randint(0, 100)
    guessesDict = {}
    guessesList = []
    i = 0
    guess = 0.0
    breaker = False
    conn = create_connection(DATABASE)
    prefix = get_prefix(conn, int(message.server.id))[0]

    await bot.send_message(message.channel, "COME ON DOWN! :musical_note: *price is right jingle*:musical_note: ")

    webhoseio_api_key = "69c5d207-91a4-46a9-aa46-7d798b1e8b35"
    webhoseio_url = "http://webhose.io/productFilter?token={}&format=json".format(webhoseio_api_key)
    response = requests.get(webhoseio_url)

    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))
    else:
        bot.send_message(message.channel, "<API ERROR> Request not successful ({})".format(response.status_code))
        return

    try:
        price = float(data['products'][randItem]['price'])
    except ValueError:
        await bot.send_message(message.channel, "<Error> converting price of product to float")
        return

    PIRBed = discord.Embed(title="THE PRICE IS RIGHT! (Beta)", url=data['products'][randItem]['url'], color=0xfffa2d)
    PIRBed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/a/a0/Tpir_40_logo.png")
    PIRBed.add_field(name="Product Name", value=data['products'][randItem]['name'], inline=True)
    PIRBed.set_footer(text="Be closest to actual price without going over to win! Use \'{}guess\' <amount>"
                      .format(prefix))

    try:
        PIRBed.set_image(url=data['products'][randItem]['images'][0])
    except IndexError:
        pass
    try:
        PIRBed.add_field(name="Category", value=data['products'][randItem]['categories'][0].capitalize(),
                         inline=True)
    except IndexError:
        pass

    await bot.send_message(message.channel, embed=PIRBed)

    def check(msg1):
        return msg1.content.startswith("{}guess".format(prefix))

    while i < 4:
        msg = await bot.wait_for_message(check=check, timeout=30.0, channel=message.channel)
        try:
            guess = float(msg.content[7:])
            if guess > 50000:
                await bot.send_message(message.channel, "{}, that is definitely too high".format(msg.author.name))
                if i:
                    i = len(guessesList)
                continue
            if guess < 0:
                await bot.send_message(message.channel, "{}, that is definitely too low".format(msg.author.name))
                if i:
                    i = len(guessesList)
                continue
        except ValueError:
            await bot.send_message(message.channel, "{}, that is not a valid input".format(msg.author.name))
            if i:
                i = len(guessesList)
            continue
        except AttributeError:
            break

        for key, value in guessesDict.items():
            if value == msg.author.id:
                await bot.send_message(message.channel, "{}, you have already guessed".format(msg.author.name))
                if i:
                    i = len(guessesList)
                breaker = True
                continue

        if breaker:
            breaker = False
            continue

        if guess not in guessesList:
            guessesList.append(guess)
        else:
            await bot.send_message(message.channel, "{}, amount already guessed".format(msg.author.name))
            if i:
                i = len(guessesList)
            continue

        guessesDict[guess] = msg.author.id
        i += 1

    await bot.send_message(message.channel, "```ml\nActual Retail Price Is: ${}\n```".format(price))

    guessesList.sort(reverse=True)

    if not len(guessesList):
        await bot.send_message(message.channel, "Nobody played :cry:")
        return

    if guessesList[0] > price:
        try:
            if guessesList[1] <= price:
                user = message.server.get_member(guessesDict[guessesList[1]])
                await bot.send_message(message.channel, "{} WINS!".format(user.name))
            elif guessesList[2] <= price:
                user = message.server.get_member(guessesDict[guessesList[2]])
                await bot.send_message(message.channel, "{} WINS!".format(user.name))
            elif guessesList[3] <= price:
                user = message.server.get_member(guessesDict[guessesList[3]])
                await bot.send_message(message.channel, "{} WINS!".format(user.name))
            else:
                await bot.send_message(message.channel, "Sorry, you all went over the retail amount!")
        except IndexError:
            await bot.send_message(message.channel, "Sorry, you all went over the retail amount!")
    elif guessesList[0] <= price:
        user = message.server.get_member(guessesDict[guessesList[0]])
        await bot.send_message(message.channel, "{} WINS!".format(user.name))
    else:
        await bot.send_message(message.channel, "Sorry, you all went over the retail amount!")


async def google_trends(message, bot):
    term = random.choice(trendTerms)
    guessesList = []
    guessesDict = {}
    playerCount = 0
    conn = create_connection(DATABASE)
    prefix = get_prefix(conn, int(message.server.id))[0]

    trendBed = discord.Embed(title="Let's play Google Trends! (Beta)", url="https://www.youtube.com/watch?v=AIsYJ_7chNc",
                             color=0x11FF11, description="*Guess a word that would be combined with the "
                                                         "Trend term (either before or after) you think is the most"
                                                         " frequently searched on Google.*\n\n Today's Trend term is: "
                                                         "__**{}**__".format(term))
    trendBed.set_thumbnail(url="https://www.alternatememories.com/images/intro/science/google-trends_300x300.jpg.pagespeed.ce.7Zj5pQHJ5n.jpg")
    trendBed.set_footer(text="Use {0}before <word> if you think your word comes before the Trend term or {0}after <word>"
                             " if you think your word comes after the Trend term.".format(prefix))
    await bot.send_message(message.channel, embed=trendBed)

    def check(msg):
        if msg.content.startswith("{}before".format(prefix)):
            return msg.content.startswith("{}before".format(prefix))
        elif msg.content.startswith("{}after".format(prefix)):
            return msg.content.startswith("{}after".format(prefix))

    while playerCount < 5:
        u_msg = await bot.wait_for_message(check=check, timeout=30.0, channel=message.channel)
        try:
            word = u_msg.content.split()[1].lower()
            player = u_msg.author.name
        except AttributeError:
            break

        if u_msg.author.name in guessesDict:
            await bot.send_message(message.channel, "{}, You have already guessed".format(player))
            continue

        if len(u_msg.content.split()) == 1:
            await bot.send_message(message.channel, "{}, You need to enter a word".format(player))
            continue

        if len(u_msg.content.split()) > 2:
            await bot.send_message(message.channel, "{}, Only single word answers".format(player))
            continue

        if len(word) > 25:
            await bot.send_message(message.channel, "{}, That word is too long".format(player))
            continue

        guessDataBefore = "{} {}".format(word, term)
        guessDataAfter = "{} {}".format(term, word)

        if u_msg.content.split()[0] == "{}before".format(prefix):
            if guessDataBefore in guessesList:
                await bot.send_message(message.channel, "{}, {} is already taken". format(player, word))
                continue
            guessesList.append(guessDataBefore)
            guessesDict[u_msg.author.name] = guessDataBefore
        elif u_msg.content.split()[0] == "{}after".format(prefix):
            if guessDataAfter in guessesList:
                await bot.send_message(message.channel, "{}, {} is already taken". format(player, word))
                continue
            guessesList.append(guessDataAfter)
            guessesDict[u_msg.author.name] = guessDataAfter

        playerCount += 1

    trend = TrendReq()
    try:
        trend.build_payload(kw_list=guessesList, timeframe='today 1-m')
    except ResponseError:
        await bot.send_message(message.channel, "Nobody played :cry:, game over")
        return

    playerCount = 0
    for key, value in guessesDict.items():
        try:
            guessesDict[key] = [value, trend.interest_over_time().tail(10).iloc[9, playerCount]]
            playerCount += 1
        except IndexError:
            await bot.send_message(message.channel, "All guesses were so bad, there is no data for that on Google\n"
                                                    "Everyone loses")
            return

    trendGraph = trend.interest_over_time().tail(10).plot(kind='line')
    saveGraph = trendGraph.get_figure()
    saveGraph.savefig("../pics/plots/plot{}.png".format(message.channel))

    await bot.send_file(message.channel, "../pics/plots/plot{}.png".format(message.channel))
    for key, value in guessesDict.items():
        await bot.send_message(message.channel, "```ml\n{} guessed \"{}\" and scored {}\n```"
                               .format(str(key).title(), value[0], value[1]))
    await bot.send_message(message.channel, "```css\n[ {} WINS! ]\n```"
                           .format(max(guessesDict, key=lambda k: guessesDict[k][1])))
