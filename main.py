import random

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
        if isinstance(other, list): # if other is a list
            return self.suit == other[0] and self.rank == other[1]
        return False # if neither, return unequal
    
    def __repr__(self): # defines the string REPResentation of a card
        rankStr = ranks.get(self.rank, str(self.rank)) # checks to see if rank had letter in ranks, if not pass card number (default)
        return f"{self.suit}{rankStr}"
    
    def toDeck(self, deck): # function which when called will add this card (self) to a list called deck
        deck.append(self)

class Game: # defines a game class
    def __init__(self): # constructor, runs automatically when a new game is started
        self.deck = [] # the container for the shuffled deck
        self.pHand = [] # player's hand
        self.dHand = [] # dealer's hand
        self.shuffleDeck() # passes self even though not in parentheses

    def shuffleDeck(self):
        while len(self.deck) != 52: # starts a loop that stops once deck has 52 cards
            rSuit = suits[random.randint(0, 3)] # randomly selects a suit from suits list
            rRank = random.randint(1, 13) # randomly selects a rank
            tempCard = [rSuit, rRank]
            if tempCard not in self.deck: # checks if tcard is already in the deck
                fCard = Card(rSuit, rRank) # if not, creates a new card object with randomized suit and rank
                fCard.toDeck(self.deck) # adds new card object to deck
    
    def dealCard(self, hand):
        nCard = self.deck.pop()
        hand.append(nCard)

    def dealStartingHands(self):
        for i in range(2):
            self.dealCard(self.pHand)
            self.dealCard(self.dHand)

    def getTotal(self, hand):
        total = 0
        aces = 0
        for card in hand:
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

game = Game()
#print("Deck Before Dealing: " + str(game.deck))
game.dealStartingHands()
print(f"Player Hand: {str(game.pHand)} Total: {game.getTotal(game.pHand)}")
print(f"Dealer Hand: {str(game.dHand)} Total: {game.getTotal(game.dHand)}")
#print("Deck After Dealing: " + str(game.deck))