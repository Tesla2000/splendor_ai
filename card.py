from enums import Resource, Tier


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
