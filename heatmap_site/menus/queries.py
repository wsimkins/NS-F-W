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


DATABASE_FILENAME = "../../mega.db"
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
		print(white_dict)

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

	sns.plt.savefig("static/heatmap.png")
	plt.clf()

	return [mean_diff, SE_diff]


World_Champs = ['steinitz,william', 'lasker,emanuel', 'capablanca,jose raul', 'alekhine,alexander',
				'euwe,max', 'botvinnik,mikhail', 'smyslov,vassily', 'tal,mihail', 'petrosian,tigran',
				'spassky,boris', 'fischer, robert james', 'karpov,anatoly', 'kasparov,garry', 
				'kramnik,vladimir', 'anand,viswanathan', 'carlsen,magnus']
Female = ['polgar,judit', 'polgar,susan', 'yifan,hou', 'stefanova,antoaneta', 'koneru,humpy', 
			'yifan,hou', 'krush,irina', 'kosteniuk,alexandra']
Positional = ['ivanchuk,vassily', 'capablanca,jose raul', 'seirawan,yasser', 'karpov,anatoly', 'nimzowitsch,aaron']
Tactical = ['tal,mihail', 'shirov,alexei', 'topalov,veselin', 'christiansen,larry mark', 'kasparov,garry', 'velimirovic,dragoljub']
Creative = ['ivanchuk,vassily', 'jobava,baadur']
Soviet = ['kotov,alexander', 'gulko,boris', 'beliavsky,alexander', 'geller,efim', 'bronstein,david', 'korchnoi,viktor']
English = ['short,nigel', 'jones,gawain', 'adams,michael', 'nunn,john', 'davies,nigel']
Chinese = ['yifan,hou', 'yue,wang', 'hao,wang', 'jun,xie', 'liren,ding', 'yangyi,yu']

Top_10 = ['carlsen,magnus', 'so,wesley', 'caruana,fabiano', 'vachier lagrave,maxime', 'nakamura,hikaru', 'anand,viswanathan', 'karjakin,sergey', 
'aronian,levon', 'giri,anish']

Before_1886 = ['morphy,paul', 'greco,gioacchino', 'lopez de segura,ruy', 
	'philidor,fracois andre dani', 'mcdonnell,alexander', 'de labourdonnais,louis charles mahe', 'staunton,howard', 'anderssen,adolf']

def player_list_query(players_list):
	'''
	Returns the gameids of the db, based on a list of players
	'''

	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()
	games_query = "SELECT gameid FROM games WHERE games.white_player IN ? OR games.black_player IN ?;"
	r = c.execute(games_query, players_list)
	gameids = r.fetchall()
	return gameids
 

def create_plot_title(input_dict):
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
			title += "when rated between " + input_dict['white_rating_min'] + " and " + input_dict['white_rating_max']
		elif input_dict.get('white_rating_min', None):
			title += "when rated at least " + input_dict.get['white_rating_min']
		elif input_dict.get('white_rating_max', None):
			title += "when rated at most " + input_dict['white_rating_max']
			
		# Check for opponent's rating
		elif input_dict.get('black_rating_min', None) and input_dict.get('black_rating_max', None):
			title += "when against opponents rated between " + input_dict['black_rating_min'] + " and " + input_dict['black_rating_max']
		elif input_dict.get('black_rating_min', None):
			title += " when against opponents rated at least " + input_dict['black_rating_min']
		elif input_dict.get('black_rating_max', None):
			title += "when against opponents rated at most " + input_dict['black_rating_max']
			
	# check if the player of interest is playing black
	elif input_dict.get('black_player', None):
		title += input_dict['black_player']
		title += " as black, "
		
		# Only add one statement about ratings queried
		# Priority is given to the white_player's rating information
		if input_dict.get('black_rating_min', None) and input_dict.get('black_rating_max', None):
			title += "when rated between " + input_dict['black_rating_min'] + " and " + input_dict['black_rating_max']
		elif input_dict.get('black_rating_min', None):
			title += "when rated at least " + input_dict['black_rating_min']
		elif input_dict.get('black_rating_max', None):
			title += "when rated at most " + input_dict['black_rating_max']
			
		# Check for opponent's rating
		elif input_dict.get('white_rating_min', None) and input_dict.get('white_rating_max', None):
			title += "when against opponents rated between " + input_dict['white_rating_min'] + " and " + input_dict['white_rating_max']
		elif input_dict.get('white_rating_min', None):
			title += " when against opponents rated at least " + input_dict['white_rating_min']
		elif input_dict.get('white_rating_max', None):
			title += "when against opponents rated at most " + input_dict['white_rating_max']
			
		
	if input_dict.get('year_min', None) and input_dict.get('year_max', None):
		title += "played between " + input_dict['year_min'] + " and " + input_dict['year_max']
	
	if input_dict.get('year_min', None):
		title += "played after " + input_dict['year_min']
		
	if input_dict.get('year_max', None):
		title += "played before " + input_dict['year_max']
		
	opening = ' '
	if input_dict.get('ECO', None):
		opening = " Opening code: " + input_dict.get('ECO', '')
	title += opening
	
	if input_dict.get('num_moves_min', None) and input_dict.get('num_moves_max', None):
		title += "in games lasting between " + input_dict['num_moves_min'] + 'and' + input_dict['num_moves_max'] + " moves."
	
	if input_dict.get('num_moves_min', None):
		title += "in games lasting at least " + input_dict['num_moves_min']
		
	if input_dict.get('num_moves_max', None):
		title += "in games lasting at most " + input_dict['num_moves_max']
		
	if input_dict.get('result', None) == '1-0':
		title += 'White wins'
		
	if input_dict.get('result', None) == '0-1':
		title += 'Black wins'
	
	if input_dict.get('result', None) == '1/2-1/2':
		title += 'games drawn'
	
	# Make the title camelcase
	title = title.title()
	
	return title
	
