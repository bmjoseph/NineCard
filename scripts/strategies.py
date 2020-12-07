#----------------------------------------------------------
# Strategy functions and their associated helpers.
#----------------------------------------------------------

import numpy as np
import pandas as pd
from gameLogic import *

def sort_hand(hand):
    
    '''
    
    This function takes in your hand and sorts it by suit, rank, value, and numeric rank. 
    The difference between numeric rank and value is for face cards (i.e. J, Q, K) -- their value is 10 
    but their numeric rank (i.e. for computing sets and runs) is 11, 12, 13 respectively
    
    We output a dataframe that is sorted with 4 columns: suit, rank, value, numericrank
    
    '''
    
    
    
    frame_of_cards = pd.DataFrame(
                            {'suits': [c.suit for c in hand.cards], 'ranks': [c.rank for c in hand.cards], 
                             'values': [c.value for c in hand.cards], 'numeric_ranks': [c.numeric_rank for c in hand.cards]}
                             ).sort_values(['suits', 'values', 'numeric_ranks']).reset_index().drop('index', axis = 1)
    
    return frame_of_cards
    
    
def add_keeper_column(df):
    
    '''
    
    HELPER FUNCTION:
    
    
    takes in dataframe with 4 columns that are sorted by suit, value, numeric rank 
    (data also includes rank column but is not sorted by it).
    
    We see if the cards are a part of 1. any runs (3 or more straight flush) and 2. any sets (3 or 4 of a kin)
    
    outputs keeper column (i.e. do we keep the card in the associated record or not)
        
    '''
    
    ## checking if it's a part of a set
    
    keeper = np.array([])

    for suit in df['suits'].unique():

        suit_frame = df[df['suits'] == suit]

        if len(suit_frame) < 3: #i.e. there are less than 3 cards in the deck that have a certain suit

            lstvals = np.repeat(0, len(suit_frame))

            pass

        else:

            lstvals = np.repeat(0, len(suit_frame))

            for i in range(len(suit_frame) - 2):

                if (suit_frame['numeric_ranks'].iloc[i] - suit_frame['numeric_ranks'].iloc[i+1] == -1 and 
                   suit_frame['numeric_ranks'].iloc[i+1] - suit_frame['numeric_ranks'].iloc[i+2] == -1):

                    lstvals[i] = 1
                    lstvals[i+1] = 1
                    lstvals[i+2] = 1
        keeper = np.append(keeper, lstvals)


    df['run_keeper'] = keeper
    
    
    ## checking if the cards are part of a set and overwriting keeper
    
    parts_of_sets = df['ranks'].value_counts()[df['ranks'].value_counts() >= 3].index.values

    df['set_keeper'] = np.where(df['ranks'].isin(parts_of_sets), 1, 0)
    
    # adding an either column and a both column
    
    df['either'] = np.where((df['run_keeper'] == 1) | (df['set_keeper'] == 1), 1, 0)
    df['both'] = np.where((df['run_keeper'] == 1) & (df['set_keeper'] == 1), 1, 0)
    return df

def make_constant_score_knock_strategy(cutoff):
    """Return a knock strategy where the player will knock if they can achieve a score less than cutoff."""
    def knock_strategy(hand, deck, pile, anyone_knocked, turn):
        if anyone_knocked:
            return False
        return hand.score() < cutoff
    return knock_strategy


def make_list_knock_strategy(lst):
    '''
    Return a knock_strategy where the player will knock if they can achieve a score less than a dynamic cutoff based on turns. 
    The function will be used to for different levels of "aggressiveness" in knock strategies.
    '''
    def strategy(hand, deck, pile, anyone_knocked, turn):
        
        if turn < len(lst): # indexed from 1
            return lst[turn - 1]
        
        else:
            return lst[len(lst) - 1]
        
        return strategy
    

def always_draw_from_pile(hand, deck, pile, anyone_knocked, turn):
    
    '''
    
    Always draw from the pile.
    
    Returns True (as long as there is a card to draw from the pile)
    
    '''
    if not pile.length():
        return False
    
    return True

def never_draw_from_pile(hand, deck, pile, anyone_knocked, turn):
    
    '''
    
    Never draw from pile (always draw from the deck).
    
    Returns False
    
    '''
     
    return False

    
