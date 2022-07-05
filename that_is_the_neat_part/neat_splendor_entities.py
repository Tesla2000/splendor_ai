from enums import Resource, Tier
import random
import numpy as np

resource_limit = 7
gold_limit = 5
cards_in_row = 4


class Card:
    def __init__(self, points, production, red, green, blue, brown, white, tier):
        self.points = points
        self.production = production
        self.cost = {
            Resource.RED: red,
            Resource.GREEN: green,
            Resource.BLUE: blue,
            Resource.BROWN: brown,
            Resource.WHITE: white
        }
        self.tier = tier


class Aristocrat:
    def __init__(self, points=3, red=0, green=0, blue=0, brown=0, white=0):
        self.points = points
        self.requirements = {
            Resource.RED: red,
            Resource.GREEN: green,
            Resource.BLUE: blue,
            Resource.BROWN: brown,
            Resource.WHITE: white
        }


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
    def __init__(self, red=resource_limit, green=resource_limit, blue=resource_limit, brown=resource_limit,
                 white=resource_limit,
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
        self.cards[0] = self.cards[0][cards_in_row:]
        self.cards[1] = self.cards[1][cards_in_row:]
        self.cards[2] = self.cards[2][cards_in_row:]

    @staticmethod
    def _shove_cards(deck):
        holder = []
        while len(deck) >= 1:
            holder.append(deck.pop(random.randint(0, len(deck) - 1)))
        return holder

    def take_card(self, tier, index):
        if len(self.cards[tier.value]) > 0:
            self.visible_cards.insert(cards_in_row * (tier.value + 1), self.cards[tier.value].pop())
        else:
            self.visible_cards.insert(cards_in_row * (tier.value + 1), None)
        return self.visible_cards.pop(index + cards_in_row * tier.value)

    def show_card(self, tier, index):
        if index == 4:
            return self.cards[tier.value]
        return self.visible_cards[index + cards_in_row * tier.value]

    def give_resource(self, amount):
        if isinstance(amount, tuple):
            if len(amount) == 2 and amount[0] == amount[1]:
                pass
            for resource in amount:
                self.available_resources[resource] -= 1
        else:
            for resource in amount:
                if self.available_resources[resource] < amount[resource]:
                    raise ValueError
                else:
                    self.available_resources[resource] -= amount[resource]

    def get_resource(self, resource):
        self.available_resources[resource] += 1

    def remove_resource(self, resource):
        self.available_resources[resource] -= 1

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


class Player:
    def __init__(self, points=0, cards=None, aristocrats=None, reserve=None, red=0, green=0, blue=0,
                 brown=0, white=0):
        if cards is None:
            self.cards = []
        self.resources = {
            Resource.RED: red,
            Resource.GREEN: green,
            Resource.BLUE: blue,
            Resource.BROWN: brown,
            Resource.WHITE: white
        }
        self.points = points
        if aristocrats is None:
            self.aristocrats = []
        if reserve is None:
            self.reserve = []

    def get_production(self):
        counter = {
            Resource.RED: 0,
            Resource.GREEN: 0,
            Resource.BLUE: 0,
            Resource.BROWN: 0,
            Resource.WHITE: 0
        }
        for card in self.cards:
            counter[card.production] = counter.get(card.production, 0) + 1
        return counter

    def get_card(self, card):
        self.cards.append(card)
        self.points += card.points

    def get_resource(self, option):
        # for resource in option:
        self.resources[option] = self.resources.get(option, 0) + 1

    def get_aristocrat(self, aristocrat):
        self.aristocrats.append(aristocrat)
        self.points += aristocrat.points

    def add_reserve(self, card):
        self.reserve.append(card)

    def build_reserve(self, index):
        self.cards.append(self.reserve.pop(index))

    def pay(self, cost):
        gold_needed = 0
        paid = {}
        for resource in cost:
            gold_needed += max(0, -self.resources.get(resource, 0) - self.get_production().get(resource, 0) + cost.get(
                resource, 0))
        if gold_needed > self.resources.get(Resource.GOLD, 0):
            raise ValueError("Too little gold")
        else:
            paid[Resource.GOLD] = gold_needed
            self.resources[Resource.GOLD] = self.resources.get(Resource.GOLD, 0) - gold_needed
            for resource in cost:
                paid[resource] = max(0, cost[resource] - self.get_production().get(resource, 0))
                self.resources[resource] = max(0, self.resources.get(resource, 0) - max(0,
                                                                                        cost[
                                                                                            resource] - self.get_production().get(
                                                                                            resource, 0)))
            return paid


class Game:
    def __init__(self, players=2):
        self.players = []
        self.board = Board()
        self.round = 0
        for _ in range(players):
            self.players.append(Player())

    def end_turn(self):
        self.update_resources()
        self.round += 1
        self.players.append(self.players.pop(0))

    def get_state(self):
        state = [self.board.available_resources[Resource.RED], self.board.available_resources[Resource.GREEN],
                 self.board.available_resources[Resource.BLUE], self.board.available_resources[Resource.BROWN],
                 self.board.available_resources[Resource.WHITE], self.board.available_resources[Resource.GOLD]]
        for player in self.players:
            player_production = player.get_production()
            for card in self.board.visible_cards:
                if card:
                    production = 5 * [0]
                    production[card.production.value - 1] = len(tuple(
                        filter(lambda card: card.cost[card.production] - player.get_production()[
                            card.production] > 0 if card else 0,
                               self.board.visible_cards)))
                    state.append(card.points)
                    state.extend(
                        (
                            max(0, card.cost[Resource.RED] - player_production[Resource.RED]),
                            max(0, card.cost[Resource.GREEN] - player_production[Resource.GREEN]),
                            max(0, card.cost[Resource.BLUE] - player_production[Resource.BLUE]),
                            max(0, card.cost[Resource.BROWN] - player_production[Resource.BROWN]),
                            max(0, card.cost[Resource.WHITE] - player_production[Resource.WHITE])
                        )
                    )
                    state.extend(
                        (
                            card.cost[Resource.RED] - player_production[Resource.RED] - player.resources[Resource.RED],
                            card.cost[Resource.GREEN] - player_production[Resource.GREEN] - player.resources[
                                Resource.GREEN],
                            card.cost[Resource.BLUE] - player_production[Resource.BLUE] - player.resources[
                                Resource.BLUE],
                            card.cost[Resource.BROWN] - player_production[Resource.BROWN] - player.resources[
                                Resource.BROWN],
                            card.cost[Resource.WHITE] - player_production[Resource.WHITE] - player.resources[
                                Resource.WHITE]
                        )
                    )
                    state.extend(production)
                else:
                    state.extend(
                        (
                            0,
                            0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0,
                        )
                    )
            aristocrats = self.board.aristocrats
            for i in range(4):
                if i < len(aristocrats):
                    state.extend(
                        (
                            max(0, aristocrats[i].requirements.get(Resource.RED) - player_production[Resource.RED]),
                            max(0, aristocrats[i].requirements.get(Resource.GREEN) - player_production[Resource.GREEN]),
                            max(0, aristocrats[i].requirements.get(Resource.BLUE) - player_production[Resource.BLUE]),
                            max(0, aristocrats[i].requirements.get(Resource.BROWN) - player_production[Resource.BROWN]),
                            max(0, aristocrats[i].requirements.get(Resource.WHITE) - player_production[Resource.WHITE]),
                        )
                    )
                else:
                    state.extend(
                        (
                            0,
                            0,
                            0,
                            0,
                            0,
                        )
                    )
            state.extend(
                (player.points, player_production.get(Resource.RED, 0), player_production.get(Resource.GREEN, 0),
                 player_production.get(Resource.BLUE, 0),
                 player_production.get(Resource.BROWN, 0), player_production.get(Resource.WHITE, 0),
                 player.resources.get(Resource.RED, 0),
                 player.resources.get(Resource.GREEN, 0), player.resources.get(Resource.BLUE, 0),
                 player.resources.get(Resource.BROWN, 0), player.resources.get(Resource.WHITE, 0),
                 player.resources.get(Resource.GOLD, 0),
                 len(player.reserve)))
        return np.array(state, dtype=np.int8)

    def reset(self):
        self.players = []
        self.board = Board()
        self.round += 1

    def update_resources(self):
        self.board.available_resources = {Resource.RED: resource_limit, Resource.GREEN: resource_limit,
                                          Resource.BLUE: resource_limit,
                                          Resource.BROWN: resource_limit,
                                          Resource.WHITE: resource_limit, Resource.GOLD: gold_limit}
        for player in self.players:
            for resource in player.resources:
                self.board.available_resources[resource] -= player.resources[resource]
