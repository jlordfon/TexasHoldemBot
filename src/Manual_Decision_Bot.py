import numpy as np
from math import factorial
from sys import exit as sys_exit

class Manual_Decision_Bot:
    def __init__(self, name, cash_list):
        # Initialize self
        self.name = name
        # TODO FIGURE out the cash stuff alongside betting
        self.cash_list = cash_list
        self.pot = 0
        # Set game rules
        self.hand_num = 2
        self.table_num = 5
        # Set up opponents
        self.num_players = len(cash_list)
        self.fold_list = [0] * len(cash_list)
        # Set up cards
        self.cards_in_hand = np.zeros((4,13), dtype = np.int8)
        self.cards_on_table = np.zeros((4,13), dtype = np.int8)
        # Set up probabilities
        self.cards_revealed = np.zeros((4,13), dtype = np.int8)
        self.list_of_hands = ["high", "pair", "2pair", "3kind", "straight", "flush", "fullhouse", "4kind", "straightflush"]
        self.my_probs = np.zeros((4,13,len(self.list_of_hands)), dtype = np.float64)
        self.opponent_probs = np.zeros((4,13,len(self.list_of_hands)), dtype = np.float64)

    def new_round(self):
        self.cards_in_hand = np.zeros((4,13), dtype = np.int8)
        self.cards_on_table = np.zeros((4,13), dtype = np.int8)
        self.cards_revealed = np.zeros((4,13), dtype = np.int8)
        self.fold_list = [0] * self.num_players

    def dealt_card(self, suit, num, recipient):
        # Ensure the card hasn't been dealt yet
        if self.cards_revealed[suit,num] > 0:
            sys_exit("This card has already been dealt!")
        if recipient == 'Table' or recipient == 'table':
            self.cards_on_table[suit,num] += 1
        else:
            self.cards_in_hand[suit, num] += 1
        self.cards_revealed[suit, num] += 1
    
    def COMB(self,n,r):
        return (factorial(n)/(factorial(r)*factorial(n-r)))

    def calc_probs(self):
        # Reset probabilities
        self.my_probs =  np.zeros((4,13,len(self.list_of_hands)), dtype = np.float64)
        # Calculate the total number of possible card combinations going forward.
        all_combs = self.COMB(52 - np.sum(self.cards_revealed), self.hand_num + self.table_num - np.sum(self.cards_revealed))
        # Loop through the possible poker hands.
        for hand in range(self.my_probs.shape[2]):
            # Loop through the card numbers.
            for num in range(self.my_probs.shape[1]):
                # Loop through the card suits.
                for suit in range(self.my_probs.shape[0]):
                    
                    # Calculate probability of getting an x card high hand.
                    if hand == 0:
                        # Throw out any cards less than 9 because there are 7 cards and there has to be no pair or straight
                        if num < 7:
                            continue
                        # Check if any higher cards have been drawn
                        elif num < 12 and np.sum(self.cards_revealed[:,num+1:]) > 0:
                            continue
                        # Check if any other cards of the same suit have been drawn
                        elif np.sum(self.cards_revealed[:, num]) - np.sum(self.cards_revealed[suit,num]) > 0:
                            continue
                        # Check if there are any pairs
                        elif np.amax(np.sum(self.cards_revealed, axis = 0)) > 1:
                            continue
                        # Check if all cards have been drawn
                        elif np.sum(self.cards_revealed) - self.hand_num - self.table_num == 0 and self.cards_revealed[suit,num] == 0:
                            continue
                        else:
                            reqd_cards_needed = 1 - self.cards_revealed[suit,num]
                            other_cards_needed = self.hand_num + self.table_num - np.sum(self.cards_revealed) - reqd_cards_needed
                            other_cards_opts = np.count_nonzero(np.sum(self.cards_revealed[:,:num], axis = 0)==0)
                            if other_cards_needed > 0:
                                other_cards_combs = self.COMB(other_cards_opts,other_cards_needed) * 4**other_cards_needed
                                self.my_probs[suit,num,hand] = other_cards_combs / all_combs
                            elif reqd_cards_needed == 0:
                                self.my_probs[suit,num,hand] = 1
                            elif reqd_cards_needed == 1:
                                self.my_probs[suit,num,hand] = 1/(52 - np.sum(self.cards_revealed))
                    
                    # Calculate probability of getting an x card pair.
                    elif hand == 1:
                        # Throw out any pairs of the lowest suit
                        if suit == 0:
                            continue
                        # Throw out any scenarios where we already have 3 of a kind
                        elif np.amax(np.sum(self.cards_revealed, axis=0)) >= 3:
                            continue
                        # Throw out any scenarios where we already have a pair
                        elif np.amax(np.sum(self.cards_revealed[:,np.arange(self.cards_revealed.shape[1]) != num], axis=0)) >= 2:
                            continue
                        # Throw out any scenarios where we already have a higher suit of the pair
                        elif np.sum(self.cards_revealed[suit:, num]) - self.cards_revealed[suit,num] >= 1:
                            continue
                        else:
                            reqd_cards_needed = 1 - self.cards_revealed[suit,num]
                            reqd_combs = 1
                            opt_cards_needed = 1 - np.sum(self.cards_revealed[0:suit,num])
                            if opt_cards_needed > 0:
                                opt_combs = self.COMB(suit - np.sum(self.cards_revealed[0:suit,num]),1 - np.sum(self.cards_revealed[0:suit,num]))
                            else:
                                opt_combs = 1
                            # If we need more cards than draws left, throw out possibility
                            other_needed = self.hand_num + self.table_num - np.sum(self.cards_revealed) - reqd_cards_needed - opt_cards_needed
                            if other_needed < 0:
                                continue
                            elif other_needed == 0:
                                self.my_probs[suit,num,hand] = (reqd_combs * opt_combs) / all_combs
                            else:
                                other_opts = np.count_nonzero(np.sum(self.cards_revealed[:,np.arange(self.cards_revealed.shape[1]) != num], axis = 0)==0)
                                other_combs = self.COMB(other_opts, other_needed) * 4**other_needed
                                print('other_combs B is: ', other_combs)
                                self.my_probs[suit,num,hand] = (reqd_combs * opt_combs * other_combs) / all_combs

                    # Calculate probability of getting an x card 2pair.
                    elif hand == 2:
                        # Throw out any leading pairs of the lowest suit or number.
                        if suit == 0 or num == 0:
                            continue
                        # Throw out any 2 pair possibillities if we already have 3 of a kind
                        elif np.amax(np.sum(self.cards_revealed, axis = 0)) > 2:
                            continue
                        else:
                            # Card Categories:
                            # lead_cards_needed = leading pair suit and num
                            # lead_cards_opt = leading pair 0:suit and num
                            # trail_cards_needed = 2x trailing pair num_b
                            # higher_card_none = all of the cards num_b+ that haven't been drawn
                            # lower_card_none = all of the card numbers 0:num_b that haven't been drawn
                            # lower_card_one = all of the card numbers 0:num_b that have been drawn once
                            lead_cards_needed = 1 - self.cards_revealed[suit,num]
                            # Pass if we've already revealed 2 of the lower leading cards (three of a kind)
                            if np.sum(self.cards_revealed[0:suit,num]) > 1:
                                continue
                            # Calculate the number of leading pair options
                            elif np.sum(self.cards_revealed[0:suit,num]) == 1:
                                lead_cards_opt_needed = 0
                                lead_cards_opt_opts = 0
                                lead_pair_combs = 1
                            else:
                                lead_cards_opt_needed = 1
                                lead_cards_opt_opts = suit
                                lead_pair_combs = self.COMB(lead_cards_opt_opts,lead_cards_opt_needed)
                            # Find the combinations for each trailing pair
                            total_combs = 0
                            for num_b in range(num):
                                # Make sure there's no higher trailing pair
                                if (num_b + 1) < num and np.amax(np.sum(self.cards_revealed[:, num_b+1:num], axis = 0)) == 2:
                                    continue
                                # Calculate the combinations to get the trailing pair
                                trail_cards_needed = 2 - np.sum(self.cards_revealed[:,num_b])
                                trail_cards_opts = 4 - np.sum(self.cards_revealed[:,num_b])
                                trail_pair_combs = self.COMB(trail_cards_opts,trail_cards_needed)
                                other_cards_needed = self.hand_num + self.table_num - np.sum(self.cards_revealed) - lead_cards_needed - lead_cards_opt_needed - trail_cards_needed
                                # Ensure that we can draw enough cards to finish the hand
                                if other_cards_needed < 0:
                                    continue
                                # Check if we need any other cards
                                elif other_cards_needed == 0:
                                    total_combs += lead_pair_combs * trail_pair_combs
                                # Calculate the combinations for the other card draws
                                elif other_cards_needed == 1:
                                    # higher_num_none = all of the numbers greater than num_b that haven't been drawn
                                    # lower_num_none = all of the numbers 0:num_b that haven't been drawn
                                    # lower_num_one = all of the numbers 0:num_b that have been drawn once
                                    higher_num_none = np.count_nonzero(np.sum(self.cards_revealed[:,num_b+1:], axis = 0)==0) - np.count_nonzero(np.sum(self.cards_revealed[:,num])==0)
                                    lower_num_none = np.count_nonzero(np.sum(self.cards_revealed[:,:num_b], axis = 0)==0)
                                    lower_num_one = np.count_nonzero(np.sum(self.cards_revealed[:,:num_b], axis = 0)==1)
                                    other_cards_opts = higher_num_none * 4 + lower_num_none * 4 + lower_num_one * 3
                                    other_cards_combs = other_cards_opts
                                    total_combs += lead_pair_combs * trail_pair_combs * other_cards_combs
                                elif other_cards_needed == 2:
                                    # higher_num_none = all of the number greater than num_b that haven't been drawn
                                    # lower_num_none = all of the numbers 0:num_b that haven't been drawn
                                    # lower_num_one = all of the numbers 0:num_b that have been drawn once
                                    higher_num_none = np.count_nonzero(np.sum(self.cards_revealed[:,num_b+1:], axis = 0)==0) - np.count_nonzero(np.sum(self.cards_revealed[:,num])==0)
                                    lower_num_none = np.count_nonzero(np.sum(self.cards_revealed[:,:num_b], axis = 0)==0)
                                    lower_num_one = np.count_nonzero(np.sum(self.cards_revealed[:,:num_b], axis = 0)==1)
                                    # Other draw combinations if draw 1 is higher_num_none
                                    ##########################
                                    draw_2_combs_if_higher = (higher_num_none - 1) * 4 + lower_num_none * 4 + lower_num_one * 3
                                    draw_1_higher_combs = higher_num_none * 4
                                    # Other draw combinations if draw 1 is lower_num_none
                                    draw_2_combs_if_lower_none = higher_num_none * 4 + (lower_num_none - 1) * 4 + (lower_num_one + 1) * 3
                                    draw_1_lower_none_combs = lower_num_none * 4
                                    # Other draw combinations if draw 1 is lower_num_one
                                    draw_2_combs_if_lower_one = higher_num_none * 4 + lower_num_none * 4 + (lower_num_one - 1) * 3
                                    draw_1_lower_one_combs = lower_num_one * 3
                                    # Total other draw combinations
                                    other_cards_combs = draw_1_higher_combs * draw_2_combs_if_higher + draw_1_lower_none_combs * draw_2_combs_if_lower_none + draw_1_lower_one_combs * draw_2_combs_if_lower_one
                                    total_combs += lead_pair_combs * trail_pair_combs * other_cards_combs
                                elif other_cards_needed == 3:
                                    # higher_num_none = all of the number greater than num_b that haven't been drawn
                                    # lower_num_none = all of the numbers 0:num_b that haven't been drawn
                                    # lower_num_one = all of the numbers 0:num_b that have been drawn once
                                    higher_num_none = np.count_nonzero(np.sum(self.cards_revealed[:,num_b+1:], axis = 0)==0) - np.count_nonzero(np.sum(self.cards_revealed[:,num])==0)
                                    lower_num_none = np.count_nonzero(np.sum(self.cards_revealed[:,:num_b], axis = 0)==0)
                                    lower_num_one = np.count_nonzero(np.sum(self.cards_revealed[:,:num_b], axis = 0)==1)
                                    # Initial draw combinations
                                    draw_higher_combs = higher_num_none * 4
                                    draw_lower_none_combs = lower_num_none * 4
                                    draw_lower_one_combs = lower_num_one * 3
                                    total_other_draw_combs = draw_higher_combs + draw_lower_none_combs + draw_lower_one_combs
                                    # Combinations for each draw combo
                                    other_cards_combs_higher_higher = draw_higher_combs * (draw_higher_combs - 4) * (total_other_draw_combs - 8)
                                    other_cards_combs_higher_lower_none = draw_higher_combs * draw_lower_none_combs * (total_other_draw_combs - 4 - 4 + 3)
                                    other_cards_combs_higher_lower_one = draw_higher_combs * draw_lower_one_combs * (total_other_draw_combs - 4 - 3)
                                    other_cards_combs_lower_none_higher = draw_lower_none_combs * draw_higher_combs * (total_other_draw_combs - 4 + 3 - 4)
                                    other_cards_combs_lower_none_lower_none = draw_lower_none_combs * (draw_lower_none_combs - 4) * (total_other_draw_combs - 8 + 6)
                                    other_cards_combs_lower_none_lower_one = draw_lower_none_combs * (draw_lower_one_combs + 3) * (total_other_draw_combs - 4 + 3 - 3)
                                    other_cards_combs_lower_one_higher = draw_lower_one_combs * draw_higher_combs * (total_other_draw_combs - 3 - 4)
                                    other_cards_combs_lower_one_lower_none = draw_lower_one_combs * draw_lower_none_combs * (total_other_draw_combs - 3 - 4 + 3)
                                    other_cards_combs_lower_one_lower_one = draw_lower_one_combs * (draw_lower_one_combs - 3) * (total_other_draw_combs - 6)
                                    other_cards_combs = other_cards_combs_higher_higher + other_cards_combs_higher_lower_none + other_cards_combs_higher_lower_one + other_cards_combs_lower_none_higher + other_cards_combs_lower_none_lower_none + other_cards_combs_lower_none_lower_one + other_cards_combs_lower_one_higher + other_cards_combs_lower_one_lower_none + other_cards_combs_lower_one_lower_one
                                    total_combs += lead_pair_combs * trail_pair_combs * other_cards_combs
                                else:
                                    sys_exit('Line 201, 2-pair error, incorrect number of "other" cards to draw')
                            self.my_probs[suit,num,hand] = total_combs / all_combs

                    # Calculate probability of getting an x card 3kind.
                    elif hand == 3:
                        continue
                    # Calculate probability of getting an x card straight.
                    elif hand == 4:
                        continue
                        reqd_cards = 5
                        # if the "lead" card is too low, throw it out
                        if num < reqd_cards - 1:
                            continue
                        # if there aren't enough cards for a flush in that suit, throw it out
                        if np.sum(self.cards_revealed) - np.sum(self.cards_revealed[suit,num]) > self.hand_num + self.table_num - reqd_cards:
                            continue
                    # Calculate probability of getting an x card flush.
                    elif hand == 5:
                        continue
                        reqd_cards = 5
                        # if the "lead" card is too low, throw it out
                        if num < reqd_cards - 1:
                            continue
                        # if there aren't enough cards for a flush in that suit, throw it out
                        if np.sum(self.cards_revealed) - np.sum(self.cards_revealed[suit,num]) > self.hand_num + self.table_num - reqd_cards:
                            continue
                    # Calculate probability of getting an x card fullhouse.
                    elif hand == 6:
                        # if the num or suit is too low, throw it out
                        if num == 0 or suit == 0:
                            continue
                        # if there is 4 of a kind, throw it out
                        if np.amax(np.sum(self.cards_revealed, axis = 1)) > 3:
                            continue
                        # if there is a higher lead card, throw it out
                        if np.sum(self.cards_revealed[suit+1:,num]) > 0:
                            continue
                        reqd_cards = 1 # lead card
                        opt_cards = 4 # Any lower combination of 2 and 2 or 1 and 3
                        # if there aren't enough cards left, throw it out
                        
                        # There are many combinations of required cards (3 out of 4 and 2 out of 4 OR 2 out of 4 and 3 out of 4)
                        # Can be superseded by only 4 of a kind
                        continue
                    # Calculate probability of getting an x card 4kind.
                    elif hand == 7:
                        reqd_cards = 4
                        # if there aren't enough cards left, throw it out
                        if np.sum(self.hand_num + self.table_num - np.sum(self.cards_revealed) + np.sum(self.cards_revealed[:,num]) < reqd_cards):
                            continue
                        # There is only 1 combination of required cards
                        # There is no possibility of a superseding hand
                        # Calculate the total combs of other cards
                        other_in_deck = 52 - np.sum(self.cards_revealed) + np.sum(self.cards_revealed[:,num]) - reqd_cards
                        other_to_draw = self.hand_num + self.table_num - np.sum(self.cards_revealed) + np.sum(self.cards_revealed[:,num] - reqd_cards)
                        total_combs = self.COMB(other_in_deck, other_to_draw)
                        self.my_probs[suit,num,hand] = total_combs / all_combs
                    # Calculate probability of getting an x card straightflush.
                    else:
                        reqd_cards = 5
                        # if the "lead" card is too low, throw it out
                        if num < reqd_cards - 1:
                            continue
                        # if the same-suited card immediately above has been drawn, throw it out
                        if num+1 < self.cards_revealed.shape[1] and self.cards_revealed[suit, num+1] == 1:
                            continue
                        # if there aren't enough cards for that straight flush, throw it out
                        if np.sum(self.cards_revealed) - np.sum(self.cards_revealed[suit,num-reqd_cards:num]) > self.hand_num + self.table_num - reqd_cards:
                            continue
                        num_req_drawn = np.sum(self.cards_revealed[suit,num-reqd_cards:num])
                        # There is only 1 combination of required cards
                        # Calculate the total combos of other cards, which excludes the card one higher in the same suit
                        total_combs = 0
                        other_to_draw = self.hand_num + self.table_num - np.sum(self.cards_revealed) - reqd_cards + num_req_drawn
                        # There *is* a possible higher straight
                        if num + 1 < self.cards_revealed.shape[1]:
                            total_combs += self.COMB(52 - np.sum(self.cards_revealed) - reqd_cards + num_req_drawn - 1, other_to_draw)
                        # There is *not* a possible higher straight
                        else:
                            total_combs += self.COMB(52 - np.sum(self.cards_revealed) - reqd_cards + num_req_drawn, other_to_draw)
                        self.my_probs[suit,num,hand] = total_combs / all_combs