def draw_from_pile_if_completes(hand, deck, pile, anyone_knocked, turn):
    

    
    '''
    This function takes in the sorted data and whether or not we are planning to keep any of the cards
    (i.e. the output from the add_keeper_column function), and adds in the new_card to see if increases the 
    the number of cards we would keep.
    
    1. We first examine if it contributes anything to the runs we already have --
    if so, we store the boolean True in adds_runs_value and return True because we already know we want to keep the card
    if not, we store the boolean False and move onto sets:
    
    2. if the new card contributes to a set, we store the boolean True in adds_sets_value and return True 
    because this card adds value.
    
    else, we store the boolean False. 
    
    3. If it doesn't contribute to either sets nor runs, we return False
    
    '''
    # getting the new card object
    
    if not pile.length():
        return False
    
    new_card = pile.view_top_card()
    
    
    #getting info on new card
    
    suit = new_card.suit
    value = new_card.value
    rank = new_card.rank
    numericrank = new_card.numeric_rank
    
    #checking to see if it adds value to runs (store answer in adds_runs_value)
    
    keeperdata = add_keeper_column(df = sort_hand(hand))
    
    suited_data = keeperdata[keeperdata['suits'] == suit] # getting the relevant suit data that the new card is in
    
    if len(suited_data) < 2:
        adds_runs_value = False
    else:
        # this if statement checks whether or not the new card is part of a run
        if (len(suited_data[suited_data['numeric_ranks'].isin([numericrank - 2, numericrank - 1])]) == 2 or
            len(suited_data[suited_data['numeric_ranks'].isin([numericrank - 1, numericrank + 1])]) == 2 or
            len(suited_data[suited_data['numeric_ranks'].isin([numericrank + 1, numericrank + 2])]) == 2):
            
            #print('adds value to runs')
            return True
            
    
        else: 
            adds_runs_value = False
            
    #checking to see if it adds value to sets (store answer in adds_sets_value)
    
    
    if len(keeperdata[keeperdata['numeric_ranks'] == numericrank]) >= 2:
        
        #print('adds value to sets')
        return True
        
    else:
        
        adds_sets_value = False
        
    
    #finally, if neither adds_runs_value nor adds_sets_value is True, we return False
    
    
    return False



#### not used after creating higher order function below, used initially for aggressive strategy ####
def half_length_near_runs_sets_draw_from_pile(hand, deck, pile, anyone_knocked, turn):
    
    '''
    Takes in the hand and the card we are considering.
    
    If there is more than half the deck remaining, we figure out if it is part of a near set/run, and keep it if it is.
    
    If less than half the deck is remaining, we figure out if it is part of an actual set/run, and keep it if it is.
    
    Return Boolean (whether to keep it or not).
    
    '''
    
    # getting the new card object
    
    if not pile.length():
        return False
    
    num_players = 2
    
    starting_deck_length = 52 - (num_players*9)
    
    if deck.length()*2 > starting_deck_length: #i.e. more than half of the original cards in the deck to draw (after the cards are dealt)
        #look for near sets and near runs
    
        sorted_hand = sort_hand(hand)

        new_card = pile.view_top_card()


        #getting info on new card

        suit = new_card.suit
        value = new_card.value
        rank = new_card.rank
        numericrank = new_card.numeric_rank

        #checking if part of near set:

        if len(sorted_hand[sorted_hand['numeric_ranks'] == numericrank]) >= 1:

            return True

        else:
            #checking if part of near run:

            if len(sorted_hand[(sorted_hand['suits'] == suit) & (abs(sorted_hand['numeric_ranks'] - numericrank) == 1)] >= 1):

                return True

            return False
       
    else: #i.e. there are less than or equal to half the cards remaining in the deck (after the cards are dealt)
        
        #only keep the card if it completes a set or a run
        return draw_from_pile_if_completes(hand, deck, pile, anyone_knocked, turn) # returns boolean     
        
