import math
import pandas as pd
import numpy as np
from scipy import stats
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

def example():
       white_moves1, black_moves1, white_moves2, black_moves2, white_moves3, black_moves3 = heatmaps.create_database("working_html.htm", "output_file.db")

       white_dict1, black_dict1 = gda.generate_time_spent_data(white_moves1, black_moves1)
       white_dict2, black_dict2 = gda.generate_time_spent_data(white_moves2, black_moves2)
       white_dict3, black_dict3 = gda.generate_time_spent_data(white_moves3, black_moves3)

       df = np.zeros((8,8))
       for array in white_dict1.values():
              df = np.add(df, array)

       #for array in white_dict3.values():
        #      df = np.add(df, array)

       #for array in white_dict2.values():
        #      df = np.add(df, array)
              
       df2 = np.zeros((8,8))
       for array in black_dict1.values():
              df2 = np.add(df2, array)

       for array in black_dict3.values():
              df2 = np.add(df2, array)

       #for array in black_dict2.values():
         #     df2 = np.add(df2, array)


       df = df.astype("int")
       df2 = df2.astype("int")

       xlabels = ["a", "b", "c", "d", "e", "f", "g", "h"]
       ylabels = ["8", "7", "6", "5", "4", "3", "2", "1"]

       plt.figure(1)

       plt.subplot(211)
       sns.heatmap(df, annot=False, fmt="d", cmap = "coolwarm", xticklabels = xlabels, yticklabels = ylabels)
       plt.title("Game 1")

       plt.subplot(212)

       sns.heatmap(df2, annot=False, fmt="d", cmap = "coolwarm", xticklabels = xlabels, yticklabels = ylabels)
       plt.title("Game 2")
       sns.plt.show()

       compare_heatmaps(df, df2, len(white_moves1) + len(white_moves3), len(black_moves1) + len(black_moves3))



def compare_heatmaps(df1, df2, num_moves1, num_moves2):
       diff_df = (df1 / num_moves1) - (df2 / num_moves2)
       abs_diff = abs(diff_df)
       mean_diff = np.mean(abs_diff)

       sumsq = 0
       for i in range(len(abs_diff)):
              for j in range(len(abs_diff[0])):
                     sumsq += abs_diff[i][j]**2
       sumsq /= 64
       sd_diff = math.sqrt(sumsq)
       SE_diff = sd_diff / 8

       print("Mean:", mean_diff)
       print("SE(d)", SE_diff)

       xlabels = ["a", "b", "c", "d", "e", "f", "g", "h"]
       ylabels = ["8", "7", "6", "5", "4", "3", "2", "1"]

       ax3 = plt.axes()
       sns.heatmap(diff_df, annot=False, fmt="f", cmap = "coolwarm", xticklabels = xlabels, yticklabels = ylabels)
       ax3.set_title("Normalized Difference")
       sns.plt.show()

       




