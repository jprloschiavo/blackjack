# Goal: Get closer to 21 than the dealer without going over 21
# How you lose: Going over 21 or, if at the end of the round, the dealer is closer to 21 than you are without going over
# Card values: From 2 to 10, the cards are worth their point value. Face cards are worth 10 points. Aces are worth 1 or 11 depending on what is better for the player

# Players bet before being dealt cards
# Each player and the dealer is dealt one card and then a second card
# Players can hit or stand, but the dealer has to hit until they have 17 or higher
# Playing decisions:
#  Hit: Tap the table, you get another card
#  Stand: Wave hand, you do not want anymore cards, you can not make anymore decisions
#  Double down: Double your bet in exchange for one more card, you can not take anymore cards at this point
#  Split: When you have a pair, you can split your hand into two by matching your bet, you can hit or stay on both hands, you can also double down on a split hand
# When everyone is done making their decisions, the dealer reveals their card. If the dealer has less than 17, they hit and take another card until they have 17 or higher
# If you have the same hand as the dealer, you do not win or lose any money. This is called a push
# If you hit and go over 21, you lose right away. This is called a bust
# If the dealer busts and you do not, you win
# BUT WAIT! If you are dealt a blackjack (21), you win automatically. Pays 3 to 2 (150%)
# If the dealer is dealt an ace up or a 10 up, they check to see if they have a blackjack. If they do, the hand ends immediately. Anyone who does not have a blackjack loses, people with blackjacks push
# When the dealer has an ace, players can buy insurance, which is a bet on whether the dealer has blackjack or not
# Sometimes dealers will offer surrender if they have a strong upcard. When you surrender, you forfeit 50% of your bet, keep the rest, and leave the round

# REMEMBER: self passes automatically except when you call a method through the class itself and not the instance

import random
import math

DNAME = "DEALER"
PSTAND = "STAND"
suits = ["♣", "♦", "♥", "♠"] # clubs, diamonds, hearts, spades
ranks = {1: "A", 11: "J", 12: "Q", 13: "K"}

class Setup:
    def __init__(self):
        self.players = []
        self.playerNames = self.takeNames()
        self.addPlayers()
        self.game = self.createGame()        
    
    def takeNames(self):
        #print("MAXIMUM PLAYER COUNT: SEVEN (7)")
        #nInput = input("PLEASE INPUT PLAYER NAMES SEPARATED BY SPACES: ")

        # CREATE CHECK TO MAKE SURE nInput IS NOT EMPTY AND THAT THERE ARE NO DUPLICATE NAMES

        nInput = ("JOE EMMA GOJI")
        #nInput = ("JOE EMMA")
        #nInput = ("JOE")

        return nInput.split(" ")

    def addPlayers(self):
        for name in filter(None, self.playerNames[:7]): # ignores empty strings in case of misinput and slice syntax (:) says "take first {playerLimit} from playerNames"
            self.players.append(Player(name))

    def createGame(self):
        print("\n")
        return Game(self.players)

class Player:
    def __init__(self, name):
        self.name = name
        self.wallet = 500
        self.hands = [Hand()]
    
    def getHand(self, i=0):
        if i <= len(self.hands) - 1:
            return self.hands[i]
        print(f"INDEX {i} DOES NOT EXIST IN {self.name} HANDS")
        print(f"RETURNING INDEX 0 INSTEAD")
        return self.hands[0]

    def addMoney(self, amount):
        self.wallet = self.wallet + amount
    
    def subtractMoney(self, amount):
        self.wallet = self.wallet - amount

class Card: # define a class for cards
    def __init__(self, suit, rank): # the constructor for the card class
        self.suit = suit # stores the suit of the card
        self.rank = rank # stores the rank of the card

    def __eq__(self, other): # defines how to compare cards, other represents what card is being compared to
        if isinstance(other, Card): # if other is another card
            return self.suit == other.suit and self.rank == other.rank
        return False # if neither, return unequal
    
    def render(self): # defines the string REPResentation of a card
        rankStr = ranks.get(self.rank, str(self.rank)) # checks to see if rank had letter in ranks, if not pass card number (default)
        left = f"{rankStr:<2}"
        right= f"{rankStr:>2}"
        return [
            f"┌─────────┐",
            f"│{left}       │",
            f"│         │",
            f"│    {self.suit}    │",
            f"│         │",
            f"│       {right}│",
            f"└─────────┘"
        ]
    
class Hand:
    def __init__(self, isDealer=False):
        self.cards = []
        self.isDealer = isDealer
    
    def renderHand(self, hideHole=False):
        cardRows = []
        if self.isDealer == False:
            cardRows = [card.render() for card in self.cards] # list of lists: each inner list is the ASCII lines of a card
            lines = [] 
            for row in zip(*cardRows): # combine the rows of each card from the same line together
                lines.append(" ".join(row)) # joins the lines from all cards from this row into one string with a space between them
            return "\n".join(lines) # lines is now a list of strings, each representing one horizontal row of the hand
        else:     
            if hideHole:
                hidden = [
                    f"┌─────────┐",
                    f"│?        │",
                    f"│         │",
                    f"│    ?    │",
                    f"│         │",
                    f"│        ?│",
                    f"└─────────┘"
                ]
                cardRows.append(hidden)
                cardRows.append(self.cards[1].render())
            else:
                cardRows = [card.render() for card in self.cards]
            lines = []
            for row in zip(*cardRows):
                lines.append(" ".join(row))
            return "\n".join(lines)
    
    def addCard(self, card):
        self.cards.append(card)
    
    def getTotal(self):
        total = 0
        aces = 0
        for card in self.cards:
            if card.rank >= 11: # face cards count as 10
                total += 10
            elif card.rank == 1:
                aces += 1
                total += 11 # aces count as 11 initially
            else:
                total += card.rank
        while total > 21 and aces: # if total is over 21 and hand has aces, aces count as 1 until total is less than or equal to 21
            total -= 10
            aces -= 1
        return total

