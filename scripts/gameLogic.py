# ---------------------------------------------------------
# Core Game Logic 
# ---------------------------------------------------------

import random
from scoring import *
# Ideally we can remove this import. 
# It's only used for setting the seed which is later used by the strategy functions
import numpy as np
import pandas as pd # :(
import os
import sys
from datetime import datetime, timedelta

class Card:
    """
    Defines a card.
    A card has a rank, a suit, a value, and a numeric_rank.
    
    rank: String. A one character descriptor of the rank
    suit: String. Either C, H, S, D.
    value: Int. Value of the card. 1 - 10
    numeric_rank: Int. Order of the card, going from A = 1 to K = 13.
    """
    
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        face_to_value = {"T":10, "J":11, "Q":12, "K":13}
        if rank in ["T", "J", "Q", "K"]:
            self.value = 10
            self.numeric_rank = face_to_value.get(rank)
        elif rank in ["A"]:
            self.value = 1
            self.numeric_rank = 1
        else:
            self.value = int(rank)
            self.numeric_rank = int(rank)
            
    def __repr__(self):
        """Representation is of the form: 6 of S or Q of H."""
        return self.rank + " of " + self.suit
    
    def __eq__(self, other): 
        """Cards are equal if they have the same rank and suit."""
        if not isinstance(other, Card):
            return False
        else:
            return self.rank == other.rank and self.suit == other.suit

class CardCollection:
    """
    An arbitrary collection of cards
    """
    def __init__(self):
        self.cards = []
    
    def add_cards(self, new_cards):
        """
        Add either a card or a list of cards to the hand.
        new_cards: Either a list of Card objects or a single Card
                   These card(s) will be added to the collection
        """
        if type(new_cards) == list:
            self.cards.extend(new_cards)
        else:
            self.cards.append(new_cards)
            
    def remove_cards(self, cards_to_remove):
        """
        Remove these cards from the collection.
        cards_to_remove: Either a list of Card objects or a single Card
                         These card(s) will be removed from the collection
        """
        #print(self)
        #print(cards_to_remove)
        if type(cards_to_remove) == list:
            for c in cards_to_remove:
                self.cards.remove(c)
        else:
            self.cards.remove(cards_to_remove)
            
    def length(self):
        """Return the number of cards in the collection."""
        return(len(self.cards))

            
    def __repr__(self):
        """The representation is the representation of each card in the collection in a list."""
        return(str(self.cards))

class Deck(CardCollection):
    '''
    The deck object will start with 52 cards -- every time that a card is pulled from the deck, the
    deck object should update and show that the card is no longer in the deck.

    The deck should have a notion of card, value, and suit -- there are 4 suits and 13 unique types of cards,
    and 10 unique values of the card (i.e J, Q, K are all unique cards but have a value of 10).

    We can denote these face cards as 11, 12, 13 as those are their inherent ordering, and then we calculating 
    total points at the end, we can map 11, 12, 13 all to 10.
    '''
    def __init__(self):
        super().__init__()
        SUITS = ['C','D','H','S'] 
        RANKS = ['A','2','3','4','5','6','7','8','9','T','J','Q','K']
        for rank in RANKS:
            for suit in SUITS:
                self.cards.append(Card(rank, suit))
                
        # Randomize the order of the cards
        self.cards = self.shuffle()
    
    def draw(self, n = 1):
        """Take off and return a list of the top n cards on the deck."""
        drawn_cards = self.cards[:n]
        self.cards = self.cards[n:]
        return(drawn_cards)
        
    def shuffle(self):
        """Randomize the order of the cards."""
        self.cards = random.sample(self.cards, 52)
        return(self.cards)

class Hand(CardCollection):
    """
    This abstraction will be used for the player's hand. Will have 9 or 10 cards at any point.
    """
    
    def __init__(self):
        super().__init__()
        
    def score_basic(self):
        """Return the current score of the hand, without removing anything for runs or sets."""
        # TODO: this needs to change. Right now it does not remove any runs or sets.
        return(sum([c.value for c in self.cards]))   
    
    def score(self):
        '''
        @Author: Dan
        Return the score of the hand after optimally removing cards that can be considered in a run or a set.

        When scoring your hand, it's possible that some cards will belong to multiple runs / sets. When that is the case, 
        we must find the optimal outcome that minimizes the number of points that you have left over.

        Example: if you have a 4D, 4C, 4S, 5S, and 6S -- then you would choose to accept the 4S, 5S, and 6S run
        and forfeit the points for 4D and 4C (a total of 8 points). If you had chosen to stick with the three of a kind
        of fours, you would have to forfeit 5S and 6S (a total of 11 points).

        '''
        
        hand_boof, suitStarts, sz = give_me_handBoof_suitStarts_and_sz(self) #creates 3 inputs to scoring algorithm

        maxScore = F(sz, hand_boof, suitStarts) 
        totalScore = sum([c.value for c in self.cards])
        finalScore = totalScore - maxScore
        
        return finalScore


