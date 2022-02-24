import random
from enums import Resource, Tier
from aristocrat import Aristocrat
from card import Card
from player import Player

res_limit = 7
gold_limit = 5
cards_in_row = 4


def generate_aristocrats():
    return [Aristocrat(red=4, green=4), Aristocrat(red=4, brown=4),
            Aristocrat(brown=4, white=4), Aristocrat(green=4, blue=4),
            Aristocrat(white=4, blue=4), Aristocrat(white=3, blue=3, green=3),
            Aristocrat(green=3, red=3, brown=3), Aristocrat(blue=3, green=3, red=3),
            Aristocrat(red=3, white=3, brown=3), Aristocrat(blue=3, white=3, brown=3)]


def generate_cards():
    with open("buildings.txt", 'r') as file:
        content = file.read()
    cards = [[], [], []]
    for line in content.split('\n'):
        try:
            tier, production, points, _, white, blue, green, red, brown = line.split('\t')
            productions = {'black': Resource.BROWN, 'blue': Resource.BLUE, 'red': Resource.RED, 'white': Resource.WHITE,
                           'green': Resource.GREEN}
            if tier == '1':
                cards[0].append(
                    Card(int(points), productions[production], int(red), int(green), int(blue), int(brown), int(white),
                         Tier.FIRST))
            elif tier == '2':
                cards[1].append(
                    Card(int(points), productions[production], int(red), int(green), int(blue), int(brown), int(white),
                         Tier.SECOND))
            else:
                cards[2].append(
                    Card(int(points), productions[production], int(red), int(green), int(blue), int(brown), int(white),
                         Tier.THIRD))
        except ValueError:
            pass

    return cards


class Board:
    def __init__(self, number_of_players=2, red=res_limit, green=res_limit, blue=res_limit, brown=res_limit,
                 white=res_limit,
                 gold=gold_limit, aristocrats=None, cards=None):
        if cards is None:
            cards = generate_cards()
        if aristocrats is None:
            aristocrats = generate_aristocrats()
        self.available_resources = {Resource.RED: red, Resource.GREEN: green, Resource.BLUE: blue,
                                    Resource.BROWN: brown,
                                    Resource.WHITE: white, Resource.GOLD: gold}
        self.aristocrats = aristocrats
        self.cards = cards
        self.visible_aristocrats = self._shove_cards(self.aristocrats)[:cards_in_row]
        for i in range(len(cards)):
            cards[i] = self._shove_cards(cards[i])
        self.visible_cards = self.cards[0][:cards_in_row] + self.cards[1][:cards_in_row] + self.cards[2][:cards_in_row]


    @staticmethod
    def _shove_cards(deck):
        holder = []
        while len(deck) >= 1:
            holder.append(deck.pop(random.randint(0, len(deck) - 1)))
        return holder

    def take_card(self, tier, index):
        if len(self.cards[tier.value]) > 0:
            self.visible_cards.insert(self.cards[tier.value].pop(), cards_in_row * (tier.value + 1))
        else:
            self.visible_cards.insert(None, cards_in_row * (tier.value + 1))
        return self.visible_cards.pop(index + cards_in_row * tier.value)

    def give_resource(self, amount):
        for resource in amount:
            if self.available_resources[resource] < amount[resource]:
                raise ValueError
            else:
                self.available_resources[resource] -= amount[resource]

    def get_resource(self, amount):
        for resource in amount:
            self.available_resources[resource] += amount[resource]

    def reserve_card(self, tier, index):
        if index == cards_in_row:
            return self.cards[tier.value].pop()
        return self.take_card(tier, index)

    def check_aristocrats(self, player):
        for aristocrat in self.aristocrats:
            for resource in aristocrat.requirements:
                if aristocrat.requirements[resource] > player.get_production()[resource]:
                    break
            else:
                player.get_aristocrat(self.aristocrats.pop(aristocrat))



