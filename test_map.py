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
       white_moves = heatmaps.create_database("working_html.htm", "output_file.db")
       white_moves_string = " "
       for moves in white_moves:
           white_moves_string += str(moves)[2:-3] + " "
       white_moves_list = white_moves_string.split()

       df = gda.generate_moved_to_data_all_pieces(white_moves_list, "white")

       xlabels = ["a", "b", "c", "d", "e", "f", "g", "h"]
       ylabels = ["8", "7", "6", "5", "4", "3", "2", "1"]

       ax = plt.axes()
       sns.heatmap(df, annot=False, fmt="d", cmap = "coolwarm", xticklabels = xlabels, yticklabels = ylabels)
       ax.set_title("2007 Czech Open - White Pieces")

       sns.plt.show()

       df2 = gda.generate_moved_to_data(white_moves_list, "white", "queen")

       ax2 = plt.axes()
       sns.heatmap(df2, annot=False, fmt="d", cmap = "Reds", xticklabels = xlabels, yticklabels = ylabels)
       ax2.set_title("2007 Czech Open - White Queen")
       sns.plt.show()





