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

import generate_data_array as gda


DATABASE_FILENAME = 'menus/mini.db'
PIECE_TO_LETTER = {"Queen":"Q", "Rook":"R", "Knight":"N", "King":"K", "Bishop":"B"}
XLABELS = ["a", "b", "c", "d", "e", "f", "g", "h"]
YLABELS = ["8", "7", "6", "5", "4", "3", "2", "1"]

def generate_heatmap_from_user_input(input_dict):
	gameids = games_query(input_dict)
	if gameids == []:
		return False, False

	heatmap_type = input_dict["heatmap_type"]

	stats1 = " "
	stats2 = " "

	if heatmap_type == "moved to":
		df, num_moves, ksp = moved_to_query(gameids, input_dict["color"], input_dict["piece"])
		stats1 = "Percent of " + input_dict["piece"] + " moves to kingside: " + str(round(100*ksp, 2))
	elif heatmap_type == "time spent":
		df, num_moves, ai = time_spent_query(gameids, input_dict["color"], input_dict["piece"])
		stats1 = "Percent moves foward: " + str(round(100*ai, 2))
	elif heatmap_type == "captures":
		cp, rp, df, num_moves = captures_query(gameids, input_dict["color"], input_dict["piece"])
		if cp:
			stats1 = "Percent of moves which are captures: " + str(round(100*cp, 2))  
			stats2 = "Percent of moves which are recaptures: " + str(round(100*rp, 2))

	annot = False
	if input_dict["annotation"] == "yes":
		annot = True

	title = create_plot_title(input_dict, len(gameids))

	df = df.astype("int")

	plt.figure(1)

	plt.subplot(111)
	sns.heatmap(df, annot=annot, fmt="d", cmap = "Reds", xticklabels = XLABELS, yticklabels = YLABELS)
	plt.title(title)

	sns.plt.savefig("static/heatmap.png")
	plt.clf()

	return stats1, stats2


def games_query(input_dict):
	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()

	games_query = "SELECT gameid FROM games WHERE "
	args = []
	keys = input_dict.keys()

	for key in keys:
		if key == "color" or key == "piece" or key == "heatmap_type" or key == "annotation":
			continue
		elif key == "ECO":
			games_query += "substr(ECO, 1, 1) = ? AND CAST(substr(ECO, 2, 2) as int) >= ? AND CAST(substr(ECO, 6, 2) as int) <= ? AND "
			args += [input_dict[key][0], int(input_dict[key][1:3]), int(input_dict[key][5:])]
			continue
		elif "max" in key:
			games_query += key[:-4] + " <= ? AND "
		elif "min" in key:
			games_query += key[:-4] + " >= ? AND "
		elif key == "white_player" or key == "black_player":
			games_query += key + " LIKE ? AND "
			args.append(input_dict[key].replace(", ", ",").lower())
			continue
		else:
			games_query += key + " = ? AND "
		args.append(input_dict[key])

	if "AND" in games_query:
		games_query = games_query[:-5] + ";"
	else:
		games_query = "SELECT gameid FROM games;"

	print(games_query, args)

	r = c.execute(games_query, args)
	gameids = r.fetchall()
	return gameids


