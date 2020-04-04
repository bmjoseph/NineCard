# ---------------------------------------------------------
# Code to score a hand in Nine Card
# @Source: https://www.reddit.com/r/algorithms/comments/4zfv8o/a_dynamic_programming_algorithm_for_gin_rummy/d6w04hr/
# Core algorithm is from the source, we made some modifications
# in order to make it fit into our framework and return
# the score of the cards that do not fit into a run or a set.
# ---------------------------------------------------------


ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', \
     'T', 'J', 'Q', 'K']

suits = ['S', 'H', 'D', 'C']


def lreversed(l, hand_boof):
    return [k for k in reversed(l)]

def rankOf(x, hand_boof):
    return x[0]

def nextRankOf(x, hand_boof):
    if x == 'K': return 'nothing higher'
    return ranks[ranks.index(x) + 1]

def suitOf(x, hand_boof):
    return x[1]

def scoreOf(x, hand_boof):
    if rankOf(x, hand_boof) in ['T', 'J', 'Q', 'K']:
        return 10
    elif rankOf(x, hand_boof) == 'A':
        return 1
    else:
        return ranks.index(rankOf(x, hand_boof)) + 1    

def F(sz, hand_boof, suitStarts):
    mem = dict() # stores answer score
    prev = dict() # stores previous state
    cards = dict() # stores cards to get to prev state
    tsz = tuple(sz)
    if tsz in mem:
        return mem[tsz]
    if sum(sz) == 0:
        mem[tsz] = 0
        return 0
    maxScore = 0
    maxPrev = None
    maxCards = None
    # Ignore one card in each set:
    for s in range(4):
        if sz[s] > 0:
            sz[s] = sz[s] - 1
            if maxScore < F(sz, hand_boof, suitStarts):
                maxScore = F(sz, hand_boof, suitStarts)
                maxPrev = tuple(sz)
                maxCards = None
            sz[s] = sz[s] + 1
    # Get ranks of last cards in each suit
    r = [None if sz[s] == 0 else hand_boof[suitStarts[suits[s]] + sz[s] - 1][0] for s in range(4)]
    # Try to take all cards as a set except suit #i
    for i in range(0,5):
        canTake = True
        rank = None
        for j in range(0, 4):
            if j == i:
                continue
            if r[j] == None:
                canTake = False
            if rank != None and rank != r[j]:
                canTake = False
            rank = r[j]
        if canTake:
            curCards = []
            curScore = 0
            for j in range(0, 4):
                if j == i: 
                    continue
                sz[j] = sz[j] - 1
                curCards.append([rank, suits[j]])
                curScore = curScore + scoreOf([rank, suits[j]], hand_boof)
            curScore = curScore + F(sz, hand_boof, suitStarts)
            if curScore > maxScore:
                maxScore = curScore
                maxPrev = tuple(sz)
                maxCards = curCards
            for j in range(0, 4):
                if j == i: 
                    continue
                sz[j] = sz[j] + 1
    # Try to get streak in suit s
    for s in range(4):
        if sz[s] < 2: 
            continue
        r = hand_boof[suitStarts[suits[s]] + sz[s] - 1][0]
        curCards = [hand_boof[suitStarts[suits[s]] + sz[s] - 1]]
        curScore = scoreOf(curCards[-1], hand_boof)
        for i in range(2,sz[s]+1):
            rr = hand_boof[suitStarts[suits[s]] + sz[s] - i][0]    
            if nextRankOf(rr, hand_boof) != r: # streak is broken
                break
            r = rr
            curCards.append(hand_boof[suitStarts[suits[s]] + sz[s] - i])
            curScore += scoreOf(curCards[-1], hand_boof)
            if i >= 3:
                sz[s] -= i
                if maxScore < curScore+F(sz, hand_boof, suitStarts):
                    maxScore = curScore+F(sz, hand_boof, suitStarts)
                    maxPrev = tuple(sz)
                    maxCards = [_ for _ in reversed(curCards)]
                sz[s] += i
    mem[tsz] = maxScore
    prev[tsz] = maxPrev
    cards[tsz] = maxCards
    return maxScore

def Restore(sz, hand_boof):
    if sz == None or mem[sz] == 0:
        return
    Restore(prev[sz], hand_boof)
    if cards[sz]:
        print (cards[sz])
        
def boofify(hand):
    
    '''
    
    change a perfectly good hand, to a hand_boof
    
    '''

    formatrank = [c.rank for c in hand.cards]
    formatsuit = [c.suit for c in hand.cards]

    hand_boof = []
    for i in range(len(formatrank)):

        hand_boof.append([formatrank[i], formatsuit[i]])
        
    hand_boof.sort(key=lambda u: suits.index(u[1]) * 20 + ranks.index(u[0]))
    
    return hand_boof


def give_me_handBoof_suitStarts_and_sz(hand):
    
    '''takes in a hand, outputs hand_boof, suitStarts, sz'''
    
    hand_boof = boofify(hand) 
    suitStarts = dict()
    suitStarts[suits[0]] = 0 #first card with given suit
    for i in range(1, len(hand_boof)):
        if hand_boof[i-1][1] != hand_boof[i][1]:
            suitStarts[hand_boof[i][1]] = i
    suitSize = dict()
    last = len(hand_boof)
    for s in reversed(suits):
        if not s in suitStarts:
            suitStarts[s] = last
            suitSize[s] = 0
        else:
            suitSize[s] = last - suitStarts[s]
        last = suitStarts[s]



    sz = [suitSize[s] for s in suits]  
    
    return hand_boof, suitStarts, sz


        
