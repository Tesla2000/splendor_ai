import neat
from neat_splendor_entities import Game
from neat_splendor_game_controller import go_for_option


def eval_genomes(genomes, config):
    evaluations = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        evaluations.append((genome, net))
    # errors = 0
    for player_1 in range(0, len(evaluations)):
        for player_2 in range(player_1, len(evaluations)):
            game = Game()
            while True:
                try:
                    go_for_option(game, evaluations[player_1][1].activate(game.get_state()))
                except ValueError:
                    print('Error')
                    evaluations[player_2][0].fitness += 1
                    evaluations[player_1][0].fitness -= 1
                    # errors += 1
                    break
                if game.players[0].points >= 15:
                    # print('Finished')
                    evaluations[player_1][0].fitness += 1
                    evaluations[player_1][0].fitness += 1 / game.round
                    evaluations[player_2][0].fitness -= 1
                    break
                game.end_turn()
                try:
                    go_for_option(game, evaluations[player_2][1].activate(game.get_state()))
                except ValueError:
                    print('Error')
                    evaluations[player_1][0].fitness += 1
                    evaluations[player_2][0].fitness -= 1
                    # errors += 1
                    break
                if game.players[0].points >= 15:
                    # print('Finished')
                    evaluations[player_2][0].fitness += 1
                    evaluations[player_2][0].fitness += 1 / game.round
                    evaluations[player_1][0].fitness -= 1
                    break
                game.end_turn()


def compare_networks(winner1, winner2):
    score_1 = score_2 = 0
    for _ in range(100):
        game = Game()
        while True:
            try:
                go_for_option(game, winner1.activate(game.get_state()))
            except ValueError:
                print('Error')
                score_2 += 1
                # errors += 1
                break
            if game.players[0].points >= 15:
                # print('Finished')
                score_1 += 1
                break
            game.end_turn()
            try:
                go_for_option(game, winner2.activate(game.get_state()))
            except ValueError:
                print('Error')
                score_1 += 1
                break
            if game.players[0].points >= 15:
                # print('Finished')
                score_2 += 1
                break
            game.end_turn()
    for _ in range(100):
        game = Game()
        while True:
            try:
                go_for_option(game, winner2.activate(game.get_state()))
            except ValueError:
                print('Error')
                score_1 += 1
                # errors += 1
                break
            if game.players[0].points >= 15:
                # print('Finished')
                score_2 += 1
                break
            game.end_turn()
            try:
                go_for_option(game, winner1.activate(game.get_state()))
            except ValueError:
                print('Error')
                score_2 += 1
                break
            if game.players[0].points >= 15:
                # print('Finished')
                score_1 += 1
                break
            game.end_turn()
    print("Score 1: ", score_1)
    print("Score 2: ", score_2)


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    # p2 = neat.Checkpointer.restore_checkpoint('neat-checkpoint-226')

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(10))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 100000)
    # winner1 = p.run(eval_genomes, 1)
    # winner2 = p2.run(eval_genomes, 1)
    # compare_networks(neat.nn.FeedForwardNetwork.create(winner1, config), neat.nn.FeedForwardNetwork.create(winner2, config))
    # print('\nBest genome:\n{!s}'.format(winner))


def compare_checkpoints(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    p2 = neat.Checkpointer.restore_checkpoint('neat-checkpoint-50')

    # Create the population, which is the top-level object for a NEAT run.
    p1 = neat.Checkpointer.restore_checkpoint('neat-checkpoint-20')

    # Add a stdout reporter to show progress in the terminal.
    # p.add_reporter(neat.StdOutReporter(True))
    # stats = neat.StatisticsReporter()
    # p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(10))

    # Run for up to 50 generations.
    # winner = p.run(eval_genomes, 100000)
    winner1 = p1.run(eval_genomes, 1)
    winner2 = p2.run(eval_genomes, 1)
    compare_networks(neat.nn.FeedForwardNetwork.create(winner1, config),
                     neat.nn.FeedForwardNetwork.create(winner2, config))
    # print('\nBest genome:\n{!s}'.format(winner))


def calculate_order(coefficients, param):
    order = []
    for coefficient in coefficients:
        total = 0
        for index, value in enumerate(coefficient[:-1]):
            total += float(value) * float(param[index])
        total += float(coefficient[-1])
        order.append(total)
    return order


def compare_checkpoint_model(path, checkpoint, config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-' + checkpoint)
    winner = p.run(eval_genomes, 1)
    net = neat.nn.FeedForwardNetwork.create(winner, config)
    coefficients = []
    with open(path) as file:
        content = file.read()
    for line in content.split("\n"):
        coefficients.append([])
        for coefficient in line.split(','):
            coefficients[-1].append(coefficient)
    score_1 = score_2 = 0
    game = None
    for _ in range(100):
        if game: print(game.round)
        game = Game()
        while True:
            try:
                go_for_option(game, net.activate(game.get_state()))
            except ValueError:
                print('Error')
                score_2 += 1
                # errors += 1
                break
            if game.players[0].points >= 15:
                # print('Finished')
                score_1 += 1
                break
            game.end_turn()
            try:
                go_for_option(game, calculate_order(coefficients, game.get_state()))
            except ValueError:
                print('Error')
                score_1 += 1
                break
            if game.players[0].points >= 15:
                # print('Finished')
                score_2 += 1
                break
            game.end_turn()
    for _ in range(100):
        if game: print(game.round)
        game = Game()
        while True:
            try:
                go_for_option(game, calculate_order(coefficients, game.get_state()))
            except ValueError:
                print('Error')
                score_1 += 1
                # errors += 1
                break
            if game.players[0].points >= 15:
                # print('Finished')
                score_2 += 1
                break
            game.end_turn()
            try:
                go_for_option(game, net.activate(game.get_state()))
            except ValueError:
                print('Error')
                score_2 += 1
                break
            if game.players[0].points >= 15:
                # print('Finished')
                score_1 += 1
                break
            game.end_turn()
    print("Score 1: ", score_1)
    print("Score 2: ", score_2)


if __name__ == '__main__':
    # plt.ion()
    run("configuration_full.txt")
