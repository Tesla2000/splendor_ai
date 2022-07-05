import neat
from random import randint
from regresion.merge_data import to_export
import numpy as np
# import matplotlib.pyplot as plt
# from IPython import display
# import pickle

first = []
means = []
second = []
third = []
fifth = []


def eval_genomes(genomes, config):
    # global first, second, third, fifth
    evaluations = []
    # results = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        evaluations.append((genome, net))
    # best_fitness = None
    for evaluation in evaluations:
        # genome = []
        for _ in range(10):
            chosen = randint(0, len(to_export) - 1)
            x = np.array(to_export[chosen][27:], dtype=int)
            values = evaluation[1].activate(x)
            y = to_export[chosen][:27].index('1')
            # print("Initial values: ", end="")
            # print(values)
            # print("Move: ", end="")
            # print(y)
            # print("Points of move: ", end="")
            # print(values[y])
            # print("Sorted moves: ", end="")
            # print(tuple(sorted(values, reverse=True)))
            position = tuple(sorted(values, reverse=True)).index(values[y])
            # print("Position: ", position)
            # genome.append(position)
            evaluation[0].fitness -= position
        # if not best_fitness or evaluation[0].fitness > best_fitness:
        #     best_fitness = evaluation[0].fitness
        #     results = genome.copy()
    # first.append(len(tuple(filter(lambda result: result < 1, results)))/50)
    # second.append(len(tuple(filter(lambda result: result < 2, results)))/50)
    # third.append(len(tuple(filter(lambda result: result < 3, results)))/50)
    # fifth.append(len(tuple(filter(lambda result: result < 5, results)))/50)
    # plot(first, second, third, fifth)


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
    # show final stats
    # with open("winner.pickle", 'wb') as file:
    #     pickle.dump(winner, file)
    print('\nBest genome:\n{!s}'.format(winner))


# def plot(first, first_2, first_3, first_5):
#     # global means
#     display.clear_output(wait=True)
#     display.display(plt.gcf())
#     plt.clf()
#     plt.title('Training...')
#     plt.xlabel('Number of Games')
#     plt.ylabel('Percentage')
#     # means.append(sum(first[:min(len(first), 20)])/min(len(first), 20))
#     plt.plot(first)
#     plt.plot(first_2)
#     plt.plot(first_3)
#     plt.plot(first_5)
#     plt.ylim(ymin=0)
#     plt.text(len(first) - 1, first[-1], str(first[-1]))
#     plt.text(len(first_2) - 1, first_2[-1], str(first_2[-1]))
#     plt.text(len(first_3) - 1, first_3[-1], str(first_3[-1]))
#     plt.text(len(first_5) - 1, first_5[-1], str(first_5[-1]))
#     plt.show(block=False)
#     plt.pause(.01)


if __name__ == '__main__':
    # plt.ion()
    run("configuration.txt")
