from enums import Resource, Tier


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
