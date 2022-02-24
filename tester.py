from enums import Resource, Tier
from game import Game
import numpy as np
import random
from copy import deepcopy

cards_in_row = 4
player_resource_max = 60
resource_limit_for_two = 4
resource_111 = range(25)
resource_2 = range(25, 30)
reserve_card = range(30, 45)
build_card_row = range(45, 57)
build_card_reserve = range(57, 60)

options = ((Resource.RED, Resource.GREEN, Resource.BLUE), (Resource.RED, Resource.GREEN, Resource.BROWN),
           (Resource.RED, Resource.GREEN, Resource.WHITE), (Resource.RED, Resource.BLUE, Resource.BROWN),
           (Resource.RED, Resource.BLUE, Resource.WHITE), (Resource.RED, Resource.BROWN, Resource.WHITE),
           (Resource.GREEN, Resource.BLUE, Resource.BROWN), (Resource.GREEN, Resource.BLUE, Resource.WHITE),
           (Resource.GREEN, Resource.BROWN, Resource.WHITE), (Resource.BLUE, Resource.BROWN, Resource.WHITE),

           (Resource.RED, Resource.GREEN), (Resource.RED, Resource.BLUE), (Resource.RED, Resource.BROWN),
           (Resource.RED, Resource.WHITE), (Resource.GREEN, Resource.BLUE), (Resource.GREEN, Resource.BROWN),
           (Resource.GREEN, Resource.WHITE), (Resource.BLUE, Resource.BROWN), (Resource.BLUE, Resource.WHITE),
           (Resource.BROWN, Resource.WHITE),

           (Resource.RED,), (Resource.GREEN,), (Resource.BLUE,), (Resource.BROWN,), (Resource.WHITE,),

           (Resource.RED, Resource.RED), (Resource.GREEN, Resource.GREEN),
           (Resource.BLUE, Resource.BLUE), (Resource.BROWN, Resource.BROWN), (Resource.WHITE, Resource.WHITE),

           (Tier.FIRST, 0), (Tier.SECOND, 0), (Tier.THIRD, 0), (Tier.FIRST, 1), (Tier.SECOND, 1), (Tier.THIRD, 1),
           (Tier.FIRST, 2), (Tier.SECOND, 2), (Tier.THIRD, 2), (Tier.FIRST, 3), (Tier.SECOND, 3), (Tier.THIRD, 3),
           (Tier.FIRST, 4), (Tier.SECOND, 4), (Tier.THIRD, 4),

           (Tier.FIRST, 0), (Tier.SECOND, 0), (Tier.THIRD, 0), (Tier.FIRST, 1), (Tier.SECOND, 1), (Tier.THIRD, 1),
           (Tier.FIRST, 2), (Tier.SECOND, 2), (Tier.THIRD, 2), (Tier.FIRST, 3), (Tier.SECOND, 3), (Tier.THIRD, 3),

           0, 1, 2
           )


class Tester:
    def __init__(self):
        self.n_games = 0
        self.game = Game(number_of_players=1)
        self.current_player = self.game.players[0]

    def get_state(self):
        return self.game.get_state()

    def get_action(self, state=None):
        # random moves: tradeoff exploration / exploitation
        final_move = 60 * [0]
        for i in range(len(final_move)):
            final_move[i] = random.random()
        return final_move

    def play_step(self, option_index):
        if option_index in resource_111 or option_index in resource_2:
            self.current_player.get_resource(options[option_index])
        elif option_index in reserve_card:
            tier, index = options[option_index]
            self.current_player.reserve.append(self.game.board.reserve_card(tier, index))
            if self.game.board.available_resources[Resource.GOLD] > 0:
                self.current_player.get_resource((Resource.GOLD,))
        elif option_index in build_card_row:
            tier, index = options[option_index]
            card = self.game.board.take_card(tier, index)
            self.current_player.get_card(card)
        elif option_index in build_card_reserve:
            index = options[option_index]
            self.current_player.pay(self.current_player.reserve[index].cost)
            self.current_player.build_reserve(index)
        self.game.board.check_aristocrats(self.current_player)
        self.game.end_turn()
        end = self.current_player.points >= 15
        self.current_player = self.game.players[0]
        self.game.update_resources()
        return end

    def _is_possible(self, option_index):
        if option_index in resource_111:
            if sum(self.current_player.resources.values()) + len(options[option_index]) <= player_resource_max:
                for resource in options[option_index]:
                    if self.game.board.available_resources.get(resource, 0) < 1:
                        break
                else:
                    return True
        elif option_index in resource_2:
            if sum(self.current_player.resources.values()) + len(options[option_index]) <= player_resource_max:
                for resource in options[option_index]:
                    if self.game.board.available_resources[resource] < resource_limit_for_two:
                        break
                else:
                    return True
        elif option_index in reserve_card:
            if options[option_index][1] == 4:
                if len(self.game.board.cards[options[option_index][0].value]) >= 1:
                    if len(self.current_player.reserve) < 3:
                        return True
            return self.game.board.visible_cards[options[option_index][1]] is not None and len(
                self.current_player.reserve) < 3
        elif option_index in build_card_row:
            card = self.game.board.visible_cards[options[option_index][1]]
            if self._is_purchase_possible(card):
                return True
        elif option_index in build_card_reserve:
            index = options[option_index]
            if index < len(self.current_player.reserve):
                card = self.current_player.reserve[index]
                if self._is_purchase_possible(card):
                    return True
        return False

    def _is_purchase_possible(self, card):
        if card is not None:
            copy = deepcopy(self.current_player)
            try:
                copy.pay(card.cost)
                return True
            except ValueError:
                return False

    def possible_option(self, combination):
        wanted = sorted(combination, reverse=True)
        for option in wanted:
            option_index = combination.index(option)
            if self._is_possible(option_index):
                return option_index


t = Tester()
while True:
    action = t.get_action()
    option = t.possible_option(action)
    if option is None:
        # print("blocked")
        t.game.reset()
        continue
    if t.play_step(option):
        print("Finished")
        t.game.reset()


