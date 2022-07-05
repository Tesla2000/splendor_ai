from collections import namedtuple
from math import factorial, floor
import pickle
import neat
from neat_splendor_entities import Game
from neat_splendor_game_controller import go_for_option_full

NeatElement = namedtuple('NeatElement', ['genome', 'net', 'id'])


def eval_genomes_full(genomes, config):
    evaluations = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        evaluations.append(NeatElement(genome, net, genome_id))
    evaluate(evaluations)
    # errors = 0


def evaluate(evaluations):
    for player_1 in range(0, len(evaluations)):
        for player_2 in range(player_1, len(evaluations)):
            play_game(evaluations[player_1], evaluations[player_2])


def play_game(player1, player2):
    global fitnesses
    game = Game()
    while True:
        try:
            go_for_option_full(game, player1.net.activate(game.get_state()))
        except ValueError:
            print('Error')
            fitnesses[player2] = fitnesses.get(player2, 0) + 1
            # errors += 1
            break
        v = game.players[0].points
        if game.players[0].points >= 15:
            # print('Finished')
            fitnesses[player1] = fitnesses.get(player1, 0) + 1 + 1 / game.round / 50
            break
        game.end_turn()
        try:
            go_for_option_full(game, player2.net.activate(game.get_state()))
        except ValueError:
            print('Error')
            fitnesses[player1] = fitnesses.get(player1, 0) + 1
            # errors += 1
            break
        v = game.players[0].points
        if game.players[0].points >= 15:
            # print('Finished')
            fitnesses[player2] = fitnesses.get(player2, 0) + 1 + 1 / game.round / 50
            break
        game.end_turn()


def compare_networks(winner1, winner2):
    score_1 = score_2 = 0
    for _ in range(100):
        game = Game()
        while True:
            try:
                go_for_option_full(game, winner1.activate(game.get_state()))
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
                go_for_option_full(game, winner2.activate(game.get_state()))
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
                go_for_option_full(game, winner2.activate(game.get_state()))
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
                go_for_option_full(game, winner1.activate(game.get_state()))
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
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-13')

    # Create the population, which is the top-level object for a NEAT run.
    # p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(10))

    # Run for up to 50 generations.
    p.run(train_other_convention, 100)
    # winner1 = p.run(eval_genomes, 1)
    # winner2 = p2.run(eval_genomes, 1)
    # compare_networks(neat.nn.FeedForwardNetwork.create(winner1, config), neat.nn.FeedForwardNetwork.create(winner2, config))
    # print('\nBest genome:\n{!s}'.format(winner))


def train_other_convention(genomes, config):
    global master, fitnesses
    evaluations = []
    fitnesses = {}
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        evaluations.append(NeatElement(genome, net, genome_id))
    if not master:
        evaluate(evaluations)
        master = max(evaluations, key=lambda evaluation: evaluation.genome.fitness)
        with open("master" + str(master.id) + ".pickle", 'wb') as file:
            pickle.dump(master, file)
    else:
        for neat_element in evaluations:
            for _ in range(5):
                play_game(neat_element, master)
            for _ in range(6):
                play_game(master, neat_element)
        pretender = max(evaluations, key=lambda evaluation: evaluation.genome.fitness)
        fitness = fitnesses[pretender]
        if pretender.genome.fitness >= 6 and pretender.id != master.id:
            for i in range(45):
                play_game(pretender, master)
                play_game(master, pretender)
                won = fitnesses[pretender]
                total = 11 + 2*i
                chances = factorial(total)/factorial(floor(won))/(2**total)
                if won > 0.5*total and chances < 0.05:
                    master = pretender
                    with open("master" + str(master.id) + ".pickle", 'wb') as file:
                        pickle.dump(master, file)
                    print("We have a new master: ", fitnesses[pretender])
                    break
            else:
                print("Pretender vs master: ", fitnesses[pretender])
        fitnesses[pretender] = fitness
    for evaluation in evaluations:
        evaluation.genome.fitness = fitnesses[evaluation]


def compare_checkpoints(config_file, checkpoint1, checkpoint2):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    p2 = neat.Checkpointer.restore_checkpoint('neat-checkpoint-' + checkpoint2)

    # Create the population, which is the top-level object for a NEAT run.
    p1 = neat.Checkpointer.restore_checkpoint('neat-checkpoint-' + checkpoint1)

    # Add a stdout reporter to show progress in the terminal.
    # p.add_reporter(neat.StdOutReporter(True))
    # stats = neat.StatisticsReporter()
    # p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(10))

    # Run for up to 50 generations.
    # winner = p.run(eval_genomes, 100000)
    winner1 = p1.run(eval_genomes_full, 1)
    winner2 = p2.run(eval_genomes_full, 1)
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
    winner = p.run(eval_genomes_full, 1)
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
                go_for_option_full(game, net.activate(game.get_state()))
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
                go_for_option_full(game, calculate_order(coefficients, game.get_state()))
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
                go_for_option_full(game, calculate_order(coefficients, game.get_state()))
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
                go_for_option_full(game, net.activate(game.get_state()))
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
    # master = None
    with open("master1.pickle", 'rb') as file:
        master = pickle.load(file)
    m = master
    m_0 = master[0]
    run("configuration_full.txt")
    # compare_checkpoints("configuration_full.txt", '0', '14')
