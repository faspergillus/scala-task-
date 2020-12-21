# This game is for 3-10 people
from random import shuffle

CARD_VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
CARD_SUITS = ['\u2665', '\u2666', '\u2663', '\u2660']
CARD_WEIGHT = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]


class Card:
    def __init__(self, number):
        self.suit, self.value = divmod(number, 13)
        self.weight = CARD_WEIGHT[self.value]

    def __str__(self):
        return CARD_VALUES[self.value] + CARD_SUITS[self.suit]

    def __repr__(self):
        return str(self)


class Deck:
    def __init__(self):
        self.cards = [Card(i) for i in range(52)]
        self.shuffle()

    def shuffle(self):
        shuffle(self.cards)

    def __str__(self):
        return f'Deck {len(self.cards)}'

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.cards)

    def draw_card(self):
        return self.cards.pop()

    def draw_cards(self, cards_count=0):
        return [self.draw_card() for i in range(cards_count)]


class Player:
    def __init__(self, obj=Deck, number=1, stake=0):
        self.player_number = number
        self.cards = obj.draw_cards(1)
        self.player_stake = stake
        self.poker_hand = None
        self.kicker = None
        # I needed the following attributes in order to determine the winner at the end
        self.pair = 0
        self.set = 0
        self.full_house1 = 0
        self.full_house2 = 0
        self.two_pairs = 0

    def __str__(self):
        return f'Player {self.player_number}: {self.cards}'

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.cards)


