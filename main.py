import random

suits = ["♣", "♦", "♥", "♠"]
ranks = {1: "A", 11: "J", 12: "Q", 13: "K"}

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank
        return False
    
    def render(self, hide=False):
        if not hide:
            rankStr = ranks.get(self.rank, str(self.rank))
            left = f"{rankStr:<2}"
            right = f"{rankStr:>2}"
            return [
                f"┌─────────┐",
                f"│{left}       │",
                f"│         │",
                f"│    {self.suit}    │",
                f"│         │",
                f"│       {right}│",
                f"└─────────┘"]
        return [
            f"┌─────────┐",
            f"│?        │",
            f"│         │",
            f"│    ?    │",
            f"│         │",
            f"│        ?│",
            f"└─────────┘"]
    
    def getRank(self):
        return self.rank

class Deck:
    def __init__(self):
        self.deck = []
        self.createCards()
        self.shuffleDeck()

    def createCards(self):
        for suit in suits:
            for rank in range(1, 14):
                self.deck.append(Card(suit, rank))

    def shuffleDeck(self):
        for lastIndex in range(len(self.deck) - 1, 0, -1):
            indexToSwap = random.randint(0, lastIndex)
            self.deck[lastIndex], self.deck[indexToSwap] = self.deck[indexToSwap], self.deck[lastIndex]

    def popCard(self):
        if len(self.deck) > 0:
            return self.deck.pop()
        raise ValueError("DECK EMPTY")

class Hand:
    def __init__(self, owner):
        self.owner = owner
        self.bet = None
        self.cards = []

    def appendCard(self, newCard):
        self.cards.append(newCard)
    
    def popCard(self):
        if len(self.cards) > 1:
            return self.cards.pop()
        raise ValueError("HAND WOULD BE EMPTY")

    def printHand(self, hideHole=False):
        handRows = []
        if not hideHole:
            handRows = [card.render() for card in self.cards]
        else:
            handRows = [self.cards[0].render(True)] + [card.render() for card in self.cards[1:]]
        lines = []
        for row in zip(*handRows):
            lines.append(" ".join(row))
        print(f"{self.owner.getName()}: ")
        print("\n".join(lines))
        print(f"Total: {self.getTotal()}") if not hideHole else print("Total: ?")
        print("\n")

    def recordBet(self, amount):
        self.bet = amount
    
    def getTotal(self):
        total = 0
        aces = 0
        for card in self.cards:
            rank = card.getRank()
            if rank >= 11:
                total += 10
            elif rank == 1:
                aces += 1
                total += 11
            else:
                total += rank
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total
    
    def isBust(self):
        return self.getTotal() > 21
    
    def isBlackjack(self):
        return self.getTotal() == 21
    
    def isNaturalBlackjack(self):
        if not isinstance(self.owner, Dealer):
            if len(self.owner.getHands()) == 1:
                return len(self.cards) == 2 and self.isBlackjack()
            return False
        else:
            return len(self.cards) == 2 and self.isBlackjack()

    def getOwner(self):
        return self.owner
    
    def getBet(self):
        return self.bet
    
    def getCards(self):
        return self.cards

class Player:
    def __init__(self, name):
        self.hands = [Hand(self)]
        self.name = name
        self.wallet = 1000

    def addMoney(self, amount):
        self.wallet = self.wallet + amount

    def subtractMoney(self, amount):
        self.wallet = self.wallet - amount

    def appendHand(self, newHand):
        self.hands.append(newHand)
    
    def getHands(self):
        return self.hands
    
    def getName(self):
        return self.name

    def getWallet(self):
        return self.wallet

class Dealer:
    def __init__(self):
        self.hand = Hand(self)
    
    def getHand(self):
        return self.hand
    
    def getName(self):
        return "Dealer"

