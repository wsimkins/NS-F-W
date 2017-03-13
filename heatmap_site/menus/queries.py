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
from textwrap import wrap

import generate_data_array as gda


DATABASE_FILENAME = 'menus/mini.db'
PIECE_TO_LETTER = {"Queen":"Q", "Rook":"R", "Knight":"N", "King":"K", "Bishop":"B"}
XLABELS = ["a", "b", "c", "d", "e", "f", "g", "h"]
YLABELS = ["8", "7", "6", "5", "4", "3", "2", "1"]

def generate_heatmap_from_user_input(input_dict):
	'''
	Accepts an input dictionary containing specifications for a single heatmap,
	generates that heatmap and then saves that heatmap to static/heatmap.png
	and returns the accompanying stats.

	Inputs: 
		input_dict: A dictionary containing specifications for a heatmap such as 
			heatmap_type, a year range, ECO code, rating, player names, etc.

	Returns: 2 strings, stats1 and stats2 (stats 2 is possibly empty), which 
		contain descriptions of statistics intended to accompany the heatmap
	'''
	# finds the list of gameids that fit the input specifications
	gameids = games_query(input_dict)

	# returns False to the Django code if there are no gameid matches so that
	# Django can return an error "No Heatmaps Found page"
	if gameids == []:
		return False, False

	heatmap_type = input_dict["heatmap_type"]

	stats1 = " "
	stats2 = " "

	# calculates the appropriate heatmap and stats based on 
	# input_dict["heatmap_type"]
	if heatmap_type == "moved to":
		df, ksp = moved_to_query(gameids, input_dict["color"], 
											input_dict["piece"])
		stats1 = "Percent of " + input_dict["piece"] + \
			" moves to kingside: " + str(round(100*ksp, 2))
	elif heatmap_type == "time spent":
		df, ai = time_spent_query(gameids, input_dict["color"],
												 input_dict["piece"])
		stats1 = "Percent moves foward: " + str(round(100*ai, 2))
	elif heatmap_type == "captures":
		cp, rp, df = captures_query(gameids, input_dict["color"], 
													input_dict["piece"])
		if cp:
			stats1 = "Percent of moves which are captures: " + \
						str(round(100*cp, 2))  
			stats2 = "Percent of moves which are recaptures: " + \
						str(round(100*rp, 2))

	# creates and saves the proper heatmap at static/heatmap.png
	annot = False
	if input_dict["annotation"] == "yes":
		annot = True

	title = create_plot_title(input_dict, len(gameids))

	df = df.astype("int")

	plt.figure(1)

	plt.subplot(111)
	sns.heatmap(df, annot=annot, fmt="d", cmap = "Reds", xticklabels = XLABELS, 
														yticklabels = YLABELS)
	plt.title("\n".join(wrap(title, 60)))

	sns.plt.savefig("static/heatmap.png")
	plt.clf()

	return stats1, stats2


def games_query(input_dict):
	'''
	Given a list of game specifications, queries the games db and returns a 
	list of gameids which meet all of these criteria

	Inputs: 
		input_dict: a dictionary containing specifications for a heatmap such
			as a year range, ECO code, rating, player names, etc.
	'''
	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()

	# builds the games query based on the relevant information in input_dict
	games_query = "SELECT gameid FROM games WHERE "
	args = []
	keys = input_dict.keys()

	for key in keys:
		if key == "color" or key == "piece" or key == "heatmap_type" or \
												key == "annotation":
			continue
		elif key == "ECO":
			games_query += "substr(ECO, 1, 1) = ? AND " + \
				"CAST(substr(ECO, 2, 2) as int) >= ? AND " + \
				"CAST(substr(ECO, 6, 2) as int) <= ? AND "
			args += [input_dict[key][0], int(input_dict[key][1:3]), 
					int(input_dict[key][5:])]
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

	# executes the games query and returns the resulting list of gameids
	r = c.execute(games_query, args)
	gameids = r.fetchall()
	return gameids


