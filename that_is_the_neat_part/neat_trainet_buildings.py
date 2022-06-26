import neat
from neat_splendor_entities import Game
from neat_splendor_game_controller import go_for_option


def eval_genomes(genomes, config):
    evaluations = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        evaluations.append((genome, net))

    for i in range(0, len(evaluations), 2):
        game = Game()
        for _ in range(3):
            while True:
                values = evaluations[i][1].activate(game.get_state())
                try:
                    go_for_option(game, values)
                except ValueError:
                    evaluations[i + 1][0].fitness += 1
                    evaluations[i][0].fitness -= 1
                    break
                if game.players[0].points >= 15:
                    # print('Finished')
                    evaluations[i][0].fitness += 1
                    evaluations[i][0].fitness += 1 / game.round
                    evaluations[i + 1][0].fitness -= 1
                    break
                game.end_turn()
                values = evaluations[i + 1][1].activate(game.get_state())
                try:
                    go_for_option(game, values)
                except ValueError:
                    # print('Error')
                    evaluations[i][0].fitness += 1
                    evaluations[i + 1][0].fitness -= 1
                    break
                if game.players[0].points >= 15:
                    # print('Finished')
                    evaluations[i + 1][0].fitness += 1
                    evaluations[i + 1][0].fitness += 1 / game.round
                    evaluations[i][0].fitness -= 1
                    break


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-793')

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(100))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 100000)
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # plt.ion()
    run("configuration_building.txt")
