import numpy as np
from math import factorial
from Manual_Decision_Bot import Manual_Decision_Bot
import time

# Note: Suit order: 0 - Clubs, 1 - Diamonds, 2 - Hearts, 3 - Spades
# Note: The card_number is the actual number - 2 (because the lowest card is 2 and the arrays are 0-indexed)

Player_1 = Manual_Decision_Bot('Tex', [1500, 2000, 3500])
Player_1.new_round()
# Deal the player a 7 (5+2) of Diamonds
Player_1.dealt_card(1, 5, Player_1.name)
# Deal the player an Ace of Hearts
Player_1.dealt_card(2, 12, Player_1.name)
# Deal to the table a 2 of Spades
Player_1.dealt_card(3, 0, 'Table')
# Deal to the table a 6 of Spades
Player_1.dealt_card(3, 4, 'Table')
# Deal to the table a 5 of Diamonds
Player_1.dealt_card(1, 3, 'Table')
# Deal to the table a 10 of Clubs
Player_1.dealt_card(0, 8, 'Table')
# Ask the player to calculate probabilities
Player_1.calc_probs()
player_1_probs = Player_1.my_probs
player_1_cards = Player_1.cards_in_hand
table_cards = Player_1.cards_on_table
num_cards_left = 7 - np.sum(player_1_cards) - np.sum(table_cards)
num_combs_total = (factorial(52-player_1_cards-table_cards)/(factorial(num_cards_left)*factorial(52-player_1_cards-table_cards-num_cards_left)))

