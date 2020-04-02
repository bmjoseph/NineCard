# Strategies to test (add to research questions):


We have to decide a few things when comprising a game strategy:
1. When to knock
2. When to draw from pile vs rest of deck
3. What to discard

Things to consider:

1. Knocking:
    - How many cards have been taken off the deck
    - How many times has each player taken from the pile
    - What score your opponents knocked at last turn
2. Drawing from Discard Pile vs rest of Deck:
    - Number of cards left in deck
    - Can taking the top card complete a set or a run?
    - Can taking the top card get 2/3 cards for a set or a run?
        - Is that better than drawing a random card
        - Does the amount of cards left in deck play into this?
    - Given perfect info (i.e. you remember all of the cards that have been discarded into the discard pile), how many cards are left in the deck that can help your hand (i.e. fill a set or a run)?
    
3. Discarding:
    - How many cards are left in the deck?
        - (you would potentially take less risk later in the deck and just throw away big cards while in the beginning you might hold onto them to try to get a set/run)
    - Should you discard the highest card not yet in a run or a set even if it's one card away from becoming a run/set?
        - Does the amount of cards left in deck play into this?
        
        
        
As of the time of writing this strategy, we don't know some of the optimal parameters that are chosen in these strategies (i.e. what the optimal score to knock is at, whether it's helpful to draw from the discard pile only until a certain amount of cards remain in the deck, etc... Therefore, the values selected in these strategies are mere guesses from experience/intuition, and we should first seek to solve for these values, and then test the strategies. 


Strategy 0 (random):

1. Knocks: randomly select every turn whether to knock or not
2. Draws: randomly select every turn whether to draw from pile or draw from rest of deck
3. Discard: randomly select a card to discard (doesn't matter if it's in a run/set or not)

Strategy 1 (constant):

1. Knocks: Knock when you have less than [50, 30, 10] (choose one of those values for the whole game)
2. Draws: Draw from [pile, rest of deck] (choose one of those values for the whole game)
3. Discard: Always discard highest card that is not in a set or a run

*Note: There are 6 sub-strategies in strategy 1, by choosing one of the knock values and pairing it with a "draw from" selection*

Strategy 2 (beginner/basic):

1. Knocks: Knock when you have less than [50, 30, 10] (choose one of those values for the whole game)
2. Draws: If you can complete a set/run by picking up a card from pile, then do so, otherwise, draw from rest of deck
3. Discard: Always discard highest card that is not in a set or a run


Strategy 3 (Intermediate):

1. Knocks: Knock when you have less than [50, 30, 10] (choose one of those values for the whole game)
2. Draws: If you can complete a set/run by picking up a card from pile, then do so, otherwise, draw from rest of deck
3. Discard: If there is still *more than half of the deck available to draw from*, isolate all of the cards that are parts of "near runs" or "near sets" (i.e. cards that are 2/3 of the way to completion of a set or a run). Then discard the highest remaining card that is not part of a set/run or a near-set/run. If there is *less than half of the deck available to draw from,* discard the highest remaining card that is not a part of a set/run. 

*Note, "half the deck" is a parameter that can be changed*

Strategy 3b (Intermediate + more risky):

1. Knocks: Knock when you have less than [50, 30, 10] (choose one of those values for the whole game)
2. Draws: *If there is still more than half of the deck available to draw from* and *if you can add a card to your deck that gets your a "near run" or a "near set" by picking up from the discard pile, then do so,* otherwise, draw from rest of deck. *If there is less than half of the deck available to draw from,* only pick up from the discard pile if you can complete a set/run by doing so, otherwise, pick up from the rest of the deck.
3. Discard: If there is still *more than half of the deck available to draw from*, isolate all of the cards that are parts of "near runs" or "near sets" (i.e. cards that are 2/3 of the way to completion of a set or a run). Then discard the highest remaining card that is not part of a set/run or a near-set/run. If there is *less than half of the deck available to draw from,* discard the highest remaining card that is not a part of a set/run. 

*Note, "half the deck" is a parameter that can be changed*


Strategy 4 (Advanced):

1. Knocks: Knock based on two parameters (your score and the turn number you are on): 
    - For the riskiest strategy (where you'll knock at 50 on the first hand), the rules are as follows:
        - first turn, you must have <=50 to knock
        - second turn, you must have <=40 to knock
        - third turn, you must have <=30 to knock
        - fourth turn, you must have <=20 to knock
        - fifth turn and all turns thereafter, you must have <=10 to knock
    - For the moderate strategy (where you'll knock at 30 on the first hand), the rules are as follows:
        - first turn, you must have <=30 to knock
        - second turn, you must have <=25 to knock
        - third turn, you must have <=20 to knock
        - fourth turn, you must have <=15 to knock
        - fifth turn and all turns thereafter, you must have <=10 to knock
    - For the most conservative strategy (where you'll knock at 10 on the first hand), the rules are as folows:
        - first turn, you must have <= 10 to knock
        - second turn, you must have <= 10 to knock
        - third turn, you must have <= 8 to knock
        - fourth turn, you must have <= 8 to knock
        - fifth turn and thereafter, you must have <= 5 to knock
2. Draws: *If there is still more than half of the deck available to draw from* and *if you can add a card to your deck that gets your a "near run" or a "near set" by picking up from the discard pile, then do so,* otherwise, draw from rest of deck. *If there is less than half of the deck available to draw from,* only pick up from the discard pile if you can complete a set/run by doing so, otherwise, pick up from the rest of the deck.
3. Discard: If there is still *more than half of the deck available to draw from*, isolate all of the cards that are parts of "near runs" or "near sets" (i.e. cards that are 2/3 of the way to completion of a set or a run). Then discard the highest remaining card that is not part of a set/run or a near-set/run. If there is *less than half of the deck available to draw from,* discard the highest remaining card that is not a part of a set/run. 

Strategy 5 (Expert):

TODO

Strategy 6 (Master):

TODO