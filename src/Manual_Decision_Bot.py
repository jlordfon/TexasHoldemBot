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
        all_combs = self.COMB(52 - np.sum(self.cards_revealed), self.hand_num + self.table_num - np.sum(self.cards_in_hand) - np.sum(self.cards_on_table))
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
                    # Calculate probability of getting an x card flush.
                    elif hand == 5:
                        continue
                    # Calculate probability of getting an x card fullhouse.
                    elif hand == 6:
                        continue
                    # Calculate probability of getting an x card 4kind.
                    elif hand == 7:
                        continue
                    # Calculate probability of getting an x card straightflush.
                    else:
                        continue

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