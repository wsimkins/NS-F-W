#CS122: Group Project - Chess Heatmaps
#
#Names: Will Simkins, Natalie Gray, Steven Cooklev


import numpy as np
import re


STARTING_SQUARES = {"white":{"rook":[(1, 1), (8, 1)], "knight":[(2, 1), (7, 1)],
	"bishop":[(3, 1), (6, 1)], "queen":[(4, 1)], "king":[(5, 1)], 
	"pawn":[(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2)]}, 
	"black":{"rook":[(1, 8), (8, 8)], "knight":[(2, 8), (7, 8)], 
	"bishop":[(3, 8), (6, 8)], "queen":[(4, 8)], "king":[(5, 8)], 
	"pawn":[(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7)]}}

LETTER_TO_NUM = {"a":"1", "b":"2", "c":"3", "d":"4", "e":"5", "f":"6", "g":"7", "h":"8"}
PIECE_TO_LETTER = {"rook":"R", "knight":"N", "bishop":"B", "queen":"Q", "king":"K", "pawn":"P"}

def generate_moved_to_data(move_list, color, piece):
	heatmap_data = np.zeros((8,8))
	starting_squares = STARTING_SQUARES[color][piece]
	for starting_square in starting_squares:
		heatmap_data[tuple(np.subtract(starting_square, (1,1)))] += 1

	for move in move_list:
		destination_tuple = None
		if move[0].islower() and move[0] != "0":
			move = "P" + move

		if move[0] == PIECE_TO_LETTER[piece]:
			destination = re.search("[a-h][1-8]", move).group()
			destination_tuple = (int(LETTER_TO_NUM[destination[0]]), int(destination[1]))

		elif move == "0-0,":
			if piece == "rook":
				if color == "white":
					destination_tuple = (6, 1)
				else:
					destination_tuple = (6, 8)
			if piece == "king":
				if color == "white":
					destination_tuple = (7, 1)
				else:
					destination_tuple = (7, 8)

		elif move == "0-0-0,":
			if piece == "rook":
				if color == "white":
					destination_tuple = (4, 1)
				else:
					destination_tuple = (4, 8)
			if piece == "king":
				if color == "white":
					destination_tuple = (3, 1)
				else:
					destination_tuple = (3, 8)

		if destination_tuple:
			heatmap_data[tuple(np.subtract(destination_tuple, (1, 1)))] += 1

	return np.rot90(heatmap_data)


def generate_moved_to_data_all_pieces(move_list, color):
	heatmap_data = np.zeros((8, 8))
	for piece in STARTING_SQUARES[color].keys():
		for starting_square in STARTING_SQUARES[color][piece]:
			heatmap_data[tuple(np.subtract(starting_square, (1,1)))] += 1

	for move in move_list:
		destination_tuples = []
		
		if move == "0-0,":
			if color == "white":
				destination_tuples.append((6, 1))
				destination_tuples.append((7, 1))
			else:
				destination_tuples.append((6, 8))
				destination_tuples.append((7, 8))
		
		elif move == "0-0-0,":
			if color == "white":
				destination_tuples.append((3, 1))
				destination_tuples.append((4, 1))
			else:
				destination_tuples.append((3, 8))
				destination_tuples.append((4, 8))

		else:
			destination = re.search("[a-h][1-8]", move).group()
			destination_tuples.append((int(LETTER_TO_NUM[destination[0]]), int(destination[1])))

		for destination_tuple in destination_tuples:
			heatmap_data[tuple(np.subtract(destination_tuple, (1, 1)))] += 1

	return np.rot90(heatmap_data)








	


