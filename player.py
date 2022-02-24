from enums import Resource, Tier


class Player:
    def __init__(self, points=0, cards=None, aristocrats=None, reserve=None, red=0, green=0, blue=0, brown=0, white=0):
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
        counter = dict()
        for card in self.cards:
            counter[card.production] = counter.get(card.production, 0) + 1
        return counter

    def get_card(self, card):
        self.cards.append(card)
        self.points += card.points

    def get_resource(self, option):
        for resource in option:
            self.resources[resource] = self.resources.get(resource, 0) + 1

    def get_aristocrat(self, aristocrat):
        self.aristocrats.append(aristocrat)
        self.points += aristocrat.points

    def add_reserve(self, card):
        self.reserve.append(card)
        print(len(self.reserve))
        if sum(self.resources.values()) < 10:
            self.resources[Resource.GOLD] = self.resources.get(Resource.GOLD, 0) + 1

    def build_reserve(self, index):
        self.cards.append(self.reserve.pop(index))

    def pay(self, cost):
        gold_needed = 0
        for resource in cost:
            gold_needed -= max(0, self.resources.get(resource, 0) + self.get_production().get(resource, 0) - cost.get(
                resource, 0))
        if gold_needed > self.resources.get(Resource.GOLD, 0):
            raise ValueError("Too little gold")
        else:
            self.resources[Resource.GOLD] = self.resources.get(Resource.GOLD, 0) - gold_needed
            for resource in cost:
                self.resources[resource] = max(0, self.resources.get(resource, 0) - cost[resource])