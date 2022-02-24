from enums import Resource, Tier
from game import Game

import random
import numpy as np
from collections import deque

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


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


class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(103, 256, 60)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.game = Game(number_of_players=1)
        self.score = 0

    @staticmethod
    def get_state(game):
        state = [game.board.available_resources[Resource.RED], game.board.available_resources[Resource.GREEN],
                 game.board.available_resources[Resource.BLUE], game.board.available_resources[Resource.BROWN],
                 game.board.available_resources[Resource.WHITE], game.board.available_resources[Resource.GOLD]]
        for card in game.board.visible_cards:
            if card:
                state.extend(
                    (card.cost[Resource.RED], card.cost[Resource.GREEN], card.cost[Resource.BLUE],
                     card.cost[Resource.BROWN],
                     card.cost[Resource.WHITE], card.points, card.production.value))
            else:
                state.extend(
                    (1000, 1000, 1000, 1000,
                     1000, 0, 0))
        for aristocrat in game.board.aristocrats:
            state.extend((aristocrat.requirements.get(Resource.RED), aristocrat.requirements.get(Resource.GREEN),
                          aristocrat.requirements.get(Resource.BLUE), aristocrat.requirements.get(Resource.BROWN),
                          aristocrat.requirements.get(Resource.WHITE),))
        for player in game.players:
            prod = player.get_production()
            state.extend(
                (player.points, prod.get(Resource.RED, 0), prod.get(Resource.GREEN, 0), prod.get(Resource.BLUE, 0),
                 prod.get(Resource.BROWN, 0), prod.get(Resource.WHITE, 0), player.resources.get(Resource.RED, 0),
                 player.resources.get(Resource.GREEN, 0), player.resources.get(Resource.BLUE, 0),
                 player.resources.get(Resource.BROWN, 0), player.resources.get(Resource.WHITE, 0),
                 player.resources.get(Resource.GOLD, 0),
                 len(player.reserve)))
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        # for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = 60 * [0]
        if random.randint(0, 200) < self.epsilon:
            for i in range(len(final_move)):
                final_move[i] = random.random()
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            rating = list(self.model(state0))
            wanted = sorted(rating, reverse=True)
            for option in wanted:
                option_index = rating.index(option)
                if is_possible(option_index, self.game.players[0], self.game.board):
                    return option_index

        return final_move

    def play_step(self, option_index):
        current_player = self.game.players[0]
        points = current_player.points
        if option_index in resource_111 or option_index in resource_2:
            current_player.get_resource(options[option_index])
        elif option_index in reserve_card:
            tier, index = options[option_index]
            current_player.reserve.append(self.game.board.reserve_card(tier, index))
        elif option_index in build_card_row:
            tier, index = options[option_index]
            card = self.game.board.take_card(tier, index)
            current_player.pay(card.cost)
            current_player.get_card(card)
        elif option_index in build_card_reserve:
            index = options[option_index]
            current_player.pay(current_player.reserve[index].cost)
            current_player.build_reserve(index)
        self.game.board.check_aristocrats(current_player)
        self.game.end_turn()
        return 10 * (current_player.points - points), current_player.points >= 15, self.score


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    while True:
        # get old state
        state_old = agent.game.get_state()

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = agent.play_step(final_move)
        state_new = agent.get_state(agent.game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            agent.game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()