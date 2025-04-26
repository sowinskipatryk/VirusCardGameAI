import matplotlib.pyplot as plt
import numpy as np
from neat.reporting import BaseReporter


class LiveGraphReporter(BaseReporter):
    def __init__(self):
        self.generation = []
        self.avg_fitness = []
        self.fig, self.ax = plt.subplots()
        plt.ion()  # Interactive mode on!
        self.line, = self.ax.plot([], [], label="Average Fitness")
        self.trend_line, = self.ax.plot([], [], 'r--', label="Trend Line")

        self.ax.set_xlabel("Generation")
        self.ax.set_ylabel("Fitness")
        self.ax.set_title("Live Fitness Progress")
        self.ax.legend()

    def post_evaluate(self, config, population, species, best_genome):
        current_gen = len(self.generation)
        fitnesses = [genome.fitness for genome in population.values()]
        average_fitness = sum(fitnesses) / len(fitnesses)

        self.generation.append(current_gen)
        self.avg_fitness.append(average_fitness)

        # Update plot data
        self.line.set_xdata(self.generation)
        self.line.set_ydata(self.avg_fitness)

        # Calculate trend line (linear fit)
        if len(self.generation) >= 2:
            coeffs = np.polyfit(self.generation, self.avg_fitness, 1)  # degree 1 = linear
            trend = np.poly1d(coeffs)
            y_trend = trend(self.generation)
            self.trend_line.set_xdata(self.generation)
            self.trend_line.set_ydata(y_trend)

        self.ax.relim()
        self.ax.autoscale_view()

        plt.pause(0.01)

    def complete_extinction(self):
        print("Complete extinction happened!")