def opponents_bets(self, opponents, cash, folded):
    for opponent in opponents:
        self.opponents_cash[opponent] -= cash[opponent]
        self.pot += cash[opponent]
        if folded[opponent]:
            self.opponents_folded[opponent] += 1
        else:
            continue                      

def bet(self, curr_bet):
    # 0 = fold
    # 1 = match
    # 2 = raise
    if self.cash < curr_bet:
        # Return folding and no cash added to pot.
        return 0, 0

        
# Manual Decision Bot Unit Test
if __name__ == "__main__":
    # Note: Suit order: 0 - Clubs, 1 - Diamonds, 2 - Hearts, 3 - Spades
    # Note: The card_number is the actual number minus 2 (because the lowest card is 2 and the arrays are 0-indexed)

    # Initialize
    # Create a bot
    Player_1 = Manual_Decision_Bot('Tex', [1500, 2000, 3500])
    Player_1.new_round()
    # Set up checker
    dealt_cards = np.zeros((4,13), dtype = np.int) # Suit x Rank
    
    # Deal Cards
    # Deal the player a 7 (5+2) of Diamonds
    # Player_1.dealt_card(1, 5, Player_1.name)
    # dealt_cards[1,5] = 1
    # Deal the player an Ace of Hearts
    # Player_1.dealt_card(2, 12, Player_1.name)
    # dealt_cards[2,12] = 1
    # Deal to the table a 2 of Spades
    # Player_1.dealt_card(3, 0, 'Table')
    # dealt_cards[3,0] = 1
    # Deal to the table a 6 of Spades
    # Player_1.dealt_card(3, 4, 'Table')
    # dealt_cards[3,4] = 1
    # Deal to the table a 5 of Diamonds
    # Player_1.dealt_card(1, 3, 'Table')
    # dealt_cards[1,3] = 1
    # Deal to the table a 10 of Clubs
    # Player_1.dealt_card(0, 8, 'Table')
    # dealt_cards[0,8] = 1
    
    # Calculate Probabilities
    # Ask the player to calculate probabilities
    Player_1.calc_probs()
    player_probs = Player_1.my_probs
    # Manually Calculate Probabilities
    cards_left = 7 - np.sum(dealt_cards)
    total_possibilities = 0
    hand_possibilities = np.zeros((4,13,9), dtype = np.int) # Suit x Rank x Poker hand
    # Initialize possibilities list
    current_possibility = []
    prev_idx = -1
    valid_possibility = True
    for ii in range(cards_left):
        for jj in range(prev_idx + 1, 4 * 13):
            if dealt_cards[jj // 13, jj % 13] == 0:
                current_possibility.append(jj)
                prev_idx = jj
                break
    while(valid_possibility):
        print("current_possibility: ", current_possibility)
        total_possibilities += 1
        # Add cards to virtual hand
        for ii in range(len(current_possibility)):
            dealt_cards[current_possibility[ii] // 13, current_possibility[ii] % 13] = 1

        # Determine which poker hand was achieved
        hand_found = False
        # Straight Flush (idx: 8)
        for suit in range(3,-1,-1):
            if hand_found:
                break
            streak = 0
            for rank in range(12,-1,-1):
                if hand_found:
                    break
                if dealt_cards[suit, rank] == 1:
                    streak += 1
                    if streak == 5:
                        hand_found = True
                        hand_possibilities[suit, rank + 4, 8] += 1
                else:
                    streak = 0
        # Four of a Kind (idx: 7)
        if not hand_found:
            dealt_cards_rank_summed = np.sum(dealt_cards, axis = 0)
            for rank in range(12, -1, -1):
                if dealt_cards_rank_summed[rank] == 4:
                    hand_found = True
                    hand_possibilities[3, rank, 7] += 1
                    break
        # Full House (idx: 6)
        if not hand_found:
            three_kind = False
            two_kind = False
            high_suit = 0
            high_rank = 0
            for rank in range(12, -1, -1):
                if hand_found:
                    break
                if dealt_cards_rank_summed[rank] == 3:
                    if not three_kind and not two_kind:
                        three_kind = True
                        high_rank = rank
                        if dealt_cards[3, rank] == 1:
                            high_suit = 3
                        else:
                            high_suit = 2
                    else:
                        hand_found = True
                        hand_possibilities[high_suit, high_rank, 6] += 1
                elif dealt_cards_rank_summed[rank] == 2:
                    if three_kind:
                        hand_found = True
                        hand_possibilities[high_suit, high_rank, 6] += 1
                    elif not two_kind:
                        two_kind = True
                        high_rank = rank
                        if dealt_cards[3, rank] == 1:
                            high_suit = 3
                        elif dealt_cards[2, rank] == 1:
                            high_suit = 2
                        else:
                            high_suit = 1
        # Flush (idx: 5)
        if not hand_found:
            dealt_cards_suit_summed = np.sum(dealt_cards, axis = 1)
            for suit in range(3,-1,-1):
                if dealt_cards_suit_summed[suit] >= 5 and not hand_found:
                    hand_found = True
                    for rank in range(12,-1,-1):
                        if dealt_cards[suit,rank] == 1:
                            hand_possibilities[suit, rank, 5] += 1
                            break
        # Straight (idx: 4)
        if not hand_found:
            streak = 0
            for rank in range(12,-1,-1):
                if dealt_cards_rank_summed[rank] >= 1:
                    streak += 1
                    if streak == 5:
                        hand_found = True
                        if dealt_cards[3, rank + 4] == 1:
                            suit = 3
                        elif dealt_cards[2, rank + 4] == 1:
                            suit = 2
                        elif dealt_cards[1, rank + 4] == 1:
                            suit = 1
                        else:
                            suit = 0
                        hand_possibilities[suit, rank + 4, 4] += 1
                else:
                    streak = 0
        # Three of a Kind (idx: 3)
        if not hand_found:
            for rank in range(12,-1,-1):
                if dealt_cards_rank_summed[rank] == 3:
                    hand_found = True
                    if dealt_cards[3, rank] == 1:
                        hand_possibilities[3, rank, 3] += 1
                    else:
                        hand_possibilities[2, rank, 3] += 1
                    break
        # Two Pair (idx: 2)
        if not hand_found:
            two_kind = False
            high_suit = 0
            high_rank = 0
            for rank in range(12, -1, -1):
                if hand_found:
                    break
                elif dealt_cards_rank_summed[rank] == 2:
                    if two_kind:
                        hand_found = True
                        hand_possibilities[high_suit, high_rank, 2] += 1
                    else:
                        two_kind = True
                        high_rank = rank
                        if dealt_cards[3, rank] == 1:
                            high_suit = 3
                        elif dealt_cards[2, rank] == 1:
                            high_suit = 2
                        else:
                            high_suit = 1
        # Pair (idx: 1)
        if not hand_found:
            for rank in range(12, -1, -1):
                if dealt_cards_rank_summed[rank] == 2:
                    hand_found = True
                    if dealt_cards[3, rank] == 1:
                        suit = 3
                    elif dealt_cards[2, rank] == 1:
                        suit = 2
                    else:
                        suit = 1
                    hand_possibilities[suit, rank, 1] += 1
        # High (idx: 0)
        if not hand_found:
            for rank in range(12,-1,-1):
                for suit in range(3,-1,-1):
                    if dealt_cards[suit, rank] == 1 and not hand_found:
                        hand_found = True
                        hand_possibilities[suit, rank, 0] += 1

        # Remove cards from virtual hand
        for ii in range(len(current_possibility)):
            dealt_cards[current_possibility[ii] // 13, current_possibility[ii] % 13] = 0
        # Determine next possibility
        cur_list_idx = cards_left - 1
        while(valid_possibility):
            current_possibility[cur_list_idx] += 1
            cur_hand_idx = current_possibility[cur_list_idx]
            if cur_hand_idx <= 51 + cur_list_idx - cards_left + 1:
                if dealt_cards[cur_hand_idx // 13, cur_hand_idx % 13] == 0:
                    cur_list_idx += 1
                    if cur_list_idx == cards_left:
                        break
                    current_possibility[cur_list_idx] = current_possibility[cur_list_idx - 1]
                else:
                    continue
            else:
                cur_list_idx -= 1
                if cur_list_idx < 0:
                    valid_possibility = False
    manual_probabilities = hand_possibilities.astype(float) / float(total_possibilities)
    list_of_hands = ["high", "pair", "2pair", "3kind", "straight", "flush", "fullhouse", "4kind", "straightflush"]
    for poker_hand in range(8,-1,-1):
        print("Poker_hand: ", list_of_hands[poker_hand])
        if np.array_equal(manual_probabilities[:,:,poker_hand], Player_1.my_probs[:,:,poker_hand]):
            print("Equivalent?: Yes")
        else:
            print("Equivalent?: No")
        if np.allclose(manual_probabilities[:,:,poker_hand], Player_1.my_probs[:,:,poker_hand], atol=1e-3):
            print("Close?: Yes")
        else:
            print("Close?: No")
        print("Manual Probabilities:")
        print(manual_probabilities[:,:,poker_hand])
        print("Bot Probabilities:")
        print(Player_1.my_probs[:,:,poker_hand])
        print("Difference:")
        print(manual_probabilities[:,:,poker_hand] - Player_1.my_probs[:,:,poker_hand])
        print("Percent Difference:")
        print((manual_probabilities[:,:,poker_hand] - Player_1.my_probs[:,:,poker_hand]) / Player_1.my_probs[:,:,poker_hand])