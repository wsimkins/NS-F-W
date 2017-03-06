#Building Queries and Returning Heatmaps

import math
import pandas as pd
import numpy as np
from scipy import stats
import random
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import sqlite3 as sql
import os

import heatmaps 
import generate_data_array as gda


DATABASE_FILENAME = "cooklev"
PIECE_TO_LETTER = {"Queen":"Q", "Rook":"R", "Knight":"N", "King":"K", "Bishop":"B"}
XLABELS = ["a", "b", "c", "d", "e", "f", "g", "h"]
YLABELS = ["8", "7", "6", "5", "4", "3", "2", "1"]

'''
color, white_player, black_player, white_rating_min, white_rating_max, black_rating_min, black_rating_max,
result, ECO, year_min, year_max, num_moves_min, num_moves_max, piece, heatmap_type, compare
'''


def generate_heatmap_from_user_input(input_dict):
	gameids = games_query(input_dict)

	heatmap_type = input_dict["heatmap_type"]
	
	print(input_dict)

	annot = True
	if input_dict.get("annotation", None) == "no":
		annot = False

	stats = []

	if heatmap_type == "moved to":
		df, title, num_moves = moved_to_query(gameids, input_dict["color"], input_dict["piece"])
	elif heatmap_type == "time spent":
		df, title, num_moves = time_spent_query(gameids, input_dict["color"], input_dict["piece"])
	elif heatmap_type == "captures":
		cp, rp, df, title, num_moves = captures_query(gameids, input_dict["color"], input_dict["piece"])
		stats = [cp, rp]

	df = df.astype("int")

	plt.figure(1)

	plt.subplot(111)
	sns.heatmap(df, annot=annot, fmt="d", cmap = "Reds", xticklabels = XLABELS, yticklabels = YLABELS)
	plt.title(title)

	sns.plt.savefig("static/heatmap.png")
	plt.clf()

	return stats


def games_query(input_dict):
	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()

	games_query = "SELECT gameid FROM games WHERE "
	args = []
	keys = input_dict.keys()

	for key in keys:
		if key == "color" or key == "piece" or key == "heatmap_type" or key == "annotation":
			continue
		elif "max" in key:
			games_query += key[:-4] + " <= ? AND "
		elif "min" in key:
			games_query += key[:-4] + " >= ? AND "
		elif key == "white_player" or key == "black_player":
			games_query += key + " LIKE ? AND "
		else:
			games_query += key + " = ? AND "
		args.append(input_dict[key].replace(" ", "_"))

	if "AND" in games_query:
		games_query = games_query[:-5] + ";"
	else:
		games_query = "SELECT gameid FROM games;"

	r = c.execute(games_query, args)
	gameids = r.fetchall()
	return gameids


def generate_comparison_from_user_input(input_list):
	input_dict1 = input_list[0]
	input_dict2 = input_list[1]
	gameids1 = games_query(input_dict1)
	gameids2 = games_query(input_dict2)

	heatmap_type1 = input_dict1["heatmap_type"]

	stats1 = []

	if heatmap_type1 == "moved to":
		df1, title1, num_moves1 = moved_to_query(gameids1, input_dict1["color"], input_dict1["piece"])
	elif heatmap_type1 == "time spent":
		df1, title1, num_moves1 = time_spent_query(gameids1, input_dict1["color"], input_dict1["piece"])
	elif heatmap_type == "captures":
		cp, rp, df1, title1, num_moves1 = captures_query(gameids1, input_dict1["color"], input_dict1["piece"])
		stats1 = [cp, rp]

	heatmap_type2 = input_dict2["heatmap_type"]

	stats2 = []

	if heatmap_type2 == "moved to":
		df2, title2, num_moves2 = moved_to_query(gameids2, input_dict2["color"], input_dict2["piece"])
	elif heatmap_type1 == "time spent":
		df2, title2, num_moves2 = time_spent_query(gameids2, input_dict2["color"], input_dict2["piece"])
	elif heatmap_type == "captures":
		cp, rp, df2, title2, num_moves2 = captures_query(gameids2, input_dict2["color"], input_dict2["piece"])
		stats2 = [cp, rp]

	return stats1, stats2, compare_heatmaps(df1, df2, num_moves1, num_moves2, title1, title2)


