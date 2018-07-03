'''
V1.0

GamblingAddiction Texas Holdem Bot
Created by Derek Zhang

Hand Evaluation - Deuces (https://github.com/worldveil/deuces)
Creds to Kusha Farhadian for teaching me betting rules
Creds to Andy Pham for basic queue framework
Creds to Evan Zhang for random debugging help
'''

import discord,asyncio,random,copy,requests,json,operator

import game,player,pokereval,pokereval,commands,info,dtime,hidden

#Discord Stuff
client = discord.Client()
bot_prefix = '*'
version = "V1.0"

@client.event
@asyncio.coroutine

#go to the next non-folded player and handle new rounds
async def nextTurn(current_game):
    new = current_game.turn

    #Loop until its a player that hasn't folded or all in'd
    while(True): 

        # If this is the last player on the list
        if(new==current_game.capacity-1):
            # Turn goes to the first player in the list
            new = 0
        else:
            # Increment turn
            new += 1
        if ((current_game.players[new].status != "Folded" and current_game.players[new].status != "Allin") or current_game.round == 99 ):
            current_game.turn = new 
            break

    if(not current_game.canCheck):
        current_game.turn_count+=1
    
    # check for new round
    if(current_game.turn_count == current_game.round_players or current_game.checkCount == current_game.round_players or current_game.round == 99):
        current_game.round += 1
        #reset turn count and check ability
        current_game.turn_count = 0
        current_game.checkCount = 0
        current_game.canCheck = True
        current_game.bet = 0

        #Reset the turn to the starting player
        if(current_game.round <98):
            current_game.turn = current_game.playerNames.index(current_game.starting_player.display_name)

        #Reset player bets
        for player in current_game.players:
            player.bet = 0  
            player.first_turn = True

        #Flop
        if (current_game.round == 2):
            embed = discord.Embed(title="The Flop",description="{0} | {1} | {2}".format(current_game.deal(),current_game.deal(),current_game.deal()),color=0xDCDCDC)
            await client.send_message(current_game.channel,embed=embed)
            for player in current_game.players:
                embed.add_field(name="Your Hand",value="{} | {}".format(player.hand[0],player.hand[1]))
                await client.send_message(player.user,embed=embed)
                await client.send_message(player.user,"Your best hand: {}".format(pokereval.besthand(current_game.tableCards,player)))
                embed.remove_field(0)
        #Turn
        elif (current_game.round == 3):
            embed = discord.Embed(title="The Turn",description="{0} | {1} | {2} | {3}".format(current_game.tableCards[0],current_game.tableCards[1],current_game.tableCards[2],current_game.deal()),color=0xDCDCDC)
            await client.send_message(current_game.channel,embed=embed)
            for player in current_game.players:
                embed.add_field(name="Your Hand",value="{} | {}".format(player.hand[0],player.hand[1]))
                await client.send_message(player.user,embed=embed)
                await client.send_message(player.user,"Your best hand: {}".format(pokereval.besthand(current_game.tableCards,player)))
                embed.remove_field(0)
        #River
        elif (current_game.round == 4 or current_game.round == 100):
            embed = discord.Embed(title="The River",description="{0} | {1} | {2} | {3} | {4}".format(
                current_game.tableCards[0],current_game.tableCards[1],current_game.tableCards[2],current_game.tableCards[3],current_game.deal()),color=0xDCDCDC)
            current_game.river_shown = True
            await client.send_message(current_game.channel,embed=embed)
            if(current_game.round != 100):
                for player in current_game.players:
                    embed.add_field(name="Your Hand",value="{} | {}".format(player.hand[0],player.hand[1]))
                    await client.send_message(player.user,embed=embed)
                    await client.send_message(player.user,"Your best hand: {}".format(pokereval.besthand(current_game.tableCards,player)))
                    embed.remove_field(0)
        #End of game, card reveals and winner
        if (current_game.round == 5 or current_game.round == 100):
            if not current_game.river_shown:
                embed = discord.Embed(title="The River",description="{0} | {1} | {2} | {3} | {4}".format(
                    current_game.tableCards[0],current_game.tableCards[1],current_game.tableCards[2],current_game.tableCards[3],current_game.tableCards[4]),color=0xDCDCDC)
                await client.send_message(current_game.channel,embed=embed)

            activeplayers = []
            embed = discord.Embed(title="Card Reveal",description="",color=0xDCDCDC)
            for player in current_game.players:
                if player.status == "Active" or player.status == "Allin":
                    embed.add_field(name=player.display_name,value="{0} | {1}".format(player.hand[0],player.hand[1]),inline=False)
                    activeplayers.append(player)

            #Calculate winner
            win_data = pokereval.winner(current_game.tableCards,activeplayers)
            winner = win_data[0]
            embed.add_field(name="FINAL",value="{0} wins with: {1}".format(winner.display_name,win_data[1]),inline=False)      
            embed.add_field(name="EARNINGS",value=":moneybag: {0} wins ${1}".format(winner.display_name,current_game.pot)) 
            await client.send_message(current_game.channel,embed=embed)

            #Add winnings
            winner.money += current_game.pot
            winner.won = True

            #Update player data into json file
            for player in current_game.players:
                player.update()

            #Remove game
            games.pop(current_game.channel.name,None)
            
    
    if current_game.round != 5 and current_game.round != 100:
        await client.send_message(
            current_game.channel, "{} It's your turn!".format(current_game.players[current_game.turn].user.mention)
        )