def generate_comparison_from_user_input(input_list):
	input_dict1 = input_list[0]
	input_dict2 = input_list[1]
	gameids1 = games_query(input_dict1)

	if not gameids1:
		return False, True, False, False, False, False

	gameids2 = games_query(input_dict2)

	if not gameids2:
		return True, False, False, False, False, False

	title1 = create_plot_title(input_dict1, len(gameids1))
	title2 = create_plot_title(input_dict2, len(gameids2))

	heatmap_type1 = input_dict1["heatmap_type"]

	stats1 = " "
	stats2 = " "
	stats3 = " "
	stats4 = " "

	if heatmap_type1 == "moved to":
		df1, num_moves1, ksp = moved_to_query(gameids1, input_dict1["color"], input_dict1["piece"])
		stats1 = "Heatmap 1: Percent of " + input_dict1["piece"] + " moves to kingside: " + str(round(100*ksp, 2))
	elif heatmap_type1 == "time spent":
		df1, num_moves1, ai = time_spent_query(gameids1, input_dict1["color"], input_dict1["piece"])
		stats1 = "Heatmap 1: Percent of forward moves: " + str(round(100*ai, 2))
	elif heatmap_type1 == "captures":
		cp, rp, df1, num_moves1 = captures_query(gameids1, input_dict1["color"], input_dict1["piece"])
		if cp:
			stats1 = "Heatmap 1: Percent of moves which are captures: " + str(round(100*cp, 2))  
			stats2 = "Heatmap 1: Percent of moves which are recaptures: " + str(round(100*rp, 2))

	heatmap_type2 = input_dict2["heatmap_type"]

	if heatmap_type2 == "moved to":
		df2, num_moves2, ksp = moved_to_query(gameids2, input_dict2["color"], input_dict2["piece"])
		stats3 = "Heatmap 2: Percent of " + input_dict2["piece"] + " moves to kingside: " + str(round(100*ksp, 2))
	elif heatmap_type2 == "time spent":
		df2, num_moves2, ai = time_spent_query(gameids2, input_dict2["color"], input_dict2["piece"])
		stats2 = "Heatmap 2: Percent of forward moves: " + str(round(100*ai, 2))
	elif heatmap_type2 == "captures":
		cp, rp, df2, num_moves2 = captures_query(gameids2, input_dict2["color"], input_dict2["piece"])
		if cp:
			stats3 = "Heatmap 2: Percent of moves which are captures: " + str(round(100*cp, 2))  
			stats4 = "Heatmap 2: Percent of moves which are recaptures: " + str(round(100*rp, 2))

	annot1 = False
	if input_dict1["annotation"] == "yes":
		annot1 = True

	annot2 = False
	if input_dict2["annotation"] == "yes":
		annot2 = True

	compare_stats = compare_heatmaps(df1, df2, num_moves1, num_moves2, title1, title2, annot1, annot2)

	stats5 = "Mean Magnitude of Normalized Differences: " + str(compare_stats[0])
	stats6 = "Standard Error of Magnitude of Normalized Differences: " + str(compare_stats[1])

	return stats1, stats2, stats3, stats4, stats5, stats6


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
	else: 
		moves_query = "SELECT move FROM moves WHERE color = ?"
	moves_query += " AND gameid = ? ORDER BY move_num;"

	num_moves = 0

	move_list = []

	for gameid in gameids:
		gameid = gameid[0]

		r = c.execute(moves_query, args + [gameid])
		moves = r.fetchall()
		num_moves += len(moves)
		move_list += moves

	df, kingside = gda.generate_moved_to_data(move_list, color, piece)
     
	return df, num_moves, float(kingside) / num_moves


def time_spent_query(gameids, color, piece):
	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()

	df = np.zeros((8, 8))
	num_moves = 0
	aggression = 0

	for gameid in gameids:
		gameid = gameid[0]

		w = c.execute("SELECT move FROM moves WHERE gameid = ? AND color = ? ORDER BY move_num;", (gameid, "white"))
		white_moves = w.fetchall()

		b = c.execute("SELECT move FROM moves WHERE gameid = ? AND color = ? ORDER BY move_num;", (gameid, "black"))
		black_moves = b.fetchall()

		white_dict, black_dict, white_aggression, black_aggression = gda.generate_time_spent_data(white_moves, black_moves)

		if color == "white":
			if piece == "All":
				for key in white_dict:
					df = np.add(df, white_dict[key])
			else:
				df = np.add(df, white_dict[piece.lower()])
			num_moves += len(white_moves)
			aggression += white_aggression
		else:
			if piece == "All":
				for key in black_dict:
					df = np.add(df, black_dict[key])
			else:
				df = np.add(df, black_dict[piece.lower()])
			num_moves += len(black_moves)
			aggression += black_aggression
	ai = float(aggression) / num_moves
	return df, num_moves, ai


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
		white_moves = r.fetchall()
		white_move_lists.append(white_moves)
		num_moves_white += len(white_moves)

		q = c.execute(moves_query, ["black"] + args + [gameid])
		black_moves = q.fetchall()
		black_move_lists.append(black_moves)
		num_moves_black += len(black_moves)

		if color == "white":
			df = np.add(df, gda.generate_captures_heatmap(white_moves))
		else:
			df = np.add(df, gda.generate_captures_heatmap(black_moves))

	wcp, bcp, wrp, brp = None, None, None, None

	if piece == "All":
		wcp, bcp, wrp, brp = gda.calculate_trade_statistics(white_move_lists, black_move_lists, num_moves_white, num_moves_black)

	if color == "white":
		return wcp, wrp, df, num_moves_white
	else:
		return bcp, brp, df, num_moves_black