def generate_specific_length_near_runs_sets_draw_from_pile(deck_fraction):
    
    
    def specific_length_near_runs_sets_draw_from_pile(hand, deck, pile, anyone_knocked, turn):
        
        '''
        Takes in the hand and the card we are considering.

        If there is more than the deck fraction remaining, we figure out if it is part of a near set/run, and keep it if it is.

        If less than the given deck fraction is remaining, we figure out if it is part of an actual set/run, and keep it if it is.

        Return Boolean (whether to keep it or not).
    
        '''
        
        
    
        # getting the new card object

        if not pile.length():           
            return False
        
        if anyone_knocked:
            return draw_from_pile_if_completes(hand, deck, pile, anyone_knocked, turn) 

        num_players = 2

        starting_deck_length = 52 - (num_players*9)

        if deck.length() > starting_deck_length*deck_fraction: #i.e. more than half of the original cards in the deck to draw (after the cards are dealt)
            #look for near sets and near runs

            sorted_hand = sort_hand(hand)

            new_card = pile.view_top_card()


            #getting info on new card

            suit = new_card.suit
            value = new_card.value
            rank = new_card.rank
            numericrank = new_card.numeric_rank

            #checking if part of near set:

            if len(sorted_hand[sorted_hand['numeric_ranks'] == numericrank]) >= 1:

                return True

            else:
                #checking if part of near run:

                if len(sorted_hand[(sorted_hand['suits'] == suit) & (abs(sorted_hand['numeric_ranks'] - numericrank) == 1)] >= 1):

                    return True

                return False

        else: #i.e. there are less than or equal to half the cards remaining in the deck (after the cards are dealt)

            #only keep the card if it completes a set or a run
            return draw_from_pile_if_completes(hand, deck, pile, anyone_knocked, turn) # returns boolean
        
    return specific_length_near_runs_sets_draw_from_pile
        
    
def discard_highest_useless(hand, deck, pile, anyone_knocked, turn):
    
    '''
    this function takes in your hand (as a dataframe) and discards the highest card that isn't a "keeper" 
    (i.e. has a 0 in the run_and_set_keeper column)
    
    Note: if you drew from the pile, that card cannot be discarded 
    
    Note: there can be many strategies here -- I will lay out two and we can add to this
    
    Note: needs to return a card object'''
    
    ten_card_hand = add_keeper_column(df = sort_hand(hand))
    
    todiscard = ten_card_hand[ten_card_hand['either'] == 0]
    
    #if all cards are part of a set or a run, discard a random card
    
    if len(todiscard) == 0:
        
        strategy1 = ten_card_hand.sample(n = 1)
        
    else:
        
        strategy1 = todiscard[todiscard['values'] == todiscard['values'].max()].sample(n = 1)
    
    # card is now picked -- let's turn it into a card object and return it
    
    strategy1_card_object_return = Card(strategy1['ranks'].iloc[0], strategy1['suits'].iloc[0])
    
    return strategy1_card_object_return



#### not used after creating higher order function below, used initially for aggressive strategy ####

