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
        self.suits_num = 4
        self.numbers_num = 13
        # Set up opponents
        self.num_players = len(cash_list)
        self.fold_list = [0] * len(cash_list)
        # Set up cards
        self.fresh_round = True
        self.cards_in_hand = np.zeros((self.suits_num, self.numbers_num), dtype = np.int8)
        self.cards_on_table = np.zeros((self.suits_num, self.numbers_num), dtype = np.int8)
        # Set up probabilities
        self.cards_revealed = np.zeros((self.suits_num, self.numbers_num), dtype = np.int8)
        self.list_of_hands = ["high", "pair", "2pair", "3kind", "straight", "flush", "fullhouse", "4kind", "straightflush"]
        self.my_probs = np.zeros((self.suits_num, self.numbers_num,len(self.list_of_hands)), dtype = np.float64)
        self.opponent_probs = np.zeros((self.suits_num, self.numbers_num,len(self.list_of_hands)), dtype = np.float64)

    def new_round(self):
        self.fresh_round = True
        self.cards_in_hand = np.zeros((self.suits_num, self.numbers_num), dtype = np.int8)
        self.cards_on_table = np.zeros((self.suits_num, self.numbers_num), dtype = np.int8)
        self.cards_revealed = np.zeros((self.suits_num, self.numbers_num), dtype = np.int8)
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
        self.fresh_round = False
    
    def COMB(self,n,r):
        return (factorial(n)/(factorial(r)*factorial(n-r)))

    def calc_probs(self):
        # Reset probabilities
        self.my_probs =  np.zeros((self.suits_num, self.numbers_num,len(self.list_of_hands)), dtype = np.float64)
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
                                # print('other_combs B is: ', other_combs)
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
                        if np.amax(np.sum(self.cards_revealed, axis = 0)) > 3:
                            continue
                        # if there is a higher lead card, throw it out
                        if np.sum(self.cards_revealed[suit+1:,num]) > 0:
                            continue
                        reqd_cards = 1 # lead card
                        opt_cards = 4 # Any lower combination of 2 and 2 or 1 and 3
                        reqd_cards_to_draw = 1 - self.cards_revealed[suit,num]
                        opt_cards_to_draw = np.min(opt_cards - np.sum(self.cards_revealed[:suit+1,num]) - np.amax(np.sum(self.cards_revealed[:,:num], axis = 0)),0)
                        # if there aren't enough cards left, throw it out
                        if (opt_cards_to_draw + reqd_cards_to_draw) > (self.hand_num + self.table_num - np.sum(self.cards_revealed)):
                            continue
                        # There are many combinations of required cards (3 out of 4 and 2 out of 4 OR 2 out of 4 and 3 out of 4)
                        # Can be superseded by only 4 of a kind
                        total_combs = 0
                        opt_zeros = np.count_nonzero(np.sum(self.cards_revealed[:,:num], axis=0) == 0)
                        opt_ones = np.count_nonzero(np.sum(self.cards_revealed[:,:num], axis=0) == 1)
                        opt_twos = np.count_nonzero(np.sum(self.cards_revealed[:,:num], axis=0) == 2)
                        opt_threes = np.count_nonzero(np.sum(self.cards_revealed[:,:num], axis=0) == 3)
                        # All valid combinations with leading pair
                        # Do we already have a leading pair?
                        if np.sum(self.cards_revealed[:suit,num]) == 1:
                            lead_pair_combs = 1
                        else:
                            lead_pair_combs = suit
                        # Do we already have a trailing trio?
                        if opt_threes > 0:
                            trail_trio_combs = 1
                            # Calculate all "other" possibillities here?
                            # Exclude third leading card, 4 of a kinds, and higher full houses (pairs in this case, trios further down)
                        else:
                            continue
                        # All valid combinations with leading trio
                        self.my_probs[suit,num,hand] = total_combs / all_combs
                    # Calculate probability of getting an x card 4kind.
                    elif hand == 7:
                        reqd_cards = 4
                        # if there aren't enough cards left, throw it out
                        if np.sum(self.hand_num + self.table_num - np.sum(self.cards_revealed) + np.sum(self.cards_revealed[:,num]) < reqd_cards):
                            continue
                        # if the suit is too low, throw it out (4 of a kind requires the highest suit to lead)
                        if suit < 3:
                            continue
                        # There is only 1 combination of required cards
                        # There is no possibility of a superseding hand
                        # Calculate the total combs of other cards
                        other_in_deck = 52 - np.sum(self.cards_revealed) + np.sum(self.cards_revealed[:,num]) - reqd_cards
                        other_to_draw = self.hand_num + self.table_num - np.sum(self.cards_revealed) + np.sum(self.cards_revealed[:,num]) - reqd_cards
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
                        if np.sum(self.cards_revealed) - np.sum(self.cards_revealed[suit,num+1-reqd_cards:num+1]) > self.hand_num + self.table_num - reqd_cards:
                            continue
                        num_req_drawn = np.sum(self.cards_revealed[suit,num+1-reqd_cards:num+1])
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
    Player_1.dealt_card(1, 5, Player_1.name)
    dealt_cards[1,5] = 1
    # Deal the player an 8 of Diamonds
    Player_1.dealt_card(1, 6, Player_1.name)
    dealt_cards[1,6] = 1
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
    
    Test_Set_0_Initialization_Tests = True
    Test_Set_1_Individual_Function_Tests = True
    Test_Set_2_Dealing_Cards_Tests = True
    Test_Set_3_Probability_Calc_Tests = True
    Test_Set_4_Decision_Tests = True
    
    ## 0) Bot Initialization Tests
    if (Test_Set_0_Initialization_Tests):
        print("Running Test Set 0: Initialization Tests")
        
        # Case 0.0, Nominal Variables Check
        Test0_0 = Manual_Decision_Bot("Test", [1, 20, 300])
        assert Test0_0.num_players == 3, print("Case 0.0 failed: num_players is %i, not 3.", Test0_0.num_players)
        assert Test0_0.fold_list == [0, 0, 0], print("Case 0.0 failed: fold_list is %l, not [0, 0, 0].", *Test0_0.fold_list)
        assert np.sum(Test0_0.cards_in_hand) == 0, "Case 0.0 failed: hand not empty of cards."
        assert np.sum(Test0_0.cards_on_table) == 0, "Case 0.0 failed: table not empty of cards."
        assert np.sum(Test0_0.cards_revealed) == 0, "Case 0.0 failed: cards revealed."
        assert np.sum(Test0_0.my_probs) == 0, "Case 0.0 failed: probabilities not null."
        assert np.sum(Test0_0.opponent_probs) == 0, "Case 0.0 failed: opponent probabilities not null."
        del Test0_0
        
        # Case 0.1, No name
        try:
            Test0_1 = Manual_Decision_Bot("", [1000, 1000, 1000])
        except:
            assert False, "Case 0.1 failed: bot could not be created without name."
        else:
            del Test0_1
        
        # Case 0.2, Long name
        try:
            Test0_2 = Manual_Decision_Bot("This is a very long name and I don't know why anyone would choose something like this in their code", [1000, 1000, 1000])
        except:
            assert False, "Case 0.2 failed: bot could not be created with a long name."
        else:
            del Test0_2
            
        # Case 0.3, Improper name
        # Not sure we have an improper name
        try:
            Test0_3 = Manual_Decision_Bot("''", [1000, 1000, 1000])
        except:
            assert True
        else:
            assert False, "Case 0.3 failed: bot successfully created with an improper name."
            del Test0_3
    
        # Case 0.4, No cash
        try:
            Test0_4 = Manual_Decision_Bot("Test", [0, 0, 1000])
        except:
            assert True
        else:
            assert False, "Case 0.4 failed: bot successfully created with players lacking cash."
            del Test0_4
        
        # Case 0.5, Lots of Cash
        try:
            Test0_5 = Manual_Decision_Bot("Test", [10000000000000000000000000000000, 10000000000000000000000000000000, 1000])
        except:
            assert False, "Case 0.5 failed: bot could not be created with lots of cash."
        else:
            del Test0_5
            
        # Case 0.6, Negative Cash
        try:
            Test0_6 = Manual_Decision_Bot("Test", [-1, -900, 1000])
        except:
            assert True
        else:
            assert False, "Case 0.6 failed: bot successfully created with negative cash."
            del Test0_6
            
        # Case 0.7, Improper Cash Type
        try:
            Test0_7 = Manual_Decision_Bot("Test", ["gh", 1.033, 1000])
        except:
            assert True
        else:
            assert False, "Case 0.7 failed: bot successfully created with improper cash type(s)."
            del Test0_7
        
        # Case 0.8, No players
        try:
            Test0_8 = Manual_Decision_Bot("Test", [])
        except:
            assert True
        else:
            assert False, "Case 0.8 failed: bot successfully created with no players."
            del Test0_8
    
        # Case 0.9, No opponents
        try:
            Test0_9 = Manual_Decision_Bot("Test", [1000])
        except:
            assert True
        else:
            assert False, "Case 0.9 failed: bot successfully created with no opponents."
            del Test0_9
    
        # Case 0.10, Lots of players
        try:
            Test0_10 = Manual_Decision_Bot("Test", [1, 20, 300, 4000, 50000, 600000, 7000000, 80000000, 900000000, 1000000000, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        except:
            assert False, "Case 0.10 failed: bot could not be created with lots of players."
            del Test0_10


    ## 1) Individual Function Unit Tests
    if(Test_Set_1_Individual_Function_Tests):
        print("Running Test Set 1: Individual Function Unit Tests")
        
        # Case 1.0.0, New Round Reset Checks
        
        # Case 1.1.0, comb - Nominal
        
        # Case 1.1.1, comb - Negative
        
        # Case 1.1.2, comb - Too Large
        
        # Case 1.1.3, comb - Improper Type
    
    ## 2) Dealing Cards Unit Tests
    if(Test_Set_2_Dealing_Cards_Tests):
        print("Running Test Set 2: Dealing Cards Unit Tests")
        Test_2 = Manual_Decision_Bot('Test', [1500, 2000, 3500])

        # Case 2.0.0, Impossible card dealt - Number Negative
        Test_2.new_round()
        Test_2.dealt_card
        
        # Case 2.0.1, Impossible card dealt - Number Too Large
        
        # Case 2.0.2, Impossible card dealt - Number Improper Type
        
        # Case 2.0.3, Impossible card dealt - Suit Negative
        
        # Case 2.0.4, Impossible card dealt - Suit Too Large
        
        # Case 2.0.5, Impossible card dealt - Suit Improper Type
        
        # Case 2.1, Multiple of the same card dealt
        
        # Case 2.2, Too many cards dealt

    
    ## 3) Probability Calc Unit Tests
    if(Test_Set_3_Probability_Calc_Tests):
       print("Running Test Set 3: Probability Calc Unit Tests")
       
       # Case 3.0, No Cards Dealt
       Player_1.new_round()
       dealt_cards = np.zeros((4,13), dtype = np.int) # Suit x Rank
       probs = np.zeros((4,13,9), dtype = np.float64)
       Player_1.calc_probs()
       assert np.equal(Player_1.my_probs, probs), "Case 3.0 Failed, No Cards Dealt"
       
       # Case 3.1, Hand Dealt
       
       # Case 3.2, Flop
       
       # Case 3.3, All Revealed - High (Jack Spade)
       
       # Case 3.4, All Revealed - Pair (Queen Diamonds)
       
       # Case 3.5, All Revealed - Two Pair (6 Spades, 3 Diamonds)
       
       # Case 3.6, All Revealed - Three of a Kind (2 Hearts)
       
       # Case 3.7, All Revealed - Straight (7 Spades)
       
       # Case 3.8, All Revealed - Flush (10 Clubs)
       
       # Case 3.9, All Revealed - Full House (Pair: King of Hearts, Triple: 3 Spades)
       
       # Case 3.10, All Revealed - Four of a Kind (Ace Spades)
       
       # Case 3.11, All Revealed - Straight Flush (9 Diamonds)


    ## 4) Decision Unit Tests
    if(Test_Set_4_Decision_Tests):
        print("Running Test Set 4: Decision Unit Tests")