def compare_heatmaps(df1, df2, num_moves1, num_moves2, title1, title2, annot1, annot2):
	df1 = df1.astype("float")
	df2 = df2.astype("float")

	diff_df = (df1 / num_moves1) - (df2 / num_moves2)

	abs_diff = abs(diff_df)
	mean_diff = np.mean(abs_diff)

	df1 = df1.astype("int")
	df2 = df2.astype("int")

	sumsq = 0
	for i in range(len(abs_diff)):
	      for j in range(len(abs_diff[0])):
	             sumsq += abs_diff[i][j]**2
	sumsq /= 64
	sd_diff = math.sqrt(sumsq)
	SE_diff = sd_diff / 8

	plt.figure(1)
	sns.heatmap(df1, annot=annot1, fmt="d", cmap = "Reds", xticklabels = XLABELS, yticklabels = YLABELS, square=True)
	plt.title(title1)
	sns.plt.savefig("static/heatmap1.png")
	sns.plt.clf()

	plt.figure(2)
	sns.heatmap(df2, annot=annot2, fmt="d", cmap = "Reds", xticklabels = XLABELS, yticklabels = YLABELS, square=True)
	plt.title(title2)
	sns.plt.savefig("static/heatmap2.png")
	sns.plt.clf()

	plt.figure(3)
	sns.heatmap(diff_df, annot=False, fmt="f", cmap = "coolwarm", xticklabels = XLABELS, yticklabels = YLABELS, square=True)
	plt.title("Normalized Difference")
	sns.plt.savefig("static/heatmapc.png")
	plt.clf()

	return [mean_diff, SE_diff]