def near_runs_sets_discarder(hand, deck, pile, anyone_knocked, turn):
    
    '''
    
    This function helps discard cards in a smarter way. (Note, the hand object here already has 10 cards, waiting for one to be discarded) 
    
    If there are more than half of the cards in the deck left, isolate all of the cards that are part of near sets/runs. 
    Then discard the highest remaining card that is not part of a full set/run or near set/run.
    If there are less than half of the cards in the deck left, discard the highest remaining card that is not a part of a set/run. 
    
    Returns Card Object
    
    '''
    
    num_players = 2
    
    starting_deck_length = 52 - (num_players*9)
    
    if deck.length()*2 > starting_deck_length: #i.e. more than half of the original cards in the deck to draw (after the cards are dealt)
        #look for near sets and near runs
        
        #get the info about the cards
        suits = np.array([c.suit for c in hand.cards])
        ranks = np.array([c.rank for c in hand.cards])
        values = np.array([c.value for c in hand.cards])
        numeric_ranks = np.array([c.numeric_rank for c in hand.cards])
        
        # looking for near sets and near runs:
        
        bool_array = np.repeat(False, len(numeric_ranks))
        
        for i in range(len(numeric_ranks)):
            
            near_set_array = numeric_ranks == numeric_ranks[i] # generates boolean for card's near sets
            near_set_array[i] = False # avoiding an incorrect True here: will get populated by a different element
            near_run_array = (abs(numeric_ranks - numeric_ranks[i]) == 1) & (suits == suits[i]) # generates boolean for card's near runs
            near_run_array[i] = False # # avoiding an incorrect True here: will get populated by a different element
            bool_array = bool_array + near_set_array + near_run_array # adding booleans
            # (once element is true, it's never false later (at the end we'll know which cards we can discard)
            
            
            
            
        # selecting the card to discard
        
        ## getting all of the "false" indexes from bool_array, then selecting the max of those in numeric_ranks to discard
               
        if sum(bool_array) == len(bool_array): # i.e. if every value is True, then each card is part of a near set/run (this is rare)
            
            # discard a random card
            
            final_index = np.where(numeric_ranks == np.random.choice(numeric_ranks))[0][0] #the extra indexing breaks a tie if needed
            
            return Card(ranks[final_index], suits[final_index])
            
            
            
        relevant_indices = np.where(bool_array == False) # note, this should never return an empty array as per above condition
        
        final_index = np.where(numeric_ranks == max(numeric_ranks[relevant_indices]))[0][0] # the extra indexing breaks a tie if needed
        
        return Card(ranks[final_index], suits[final_index])
        
        
    else:
        
        return discard_highest_useless(hand, deck, pile, anyone_knocked, turn)
    

def generate_near_runs_sets_discarder(deck_fraction):
    
    def near_runs_sets_discarder(hand, deck, pile, anyone_knocked, turn):

        '''

        This function helps discard cards in a smarter way. (Note, the hand object here already has 10 cards, waiting for one to be discarded) 

        If there are more than the deck fraction of cards left in the deck, isolate all of the cards that are part of near sets/runs. 
        Then discard the highest remaining card that is not part of a full set/run or near set/run.
        If there are less than the deck fraction of cards in the deck left, discard the highest remaining card that is not a part of a set/run. 

        Returns Card Object

        '''

        if anyone_knocked:
            return discard_highest_useless(hand, deck, pile, anyone_knocked, turn)

        num_players = 2

        starting_deck_length = 52 - (num_players*9)

        if deck.length() > starting_deck_length*deck_fraction: #i.e. more than half of the original cards in the deck to draw (after the cards are dealt)
            #look for near sets and near runs

            #get the info about the cards
            suits = np.array([c.suit for c in hand.cards])
            ranks = np.array([c.rank for c in hand.cards])
            values = np.array([c.value for c in hand.cards])
            numeric_ranks = np.array([c.numeric_rank for c in hand.cards])

            # looking for near sets and near runs:

            bool_array = np.repeat(False, len(numeric_ranks))

            for i in range(len(numeric_ranks)):

                near_set_array = numeric_ranks == numeric_ranks[i] # generates boolean for card's near sets
                near_set_array[i] = False # avoiding an incorrect True here: will get populated by a different element
                near_run_array = (abs(numeric_ranks - numeric_ranks[i]) == 1) & (suits == suits[i]) # generates boolean for card's near runs
                near_run_array[i] = False # # avoiding an incorrect True here: will get populated by a different element
                bool_array = bool_array + near_set_array + near_run_array # adding booleans
                # (once element is true, it's never false later (at the end we'll know which cards we can discard)




            # selecting the card to discard

            ## getting all of the "false" indexes from bool_array, then selecting the max of those in numeric_ranks to discard

            if sum(bool_array) == len(bool_array): # i.e. if every value is True, then each card is part of a near set/run (this is rare)

                # discard a random card

                final_index = np.where(numeric_ranks == np.random.choice(numeric_ranks))[0][0] #the extra indexing breaks a tie if needed

                return Card(ranks[final_index], suits[final_index])



            relevant_indices = np.where(bool_array == False) # note, this should never return an empty array as per above condition

            final_index = np.where(numeric_ranks == max(numeric_ranks[relevant_indices]))[0][0] # the extra indexing breaks a tie if needed

            return Card(ranks[final_index], suits[final_index])


        else:

            return discard_highest_useless(hand, deck, pile, anyone_knocked, turn)
        
    return near_runs_sets_discarder

    