def generate_comparison_from_user_input(input_list):
	'''
	Accepts an input dictionary containing specifications for two heatmaps, and
	generates those heatmap as well as a comparison heatmap and saves those 
	heatmaps to static/heatmap1.png, static/heatmap2.png, and static/heatmapc.png
	and returns the accompanying stats.

	Inputs: 
		input_list: A list of two input dictionaries containing specifications
			for heatmaps such as heatmap_type, a year range, ECO code, rating, 
			player names, etc.

	Returns: 6 strings, stats1-stats6 (stats 2 and stats 4 are possibly empty),
	which contain descriptions of statistics intended to accompany the heatmaps
	'''
	# separates the input_dicts and uses games_query to find the list of
	# gameids that fit the two sets of specifications
	input_dict1 = input_list[0]
	input_dict2 = input_list[1]
	gameids1 = games_query(input_dict1)

	# tells Django code that no heatmaps fit specifications for heatmap1
	if not gameids1:
		return False, True, False, False, False, False

	gameids2 = games_query(input_dict2)

	# tells Django code that no heatmaps fit spefications for heatmap2
	if not gameids2:
		return True, False, False, False, False, False

	# generates titles for both heatmaps
	title1 = create_plot_title(input_dict1, len(gameids1))
	title2 = create_plot_title(input_dict2, len(gameids2))

	heatmap_type1 = input_dict1["heatmap_type"]

	stats1 = " "
	stats2 = " "
	stats3 = " "
	stats4 = " "

	# generates the correct heatmap1 and stats based on the value of
	# input_dict1["heatmap_type"]
	if heatmap_type1 == "moved to":
		df1, ksp = moved_to_query(gameids1, input_dict1["color"], input_dict1["piece"])
		stats1 = "Heatmap 1: Percent of " + input_dict1["piece"] + " moves to kingside: " + str(round(100*ksp, 2))
	elif heatmap_type1 == "time spent":
		df1, ai = time_spent_query(gameids1, input_dict1["color"], input_dict1["piece"])
		stats1 = "Heatmap 1: Percent of forward moves: " + str(round(100*ai, 2))
	elif heatmap_type1 == "captures":
		cp, rp, df1 = captures_query(gameids1, input_dict1["color"], input_dict1["piece"])
		if cp:
			stats1 = "Heatmap 1: Percent of moves which are captures: " + str(round(100*cp, 2))  
			stats2 = "Heatmap 1: Percent of moves which are recaptures: " + str(round(100*rp, 2))

	heatmap_type2 = input_dict2["heatmap_type"]

	# generates the correct heatmap2 and stats based on the value of
	# input_dict2["heatmap_type"]
	if heatmap_type2 == "moved to":
		df2, ksp = moved_to_query(gameids2, input_dict2["color"], input_dict2["piece"])
		stats3 = "Heatmap 2: Percent of " + input_dict2["piece"] + " moves to kingside: " + str(round(100*ksp, 2))
	elif heatmap_type2 == "time spent":
		df2, ai = time_spent_query(gameids2, input_dict2["color"], input_dict2["piece"])
		stats3 = "Heatmap 2: Percent of forward moves: " + str(round(100*ai, 2))
	elif heatmap_type2 == "captures":
		cp, rp, df2 = captures_query(gameids2, input_dict2["color"], input_dict2["piece"])
		if cp:
			stats3 = "Heatmap 2: Percent of moves which are captures: " + str(round(100*cp, 2))  
			stats4 = "Heatmap 2: Percent of moves which are recaptures: " + str(round(100*rp, 2))

	annot1 = False
	if input_dict1["annotation"] == "yes":
		annot1 = True

	annot2 = False
	if input_dict2["annotation"] == "yes":
		annot2 = True

	# calculates comparison stats and saves the heatmaps
	meandiff = compare_heatmaps(df1, df2, title1, title2, annot1, annot2)

	stats5 = " "
	stats6 = "Mean Magnitude of Normalized Differences: " + str(round(meandiff, 3))

	return stats1, stats2, stats3, stats4, stats5, stats6