class Game():
    def __init__(self):
        self.dealer = None
        self.small_blind = None
        self.big_blind = None
        self.biggest_stake = None
        self.stake_list = []
        self.flop = []
        self.turn = []
        self.river = []
        self.deleted_ones = []
        self.winner = None
        self.winners = []

    def define_dealer(self, lst_of_players):  # In order to determine the dealer, all players need to give a card. The dealer will be the one with the strongest card
        self.dealer = lst_of_players[0]
        for player in lst_of_players:
            if player.cards[0].weight > self.dealer.cards[0].weight:
                self.dealer = player

    def define_small_blind(self, nmb_of_players, lst_of_players):
        self.small_blind = self.dealer.player_number + 1
        if self.small_blind > nmb_of_players:
            self.small_blind = lst_of_players[0].player_number
        elif self.small_blind == nmb_of_players:
            self.small_blind = lst_of_players[nmb_of_players - 1].player_number
        else:
            self.small_blind = lst_of_players[self.small_blind - 1].player_number
        self.small_blind = lst_of_players[self.small_blind - 1]
        if self.small_blind.player_number == 1:
            # print('Please make a stake')
            # input
            stake = 1
            self.small_blind.player_stake = stake
        else:
            stake = 2
            self.small_blind.player_stake = stake

    def define_big_blind(self, nmb_of_players, lst_of_players):
        self.big_blind = self.small_blind.player_number + 1
        if self.big_blind > nmb_of_players:
            self.big_blind = lst_of_players[0].player_number
        elif self.big_blind == nmb_of_players:
            self.big_blind = lst_of_players[nmb_of_players - 1].player_number
        else:
            self.big_blind = lst_of_players[self.big_blind - 1].player_number

        self.big_blind = lst_of_players[self.big_blind - 1]
        self.big_blind.player_stake = self.small_blind.player_stake * 2
        self.biggest_stake = self.big_blind.player_stake

    def make_raise(self):
        self.biggest_stake = self.biggest_stake * 2
        self.stake_list.append('raise')
        return self.biggest_stake

    def reraise(self):
        self.biggest_stake = self.biggest_stake * 2
        self.stake_list.append('reraise')
        return self.biggest_stake

    def call(self):
        self.stake_list.append('call')
        return self.biggest_stake

    def check(self):
        pass

    def fold(self, pl):
        self.stake_list.append('fold')
        self.deleted_ones.append(pl)

    def evaluate_starting_hands(self, pl):    # make a raise with the cards that most often win
        card1 = pl.cards[0][0].weight         # exit the game with the cards that have a very small chance
        card2 = pl.cards[0][1].weight         # of a good combination
        suit1 = pl.cards[0][0].suit
        suit2 = pl.cards[0][1].suit
        if (card1 == 14 and card2 == 14) or (card1 == 13 and card2 == 13):
            if self.stake_list.count('raise') == 0:
                return self.make_raise()
            else:
                if self.stake_list.count('reraise') == 0:
                    return self.reraise()
                else:
                    return self.call()
        elif (card1 == 14 and card2 == 13) or (card1 == 13 and card2 == 14):
            if self.stake_list.count('raise') == 0:
                return self.make_raise()
            else:
                if self.stake_list.count('reraise') == 0:
                    return self.reraise()
                else:
                    return self.call()
        elif card1 >= 10 and card2 >= 10:
            if self.stake_list.count('raise') == 0:
                return self.make_raise()
            else:
                return self.call()
        if (card1 == 3 and card2 == 7) or (card1 == 7 and card2 == 3):
            return self.fold(pl)
        if (card1 == 3 and card2 == 11) or (card1 == 11 and card2 == 3):
            return self.fold(pl)
        if (card1 == 2 and card2 == 9) or (card1 == 9 and card2 == 2):
            return self.fold(pl)
        else:
            return self.call()

    def evaluate_combination(self, pl, r, board):
        self.make_combination(pl, board)
        if pl.poker_hand == 'Royal Flush' or pl.poker_hand == 'Straight-flush':
            return self.make_raise()
        elif pl.poker_hand == 'Four of a kind':
            if self.stake_list.count('raise') == 0 or self.stake_list.count('reraise') == 0:
                return self.make_raise()
            else:
                return self.call()
        elif pl.poker_hand == 'Full House' or pl.poker_hand == 'Flush' or pl.poker_hand == 'Straight':
            if self.stake_list.count('raise') == 0 or self.stake_list.count('reraise') == 0:
                return self.make_raise()
        elif pl.poker_hand == 'Three of a kind' or pl.poker_hand == 'Two Pairs' or pl.poker_hand == 'Pair':
            return self.call()
        else:
            return self.call()

    def first_round_bidding(self, nmb_of_players, lst_of_players):
        next_stake = self.big_blind.player_number + 1
        while next_stake != False:
            if next_stake == nmb_of_players:
                lst_of_players[nmb_of_players - 1].player_stake = self.evaluate_starting_hands(
                    lst_of_players[nmb_of_players - 1])
                print('Next is:', nmb_of_players, ', His stake:', lst_of_players[nmb_of_players - 1].player_stake)
                next_stake = lst_of_players[0].player_number
            elif next_stake > nmb_of_players:
                lst_of_players[0].player_stake = self.evaluate_starting_hands(lst_of_players[0])
                print('Next is:', lst_of_players[0].player_number, ', His stake:', lst_of_players[0].player_stake)
                next_stake = lst_of_players[1].player_number
            else:
                lst_of_players[next_stake - 1].player_stake = self.evaluate_starting_hands(
                    lst_of_players[next_stake - 1])
                print('Next is:', next_stake, ', His stake:', lst_of_players[next_stake - 1].player_stake)
                next_stake = next_stake + 1
            if next_stake == self.big_blind.player_number:
                lst_of_players[next_stake - 1].player_stake = self.evaluate_starting_hands(
                    lst_of_players[next_stake - 1])
                print('Next is:', next_stake, ', His stake:', lst_of_players[next_stake - 1].player_stake)
                next_stake = False

    def next_round_bidding(self, nmb_of_players, lst_of_players, r, board):
        if len(self.deleted_ones) != 0:
            making_stake = 0
            if self.dealer.player_number > nmb_of_players:
                making_stake = lst_of_players[ 0 ].player_number
            else:
                for player in lst_of_players:
                    if player.player_number == self.dealer.player_number:
                        making_stake = player.player_number
                        break
            if making_stake == 1:
                stop = nmb_of_players
            else:
                stop = making_stake - 1
            while making_stake != stop:
                lst_of_players[making_stake - 1].player_stake = self.evaluate_combination(
                    lst_of_players[making_stake - 1], r, board)
                print('Next is:', lst_of_players[making_stake - 1].player_number, ', His stake:',
                      lst_of_players[making_stake - 1].player_stake)
                making_stake = making_stake + 1
                if making_stake > nmb_of_players:
                    making_stake = 1
        else:
            making_stake = self.dealer.player_number + 1
            while making_stake != self.dealer.player_number:
                if making_stake == nmb_of_players:
                    lst_of_players[nmb_of_players - 1].player_stake = self.evaluate_combination(
                        lst_of_players[nmb_of_players - 1], r, board)
                    print('Next is:', lst_of_players[nmb_of_players - 1].player_number, ', His stake:',
                          lst_of_players[nmb_of_players - 1].player_stake)
                    making_stake = lst_of_players[0].player_number
                elif making_stake > nmb_of_players:
                    lst_of_players[0].player_stake = self.evaluate_combination(lst_of_players[0], r, board)
                    print('Next is:', lst_of_players[0].player_number, ', His stake:',
                          lst_of_players[0].player_stake)
                    making_stake = lst_of_players[1].player_number
                else:
                    lst_of_players[making_stake - 1].player_stake = self.evaluate_combination(
                        lst_of_players[making_stake - 1], r, board)
                    print('Next is:', lst_of_players[making_stake - 1].player_number, ', His stake:',
                          lst_of_players[making_stake - 1].player_stake)
                    making_stake = making_stake + 1
                if making_stake == self.dealer.player_number:
                    lst_of_players[making_stake - 1].player_stake = self.evaluate_combination(
                        lst_of_players[making_stake - 1], r, board)
                    print('Next is:', lst_of_players[making_stake - 1].player_number, ', His stake:',
                          lst_of_players[making_stake - 1].player_stake)

    def equalize(self, lst_of_players):    #this feature equalizes all bets to start the next round
        stake = lst_of_players[0].player_stake
        count = 0
        for player in lst_of_players:
            if player.player_stake == stake:
                count = count + 1
        if count != number_of_players:
            for player in players:
                player.player_stake = game.call()
        game.stake_list.clear()

    def check_del(self, nmb_of_players, lst_of_players):
        if len(game.deleted_ones) != 0:
            for player in game.deleted_ones:
                lst_of_players.remove(player)
            for idx, player in enumerate(lst_of_players):
                if idx == 0:
                    player.player_number = 1
                else:
                    player.player_number = players[idx - 1].player_number + 1
            nmb_of_players = nmb_of_players - len(game.deleted_ones)

    def make_combination(self, playerr, lst_of_cards):
        lst_of_cards.append(playerr.cards[0][0])
        lst_of_cards.append(playerr.cards[0][1])
        lst_of_suits = []
        lst_of_weights = []
        for card in lst_of_cards:
            lst_of_suits.append(card.suit)
        for idx, suit in enumerate(lst_of_suits):
            if lst_of_suits.count(suit) == 5:
                for card in lst_of_cards:
                    if card.suit == suit:
                        lst_of_weights.append(card.weight)
                lst_of_weights = list(set(lst_of_weights))
                if len(lst_of_weights) == 5:
                    if lst_of_weights[0] == 10:
                        playerr.poker_hand = 'Royal Flush'
                    elif lst_of_weights[len(lst_of_weights) - 1] - lst_of_weights[0] == 4:
                        playerr.poker_hand = 'Straight-flush'
                else:
                    playerr.poker_hand = 'Flush'
                break
            if idx + 1 == 4:  # there is no point in checking further if the first 3 cards did not find the required number of matches
                break
        if playerr.poker_hand != 'Royal Flush' or playerr.poker_hand != 'Straight-flush':
            lst_of_ranks = []
            result_lst = []
            for card in lst_of_cards:
                lst_of_ranks.append(card.weight)
            for rank in lst_of_ranks:
                quantity = lst_of_ranks.count(rank)
                if quantity == 2 or quantity == 3:
                    if result_lst.count(str(rank)) == 0:
                        result_lst.append(str(rank))
                        result_lst.append(quantity)
                if quantity == 4:
                    if playerr.cards[0][0] == rank or playerr.cards[0][1] == rank:
                        playerr.poker_hand = 'Four of a kind'
            if result_lst.count(3) == 1 and result_lst.count(2) == 1:
                if playerr.poker_hand != 'Four of a kind':
                    playerr.poker_hand = 'Full House'
            elif result_lst.count(3) == 1:
                playerr.poker_hand = 'Three of a kind'
            elif result_lst.count(2) == 2:
                playerr.poker_hand = 'Two Pairs'
            elif result_lst.count(2) == 1:
                playerr.poker_hand = 'Pair'
        if playerr.poker_hand == None:
            if playerr.cards[0][0].weight > playerr.cards[0][1].weight:
                playerr.poker_hand = playerr.cards[0][0]
            else:
                playerr.poker_hand = playerr.cards[0][1]
        lst_of_cards.pop()
        lst_of_cards.pop()

    def i_forgot_about_the_street_but_its_too_late(self, lst_of_players, lst_of_cards):
        for player in lst_of_players:
            if player.poker_hand != 'Royal Flush' and player.poker_hand != 'Straight-flush' and player.poker_hand != 'Four of a kind' and player.poker_hand != 'Full House' and player.poker_hand != 'Flush':
                lst_of_cards.append(player.cards[ 0 ][ 0 ])
                lst_of_cards.append(player.cards[ 0 ][ 1 ])
                lst_of_ranks = [ ]
                for card in lst_of_cards:
                    lst_of_ranks.append(card.weight)
                first_straight = [ ]
                second_straight = [ ]
                third_straight = [ ]
                for rank in lst_of_ranks:
                    if 2 < rank <= 6:
                        if first_straight.count(rank) == 0:
                            first_straight.append(rank)
                    if 5 < rank <= 9:
                        if second_straight.count(rank) == 0:
                            second_straight.append(rank)
                    if 9 < rank <= 13:
                        if third_straight.count(rank) == 0:
                            third_straight.append(rank)
                    if len(first_straight) == 5 or len(second_straight) == 5 or len(third_straight) == 5:
                        player.poker_hand = 'Straight'

    def define_winner(self, lst_of_players):
        for player in lst_of_players:
            if player.cards[0][0].weight > player.cards[0][1].weight:
                player.kicker = player.cards[0][0].weight
            else:
                player.kicker = player.cards[0][1].weight
        ph_lst = []
        for player in lst_of_players:
            ph_lst.append(player.poker_hand)
        # ---------------------------------
        for player in lst_of_players:
            if player.poker_hand == 'Royal Flush' or player.poker_hand == 'Straight-flush':
                self.winner = player
                break
            elif player.poker_hand == 'Four of a kind' and (
                    ph_lst.count('Royal Flush') == 0 and ph_lst.count('Straight-flush') == 0):
                if ph_lst.count('Four of a kind') == 0:
                    self.winner = player
                    break
                else:  # otherwise, Four of a kind is collected on the Board
                    kickers_lst = []
                    for player in lst_of_players:
                        kickers_lst.append(player.kicker)
                    the_biggest = max(kickers_lst)
                    if kickers_lst.count(the_biggest) != 1:
                        for player in lst_of_players:
                            if player.kicker == the_biggest:
                                self.winners.append(player)
                    else:
                        for player in lst_of_players:
                            if player.kicker == the_biggest:
                                self.winner = player
                                break
            elif player.poker_hand == 'Full House' and (
                    ph_lst.count('Four of a kind') == 0 and ph_lst.count('Royal Flush') == 0 and ph_lst.count(
                    'Straight-flush') == 0):
                if ph_lst.count('Full House') == 0:
                    self.winner = player
                    break
                else:
                    # we need to find all the players who have a full house
                    for player in players:
                        if player.poker_hand == 'Full House':
                            self.river.append(player.cards[0][0])
                            self.river.append(player.cards[0][1])
                            lst_of_ranks = [ ]
                            for card in self.river:
                                lst_of_ranks.append(card.weight)
                            # looking for "тройки"
                            for card in lst_of_ranks:
                                if lst_of_ranks.count(card) == 3:
                                    player.full_house1 = card  # add kind of "тройки"
                                    break  # we stop if we find it
                            # same with the deuce
                            for card in lst_of_ranks:
                                if lst_of_ranks.count(card) == 2:
                                    player.full_house2 = card
                                    break
                            self.river.pop()
                            self.river.pop()
                            lst_of_ranks.clear()
                    # now players with this combination have their highest triples and deuces recorded
                    # now we are trying to calculate the highest three, to do this, we will combine them all in one sheet
                    lst_of_max = [ ]
                    for player in players:
                        if player.poker_hand == 'Full House':
                            lst_of_max.append(player.full_house1)
                    max_rank = max(lst_of_max)
                    if lst_of_max.count(max_rank) == 1:  # if the triples of different players do not match
                        for player in players:
                            if player.poker_hand == 'Full House':
                                if player.full_house1 == max_rank:
                                    self.winner = player
                    else:
                        # if the ranks of triples are the same for all
                        lst_of_max.clear()
                        for player in players:
                            if player.poker_hand == 'Full House':
                                lst_of_max.append(player.full_house2)
                        max_rank = max(lst_of_max)
                        if lst_of_max.count(max_rank) == 1:
                            for player in players:
                                if player.poker_hand == 'Full House':
                                    if player.full_house2 == max_rank:
                                        self.winner = player
                                        break
                        else:
                            for player in players:
                                if player.poker_hand == 'Full House':
                                    if player.full_house2 == max_rank:
                                        self.winners.append(player)
            elif player.poker_hand == 'Flush' and (
                    ph_lst.count('Full House') == 0 and ph_lst.count('Four of a kind') == 0 and ph_lst.count(
                    'Royal Flush') == 0 and ph_lst.count('Straight-flush') == 0):
                if ph_lst.count('Flush') == 0:
                    self.winner = player
                    break
                else:
                    lst_of_suits = [ ]
                    for card in self.river:
                        lst_of_suits.append(card.suit)
                    for card in lst_of_suits:
                        if lst_of_suits.count(card) == 5:  # flush on the board
                            for player in lst_of_players:
                                self.winners.append(player)
                            break
                        elif lst_of_suits.count(card) == 3 or lst_of_suits.count(card) == 4:
                            # so you need to check the kickers
                            kickers_lst = []
                            for player in lst_of_players:
                                if player.poker_hand == 'Flush':
                                    kickers_lst.append(player.kicker)
                            max_kicker = max(kickers_lst)
                            if kickers_lst.count(max_kicker) == 1:
                                for player in lst_of_players:
                                    if player.poker_hand == 'Flush':
                                        if player.kicker == max_kicker:
                                            self.winner = player
                            else:
                                for player in lst_of_players:
                                    if player.poker_hand == 'Flush':
                                        if player.kicker == max_kicker:
                                            self.winners.append(player)
            elif player.poker_hand == 'Straight' and (
                    ph_lst.count('Flush') == 0 and ph_lst.count('Full House') == 0 and ph_lst.count(
                    'Four of a kind') == 0 and ph_lst.count('Royal Flush') == 0 and ph_lst.count(
                    'Straight-flush') == 0):
                if ph_lst.count('Straight') == 0:
                    self.winner = player
                    break
            elif player.poker_hand == 'Three of a kind' and (
                    ph_lst.count('Straight') == 0 and ph_lst.count('Flush') == 0 and ph_lst.count(
                    'Full House') == 0 and ph_lst.count('Four of a kind') == 0 and ph_lst.count(
                    'Royal Flush') == 0 and ph_lst.count('Straight-flush') == 0):
                if ph_lst.count('Three of a kind') == 0:
                    self.winner = player
                    break
                else:
                    lst_of_ranks = [ ]
                    for card in self.river:
                        lst_of_ranks.append(card.weight)
                    for card in lst_of_ranks:
                        if lst_of_ranks.count(card) == 3:
                            for player in lst_of_players:
                                self.winners.append(player)
                    if len(self.winners) == 0:
                        for player in lst_of_players:
                            if player.poker_hand == 'Three of a kind':
                                # kimd of set
                                self.river.append(player.cards[0][0])
                                self.river.append(player.cards[0][1])
                                lst_of_ranks = [ ]
                                for card in self.river:
                                    lst_of_ranks.append(card.weight)
                                for card in lst_of_ranks:
                                    if lst_of_ranks.count(card) == 3:
                                        player.set = card  # adding a card from the set to the player for later comparison
                                self.river.pop()
                                self.river.pop()
                                lst_of_ranks.clear()
                        lst_of_max = []
                        for player in lst_of_players:
                            if player.poker_hand == 'Three of a kind':
                                lst_of_max.append(player.set)
                        max_card = max(lst_of_max)
                        if lst_of_max.count(max_card) == 1:
                            for player in lst_of_players:
                                if player.poker_hand == 'Three of a kind':
                                    if player.set == max_card:
                                        self.winner = player
                                        break
                                else:
                                    for player in lst_of_players:
                                        if player.poker_hand == 'Three of a kind':
                                            if player.set == max_card:
                                                self.winners.append(player)

            elif player.poker_hand == 'Two Pairs' and (
                    ph_lst.count('Three of a kind') == 0 and ph_lst.count('Straight') == 0 and ph_lst.count(
                    'Flush') == 0 and ph_lst.count('Full House') == 0 and ph_lst.count(
                    'Four of a kind') == 0 and ph_lst.count('Royal Flush') == 0 and ph_lst.count(
                    'Straight-flush') == 0):
                if ph_lst.count('Two Pairs') == 0:
                    self.winner = player
                    break
                else:
                    for player in lst_of_players:
                        if player.poker_hand == 'Two Pairs':
                            self.river.append(player.cards[0][0])
                            self.river.append(player.cards[0][1])
                            lst_of_ranks = [ ]
                            result_lst = [ ]
                            for card in self.river:
                                lst_of_ranks.append(card.weight)
                            for card in lst_of_ranks:
                                if lst_of_ranks.count(card) == 2:
                                    if result_lst.count(card) == 0:
                                        result_lst.append(card)
                            max_card = max(result_lst)
                            player.two_pairs = max_card
                            self.river.pop()
                            self.river.pop()
                            lst_of_ranks.clear()
                            result_lst.clear()
                    lst_of_max = [ ]
                    for player in lst_of_players:
                        if player.poker_hand == 'Two Pairs':
                            lst_of_max.append(player.two_pairs)
                    max_card = max(lst_of_max)
                    if lst_of_max.count(max_card) == 1:
                        for player in lst_of_players:
                            if player.poker_hand == 'Two Pairs':
                                if player.two_pairs == max_card:
                                    self.winner = player
                                    break
                    else:
                        for player in lst_of_players:
                            if player.poker_hand == 'Two Pairs':
                                if player.two_pairs == max_card:
                                    self.winners.append(player)
            elif player.poker_hand == 'Pair' and (
                    ph_lst.count('Two Pairs') == 0 and ph_lst.count('Three of a kind') == 0 and ph_lst.count(
                    'Straight') == 0 and ph_lst.count('Flush') == 0 and ph_lst.count(
                    'Full House') == 0 and ph_lst.count('Four of a kind') == 0 and ph_lst.count(
                    'Royal Flush') == 0 and ph_lst.count('Straight-flush') == 0):
                if ph_lst.count('Pair') == 0:
                    self.winner = player
                    break
                else:
                    # you need to collect all the pairs (often it is collected on the Board)
                    lst_of_ranks = [ ]
                    for card in self.river:
                        lst_of_ranks.append(card.weight)
                    for card in lst_of_ranks:
                        if lst_of_ranks.count(card) == 2:
                            for player in lst_of_players:
                                self.winners.append(player)
                    lst_of_ranks.clear()
                    if len(self.winners) == 0:
                        for player in lst_of_players:
                            if player.poker_hand == 'Pair':
                                self.river.append(player.cards[0][0])
                                self.river.append(player.cards[0][1])
                                lst_of_ranks = [ ]
                                for card in self.river:
                                    lst_of_ranks.append(card.weight)
                                for card in lst_of_ranks:
                                    if lst_of_ranks.count(card) == 2:
                                        player.pair = card
                                self.river.pop()
                                self.river.pop()
                                lst_of_ranks.clear()
                        # after all the high cards are saved we will add them to the General list and calculate the highest one
                        lst_of_max = []
                        for player in lst_of_players:
                            if player.poker_hand == 'Pair':
                                lst_of_max.append(player.pair)
                        max_card = max(lst_of_max)
                        if lst_of_max.count(max_card) == 1:
                            for player in lst_of_players:
                                if player.poker_hand == 'Pair':
                                    if player.pair == max_card:
                                        self.winner = player
                                        break
                                else:
                                    for player in lst_of_players:
                                        if player.poker_hand == 'Pair':
                                            if player.pair == max_card:
                                                self.winners.append(player)
            else:
                if ph_lst.count('Pair') == 0 and ph_lst.count('Two Pairs') == 0 and ph_lst.count(
                        'Three of a kind') == 0 and ph_lst.count('Straight') == 0 and ph_lst.count(
                        'Flush') == 0 and ph_lst.count('Full House') == 0 and ph_lst.count(
                        'Four of a kind') == 0 and ph_lst.count('Royal Flush') == 0 and ph_lst.count(
                        'Straight-flush') == 0:
                    kickers_lst = [ ]
                    for player in lst_of_players:
                        kickers_lst.append(player.kicker)
                    max_kicker = max(kickers_lst)
                    if kickers_lst.count(max_kicker) == 1:
                        for player in players:
                            if player.kicker == max_kicker:
                                self.winner = player
                                break
                    else:
                        for player in players:
                            if player.kicker == max_kicker:
                                self.winners.append(player)


