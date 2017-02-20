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
       white_moves_list, bishop_moves_list = heatmaps.create_database("working_html.htm", "output_file.db")

       df = gda.generate_moved_to_data(white_moves_list, "white", "all", 19)
       print(df)

       xlabels = ["a", "b", "c", "d", "e", "f", "g", "h"]
       ylabels = ["8", "7", "6", "5", "4", "3", "2", "1"]

       ax = plt.axes()
       sns.heatmap(df, annot=False, fmt="d", cmap = "coolwarm", xticklabels = xlabels, yticklabels = ylabels)
       ax.set_title("2007 Czech Open - White Pieces")

       sns.plt.show()

       df2 = gda.generate_moved_to_data(bishop_moves_list, "white", "bishop", 19)

       ax2 = plt.axes()
       sns.heatmap(df2, annot=True, fmt="d", cmap = "Reds", xticklabels = xlabels, yticklabels = ylabels)
       ax2.set_title("2007 Czech Open - White Bishops")
       sns.plt.show()





