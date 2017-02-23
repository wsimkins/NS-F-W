import math
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns

import heatmaps 
import generate_data_array as gda


def draw_heatmap(dataframe):
	# df = pd.DataFrame(np.random.randn(8,8))
	sns.heatmap(dataframe, annot=False, fmt="d")
	sns.plt.show()

def example_map():
	df = np.array([[ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  0.,  0.,  0.,  0.,  1.,  1.,  0.],
       [ 0.,  0.,  0.,  0.,  1.,  0.,  0.,  1.],
       [ 0.,  2.,  0.,  2.,  1.,  0.,  0.,  1.],
       [ 1.,  0.,  1.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.],
       [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]])
	sns.heatmap(df, annot=False, fmt="d")
	sns.plt.show()

def will_example():
       white_moves1, black_moves1, white_moves2, black_moves2 = heatmaps.create_database("working_html.htm", "output_file.db")

       white_dict1, black_dict1 = gda.generate_time_spent_data(white_moves1, black_moves1)
       white_dict2, black_dict2 = gda.generate_time_spent_data(white_moves2, black_moves2)

       df = np.zeros((8,8))
       for array in white_dict1.values():
              df = np.add(df, array)

       df2 = np.zeros((8,8))
       for array in white_dict2.values():
              df2 = np.add(df2, array)

       df = df.astype("int")
       df2 = df2.astype("int")

       xlabels = ["a", "b", "c", "d", "e", "f", "g", "h"]
       ylabels = ["8", "7", "6", "5", "4", "3", "2", "1"]

       ax = plt.axes()
       sns.heatmap(df, annot=False, fmt="d", cmap = "coolwarm", xticklabels = xlabels, yticklabels = ylabels)
       ax.set_title("Game 1")

       sns.plt.show()

       ax2 = plt.axes()
       sns.heatmap(df2, annot=True, fmt="d", cmap = "Reds", xticklabels = xlabels, yticklabels = ylabels)
       ax2.set_title("Game 2")
       sns.plt.show()

       df3 = (df / len(white_moves1)) - (df2 / len(white_moves2)) 

       ax3 = plt.axes()
       sns.heatmap(df3, annot=True, fmt="f", cmap = "Reds", xticklabels = xlabels, yticklabels = ylabels)
       ax3.set_title("Difference")
       sns.plt.show()

       sumsq = 0
       for i in range(len(df3)):
              for j in range(len(df3[0])):
                     sumsq += df3[i][j]**2

       sumsq /= 64
       print("SD", math.sqrt(sumsq))
       print("mean", np.mean(np.absolute(df3)))




