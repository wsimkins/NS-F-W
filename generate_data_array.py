#CS122: Group Project - Chess Heatmaps
#
#Names: Will Simkins, Natalie Gray, Steven Cooklev


import numpy as np
import re


STARTING_SQUARES = {"white":{"rook":[(1, 1), (8, 1)], "knight":[(2, 1), (7, 1)],
	"bishop":[(3, 1), (6, 1)], "queen":[(4, 1)], "king":[(5, 1)], 
	"pawn":[(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2)],
	"all":[(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1),
	 (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2)]}, 
	"black":{"rook":[(1, 8), (8, 8)], "knight":[(2, 8), (7, 8)], 
	"bishop":[(3, 8), (6, 8)], "queen":[(4, 8)], "king":[(5, 8)], 
	"pawn":[(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7)],
	"all":[(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7),
	 (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8)]}}

LETTER_TO_NUM = {"a":1, "b":2, "c":3, "d":4, "e":5, "f":6, "g":7, "h":8}
PIECE_TO_LETTER = {"rook":"R", "knight":"N", "bishop":"B", "queen":"Q", "king":"K", "pawn":"P"}

def generate_moved_to_data(move_list, color, piece, num_games):
	heatmap_data = np.zeros((8,8))
	starting_squares = STARTING_SQUARES[color][piece]
	for starting_square in starting_squares:
		heatmap_data[tuple(np.subtract(starting_square, (1,1)))] += num_games

	for move_tup in move_list:
		move = move_tup[0]
		destination_tuples = None

		destination = re.search("[a-h][1-8]", move)
		if destination:
			destination = destination.group()
			destination_tuples = [(LETTER_TO_NUM[destination[0]], int(destination[1]))]

		elif move == "0-0":
			if piece == "rook":
				if color == "white":
					destination_tuples = [(6, 1)]
				else:
					destination_tuples = [(6, 8)]
			if piece == "king":
				if color == "white":
					destination_tuples = [(7, 1)]
				else:
					destination_tuples = [(7, 8)]
			if piece == "all":
				if color == "white":
					destination_tuples = [(6, 1), (7, 1)]
				else:
					destination_tuples = [(6, 8), (7, 8)]

		elif move == "0-0-0":
			if piece == "rook":
				if color == "white":
					destination_tuples = [(4, 1)]
				else:
					destination_tuples = [(4, 8)]
			if piece == "king":
				if color == "white":
					destination_tuples = [(3, 1)]
				else:
					destination_tuples = [(3, 8)]
			if piece == "all":
				if color == "white":
					destination_tuples = [(3, 1), (4, 1)]
				else:
					destination_tuples = [(3, 8), (4, 8)]

		for destination_tuple in destination_tuples:
			heatmap_data[tuple(np.subtract(destination_tuple, (1, 1)))] += 1

	return np.rot90(heatmap_data).astype("int")









	