def create_plot_title(input_dict, num_games):
	title = input_dict['color'] + ' ' + input_dict['piece'] + ' ' + input_dict['heatmap_type'] + ' heatmap, '
	
	# check if both players names are given and put it into the title
	if input_dict.get('white_player', None) and input_dict.get('black_player', None):
		title += input_dict.get('white_player', None) + " as white vs. " + input_dict.get('black_player', None) + "as black, "
	
	# check if the player of interest is playing white
	elif input_dict.get('white_player', None):
		title += input_dict['white_player']
		title += " as white, "
		
		# Only add one statement about ratings queried
		# Priority is given to the white_player's rating information
		if input_dict.get('white_rating_min', None) and input_dict.get('white_rating_max', None):
			title += "when rated between " + input_dict['white_rating_min'] + " and " + input_dict['white_rating_max'] + " "
		elif input_dict.get('white_rating_min', None):
			title += "when rated at least " + input_dict.get['white_rating_min'] + " "
		elif input_dict.get('white_rating_max', None):
			title += "when rated at most " + input_dict['white_rating_max'] + " "
			
		# Check for opponent's rating
		elif input_dict.get('black_rating_min', None) and input_dict.get('black_rating_max', None):
			title += "when against opponents rated between " + input_dict['black_rating_min'] + " and " + input_dict['black_rating_max'] + " "
		elif input_dict.get('black_rating_min', None):
			title += " when against opponents rated at least " + input_dict['black_rating_min'] + " "
		elif input_dict.get('black_rating_max', None):
			title += "when against opponents rated at most " + input_dict['black_rating_max'] + " "
			
	# check if the player of interest is playing black
	elif input_dict.get('black_player', None):
		title += input_dict['black_player']  + " "
		title += " as black, "
		
		# Only add one statement about ratings queried
		# Priority is given to the white_player's rating information
		if input_dict.get('black_rating_min', None) and input_dict.get('black_rating_max', None):
			title += "when rated between " + input_dict['black_rating_min'] + " and " + input_dict['black_rating_max'] + " "
		elif input_dict.get('black_rating_min', None):
			title += "when rated at least " + input_dict['black_rating_min'] + " "
		elif input_dict.get('black_rating_max', None):
			title += "when rated at most " + input_dict['black_rating_max'] + " "
			
		# Check for opponent's rating
		elif input_dict.get('white_rating_min', None) and input_dict.get('white_rating_max', None):
			title += "when against opponents rated between " + input_dict['white_rating_min'] + " and " + input_dict['white_rating_max'] + " "
		elif input_dict.get('white_rating_min', None):
			title += " when against opponents rated at least " + input_dict['white_rating_min'] + " "
		elif input_dict.get('white_rating_max', None):
			title += "when against opponents rated at most " + input_dict['white_rating_max'] + " "

	if not input_dict.get("white_player", False):
		if input_dict.get('white_rating_min', None) and input_dict.get('white_rating_max', None):
			title += "White rated between " + input_dict['white_rating_min'] + " and " + input_dict['white_rating_max'] + ", "
		elif input_dict.get('white_rating_min', None):
			title += "White rated at least " + input_dict.get['white_rating_min'] + ", "
		elif input_dict.get('white_rating_max', None):
			title += "White rated at most " + input_dict['white_rating_max'] + ", "

	if not input_dict.get("black_player", False):
		if input_dict.get('black_rating_min', None) and input_dict.get('black_rating_max', None):
			title += "Black rated between " + input_dict['black_rating_min'] + " and " + input_dict['black_rating_max'] + ", "
		elif input_dict.get('black_rating_min', None):
			title += "Black rated at least " + input_dict['black_rating_min'] + ", "
		elif input_dict.get('black_rating_max', None):
			title += "Black rated at most " + input_dict['black_rating_max'] + ", "

			
		
	if input_dict.get('year_min', None) and input_dict.get('year_max', None):
		title += "played between " + input_dict['year_min'] + " and " + input_dict['year_max'] + " "
	
	if input_dict.get('year_min', None):
		title += "played after " + input_dict['year_min'] + " "
		
	if input_dict.get('year_max', None):
		title += "played before " + input_dict['year_max'] + " "
		
	opening = ' '
	if input_dict.get('ECO', None):
		opening = " Opening code: " + input_dict.get('ECO', '')
	title += opening
	
	if input_dict.get('num_moves_min', None) and input_dict.get('num_moves_max', None):
		title += "in games lasting between " + input_dict['num_moves_min'] + 'and' + input_dict['num_moves_max'] + " moves."
	
	if input_dict.get('num_moves_min', None):
		title += "in games lasting at least " + input_dict['num_moves_min'] + " "
		
	if input_dict.get('num_moves_max', None):
		title += "in games lasting at most " + input_dict['num_moves_max']+ " "
		
	if input_dict.get('result', None) == '1-0':
		title += 'White wins'
		
	if input_dict.get('result', None) == '0-1':
		title += 'Black wins'
	
	if input_dict.get('result', None) == '1/2-1/2':
		title += 'games drawn'
	
	title += " [" + str(num_games) + " Games]"
	# Make the title camelcase
	title = title.title()
	title = title.replace("  ", " ")
	return title
	