class Round:
    def __init__(self, players):
        self.deck = Deck()
        self.dealer = Dealer()
        self.players = players
        self.ongoingPlayers = players.copy()
        self.finishedPlayers = []
        self.play()

    def takeBets(self):
        for player in self.players:
            while True:
                try:
                    betInput = int(input(f"{player.getName()}, place your bet: $"))
                    if betInput <= 0:
                        print("ERROR: MUST BE GREATER THAN ZERO")
                    elif betInput <= player.getWallet():
                        playerHand = player.getHands()[0]
                        player.subtractMoney(betInput)
                        playerHand.recordBet(betInput)
                        print(f"{player.getName()} bet ${playerHand.getBet()}")
                        print(f"{player.getName()}'s current balance: ${player.getWallet()}")
                        break
                    else:
                        print("ERROR: CAN ONLY BET MONEY YOU ACTUALLY HAVE")
                except ValueError:
                    print("ERROR: BET MUST BE A WHOLE NUMBER")

    def dealStartingHands(self):
        for _ in range(2):
            for player in self.players:
                player.getHands()[0].appendCard(self.deck.popCard())
            self.dealer.getHand().appendCard(self.deck.popCard())       
    
    def finishPlayer(self, player):
        if player not in self.finishedPlayers:
            self.finishedPlayers.append(player)
            if player in self.ongoingPlayers:
                self.ongoingPlayers.remove(player)

    def checkNaturals(self):
        dealerHand = self.dealer.getHand()
        if not dealerHand.isNaturalBlackjack():
            for player in self.ongoingPlayers[:]:
                playerHand = player.getHands()[0]
                if playerHand.isNaturalBlackjack():
                    playerHand.printHand()
                    print(f"{player.getName()} natural blackjack")
                    self.finishedPlayers.append(player)
                    self.ongoingPlayers.remove(player)
            dealerHand.printHand(True)
        else:
            dealerHand.printHand()
            print(f"{self.dealer.getName()} natural blackjack")
            for player in self.players:
                self.finishPlayer(player)

    def split(self, hand, player):
        newHand = Hand(player)
        newHand.appendCard(hand.popCard())
        bet = hand.getBet()
        player.subtractMoney(bet)
        newHand.recordBet(bet)
        player.appendHand(newHand)

    def checkSplits(self, player):
        playerHands = player.getHands()
        if len(playerHands) <= 3:
            for hand in playerHands:
                handCards = hand.getCards()
                if len(handCards) == 2 and handCards[0] == handCards[1]:
                    while True:
                        hand.printHand()
                        splitInput = input(f"{player.getName()}: split? (Y/N)").upper().strip()
                        if splitInput in ["Y", "N"]:
                            match splitInput:
                                case "Y":
                                    self.split(hand, player)
                                    break
                                case "N":
                                    break
                        else:
                            print(f"{splitInput} IS AN INVALID INPUT")

    def hit(self, hand):
        player = hand.getOwner()
        hand.appendCard(self.deck.popCard())
        hand.printHand()
        if hand.isBust():
            print(f"{player.getName()} bust")
        elif hand.isBlackjack():
            print(f"{player.getName()} blackjack")

    def hitOrStand(self, hand):
        player = hand.getOwner()
        while True:
            playerInput = input(f"{player.getName()}: hit or stand? (H/S)").upper().strip()
            if playerInput in ["H", "S"]:
                match playerInput:
                    case "H":
                        self.hit(hand)
                        if hand.isBust() or hand.isBlackjack():
                            break
                    case "S":
                        break
            else:
                print(f"ERROR: {playerInput} IS AN INVALID INPUT")
        self.finishPlayer(player)

    def double(self, hand, player):
        bet = hand.getBet()
        player.subtractMoney(bet)
        hand.recordBet(bet * 2)
        self.hit(hand)   
        self.finishPlayer(player)

    def checkDoubles(self, player):
        playerHand = player.getHands()[0]
        if len(playerHand.getCards()) == 2 and playerHand.getTotal() in [9, 10, 11]:
            while True:
                playerHand.printHand()
                doubleInput = input(f"{player.getName()}: double down? (Y/N)").upper().strip()
                if doubleInput in ["Y", "N"]:
                    match doubleInput:
                        case "Y":
                            self.double(playerHand, player)
                            break
                        case "N":
                            break
                else:
                    print(f"{doubleInput} IS AN INVALID INPUT")
    
    def dealerTurn(self):
        dealerHand = self.dealer.getHand()
        if not dealerHand.isNaturalBlackjack():
            while dealerHand.getTotal() < 17:
                dealerHand.appendCard(self.deck.popCard())
            dealerHand.printHand()
            if dealerHand.isBust():
                print("Dealer bust")
            elif dealerHand.isBlackjack():
                print("Dealer blackjack")
    
    def resolveHands(self):
        dealerHand = self.dealer.getHand()
        dealerTotal = dealerHand.getTotal()
        for player in self.finishedPlayers:
            playerHands = player.getHands()
            for hand in playerHands:
                handTotal = hand.getTotal()
                bet = hand.getBet()
                if not hand.isNaturalBlackjack():
                    if hand.isBust():
                        print(f"{player.getName()} loses ${bet}!")
                    elif dealerTotal > 21 or handTotal > dealerTotal:
                        payout = bet * 2
                        print(f"{player.getName()} wins {payout}!")
                        player.addMoney(payout)
                    elif dealerTotal == handTotal:
                        print(f"{player.getName()} push")
                        player.addMoney(bet)
                    else:
                        print(f"{player.getName()} loses ${bet}!")
                else:
                    if not dealerHand.isNaturalBlackjack():
                        payout = bet * 2.5
                        print(f"{player.getName()} wins {payout}!")
                        player.addMoney(payout)
                    else:
                        print(f"{player.getName()} push")
                        player.addMoney(bet)
                print(f"{player.getName()}'s current balance: ${player.getWallet()}")
    
    def play(self):
        self.takeBets()
        self.dealStartingHands()
        self.checkNaturals()
        while len(self.ongoingPlayers) > 0:
            for player in self.ongoingPlayers[:]:
                self.checkDoubles(player)
                if player in self.ongoingPlayers[:]:
                    self.checkSplits(player)
                    for hand in player.getHands()[:]:
                        hand.printHand()
                        self.hitOrStand(hand)
            self.dealerTurn()
            self.resolveHands()

class Game:
    def __init__(self):
        self.players = []
        self.addPlayers()
        self.startRound()
    
    def addPlayers(self):
        nameInput = input("Input player names separated by spaces: ")
        for name in nameInput.split(" "):
            player = Player(name)
            self.players.append(player)
    
    def startRound(self):
        Round(self.players)

game = Game()