def moved_to_query(gameids, color, piece):
	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()

	args = [color]
	moves_query = "SELECT move FROM moves WHERE color = ? AND "

	if piece == "Pawn":
		moves_query += "substr(move, 1, 1) IN (?,?,?,?,?,?,?,?)"
		args += ["a", "b", "c", "d", "e", "f", "g", "h"]
	elif piece != "All":
		moves_query += "(substr(move, 1, 1) = ?"
		args.append(PIECE_TO_LETTER[piece])

		if piece == "Rook" or piece == "King":
			moves_query += " OR substr(move,1,1) = ?)"
			args.append("0")
		else:
			moves_query += ")"

	moves_query += " AND gameid = ? ORDER BY move_num;"

	df = np.zeros((8, 8))
	num_moves = 0

	for gameid in gameids:
		gameid = gameid[0]

		r = c.execute(moves_query, args + [gameid])
		moves = r.fetchall()[::2]
		num_moves += len(moves)
		df = np.add(df, gda.generate_moved_to_data(moves, color, piece))

	title = "Moved To " + color + " " + piece
     
	return df, title, num_moves


def time_spent_query(gameids, color, piece):
	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()

	df = np.zeros((8, 8))
	num_moves = 0

	for gameid in gameids:
		gameid = gameid[0]

		w = c.execute("SELECT move FROM moves WHERE gameid = ? AND color = ? ORDER BY move_num;", (gameid, "white"))
		white_moves = w.fetchall()[::2]

		b = c.execute("SELECT move FROM moves WHERE gameid = ? AND color = ? ORDER BY move_num;", (gameid, "black"))
		black_moves = b.fetchall()[::2]

		white_dict, black_dict = gda.generate_time_spent_data(white_moves, black_moves)

		if color == "white":
			df = np.add(df, white_dict[piece.lower()])
			num_moves += len(white_moves)
		else:
			df = np.add(df, black_dict[piece.lower()])
			num_moves += len(black_moves)


	title = "Time Spent " + color + " " + piece
     
	return df, title, num_moves
       

def captures_query(gameids, color, piece):
	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()

	args = []
	moves_query = "SELECT move FROM moves WHERE color = ?"

	if piece == "Pawn":
		moves_query += " AND substr(move, 1, 1) IN (?,?,?,?,?,?,?,?)"
		args += ["a", "b", "c", "d", "e", "f", "g", "h"]
	elif piece != "All":
		moves_query += " AND (substr(move, 1, 1) = ?"
		args.append(PIECE_TO_LETTER[piece])

		if piece == "Rook" or piece == "King":
			moves_query += " OR substr(move,1,1) = ?)"
			args.append("0")
		else:
			moves_query += ")"

	moves_query += " AND gameid = ? ORDER BY move_num;"

	white_move_lists = []
	black_move_lists = []
	num_moves_white = 0
	num_moves_black = 0

	df = np.zeros((8, 8))
	for gameid in gameids:
		gameid = gameid[0]

		r = c.execute(moves_query, ["white"] + args + [gameid])
		white_moves = r.fetchall()[::2]
		white_move_lists.append(white_moves)
		num_moves_white += len(white_moves)

		q = c.execute(moves_query, ["black"] + args + [gameid])
		black_moves = q.fetchall()[::2]
		black_move_lists.append(black_moves)
		num_moves_black += len(black_moves)

		if color == "white":
			df = np.add(df, gda.generate_captures_heatmap(white_moves))
		else:
			df = np.add(df, gda.generate_captures_heatmap(black_moves))

	wcp, bcp, wrp, brp = None, None, None, None

	if piece == "All":
		wcp, bcp, wrp, brp = gda.calculate_trade_statistics(white_move_lists, black_move_lists, num_moves_white, num_moves_black)

	title = "Captures " + color + " " + piece

	if color == "white":
		return wcp, wrp, df, title, num_moves_white
	else:
		return bcp, brp, df, title, num_moves_black



def compare_heatmaps(df1, df2, num_moves1, num_moves2, title1, title2):
	df1 = df1.astype("int")
	df2 = df2.astype("int")
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



	gs = gridspec.GridSpec(2, 4)

	ax1 = plt.subplot(gs[0, 0:2]) 
	sns.heatmap(df1, annot=False, fmt="d", cmap = "Reds", xticklabels = XLABELS, yticklabels = YLABELS)
	plt.title(title1)

	ax2 = plt.subplot(gs[0,2:])
	sns.heatmap(df2, annot=False, fmt="d", cmap = "Reds", xticklabels = XLABELS, yticklabels = YLABELS)
	plt.title(title2)

	ax3 = plt.subplot(gs[1,1:3])
	sns.heatmap(diff_df, annot=False, fmt="f", cmap = "coolwarm", xticklabels = XLABELS, yticklabels = YLABELS)
	plt.title("Normalized Difference")


	sns.plt.savefig("heatmap.png")
	plt.clf()

	return [mean_diff, SE_diff]