def moved_to_query(gameids, color, piece):
	'''
	Given a list of gameids, a color, and a piece, queries the moves database
	to find the moves of the right color and piece in the given gameids and
	then calculates the data for a moved_to heatmap

	Inputs:
		gameids: a list of gameids (games primary key) which are used to 
			build the heatmap
		color: "white" or "black" depending on which color the heatmap is 
			representing
		piece: "All", "King", "Queen", "Rook", "Bishop", "Knight", or "Pawn"
			depending on which piece the heatmap is representing

	Returns:
		an 8x8 numpy array with the moved to heatmap data,
		a float containing the % of moves made to the kingside
	'''
	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()

	# builds the moves database query based on color and piece
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

	move_list = []
	num_moves = 0

	# executes the moves query for each gameid and then adds the moved_to data
	# to a dataframe
	for gameid in gameids:
		gameid = gameid[0]

		r = c.execute(moves_query, args + [gameid])
		moves = r.fetchall()
		move_list += moves
		num_moves += len(moves)

	df, kingside = gda.generate_moved_to_data(move_list, color, piece)
     
    # returns the completed data frame and the relevant statistics
	return df, float(kingside) / num_moves


def time_spent_query(gameids, color, piece):
	'''
	Given a list of gameids, a color, and a piece, queries the moves database
	to find the white and black moves in the given games and then calculates
	the data for a time_spent heatmap

	Inputs:
		gameids: a list of gameids (games primary key) which are used to 
			build the heatmap
		color: "white" or "black" depending on which color the heatmap is 
			representing
		piece: "All", "King", "Queen", "Rook", "Bishop", "Knight", or "Pawn"
			depending on which piece the heatmap is representing

	Returns:
		an 8x8 numpy array with the time spent data,
		a float containing the % of moves going forward
	'''
	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()

	df = np.zeros((8, 8))
	aggression = 0
	piece_moves = 0

	for gameid in gameids:
		gameid = gameid[0]

		# queries for the white and black moves for the current gameid in the
		# moves databse
		w = c.execute("SELECT move FROM moves WHERE gameid = ? AND " + \
			"color = ? ORDER BY move_num;", (gameid, "white"))
		white_moves = w.fetchall()

		b = c.execute("SELECT move FROM moves WHERE gameid = ? AND " + \
			"color = ? ORDER BY move_num;", (gameid, "black"))
		black_moves = b.fetchall()

		# generates the time_spent data for the current white and black moves
		white_dict, black_dict, white_aggression, black_aggression = \
			gda.generate_time_spent_data(white_moves, black_moves)

		# adds the relevant time spent data to df depending on the values of
		# piece and color
		if color == "white":
			if piece == "All":
				for key in white_dict:
					df = np.add(df, white_dict[key])
			else:
				df = np.add(df, white_dict[piece.lower()])
			aggression += white_aggression[piece][0]
			piece_moves += white_aggression[piece][1]
		else:
			if piece == "All":
				for key in black_dict:
					df = np.add(df, black_dict[key])
			else:
				df = np.add(df, black_dict[piece.lower()])
			aggression += black_aggression[piece][0]
			piece_moves += black_aggression[piece][1]

	ai = float(aggression) / piece_moves
	return df, ai


