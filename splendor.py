import numpy as np
from board import Board
from card import Card
from player import Player
from enums import Tier, Resource
from copy import deepcopy
from game import Game
from aristocrat import Aristocrat

from copy import deepcopy

cards_in_row = 4
player_resource_max = 10
resource_limit_for_two = 4
resource_111 = range(25)
resource_2 = range(25, 30)
reserve_card = range(30, 45)
build_card_row = range(45, 57)
build_card_reserve = range(57, 60)

#  1-25 resources 1,1,1
#  26-30 2 resources
#  31-45 reserve card
#  46-57 build card from trade row
#  58-60 build card from reserve
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

res_trans = {1: Resource.RED, 2: Resource.GREEN, 3: Resource.BLUE, 4: Resource.BROWN, 5: Resource.WHITE,
             6: Resource.GOLD}


def is_possible(option_index, player_instance, game):
    if option_index in resource_111:
        if sum(player_instance.resources.values()) + len(options[option_index]) <= player_resource_max:
            for resource in options[option_index]:
                if game.available_resources.get(resource, 0) < 1:
                    break
            else:
                return True
    elif option_index in resource_2:
        if sum(player_instance.resources.values()) + len(options[option_index]) <= player_resource_max:
            for resource in options[option_index]:
                if game.available_resources[resource] < resource_limit_for_two:
                    break
            else:
                return True
    elif option_index in reserve_card:
        if options[option_index][1] == 4:
            if len(game.cards[options[option_index][0].value]) >= 1:
                print(options[option_index][0])
                print(game.cards[options[option_index][0].value])
                if len(player_instance.reserve) < 3:
                    return True
        return game.visible_cards[options[option_index][1]] is not None
    elif option_index in build_card_row:
        card = game.visible_cards[options[option_index][1]]
        if is_purchase_possible(player_instance, card):
            return True
    elif option_index in build_card_reserve:
        index = options[option_index]
        if index < len(player_instance.reserve):
            card = player_instance.reserve[index]
            if is_purchase_possible(player_instance, card):
                return True
    return False


def is_purchase_possible(player_instance, card):
    if card is not None:
        copy = deepcopy(player_instance)
        try:
            copy.pay(card.cost)
            return True
        except ValueError:
            return False


def possible_option(combination, player_instance, game):
    wanted = combination.sort(reversed=True)
    for option in wanted:
        option_index = combination.index(option)
        if is_possible(option_index, player_instance, game):
            return option_index