class Game: # defines a game class
    def __init__(self, players): # constructor, runs automatically when a new game is started
        self.players = players
        self.bets = {}
        self.deck = [] # the container for the shuffled deck
        self.dHand = Hand(True) # dealer's hand

        self.placeBets()
        self.shuffleDeck()
        self.dealStartingHands()
    
    def pressEnterToContinue(self):
        input("PRESS ENTER TO CONTINUE")
        print("\n")
    
    def placeBets(self):
        for player in self.players:
            while True:
                try: # try block contains the code expected to potentially raise an exception (error)
                    bet = float(input(f"{player.name} PLACE YOUR BET: $"))
                    if bet <= 0:
                        print("ERROR: BET MUST BE GREATER THAN ZERO")
                    elif bet <= player.wallet:
                        player.subtractMoney(bet)
                        self.bets[player.name] = bet
                        print(f"{player.name} BET ${self.bets[player.name]}")
                        self.pressEnterToContinue()
                        break
                    else:
                        print("ERROR: MUST ONLY BET MONEY YOU ACTUALLY HAVE")
                except ValueError: # except block specifies how to handle a particular exception (ValueError)
                    print("ERROR: BET MUST BE A FLOAT")

    def shuffleDeck(self):
        while len(self.deck) != 52: # starts a loop that stops once deck has 52 cards
            rSuit = suits[random.randint(0, 3)] # randomly selects a suit from suits list
            rRank = random.randint(1, 13) # randomly selects a rank
            card = Card(rSuit, rRank)
            if card not in self.deck: # checks if card is already in the deck
                self.deck.append(card) # if not, adds new card object to deck

    def dealStartingHands(self):
        for i in range(2):
            for player in self.players:
                hand = player.getHand()
                hand.addCard(self.deck.pop())
            self.dHand.addCard(self.deck.pop())

    def printHand(self, name, hideHole=False):
        if name != DNAME:
            for player in self.players:
                if player.name == name:
                    hand = player.getHand()
                    print(f"{player.name}: ${player.wallet}")
                    print(hand.renderHand(hideHole))
                    print(f"TOTAL: {hand.getTotal()}")
                    print("\n")
                    return
            print(f"ERROR: {name} DOES NOT MATCH ANY NAME OF AN EXISTING PLAYER")
        else:
            print("DEALER:")
            print(self.dHand.renderHand(hideHole))
            if hideHole == False: print(f"TOTAL: {self.dHand.getTotal()}")
            print("\n")

    def isBust(self, player=None):
        hand = player.getHand() if player else self.dHand # if player exists, hand equals player.getHand(). if player does not exist, hand equals self.dHand
        if hand.getTotal() > 21:
            if player:
                print(f"{player.name} BUST")
            else:
                print("DEALER BUST")
            self.pressEnterToContinue()
            return True
        return False
    
    def isBlackjack(self, player=None):
        hand = player.getHand() if player else self.dHand
        if hand.getTotal() == 21:
            if player:
                if len(hand.cards) == 2: # if only two cards in hand.cards list
                    print(f"{player.name} NATURAL BLACKJACK")
                    player.addMoney(self.bets[player.name] * 1.5)
                    print(player.wallet)
                else:
                    print(f"{player.name} BLACKJACK")
            else:
                print("DEALER BLACKJACK")
            self.pressEnterToContinue()
            return True
        return False

    def hitDealer(self):
        while True:
            if self.dHand.getTotal() < 17:
                self.dHand.addCard(self.deck.pop())
            else:
                break
        self.printHand(DNAME)
        self.isBust() # check if dealer bust

    def hit(self, player=None):
        if player:
            hand = player.getHand()
            hand.addCard(self.deck.pop())
            self.printHand(player.name)
        else:
            self.hitDealer()

    def stand(self, player):
        print(f"{player.name} STOOD")
        self.pressEnterToContinue()
        return PSTAND

    def checkInput(self, player, pInput):
        match pInput:
            case "H":
                self.hit(player)
            case "S":
                return self.stand(player)

    def hitOrStand(self, player):
        validInputs = ["H", "S"]
        while True: # switched method to while loop to avoid crashing from bad inputs due to recursion (calling checkInput which recalled takeInput when given invalid input)
            pInput = input(f"{player.name}: HIT OR STAND? (H/S)").upper().strip()
            print("\n")
            if pInput in (validInputs):
                return self.checkInput(player, pInput)
            print(f"{pInput} IS AN INVALID INPUT. PLEASE TRY AGAIN")

    def doubleDown(self):
        pass

    def split(self):
        # IF HAND HAS ONLY TWO CARDS AND HAND TOTAL DIVIDED BY TWO YIELDS TWO EQUAL HALVES, PLAYER CAN SPLIT
        pass

game = Setup().game
while True:
    game.printHand(DNAME, True)
    game.pressEnterToContinue()
    for player in game.players:
        # MAYBE SWITCH TO PASSING HAND TO GAME FUNCTIONS SO SPLITTING WORKS. WILL HAVE TO GET RID OF getHands() AND PASS HANDS AS FOR LOOP (for hand in player.getHands())
        game.printHand(player.name)
        if game.isBlackjack(player): # if player was dealt a natural blackjack
            continue # skip the rest of the code and move on to next player
        while True:
            if game.hitOrStand(player) == PSTAND or game.isBlackjack(player) or game.isBust(player):
                break
    game.hit() # dealer hits until 17 or higher
    game.isBlackjack()
    break