def captures_query(gameids, color, piece):
	'''
	Given a list of gameids, a color, and a piece, queries the moves database
	to find the moves of the right color and piece in the given gameids and
	then calculates the data for a captures heatmap

	Inputs:
		gameids: a list of gameids (games primary key) which are used to 
			build the heatmap
		color: "white" or "black" depending on which color the heatmap is 
			representing
		piece: "All", "King", "Queen", "Rook", "Bishop", "Knight", or "Pawn"
			depending on which piece the heatmap is representing

	Returns:
		an 8x8 numpy array containing the captures data,
		a float containing the % of moves that were captures,
		a float containing the % of captures that were recaptures
	'''
	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()

	# builds the appropriate moves database query based on color and piece
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

		# finds both black and white moves if piece is "All" so that capture
		# statistics can be calculated
		if piece == "All":
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

		# queries only relevant moves from the moves database if piece is
		# not all since capture statistics are not calculated
		else:
			r = c.execute(moves_query, [color] + args + [gameid])
			moves = r.fetchall()
			df = np.add(df, gda.generate_captures_heatmap(moves))


	wcp, bcp, wrp, brp = None, None, None, None

	# calculates capture statistics if piece is "All"
	if piece == "All":
		wcp, bcp, wrp, brp = gda.calculate_trade_statistics(white_move_lists,
			 black_move_lists, num_moves_white, num_moves_black)

	if color == "white":
		return wcp, wrp, df
	else:
		return bcp, brp, df



def compare_heatmaps(df1, df2, title1, title2, annot1, annot2):
	'''
	Given heatmap data and titles, calculates comparison statistics and 
	saves the original two heatmaps as well as a comparison heatmap

	Inputs:
		df1: an 8x8 numpy array representing the data for the first heatmap
		df2: an 8x8 numpy array representing the data for the second heatmap
		title1: the title for the first heatmap
		title2: the title for the second heatmap
		annot1: a Boolean indicating whether heatmap1 should contain counts
		annot2: a Boolean indicating whether heatmap2 should contain counts

	Returns:
		the mean magnitude of the normalized differences between heatmap1 and
			heatmap2
	'''
	df1 = df1.astype("float")
	df2 = df2.astype("float")

	# normalizes df1 and df2 by dividing by the sum of all counts
	df1_norm = df1 / df1.sum()
	df2_norm = df2 / df2.sum()

	diff_df = df1_norm - df2_norm

	# finds the mean of the absolute value of cell by cell differences for 
	# df1 and df2
	abs_diff = abs(diff_df)
	mean_diff = np.mean(abs_diff)

	df1 = df1.astype("int")
	df2 = df2.astype("int")


	# plots and titles heatmap1, heatmap2, and the normalized difference heatmap
	plt.figure(1)
	sns.heatmap(df1, annot=annot1, fmt="d", cmap = "Reds",
		 xticklabels = XLABELS, yticklabels = YLABELS, square=True)
	plt.title("\n".join(wrap(title1, 60)))
	sns.plt.savefig("static/heatmap1.png")
	sns.plt.clf()

	plt.figure(2)
	sns.heatmap(df2, annot=annot2, fmt="d", cmap = "Reds",
		 xticklabels = XLABELS, yticklabels = YLABELS, square=True)
	plt.title("\n".join(wrap(title2, 60)))
	sns.plt.savefig("static/heatmap2.png")
	sns.plt.clf()

	plt.figure(3)
	sns.heatmap(diff_df, annot=False, fmt="f", cmap = "coolwarm",
		 xticklabels = XLABELS, yticklabels = YLABELS, square=True)
	plt.title("Normalized Difference")
	sns.plt.savefig("static/heatmapc.png")
	plt.clf()

	return mean_diff*100



def create_plot_title(input_dict, num_games):
	'''
	Given an input_dict containing heatmap specifications and the number of
	games the heatmap represents, builds an appropriate title for a heatmap.

	Inputs:
		input_dict: A dictionary containing specifications for a heatmap such as 
			heatmap_type, a year range, ECO code, rating, player names, etc.
		num_games: an integer representing the number of games included in the
			heatmap data

	Returns:
		a string containing the title of the heatmap with the given 
			specifications

	'''
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
			title += "White rated at least " + input_dict['white_rating_min'] + ", "
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
	
	elif input_dict.get('year_min', None):
		title += "played after " + input_dict['year_min'] + " "
		
	elif input_dict.get('year_max', None):
		title += "played before " + input_dict['year_max'] + " "
		
	opening = ' '
	if input_dict.get('ECO', None):
		opening = " Opening code: " + input_dict.get('ECO', '') + " "
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
	
