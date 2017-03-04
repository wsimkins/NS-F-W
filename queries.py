#Building Queries

import math
import pandas as pd
import numpy as np
from scipy import stats
import random
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3 as sql

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

def generate_query(input_dict):
	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()

	games_query = "SELECT gameid FROM games WHERE "
	args = []
	keys = input_dict.keys()

	for key in keys:
		if key == "color" or key == "piece" or key == "heatmap_type":
			continue
		elif "max" in key:
			games_query += key[:-4] + " <= ? AND "
		elif "min" in key:
			games_query += key[:-4] + " >= ? AND "
		else:
			games_query += key + " = ? AND "
		args.append(input_dict[key])

	if "AND" in games_query:
		games_query = games_query[:-5] + ";"
	else:
		games_query = "SELECT moveid FROM games;"

	r = c.execute(games_query, args)
	gameids = r.fetchall()

	heatmap_type = input_dict["heatmap_type"]

	if heatmap_type == "moved to":
		return moved_to_query(gameids, input_dict["color"], input_dict["piece"])
	elif heatmap_type == "time spent":
		return time_spent_query(gameids, input_dict["color"], input_dict["piece"])
	elif heatmap_type == "captures":
		return captures_query(gameids, input_dict["color"], input_dict["piece"])



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
	for gameid in gameids:
		gameid = gameid[0]

		r = c.execute(moves_query, args + [gameid])
		moves = r.fetchall()
		df = np.add(df, gda.generate_moved_to_data(moves, color, piece))

	plt.figure(1)

	plt.subplot(111)
	sns.heatmap(df, annot=False, fmt="d", cmap = "Reds", xticklabels = XLABELS, yticklabels = YLABELS)
	plt.title("Moved To " + color + " " + piece)

	sns.plt.savefig("heatmap.png")
	plt.clf()
     
	return "heatmap.png"



def time_spent_query(gameids, color, piece):
	conn = sql.connect(DATABASE_FILENAME)
	c = conn.cursor()

	df = np.zeros((8, 8))

	for gameid in gameids:
		gameid = gameid[0]

		w = c.execute("SELECT move FROM moves WHERE gameid = ? AND color = ? ORDER BY move_num;", (gameid, "white"))
		white_moves = w.fetchall()[::2]

		## GET RID OF ::2 ONCE DATABASE HAS NO DUPLICATES

		b = c.execute("SELECT move FROM moves WHERE gameid = ? AND color = ? ORDER BY move_num;", (gameid, "black"))
		black_moves = b.fetchall()[::2]

		white_dict, black_dict = gda.generate_time_spent_data(white_moves, black_moves)

		if color == "white":
			df = np.add(df, white_dict[piece.lower()])
		else:
			df = np.add(df, black_dict[piece.lower()])

	plt.figure(1)

	plt.subplot(111)
	sns.heatmap(df, annot=False, fmt="d", cmap = "Reds", xticklabels = XLABELS, yticklabels = YLABELS)
	plt.title("Time Spent " + color + " " + piece)

	sns.plt.savefig("heatmap.png")
	plt.clf()
     
	return "heatmap.png"
       

def captures_query(gameids, color, piece):
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
	for gameid in gameids:
		gameid = gameid[0]

		r = c.execute(moves_query, args + [gameid])
		moves = r.fetchall()
		df = np.add(df, gda.generate_captures_heatmap(moves))

	plt.figure(1)

	plt.subplot(111)
	sns.heatmap(df, annot=False, fmt="d", cmap = "Reds", xticklabels = XLABELS, yticklabels = YLABELS)
	plt.title("Captures " + color + " " + piece)

	sns.plt.savefig("heatmap.png")
	plt.clf()

	return "heatmap.png"