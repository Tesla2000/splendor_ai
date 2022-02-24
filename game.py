from player import Player
from board import Board
from enums import Tier, Resource
import numpy as np


class Game:
    def __init__(self, number_of_players=4):
        self.players = []
        for _ in range(number_of_players):
            self.players.append(Player())
        self.board = Board()

    def end_turn(self):
        self.players.append(self.players.pop(0))

    def get_state(self):
        state = [self.board.available_resources[Resource.RED], self.board.available_resources[Resource.GREEN],
                 self.board.available_resources[Resource.BLUE], self.board.available_resources[Resource.BROWN],
                 self.board.available_resources[Resource.WHITE], self.board.available_resources[Resource.GOLD]]
        for card in self.board.visible_cards:
            if card:
                state.extend(
                    (
                        card.cost[Resource.RED], card.cost[Resource.GREEN], card.cost[Resource.BLUE],
                        card.cost[Resource.BROWN],
                        card.cost[Resource.WHITE], card.points, card.production.value))
            else:
              state.extend(
                    (
                        1000, 1000, 1000,
                        1000,
                        1000, 0, 6))
        for aristocrat in self.board.aristocrats:
            state.extend((aristocrat.requirements.get(Resource.RED), aristocrat.requirements.get(Resource.GREEN),
                          aristocrat.requirements.get(Resource.BLUE), aristocrat.requirements.get(Resource.BROWN),
                          aristocrat.requirements.get(Resource.WHITE),))
        for player in self.players:
            prod = player.get_production()
            state.extend(
                (player.points, prod.get(Resource.RED, 0), prod.get(Resource.GREEN, 0), prod.get(Resource.BLUE, 0),
                 prod.get(Resource.BROWN, 0), prod.get(Resource.WHITE, 0), player.resources.get(Resource.RED, 0),
                 player.resources.get(Resource.GREEN, 0), player.resources.get(Resource.BLUE, 0),
                 player.resources.get(Resource.BROWN, 0), player.resources.get(Resource.WHITE, 0),
                 player.resources.get(Resource.GOLD, 0),
                 len(player.reserve)))
        return np.array(state)

    def reset(self):
        self.players = []
        for _ in range(len(self.players)):
            self.players.append(Player())
        self.board = Board()