async def on_ready():
    print ("RUNNING")

# Stores channel.name keys with Game() object pairs
games = {}

@client.event
async def on_message(message):
    if message.content.startswith(bot_prefix):
        content = message.content.split()
        # number of words
        parts = len(content)
        # first word
        start = content[0][1:]

        # Displays version 
        if start == "info":
            if parts == 1:
                embed = discord.Embed(title="GamblingAddiction {}".format(version),
                                      description = "Developed by DerekZhang#1558\nHand Evaluation powered by Deuces",color=0xDCDCDC)
                await client.send_message(message.channel, embed=embed)

        # Initializes player
        if start == "init":
            if parts == 1:
                with open('data.json', 'r') as js:
                    data = json.load(js)

                if(message.author.id in data):
                    await client.send_message(message.channel, ":thinking: You're already initialized")
                    return 

                data[message.author.id] = {
                    "display_name":self.display_name,
                    "money":200,
                    "games":0,
                    "won":0,
                    "folds":0,
                    "winrate":0,
                    "lastbeg":[0,0,0,0]
                }
                with open('data.json', 'w') as outfile:  
                    outfile.write(json.dumps(data, sort_keys=True,indent=4, separators=(',', ': ')))

        # List of commands
        if start == "help":
            if parts == 1:
                embed = discord.Embed(title="AVAILABLE COMMANDS",description="",color=0xDCDCDC)

                for command in commands.command_list:
                    embed.add_field(name=command, value=commands.command_list[command],inline=False)
                await client.send_message(message.channel, embed=embed)

        # List of poker commands
        if start == "pokerhelp":
            if parts == 1:
                embed = discord.Embed(title="AVAILABLE COMMANDS",description="",color=0xDCDCDC)

                for command in commands.poker_list:
                    embed.add_field(name=command, value=commands.poker_list[command],inline=False)
                await client.send_message(message.channel, embed=embed)

        # pm user with rules
        if start == "instructions":
            if parts == 1:    
                await client.send_message(message.channel, "I messaged you the instructions :smiley:")
                await client.send_message(message.author, info.instructions)

        # Welcomes player
        if start == "greetings":
            # randomizes a greeting message
            x = random.randint(0,2)
            text = ""
            if(x == 0): 
                text = "Hi {}!"
            elif (x == 1): 
                text = ":smirk: {}!"
            else:
                text = "Welcome {}!"
            await client.send_message(message.channel, text.format(message.author.display_name))

        #Return players money
        if start == "money":
            # If just *money, look up author's money
            if(parts == 1):
                with open('data.json', 'r') as js:
                    data = json.load(js)
                if message.author.id in data:
                    money = data[message.author.id]["money"]
                else:
                    money = 200
                await client.send_message(message.channel, ":money_with_wings: {0}: ${1}".format(message.author.display_name,money))
            # If two parts, look up target's money
            elif(parts == 2):
                # Make sure theres only one mention/target
                if(len(message.mentions)==1):
                    with open('data.json', 'r') as js:
                        data = json.load(js)
                    if message.mentions[0].id in data:
                        money = data[message.mentions[0].id]["money"]
                    else:
                        money = 200
                    await client.send_message(message.channel, ":money_with_wings: {0}: ${1}".format(message.mentions[0].display_name,money))
                else:
                    await client.send_message(message.channel, ":sweat_smile: It's `*money` or `*money @user`")
            else:
                await client.send_message(message.channel, ":middle_finger: It's `*money` or `*money @user`, not whatever the fuck you just typed") 
        
        #Donate money
        if start == "give":
            if parts == 3:
                if(len(message.mentions)==1):
                    try:
                        int(content[1])
                    except ValueError:
                        await client.send_message(message.channel, ":sweat_smile: Integers only please!")
                        return

                    if(int(content[1])<0):
                        await client.send_message(message.channel,":angry_face: Get out of here with your negative donation lookin ass")
                        return

                    with open('data.json', 'r') as js:
                        data = json.load(js)

                    if(data[message.author.id]['money'] <= int(content[1])):
                        await client.send_message(message.channel, ":cry: Not enough funds...")
                        return
                    if(message.mentions[0] == message.author):
                        await client.send_message(message.channel, ":unamused: You can't give yourself money...")
                        return
                    if message.mentions[0].id in data:
                        data[message.mentions[0].id]["money"]+=int(content[1]) 
                        await client.send_message(message.channel, ":money_with_wings: {0} gave ${1} to {2}".format(message.author.display_name,content[1],message.mentions[0].display_name))
                        if(int(content[1]) == 0):
                            await client.send_message(message.channel, ":ok_hand: Solid donation of $0 xd, what a cheapskate...")
                        with open('data.json', 'w') as outfile:  
                            outfile.write(json.dumps(data, sort_keys=True,indent=4, separators=(',', ': ')))
                    else:
                        await client.send_message(message.channel, ":grimacing: User is not initalized (`*player` to initialize)")
                else:
                    await client.send_message(message.channel, ":upside_down: The syntax is `*give <amt> @user`")
            else:
                await client.send_message(message.channel, ":upside_down: The syntax is `*give <amt> @user`")

        #Player info
        if start == "player":
            # If just *player look up author's info
            if(parts == 1 or parts == 2):
                with open('data.json', 'r') as js:
                    data = json.load(js)
                if (parts == 1):
                    if message.author.id in data:
                        d = data[message.author.id]
                    else:
                        await client.send_message(message.channel, "Not initialized, `*init` to initialize")
                        return
                # If two parts, look up target's info
                elif(parts == 2):
                    if(message.mention_everyone):
                        await client.send_message(message.channel, "REEEEEEEE")
                        return
                    if message.mentions[0].id in data:
                        d = data[message.mentions[0].id]
                    else:
                        await client.send_message(message.channel, "Not initialized, `*init` to initialize")
                        return
                
                #Prep embed
                embed = discord.Embed(title="Player Info | "+str(d['display_name']),
                    description=":money_with_wings: Money: ${0}\
                                 \n:trident: Win Rate: {1}%\
                                 \n:black_joker: {2} games played\
                                 \n:no_entry: {3} folds".format(
                                    d['money'],
                                    d['winrate'],
                                    d['games'],
                                    d['folds']
                                 ),
                    color = 0xDCDCDC
                )
                if(parts == 1):
                    embed.set_thumbnail(url=message.author.avatar_url)
                elif(parts == 2):
                    embed.set_thumbnail(url=message.mentions[0].avatar_url)
                await client.send_message(message.channel, embed=embed)
            else:
                await client.send_message(message.channel, ":sweat_smile: It's `*player` or `*player @user`") 

        #Leaderboard
        if start == "leaderboard":
            if(parts == 1):
                with open('data.json', 'r') as js:
                    data = json.load(js)
                d = {}

                for user_id in data:
                    d[data[user_id]["display_name"]] = data[user_id]["money"]

                sorted_d = sorted(d.items(),key=lambda kv: kv[1],reverse=True)

                place = 1
                string = ""
                for pair in sorted_d:
                    if place == 11:
                        break
                    if place > 1:
                        string+="\n"
                    string += str(place)+". " + str(pair[0]) + " - $" + str(pair[1]) 
                    place+=1

                embed = discord.Embed(title = "Leaderboard :medal:", description=string, color = 0xDCDCDC)
                await client.send_message(message.channel, embed=embed)
            else:
                await client.send_message(message.channel, ":sweat_smile: It's `*leaderboard`")

        #Daily Beg
        if start == "beg":
            if(parts == 1):
                with open('data.json', 'r') as js:
                    data = json.load(js)
                if message.author.id in data:
                    now = dtime.now()
                    lastbeg = data[message.author.id]['lastbeg']
                    if(dtime.past24(lastbeg,now)):
                        await client.send_message(message.channel, ":thinking: Oh are you begging me for money? Here, have $10 :innocent:")
                        data[message.author.id]['lastbeg'] = dtime.now()
                        data[message.author.id]['money'] += 10
                        with open('data.json', 'w') as outfile:  
                            outfile.write(json.dumps(data, sort_keys=True,indent=4, separators=(',', ': ')))
                    else:
                        await client.send_message(message.channel, ":middle_finger: It hasn't been 24 hours. You asked me {}".format(dtime.dprint(lastbeg)))
                else:
                    await client.send_message(message.channel, ":unamused: You're not initialized, `*init` to initialize")
            else:
                await client.send_message(message.channel, ":unamused: At least ask me properly... the command is `*beg`")

        # Starts a new game session in text channel
        if start == "start":
            if parts == 2:
                # Game already exists
                if (message.channel.name in games):
                   await client.send_message(message.channel, ":sad: A game already exists in this channel...")
                else:

                    try:
                        int(content[1])
                    except ValueError:
                        await client.send_message(message.channel, ":sweat_smile: Integers only please!")
                        return

                    # Check if player has enough funds
                    with open('data.json', 'r') as js:
                        data = json.load(js)

                    if(message.author.id not in data or data[message.author.id]["money"]>=5):
                        # Content must be integer between 3 and 8 (inclusive)
                        if 2 <= int(content[1]) and int(content[1]) <= 8:
                            games[message.channel.name] = game.Game(int(content[1]),message.channel)
                            current_game = games[message.channel.name]
                            current_game.player_join(message.author,message.author.display_name)
                            embed = discord.Embed(
                                title = ":diamonds: :clubs: {0} started a Texas Holdem game for {1} people! :hearts: :spades:".format(
                                    message.author.display_name,current_game.capacity
                                ),
                                description = ":money_with_wings:  Entry Fee: $5\n:inbox_tray:  Type *join to join the game",
                                color = 0xDCDCDC
                            )
                            await client.send_message(message.channel, embed = embed)
                        else:
                            await client.send_message(
                                message.channel, ":smile: Sorry, the number of players must be an integer from 2 to 8..."
                            )
                    else:
                        await client.send_message(message.channel, ":cry: RIP not even enough money to start a game, `*money` to check your funds")
            else:
                await client.send_message(message.channel, ":sweat_smile: The syntax is `*start <players>`. Type `*help` for more info.")

        # Joins a game queue
        if start == "join":
            if parts == 1:
                # Check if game exists
                if (message.channel.name in games):
                    current_game = games[message.channel.name]
                    if current_game.state == "Queue":
                        if message.author.display_name in current_game.playerNames:
                            await client.send_message(message.channel, ":thinking: You're already in the queue...")                     
                        else:
                             # Check if player has enough funds
                            with open('data.json', 'r') as js:
                                data = json.load(js)
                            if(message.author.id not in data or data[message.author.id]["money"]>=5):
                                current_game.player_join(message.author,message.author.display_name)
                                await client.send_message(
                                    message.channel, ":smile: {0} has joined! ({1}/{2})".format(
                                    message.author.display_name, len(current_game.players),current_game.capacity)
                                )
                                # Game begins
                                if current_game.state == "Active":
                                    # Deal the cards to each player
                                    current_game.deal_hands();
                                    for player in current_game.players:
                                        #Admission
                                        player.money -= 5
                                        current_game.pot += 5
                                        #Dealing Hands
                                        await client.send_message(
                                            player.user,"Your hand: {0} | {1}".format(
                                            player.hand[0],player.hand[1])
                                        )

                                    await client.send_message(message.channel, "The game has started! The pot is: ${}".format(current_game.pot))

                                    #set the starting player to determine when each round ends
                                    current_game.starting_player = random.choice(current_game.players)
                                    await client.send_message(
                                        message.channel, "{} has first turn".format(current_game.starting_player.display_name)
                                    )
                                    current_game.turn = current_game.playerNames.index(current_game.starting_player.display_name)
                            else:
                                await client.send_message(message.channel, ":cry: RIP not even enough money to start a game, `*money` to check your funds")
                    else:
                        await client.send_message(message.channel, ":upside_down: The game is no longer accepting players...")                     
                else:
                    await client.send_message(message.channel, ":sad: No game exists in this channel... wanna try and start one?")
            else:
                await client.send_message(message.channel, ":sweat_smile: The syntax is `*join`. Type '*help' for more info.")  
        
        # Leaves a game queue
        if start == "leave":
            if parts == 1:
                # Check if game exists
                if (message.channel.name in games):
                    current_game = games[message.channel.name]
                    if current_game.state == "Queue":
                        if message.author.display_name in current_game.playerNames:
                            current_game.player_leave(message.author.display_name)
                            await client.send_message(
                                message.channel, ":cry: {0} has left... ({1}/{2})".format(
                                message.author.display_name, len(current_game.players), current_game.capacity)
                                )                    
                        else:
                            await client.send_message(message.channel, ":thinking: You're not in the queue...") 
                    else:
                        await client.send_message(message.channel, ":pensive: The game is in progress...")                     
                else:
                    await client.send_message(message.channel, ":sad: No game exists in this channel... wanna try and start one?")
            else:
                await client.send_message(
                    message.channel, ":sweat_smile: The syntax is {}. Type '*help' for more info.".format(text.command_info["leave"][0])
                    )

            #if game is empty
            if len(games[message.channel.name].players) == 0:         
                await client.send_message(message.channel, "`Game has been disbanded!`")
                games.pop(message.channel.name,None)

        # Displays players in queue or game
        if start == "players":
            if parts == 1:
                # Check if game exists
                if (message.channel.name in games):
                    current_game = games[message.channel.name]
                    await client.send_message(message.channel, current_game.list_players())                                          
                else:
                    await client.send_message(message.channel, ":sad: No game exists in this channel... wanna try and start one?")
            else:
                await client.send_message(message.channel, ":sweat_smile: The syntax is `*players`. Type '*help' for more info.")

        # Check
        if start == "check":
            if parts == 1:
                # Check if game exists
                if (message.channel.name in games):
                    current_game = games[message.channel.name]
                    current_player = current_game.players[current_game.turn]
                    #check if its the player's turn
                    if(current_game.turn == current_game.playerNames.index(message.author.display_name)):  
                        # Check if the player can
                        if(current_game.canCheck):
                            await client.send_message(
                                message.channel, "{} checks".format(current_player.display_name)
                            )
                            current_game.checkCount += 1
                            #next turn
                            await nextTurn(current_game)
                        else:
                            await client.send_message(message.channel, ":thinking: You can't check...")
                    else:
                        await client.send_message(message.channel, ":unamused: It's not your turn...")
                else:
                    await client.send_message(message.channel, ":sad: No game exists in this channel... wanna try and start one?")
            else:
                await client.send_message(message.channel, ":sweat_smile: The syntax is `*check`. Type '*help' for more info.")

        # Match/Call
        if start == "match" or start == "call":
            if parts == 1:
                # Check if game exists
                if (message.channel.name in games):
                    current_game = games[message.channel.name]
                    current_player = current_game.players[current_game.turn]
                    #check if its the player's turn
                    if(current_game.turn == current_game.playerNames.index(message.author.display_name)):  
                        if(current_game.bet > 0):
                            # Check if the player has enough funds
                            if(current_game.bet-current_player.bet <= current_player.money):
                                #deduct that from player funds
                                current_player.money -= current_game.bet-current_player.bet
                                #add it to the pot
                                current_game.pot += current_game.bet-current_player.bet

                                await client.send_message(
                                    message.channel, "{0} bets ${1}".format(current_player.display_name,current_game.bet)+
                                    "\nThe minimum bet is still ${0} | Pot: ${1}".format(current_game.bet,current_game.pot)
                                )
                                await client.send_message(
                                    message.author, "You matched ${0}. Remaining: ${1}".format(current_game.bet,current_player.money)
                                )
                                
                                #check to see if there is only one guy left (matching for allin)
                                tempcount = 0
                                for player in current_game.players:
                                    if (player.status != "Allin"):
                                        tempcount+=1
                                if (tempcount == 1):
                                    #Deal missing cards
                                    if(current_game.round == 1):
                                        for x in range(2):
                                            current_game.deal()
                                    for x in range(3-current_game.round):
                                        current_game.deal()
                                    current_game.round = 99                     

                                if(current_player.first_turn):
                                    current_player.first_turn = False

                                #next turn
                                await nextTurn(current_game)
                                
                            else:
                                await client.send_message(message.channel, ":grimacing: Not enough funds...")
                        else:
                            await client.send_message(message.channel, ":neutral_face: No bet to call/match")
                    else:
                        await client.send_message(message.channel, ":unamused: It's not your turn...")
                else:
                    await client.send_message(message.channel, ":sad: No game exists in this channel... wanna try and start one?")
            else:
                await client.send_message(message.channel, ":sweat_smile: The syntax is `*match`. Type '*help' for more info.")

        # Raise (inital bet as well)
        if start == "raise":
            if parts == 2:
                # Check if game exists
                if (message.channel.name in games):
                    current_game = games[message.channel.name]
                    current_player = current_game.players[current_game.turn]
                    # Check if its the player's turn
                    if(current_game.turn == current_game.playerNames.index(message.author.display_name)):  
                        if(current_player.first_turn):
                            
                            try:
                                int(content[1])
                            except ValueError:
                                await client.send_message(message.channel, ":sweat_smile: Integers only please!")
                                return

                            if(int(content[1])<=0):
                                await client.send_message(message.channel,":angry_face: Get out of here with your pot-decreasing negative/0 bet lookin ass")
                                return

                            # Check if the player has enough funds
                            if(int(content[1])+current_game.bet <= current_player.money):
                                #increase the current bet
                                current_game.bet += int(content[1])
                                current_game.pot += current_game.bet
                                #deduct from player money
                                current_player.money -= current_game.bet

                                await client.send_message(
                                    message.channel, "{0} raises by ${1} and bets ${2}".format(current_player.display_name,int(content[1]),current_game.bet) +
                                    "\nThe minimum bet is now ${0} | Pot: ${1}".format(current_game.bet,current_game.pot)
                                )
                                
                                await client.send_message(
                                    message.author, "You raised to ${0}. Remaining: ${1}".format(content[1],current_player.money)
                                )
                                #Can no longer check
                                current_game.canCheck = False
                                #Reset turn count so everyone has to respond
                                current_game.turn_count=0

                                #No longer first turn
                                current_player.first_turn = False

                                # next turn
                                await nextTurn(current_game)                           
                            else:
                                await client.send_message(message.channel, ":grimacing: Not enough funds...")
                        else:
                            await client.send_message(message.channel, "You cannot raise")
                    else:
                        await client.send_message(message.channel, ":unamused: It's not your turn...")
                else:
                    await client.send_message(message.channel, ":sad: No game exists in this channel... wanna try and start one?")
            else:
                await client.send_message(message.channel, ":sweat_smile: The syntax is `*raise <$>`. Type '*help' for more info.")

        # All in
        if start == "allin":
            if parts == 1:
                # Check if game exists
                if (message.channel.name in games):
                    current_game = games[message.channel.name]
                    current_player = current_game.players[current_game.turn]
                    #check if its the player's turn
                    if(current_game.turn == current_game.playerNames.index(message.author.display_name)):  

                        await client.send_message(
                            message.channel, ":money_mouth: {0} all ins, and dumps ${1}".format(current_player.display_name,current_player.money)
                        )
                        # All in babyyyy
                        if(current_game.bet < current_player.money):
                            #increase the current bet
                            current_game.bet = current_player.money

                        #high risk! high reward!    
                        current_game.pot += current_player.money
                        current_player.money = 0
                        
                        # can no longer check
                        current_game.canCheck = False
                        #Update player status
                        current_player.status = "Allin"  
                        #Check if this isn't the last round
                        if (current_game.round != 4):      
                            #Check if everyone else has allin
                            tempcount = 0
                            activecount = 0
                            for player in current_game.players:
                                if(player.status == "Allin"):
                                    tempcount += 1
                                if(player.status == "Active"):
                                    activecount += 1
                            if (tempcount == current_game.round_players or activecount == 1):
                                #Deal missing cards
                                if(current_game.round == 1):
                                    for x in range(2):
                                        current_game.deal()
                                for x in range(3-current_game.round):
                                    current_game.deal()

                                current_game.round = 99

                                #next turn
                                await nextTurn(current_game)
                                return
                            else:
                                await client.send_message(
                                    message.channel, "The minimum bet is now ${0} | Pot: ${1}".format(current_game.bet,current_game.pot)
                                )

                        await client.send_message(
                            message.author, "You all in'd! Remaining: ${}".format(current_player.money)
                        )
                                    
                        # next turn
                        await nextTurn(current_game)                            
                    else:
                        await client.send_message(message.channel, ":unamused: It's not your turn...")
                else:
                    await client.send_message(message.channel, ":sad: No game exists in this channel... wanna try and start one?")
            else:
                await client.send_message(message.channel, ":sweat_smile: The syntax is `*allin`. Type '*help' for more info.")

        #Fold
        if start == "fold":
            if parts == 1:
                # Check if game exists
                if (message.channel.name in games):
                    current_game = games[message.channel.name]
                    current_player = current_game.players[current_game.turn]
                    #check if its the player's turn
                    if(current_game.turn == current_game.playerNames.index(message.author.display_name)):  
                        current_player.fold()
                        await client.send_message(
                            message.channel, "{0} has folded.".format(message.author.display_name)
                        )
                        #check to see if there is only one guy left
                        tempcount = 0
                        for player in current_game.players:
                            if (player.status != "Folded"):
                                tempcount+=1
                        if (tempcount == 1):
                            print("aha")
                            #Deal missing cards
                            if(current_game.round == 1):
                                for x in range(2):
                                    current_game.deal()
                            for x in range(3-current_game.round):
                                current_game.deal()
                            current_game.round = 99
                        #Decrease number of active players
                        await nextTurn(current_game)
                        current_game.round_players-=1

                    else:
                        await client.send_message(message.channel, ":unamused: It's not your turn...")
                else:
                    await client.send_message(message.channel, ":sad: No game exists in this channel... `*start <x>` to start an x player game")
            else:
                await client.send_message(message.channel, ":sweat_smile: The syntax is `*fold`. Type '*help' for more info.")


client.run(hidden.token)