if __name__ == '__main__':

    deck = Deck()
    '''
    number_of_players = int(input('Enter the number of participants'))
    if number_of_players < 3 or number_of_players > 10:
        raise Exception("This game is for 3-10 people!")
    '''
    number_of_players = 4
    player_count = 0
    players = []

    while player_count != number_of_players:
        players.append(Player(deck, player_count + 1))
        player_count += 1

    print(players)

    game = Game()
    game.define_dealer(players)
    print('The dealer is the player number', game.dealer.player_number)

    # return the card to the deck
    for player in players:
        deck.cards.append(player.cards[0])
    deck.shuffle()

    game.define_small_blind(number_of_players, players)
    print('The small blind is player number', game.small_blind.player_number)
    print('Small blind stake is:', game.small_blind.player_stake)

    game.define_big_blind(number_of_players, players)
    print('The big blind is player number', game.big_blind.player_number)
    print('Big blind stake is:', game.big_blind.player_stake)

    print('-----------------')

    for player in players:
        player.cards.clear()
        player.cards.append(deck.draw_cards(2))

    print(players)

    game.first_round_bidding(number_of_players, players)
    # if someone decided to leave the game with bad cards
    if len(game.deleted_ones) != 0:
        for player in game.deleted_ones:
            players.remove(player)
        for idx, player in enumerate(players):
            if idx == 0:
                player.player_number = 1
            else:
                player.player_number = players[ idx - 1 ].player_number + 1
        number_of_players = number_of_players - len(game.deleted_ones)

    print(players)

    game.equalize(players)

    for player in players:
        print(player.player_stake)

    game.flop = deck.draw_cards(3)
    print('Flop:', game.flop)

    round1 = 'flop'
    game.next_round_bidding(number_of_players, players, round1, game.flop)

    game.equalize(players)

    round2 = 'turn'
    game.turn = game.flop.copy()
    game.turn.append(deck.draw_cards(1)[ 0 ])
    print('Turn:', game.turn)

    game.next_round_bidding(number_of_players, players, round2, game.turn)
    game.equalize(players)

    round3 = 'river'
    game.river = game.turn.copy()
    game.river.append(deck.draw_cards(1)[ 0 ])
    print('River:', game.river)

    game.equalize(players)

    game.next_round_bidding(number_of_players, players, round3, game.river)

    for player in players:
        print(player.player_number, player.poker_hand)

    game.define_winner(players)

    if len(game.winners) != 0:
        print(list(set(game.winners)))
    else:
        print(game.winner)
