import copy

def eval(table,hand):
    cards = table + hand
    ranks = []
    suits = []
    #histogram
    rankHisto = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for card in cards:
        temp = card.split()[0]
        temp2 = card.split()[1]
        if(temp == "J"):
            temp = 11
        elif(temp == "Q"):
            temp = 12
        elif(temp == "K"):
            temp = 13
        elif(temp == "A"):
            temp = 14

        ranks.append(int(temp))
        suits.append(temp2)
        rankHisto[int(temp)] += 1

    newHisto = copy.copy(rankHisto)
    newHisto.sort()
    newHisto.reverse()

    pairExists = False

    if(newHisto[:4] == [4,1,0,0]):
        return "Four of a Kind " + str(rankHisto.index(4))
    elif(newHisto[:4] == [3,2,0,0]):
        return "Full House " + str(rankHisto.index(3))
    elif(newHisto[:4] == [3,1,1,0]):      
                if(hand[0].split(" ")[0] == rankHisto.index(3) or (len(hand) == 2 and hand[1].split(" ")[0] == rankHisto.index(3))):
                        return "Set " + str(rankHisto.index(3))
                pairExists = True
    elif(newHisto[:4] == [2,2,1,0]):
                if(hand[0].split(" ")[0] == rankHisto.index(2) or (len(hand) == 2 and hand[1].split(" ")[0] == rankHisto.index(2))):
                        #Need to tweak for ties
                        card1 = rankHisto.index(2)
                        rankHisto[rankHisto.index(2)] = 0;
                        card2 = rankHisto.index(2)
                        
                        return "Two Pair " + str(max(card1,card2))
                pairExists = True
    elif(newHisto[:4] == [2,1,1,1]):
                if(hand[0].split(" ")[0] == rankHisto.index(2) or (len(hand) == 2 and hand[1].split(" ")[0] == rankHisto.index(2))):
                        return "One Pair " + str(rankHisto.index(2))
                pairExists = True
        
    ranks.sort()
    isFlush = False
    isStraight = False

    if suits.count(suits[0]) == 5:
        isFlush = True
    if (hand[0].split(" ")[0] == ranks[4] or hand[0].split(" ")[0] == ranks[4]) \
       and ranks[4] - ranks[0] == 4 and not pairExists:
        isStraight = True

    if (isFlush and isStraight):
        if(ranks[4] == 14):
            return "Royal Flush "
        else:
            return "Straight Flush " + str(ranks[4])
    elif (isFlush):
        return "Flush "+ str(suits[0])
    elif (isStraight):
        return "Straight " + str(ranks[4])

    if(len(hand) == 2):
        return "High Card " + str(max(hand[0].split(" ")[0],hand[1].split(" ")[0]))
    else:
        return "High Card " + str(hand[0].split(" ")[0])

rankings = ["High Card","One Pair","Two Pair","Set","Full House","Four of a Kind","Flush","Straight","Straight Flush","Royal Flush"]

def holdem(table,hand):
    possible3 = [
        [0,1,2],
        [1,2,3],
        [2,3,4],
        [0,1,3],
        [0,1,4],
        [0,2,3],
        [0,2,4],
        [1,3,4],
        [1,2,4],
        [0,3,4]
    ]
    possible4 = [
        [0,1,2,3],
        [1,2,3,4],
        [0,2,3,4],
        [0,1,2,4],
        [0,1,3,4]
    ]
    bestnumber = -1
    besthand = ""
    for x in possible3:
        tab = [table[x[0]],table[x[1]],table[x[2]]]
        cards = tab

        if((eval(cards,hand).split(" "))[:-1]) != (besthand.split(" "))[:-1]:
            if (rankings.index(" ".join(eval(cards,hand).split(" ")[:-1])) > bestnumber):
                bestnumber = rankings.index(" ".join(eval(cards,hand).split(" ")[:-1]))
                besthand = eval(cards,hand)

        else:
            if(int((eval(cards,hand).split(" "))[-1]) > int((besthand.split(" "))[-1]) ):
                besthand = eval(cards,hand)
    for x in possible4:
        tab = [table[x[0]],table[x[1]],table[x[2]],table[x[3]]]
        cards = [hand[0]] + tab

        if((eval(cards,hand).split(" "))[:-1]) != (besthand.split(" "))[:-1]:
            if (rankings.index(" ".join(eval(cards,hand).split(" ")[:-1])) > bestnumber):
                bestnumber = rankings.index(" ".join(eval(cards,hand).split(" ")[:-1]))
                besthand = eval(cards,hand)

        else:
            if(int((eval(cards,hand).split(" "))[-1]) > int((besthand.split(" "))[-1]) ):
                besthand = eval(cards,hand)
    for x in possible4:
        tab = [table[x[0]],table[x[1]],table[x[2]],table[x[3]]]
        cards = [hand[1]] + tab

        if((eval(cards,hand).split(" "))[:-1]) != (besthand.split(" "))[:-1]:
            if (rankings.index(" ".join(eval(cards,hand).split(" ")[:-1])) > bestnumber):
                bestnumber = rankings.index(" ".join(eval(cards,hand).split(" ")[:-1]))
                besthand = eval(cards,hand)
        else:
            if(int((eval(cards,hand).split(" "))[-1]) > int((besthand.split(" "))[-1]) ):
                besthand = eval(cards,hand)

    return besthand

def winner(table,players):
    winner = ""
    besthand = ""
    bestnumber = -1

    for player in players:
        
        cards = table 
        if(rankings.index(" ".join(holdem(cards,player.hand).split(" ")[:-1])) != bestnumber):
            if (rankings.index(" ".join(holdem(cards,player.hand).split(" ")[:-1])) > bestnumber):
                bestnumber = rankings.index(" ".join(holdem(cards,player.hand).split(" ")[:-1]))
                besthand = holdem(cards,player.hand)
                winner = player.display_name
        else:
            if(int((holdem(cards,player.hand).split(" "))[-1]) > int((besthand.split(" "))[-1]) ):
                besthand = holdem(cards,player.hand)
                winner = player.display_name

    return [winner,besthand]

print(eval(["6 A","7 A", "6 B"], ["6 C", "10 A"])) 
print(holdem(["11 Spades","10 Spades","6 Clubs","6 Hearts","9 Spades"],["5 Hearts","7 Hearts"]));

