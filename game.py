# Only the Classic Gamemode for now

import random,json,requests
import player

class Game:
    def __init__(self,capacity,channel):
        self.state = "Queue"
        self.capacity = capacity
        self.channel = channel

        self.tableCards = [];
        self.pot = 0;
        self.bet = 0;

        self.numbers = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
        self.suits = [":diamonds:",":clubs:",":hearts:",":spades:"]
        self.used = []

        self.players = []
        self.playerNames = []

        self.turn = -1
        self.round_players = self.capacity
        self.canCheck = True
        self.checkCount = 0
        self.turn_count = 0
        self.starting_player = ""
        self.round = 1
        self.river_shown = False 

    def list_players(self):
        """ Return a formatted string of the players."""
        output = ""
        n = 1
        
        output += "__Current Queue__\n" if (self.state == "Queue") else "__Players__\n"
        
        for x in self.players:
            #Formats to 1. emoji PlayerName 
            output += "{0}. {1} {2}\n".format(n,self.players[n-1].display_name,"(Folded)" if (self.players[n-1].status == "Folded") else "")
            n+=1

        return output
        
    def player_join(self, user,playername):
        """ Add player to queue, check for full queue. """
        self.players.append(player.Player(user,playername, self))
        self.playerNames.append(playername)
        if len(self.players) == self.capacity:
            self.state = "Active"

    def player_leave(self, playername):
        """ Player leaves queue. """
        num = self.playerNames.index(playername)
        self.players.pop(num)
        self.playerNames.remove(playername)

    def draw(self):
        while(True):
            s = random.randint(0,3)
            n = random.randint(0,12)
            if(self.numbers[n]+ " " +self.suits[s]) not in self.used:
                break
        self.used.append(self.numbers[n]+ " " +self.suits[s])
        return self.numbers[n]+ " " +self.suits[s]
        
    def deal(self):
        card = self.draw();
        self.tableCards.append(card)
        return card

    def deal_hands(self):
        for player in self.players:
            card1 = self.draw();
            player.hand.append(card1);
            card2 = self.draw();
            player.hand.append(card2);