class Pile(CardCollection):
    """
    This represents the game's discard pile.
    Starts empty. Players can always see the top card of the pile and draw from it if they wish.
    Players add one card to the pile every turn, unless they decide to knock.
    """
    
    def __init__(self):
        super().__init__()
    
    def view_top_card(self):
        """Return the last card added to the hand without removing it."""
        return(self.cards[-1])
    
    def remove_top_card(self):
        """
        Return and remove the last card added to the pile.
        """
        top_card = self.view_top_card()
        self.cards = self.cards[:-1]
        return(top_card)



class Player:
    """
    Represents one player in the game
    
    name: String. Some kind of identifier for the player
    should_knock_strategy: Function(hand, deck, pile, anyone_knocked, current_turn). Returns Boolean
    should_draw_pile_strategy: Function(hand, deck, pile, anyone_knocked, current_turn). Returns Boolean
    pick_discard_strategy: Function(hand, deck, pile, anyone_knocked, current_turn). Returns Card.
    
    """
    
    def __init__(self, name, should_knock_strategy, should_draw_pile_strategy, pick_discard_strategy, verbose = False):
        self.name = name

        self.should_knock_strategy = should_knock_strategy
        self.should_draw_pile_strategy = should_draw_pile_strategy
        self.pick_discard_strategy = pick_discard_strategy
        
        self.score = [0]        
        self.hand = Hand()
        self.knocked = False
        self.verbose = verbose
        
    def reset_hand(self):
        """Delete your hand and form a new, empty one"""
        self.hand = Hand()
        
    def draw_from_deck(self, deck, n = 1):
        """Draw n cards from the deck and add them to your hand."""
        self.hand.add_cards(deck.draw(n))
        
    def draw_from_pile(self, pile):
        """Add the top card of the discard pile to your hand."""
        self.hand.add_cards(pile.remove_top_card())
        
    def discard_to_pile(self, card, pile):
        """
        Find card in your hand and add it to the discard pile, removing it from your hand
        
        card: Card. A Card describing the card you'd like to discard.
        pile: Pile. The active discard pile to add the card to.
        
        NOTE: Throws an error if the card is not in the player's hand
        """
        
        self.hand.remove_cards(card)
        pile.add_cards(card)
            
        
    def take_turn(self, deck, pile, anyone_knocked, current_turn):
        """
        Use your strategies to take your turn. This means:
        1) Decide if you should knock
        2) If you do not want to knock, decide which pile to pick from
        3) If you picked from a pile, select a card to discard.
        
        deck: Deck. The remaining game deck.
        pile: Pile. The current discard pile.
        anyone_knocked: Boolean. True if another player has alreay knocked,
                        thus signaling the end of the game and that this player cannot knock
        current_turn: Int. Current turn in the round (starts at 1)
        """
    
        # The player first decides if he is going to knock
        # The player cannot have knocked yet if he is taking a turn. 
        self.knocked = self.should_knock_strategy(self.hand, deck, pile, anyone_knocked, current_turn)
        
        if self.verbose and self.knocked:
            print(self.name, "decided to knock! (Score of", self.hand.score(), ")")
        
        if not self.knocked:   
            # The player next decides whether to draw from the deck or the pile
            if self.verbose: 
                if pile.length():
                    print("The top card on the pile is a", pile.view_top_card())
                else:
                    print("There are no cards in the discard pile.")
            draw_from_pile = self.should_draw_pile_strategy(self.hand, deck, pile, anyone_knocked, current_turn)

            if draw_from_pile:
                if self.verbose: print(self.name, "drew the", pile.view_top_card(), "from the pile.")
                self.draw_from_pile(pile)

            else:
                self.draw_from_deck(deck)
                if self.verbose: print(self.name, "drew a", self.hand.cards[-1], "from the deck.")
                
            # The player finally decides which card to discard and add to the pile
            discard_card = self.pick_discard_strategy(self.hand, deck, pile, anyone_knocked, current_turn)
            if self.verbose: print(self.name, "discards the", discard_card)
            self.discard_to_pile(discard_card, pile)
        
    def update_score(self, round_score):
        "Update your global running score with your score for this round."
        self.score.append(self.get_score() + round_score)
        
    def get_score(self):
        """Return your current score."""
        return self.score[-1]
        
    def knock(self):
        """Set your knock status to True."""
        self.knocked = True
    
    def reset_knock(self):
        """Set your knock status to False."""
        self.knocked = False



