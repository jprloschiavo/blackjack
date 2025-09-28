import random

# REMEMBER: self passes automatically except when you call a method through the class itself and not the instance

# clubs, diamonds, hearts, spades
suits = ["♣", "♦", "♥", "♠"]
ranks = {1: "A", 11: "J", 12: "Q", 13: "K"}

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
    def __init__(self):
        self.cards = []
    
    def dealCard(self, card):
        self.cards.append(card)

    def checkCards(self):
        return self.cards
    
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
    def __init__(self): # constructor, runs automatically when a new game is started
        self.deck = [] # the container for the shuffled deck
        
        # TO HAVE MULTIPLE PLAYERS, SPLITTING, AND DOUBLING DOWN: TURN HANDS INTO THEIR OWN CLASS
        self.pHand = Hand() # player's hand
        self.dHand = Hand() # dealer's hand

    def shuffleDeck(self):
        while len(self.deck) != 52: # starts a loop that stops once deck has 52 cards
            rSuit = suits[random.randint(0, 3)] # randomly selects a suit from suits list
            rRank = random.randint(1, 13) # randomly selects a rank
            card = Card(rSuit, rRank)
            if card not in self.deck: # checks if card is already in the deck
                self.deck.append(card) # if not, adds new card object to deck

    def dealStartingHands(self):
        for i in range(2):
            self.pHand.dealCard(self.deck.pop())
            self.dHand.dealCard(self.deck.pop())

    def renderDealerHand(self, hideHole):
        cardRows = []
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
            cardRows.append(self.dHand.checkCards()[1].render())
            cardRows.extend([hidden] * (len(self.dHand.checkCards()) - 2)) # add hidden to cardRows once per card other than first
        else:
            cardRows = [card.render() for card in self.dHand.checkCards()]
        lines = []
        for row in zip(*cardRows):
            lines.append(" ".join(row))
        return "\n".join(lines)

    def renderPlayerHand(self):
        cardRows = [card.render() for card in self.pHand.checkCards()] # list of lists: each inner list is the ASCII lines of a card
        lines = [] 
        for row in zip(*cardRows): # combine the rows of each card from the same line together
            lines.append(" ".join(row)) # joins the lines from all cards from this row into one string with a space between them
        return "\n".join(lines) # lines is now a list of strings, each representing one horizontal row of the hand

    def hit(self, hand):
        hand.dealCard(self.deck.pop())

    def isBust(self, hand):
        if hand.getTotal() > 21:
            return True
        return False

    def checkDecision(self, decision):
        #action = input("HIT OR STAND (H/S)").strip().upper()
        match decision:
            case "H":
                self.hit(self.pHand)
                return self.isBust(self.pHand)
            case "ST":
                return "STAND"
            case "DD":
                return "DOUBLE DOWN"
            case "SP":
                return "SPLIT"
            case _: # default case
                #self.queryPlayer()
                # RETURN FALSE SO THAT queryPlayer METHOD WILL KNOW TO ASK AGAIN
                pass

game = Game()

game.shuffleDeck() 
game.dealStartingHands()

print(game.renderPlayerHand())
print(game.renderDealerHand(True))
print(game.renderDealerHand(False))

# GAME LOOP STEPS (WATCH BLACKJACK ROUND)

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