class Game:
    """
    Create a new game for some number of players between 2 and 3
    """
    
    def __init__(self, player_names, strategy_dict, knock_strategies, pile_strategies,
                 discard_strategies, target_score, total_rounds = None,
                 verbose = False, random_seed = None, data_path = None,
                  extra_comments = "", save_results = True, mode = 'compete'):
        """
        Create a new game to be played by players
        player_names: List of Strings. A list of the names of the game players
        strategy_dict: Dictionary. Mapping name of strategy functions to the functions themselves.
        knock_strategies: List of Strings. Ordered list of players' knock strategies
        pile_strategies: List of Stings. Ordered list of players' pile strategies
        discard_strategies: List of Strings. Ordered list of players' discard strategies
        target_score: Int. Stopping condition for the game
        total_rounds: Int. If entered, will not play to the target score but instead just
                            this many total rounds, storing each value
        verbose: Boolean. If true, will print messages to let the viewer know what's happening.
        random_seed: Int. If entered, will set a seed for game reproducibility.
        data_path: String. If entered, the path to save the results of the simulation. 
                            Should be the path to a csv file.
        extra_comments: String. Any additional comments you'd like to store in the csv database.
        save_results: Boolean. Should we save the results of the simulation?
        """
        # Set the start time time
        self.start_time = datetime.now()
        # If there is a random seed, set it for reproducibility
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)
        self.random_seed = random_seed
        # Get a list of all the game players
        self.num_players = len(player_names)
        self.players = []
        self.strategy_dict = strategy_dict
        self.knock_strategies = knock_strategies
        self.pile_strategies = pile_strategies
        self.discard_strategies = discard_strategies
        for i in range(self.num_players):
            name = player_names[i]
            knock_strat = strategy_dict[knock_strategies[i]]
            pile_strat = strategy_dict[pile_strategies[i]]
            discard_strat = strategy_dict[discard_strategies[i]]
            self.players.append(Player(name, knock_strat, pile_strat, discard_strat, verbose))
        # We will need to keep track of the next player who will take a turn. This will be
        self.curr_dealer = 0
        self.target_score = target_score
        self.verbose = verbose
        self.total_rounds = total_rounds
        # Store some information about saving
        self.data_path = data_path
        self.extra_comments = extra_comments
        self.save_results = save_results
        self.mode = mode
        if self.mode == 'turn score calculator':
            self.turn_score_dict = {'round': [], 'player0': [], 'player1': []}
        if self.verbose: 
            print("------------------------------------------------------------")
            if total_rounds is not None:
                print("New game started! Play", total_rounds, "total rounds")
            else:
                print("New game started! Play to", target_score)
            print("------------------------------------------------------------")
        
        
    def play_round(self, round_number):
        """
        Play one round. A round is defined as:
        1) Start with a fresh deck
        2) Deal hands to each player
        3) Until someone knocks or the deck runs out of cards, rotate turns.
        4) Once there are no more turns, score everyone's hand
        5) Compare the "knocker" to the scores of the other players, updating totals.
        """
        # Make a new shuffled deck
        self.deck = Deck()
        # Make an empty discard pile
        self.pile = Pile()
        # Deal to each player
        for player in self.players:
            player.reset_knock()
            player.reset_hand()
            player.draw_from_deck(self.deck, 9)   
        # Play one whole round until no more turns can be taken
        round_over = False
        current_turn = 0
        anyone_knocked = False
        player_to_go = (self.curr_dealer + 1) % self.num_players
        if self.verbose: print(self.players[self.curr_dealer].name, "is this round's dealer.")
        while not round_over:
            current_turn = current_turn + 1
            curr_player = self.players[player_to_go]
            if self.verbose: 
                print("----------------------------------------")
                print("It is", curr_player.name + "'s", "turn.")
                print("----------------------------------------")
                print(curr_player.name + "'s", "hand to start the turn is:", curr_player.hand)
            if curr_player.knocked:
                round_over = True
                if self.verbose: print(curr_player.name, "has already knocked, the round is over.")
            else:
                # This must destructively change the player's hand, knocked status, the deck, and the pile.
                curr_player.take_turn(self.deck, self.pile, anyone_knocked, current_turn)
                if self.verbose: print(curr_player.hand.score(), "is their score after their turn.")
                if curr_player.knocked:
                    anyone_knocked = True
                else:
                    if self.mode == 'turn score calculator':
                        if player_to_go == 0:
                            if self.verbose: print("append player 0 turn dictionary")
                            self.turn_score_dict['player0'][round_number].append(curr_player.hand.score())
                        elif player_to_go == 1:
                            if self.verbose: print("append player 1 turn dictionary")
                            self.turn_score_dict['player1'][round_number].append(curr_player.hand.score())
                player_to_go = (player_to_go + 1) % self.num_players
                if not self.deck.length():
                    if self.verbose: print("The deck is empty! This ends the round. We will score the round as if", curr_player.name, "knocked. (unless someone else already has)")
                    round_over = True
                    if not anyone_knocked:
                        curr_player.knocked = True
                        anyone_knocked = True
        
        # Now that the round is over, we need to score the round for each player
        for player in self.players:
            if self.verbose: print("Scoring", player.name + "'s", "hand of:", player.hand)
            player.round_score = player.hand.score()
            if self.verbose: print(player.name + "'s", "hand scores a", player.round_score)
        
        # Create a list of the players who did not knock and note the player who did knock
        non_knock_players = []
        for player in self.players:
            if self.verbose: print(player.name + "Knocked?", player.knocked)
            if not player.knocked:
                non_knock_players.append(player)
            else:
                knock_player = player
        
        # Compare the knock player's round score to each of the other round scores and update player scores 
        for player in non_knock_players:
            if self.verbose: 
                print("Comparing knocker", knock_player.name + "'s",
                      "score of", knock_player.round_score, "to",
                      player.name + "'s", "score of", player.round_score)
                print(knock_player.name + "'s", "score will change by", player.round_score - knock_player.round_score)
                print(player.name + "'s", "score will change by", knock_player.round_score - player.round_score)
            knock_player.update_score(player.round_score - knock_player.round_score)
            player.update_score(knock_player.round_score - player.round_score)
            
        
        # The next player will be the dealer in the next game
        self.curr_dealer = (self.curr_dealer + 1) % self.num_players
        
        if self.verbose:
            for player in self.players:
                print(player.name + "'s", "current score is", player.get_score())


    def store_results(self):
        end_time = datetime.now()
        elapsed_seconds = (end_time - self.start_time).total_seconds()
        new_results = pd.DataFrame({"sim_id": [], "seed": [], "player_number": [],
                               "draw_strategy": [], "discard_strategy": [], "knock_strategy": [],
                               "rounds": [], "wins": [], "avg_win": [], "var_win": [],
                               "start_time": [], "elapsed_seconds": [],
                               "notes": []})
        csv_exists = os.path.exists(self.data_path)
        if csv_exists:
            old_results = pd.read_csv(self.data_path)
            max_prev_id = max(old_results.sim_id)
        else:
            print("No data found in", self.data_path)
            print("Creating new csv.")
            max_prev_id = 0

        for i in range(len(self.players)):
            curr_row = {"sim_id": max_prev_id + 1, "seed": self.random_seed,
                        "player_number": i,
                        "draw_strategy": self.pile_strategies[i],
                        "discard_strategy": self.discard_strategies[i],
                        "knock_strategy": self.knock_strategies[i], 
                        "rounds": self.total_rounds, "wins": sum(np.diff(np.array(self.players[i].score)) > 0),
                        "avg_win": np.mean(np.diff(np.array(self.players[i].score))),
                        "var_win": np.std(np.diff(np.array(self.players[i].score)))**2,
                        "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "elapsed_seconds": elapsed_seconds,
                        "notes": self.extra_comments}
            new_results = new_results.append([curr_row], ignore_index = True)
        if csv_exists:
            all_results = old_results.append(new_results, ignore_index = True)
            all_results.to_csv(self.data_path, index = False)
        else:
            new_results.to_csv(self.data_path, index = False)
        
    def play_game(self):
        """
        Take turns taking rounds until either: 
            1) Someone achieves the target score or
            2) The total rounds are achieved,
        Thereby ending the game.
        """
        if self.total_rounds is not None:
            for round_num in range(self.total_rounds):
                if self.mode == 'turn score calculator':
                    self.turn_score_dict['round'].append(round_num)
                    self.turn_score_dict['player0'].append([])
                    self.turn_score_dict['player1'].append([])
                self.play_round(round_num)


        else:
            while max([p.get_score() for p in self.players]) < self.target_score:
                self.play_round(0)
        if self.save_results:
            self.store_results()
        # Game is now over, return a dictionary mapping names to scores
        if self.mode == 'turn score calculator':
            return self.turn_score_dict
        return {p.name:p.score for p in self.players}





