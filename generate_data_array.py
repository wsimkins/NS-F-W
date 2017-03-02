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
	"bishop":[(3, 8), (6, 8)], "queen":[(4,8)], "king":[(5, 8)], 
	"pawn":[(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7)],
	"all":[(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7),
	 (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8)]}}

LETTER_TO_NUM = {"a":1, "b":2, "c":3, "d":4, "e":5, "f":6, "g":7, "h":8}
PIECE_TO_LETTER = {"rook":"R", "knight":"N", "bishop":"B", "queen":"Q", "king":"K", "pawn":"P"}
KNIGHT_DIFFS = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]



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




def generate_time_spent_data(white_move_list, black_move_list):
	STARTING_SQUAREZ = {"white":{"rook":[(1, 1), (8, 1)], "knight":[(2, 1), (7, 1)],
	"bishop":[(3, 1), (6, 1)], "queen":[(4, 1)], "king":[(5, 1)], 
	"pawn":[(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2)],
	"all":[(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1),
	 (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2)]}, 
	"black":{"rook":[(1, 8), (8, 8)], "knight":[(2, 8), (7, 8)], 
	"bishop":[(3, 8), (6, 8)], "queen":[(4,8)], "king":[(5, 8)], 
	"pawn":[(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7)],
	"all":[(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7),
	 (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8)]}}


	white_data = {"rook":np.zeros((8,8)), "knight":np.zeros((8,8)), "bishop": np.zeros((8,8)), "queen":np.zeros((8,8)), "king":np.zeros((8,8)), "pawn":np.zeros((8,8))}
	black_data = {"rook":np.zeros((8,8)), "knight":np.zeros((8,8)), "bishop": np.zeros((8,8)), "queen":np.zeros((8,8)), "king":np.zeros((8,8)), "pawn":np.zeros((8,8))}

	cur_board = np.array([["BR", "BN", "BB", "BQ", "BK", "BB", "BN", "BR"],
       ["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"],
       ["e ", "e ", "e ", "e ", "e ", "e ", "e ", "e "],
       ["e ", "e ", "e ", "e ", "e ", "e ", "e ", "e "],
       ["e ", "e ", "e ", "e ", "e ", "e ", "e ", "e "],
       ["e ", "e ", "e ", "e ", "e ", "e ", "e ", "e "],
       ["WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP"],
       ["WR", "WN", "WB", "WQ", "WK", "WB", "WN", "WR"]])

	cur_locs = STARTING_SQUAREZ


	for piece in white_data.keys():
		white_ss = STARTING_SQUAREZ["white"][piece]
		black_ss = STARTING_SQUAREZ["black"][piece]
		for i in range(len(white_ss)):
			white_data[piece][8 - white_ss[i][1]][white_ss[i][0] - 1] = 1
			black_data[piece][8 - black_ss[i][1]][black_ss[i][0] - 1] = 1

	for move_num in range(len(white_move_list)):
		en_passant = False
		white_move = white_move_list[move_num][0]
		black_move = None
		if move_num < len(black_move_list):
			black_move = black_move_list[move_num][0]

		if white_move[0] == "K":
			destination = re.search("[a-h][1-8]", white_move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			prev_loc = cur_locs["white"]["king"][0]
			cur_locs["white"]["king"][0] = destination_tuple
			cur_board[convert_tup(prev_loc)] = "e "
			cur_board[convert_tup(destination_tuple)] = "WK"

		elif white_move[0] == "Q":
			destination = re.search("[a-h][1-8]", white_move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			prev_loc = cur_locs["white"]["queen"][0]
			cur_locs["white"]["queen"][0] = destination_tuple
			cur_board[convert_tup(prev_loc)] = "e " 
			cur_board[convert_tup(destination_tuple)] = "WQ"

		elif white_move[0] == "B":
			destination = re.search("[a-h][1-8]", white_move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			
			bishop_locs = cur_locs["white"]["bishop"]
			if len(bishop_locs) == 1:
				prev_loc = bishop_locs[0]
				cur_locs["white"]["bishop"] = []
			else:
				for i in range(len(bishop_locs)):
					loc = bishop_locs[i]
					diff = tuple(np.subtract(destination_tuple, loc))
					if diff[1] != 0:
						div = diff[0] / diff[1]
						if div == 1 or div == -1:
							prev_loc = loc
							del bishop_locs[i]
							break

			cur_locs["white"]["bishop"].append(destination_tuple)
			cur_board[convert_tup(prev_loc)] = "e "
			cur_board[convert_tup(destination_tuple)] = "WB"

		elif white_move[0] == "N":
			destination = re.search("[a-h][1-8]", white_move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			
			knight_locs = cur_locs["white"]["knight"]
			disambig_let = re.search("[a-h]{2}", white_move)
			disambig_num = re.search("[1-8][a-h]", white_move)
			if len(knight_locs) == 1:
				prev_loc = knight_locs[0]
				cur_locs["white"]["knight"] = [] 
			elif disambig_let:
				letter = disambig_let.group()[0]
				file_num = LETTER_TO_NUM[letter]
				for i in range(len(knight_locs)):
					loc = knight_locs[i]
					if loc[0] == file_num:
						prev_loc = loc
						del knight_locs[i]
						break
			elif disambig_num:
				rank_num = int(disambig_num.group()[1])
				for i in range(len(knight_locs)):
					loc = knight_locs[i]
					if loc[1] == rank_num:
						prev_loc = loc
						del knight_locs[i]
						break
			else:
				for i in range(len(knight_locs)):
					loc = knight_locs[i]
					diff = tuple(np.subtract(destination_tuple, loc))
					if diff in KNIGHT_DIFFS:
						prev_loc = loc
						del knight_locs[i]
						break

			cur_locs["white"]["knight"].append(destination_tuple)
			cur_board[convert_tup(prev_loc)] = "e "
			cur_board[convert_tup(destination_tuple)] = "WN"

		elif white_move[0] == "R":
			destination = re.search("[a-h][1-8]", white_move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			
			rook_locs = cur_locs["white"]["rook"]
			disambig_let = re.search("[a-h]{2}", white_move)
			disambig_num = re.search("[1-8][a-h]", white_move)
			if len(rook_locs) == 1:
				prev_loc = rook_locs[0]
				cur_locs["white"]["rook"] = [] 
			elif disambig_let:
				letter = disambig_let.group()[0]
				file_num = LETTER_TO_NUM[letter]
				for i in range(len(rook_locs)):
					loc = rook_locs[i]
					if loc[0] == file_num:
						prev_loc = loc
						del rook_locs[i]
						break
			elif disambig_num:
				rank_num = int(disambig_num.group()[1])
				for i in range(len(rook_locs)):
					loc = rook_locs[i]
					if loc[1] == rank_num:
						prev_loc = loc
						del rook_locs[i]
						break
			else:
				for i in range(len(rook_locs)):
					loc = rook_locs[i]
					if loc[0] == destination_tuple[0]:
						blocked = False
						for j in range(min(loc[1], destination_tuple[1]) + 1, max(loc[1], destination_tuple[1])):
							print(j)
							if cur_board[8 - loc[0]][j - 1] != "e ":
								blocked = True
								break
						if not blocked:
							prev_loc = loc
							del rook_locs[i]
							break
					if loc[1] == destination_tuple[1]:
						blocked = False
						for j in range(min(loc[0], destination_tuple[0]), max(loc[0], destination_tuple[0])):
							if cur_board[8 - loc[1]][j - 1] != "e ":
								blocked = True
								break
						if not blocked:
							prev_loc = loc
							del rook_locs[i]
							break
			cur_locs["white"]["rook"].append(destination_tuple)
			cur_board[convert_tup(prev_loc)] = "e "
			cur_board[convert_tup(destination_tuple)] = "WR"

		elif white_move[0].islower():
			destination = re.search("[a-h][1-8]", white_move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			pawn_locs = cur_locs["white"]["pawn"]
			
			if "x" not in white_move:
				for i in range(len(pawn_locs)):
					loc = pawn_locs[i]
					if loc[0] == destination_tuple[0] and loc[1] == destination_tuple[1] - 1:
						prev_loc = loc
						del pawn_locs[i]
						break
				for i in range(len(pawn_locs)):
					loc = pawn_locs[i]
					if loc[0] == destination_tuple[0] and loc[1] == 2 and destination_tuple[1] == 4:
						prev_loc = loc
						del pawn_locs[i]
						break
			else:
				letter = white_move[0]
				file_num = LETTER_TO_NUM[letter]
				for i in range(len(pawn_locs)):
					loc = pawn_locs[i]
					if loc[0] == file_num and loc[1] == destination_tuple[1] - 1:
						prev_loc = loc
						del pawn_locs[i]
						break
				if cur_board[convert_tup(destination_tuple)] == "e ":
					en_passant = True
					captured_square = convert_tup((destination_tuple[0], destination_tuple[1] - 1))
					cur_board[captured_square] = "e "
					cur_locs["black"]["pawn"].remove(captured_square)


			if "=" not in white_move:
				cur_locs["white"]["pawn"].append(destination_tuple)
				cur_board[convert_tup(prev_loc)] = "e "
				cur_board[convert_tup(destination_tuple)] = "WP"

			else:
				cur_board[convert_tup(prev_loc)] = "e "
				if "Q" in white_move:
					cur_locs["white"]["queen"].append(destination_tuple)
					cur_board[convert_tup(destination_tuple)] = "WQ"
				elif "R" in white_move:
					cur_locs["white"]["rook"].append(destination_tuple)
					cur_board[convert_tup(destination_tuple)] = "WR"
				elif "B" in white_move:
					cur_locs["white"]["bishop"].append(destination_tuple)
					cur_board[convert_tup(destination_tuple)] = "WB"
				elif "N" in white_move:
					cur_locs["white"]["knight"].append(destination_tuple)
					cur_board[convert_tup(destination_tuple)] = "WN"


		if white_move == "0-0":
			cur_locs["white"]["rook"].remove((8, 1))
			cur_locs["white"]["rook"].append((6, 1))
			cur_locs["white"]["king"] = [(7,1)]
			cur_board[7][7] = "e "
			cur_board[7][4] = "e "
			cur_board[7][6] = "WK"
			cur_board[7][5] = "WR"

		if white_move == "0-0-0":
			cur_locs["white"]["rook"].remove((1, 1))
			cur_locs["white"]["rook"].append((4, 1))
			cur_locs["white"]["king"] = [(3,1)]
			cur_board[7][0] = "e "
			cur_board[7][4] = "e "
			cur_board[7][2] = "WK"
			cur_board[7][3] = "WR"



		if "x" in white_move and not en_passant:
			for piece in cur_locs["black"].keys():
				for i in range(len(cur_locs["black"][piece])):
					loc = cur_locs["black"][piece][i]
					if loc == destination_tuple:
						del cur_locs["black"][piece][i]
						break


		en_passant = False

		if black_move:
			if black_move[0] == "K":
				destination = re.search("[a-h][1-8]", black_move).group()
				destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
				prev_loc = cur_locs["black"]["king"][0]
				cur_locs["black"]["king"][0] = destination_tuple
				cur_board[convert_tup(prev_loc)] = "e "
				cur_board[convert_tup(destination_tuple)] = "BK"

			elif black_move[0] == "Q":
				destination = re.search("[a-h][1-8]", black_move).group()
				destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
				prev_loc = cur_locs["black"]["queen"][0]
				cur_locs["black"]["queen"][0] = destination_tuple
				cur_board[convert_tup(prev_loc)] = "e " 
				cur_board[convert_tup(destination_tuple)] = "BQ"

			elif black_move[0] == "B":
				destination = re.search("[a-h][1-8]", black_move).group()
				destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
				
				bishop_locs = cur_locs["black"]["bishop"]
				if len(bishop_locs) == 1:
					prev_loc = bishop_locs[0]
					cur_locs["black"]["bishop"] = []
				else:
					for i in range(len(bishop_locs)):
						loc = bishop_locs[i]
						diff = tuple(np.subtract(destination_tuple, loc))
						div = diff[0] / diff[1]
						if diff[1] != 0:
							if div == 1 or div == -1:
								prev_loc = loc
								del bishop_locs[i]
								break

				cur_locs["black"]["bishop"].append(destination_tuple)
				cur_board[convert_tup(prev_loc)] = "e "
				cur_board[convert_tup(destination_tuple)] = "BB"

			elif black_move[0] == "N":
				destination = re.search("[a-h][1-8]", black_move).group()
				destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
				
				knight_locs = cur_locs["black"]["knight"]
				disambig_let = re.search("[a-h]{2}", black_move)
				disambig_num = re.search("[1-8][a-h]", black_move)
				if len(knight_locs) == 1:
					prev_loc = knight_locs[0]
					cur_locs["black"]["knight"] = [] 
				elif disambig_let:
					letter = disambig_let.group()[0]
					file_num = LETTER_TO_NUM[letter]
					for i in range(len(knight_locs)):
						loc = knight_locs[i]
						if loc[0] == file_num:
							prev_loc = loc
							del knight_locs[i]
							break
				elif disambig_num:
					rank_num = int(disambig_num.group()[1])
					for i in range(len(knight_locs)):
						loc = knight_locs[i]
						if loc[1] == rank_num:
							prev_loc = loc
							del knight_locs[i]
							break
				else:
					for i in range(len(knight_locs)):
						loc = knight_locs[i]
						diff = tuple(np.subtract(destination_tuple, loc))
						if diff in KNIGHT_DIFFS:
							prev_loc = loc
							del knight_locs[i]
							break

				cur_locs["black"]["knight"].append(destination_tuple)
				cur_board[convert_tup(prev_loc)] = "e "
				cur_board[convert_tup(destination_tuple)] = "BN"

			elif black_move[0] == "R":
				destination = re.search("[a-h][1-8]", black_move).group()
				destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
				
				rook_locs = cur_locs["black"]["rook"]
				disambig_let = re.search("[a-h]{2}", black_move)
				disambig_num = re.search("[1-8][a-h]", black_move)
				if len(rook_locs) == 1:
					prev_loc = rook_locs[0]
					cur_locs["black"]["rook"] = [] 
				elif disambig_let:
					letter = disambig_let.group()[0]
					file_num = LETTER_TO_NUM[letter]
					for i in range(len(rook_locs)):
						loc = rook_locs[i]
						if loc[0] == file_num:
							prev_loc = loc
							del rook_locs[i]
							break
				elif disambig_num:
					rank_num = int(disambig_num.group()[1])
					for i in range(len(rook_locs)):
						loc = rook_locs[i]
						if loc[1] == rank_num:
							prev_loc = loc
							del rook_locs[i]
							break
				else:
					for i in range(len(rook_locs)):
						loc = rook_locs[i]
						if loc[0] == destination_tuple[0]:
							blocked = False
							for j in range(min(loc[1], destination_tuple[1]), max(loc[1], destination_tuple[1])):
								if cur_board[8 - loc[0]][j - 1] != "e ":
									blocked = True
									break
							if not blocked:
								prev_loc = loc
								del rook_locs[i]
								break
						elif loc[1] == destination_tuple[1]:
							blocked = False
							for j in range(min(loc[0], destination_tuple[0]), max(loc[0], destination_tuple[0])):
								if cur_board[8 - loc[1]][j - 1] != "e ":
									blocked = True
									break
							if not blocked:
								prev_loc = loc
								del rook_locs[i]
								break
								
				cur_locs["black"]["rook"].append(destination_tuple)
				cur_board[convert_tup(prev_loc)] = "e "
				cur_board[convert_tup(destination_tuple)] = "BR"

			elif black_move[0].islower():
				destination = re.search("[a-h][1-8]", black_move).group()
				destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
				pawn_locs = cur_locs["black"]["pawn"]
				
				if "x" not in black_move:
					for i in range(len(pawn_locs)):
						loc = pawn_locs[i]
						if loc[0] == destination_tuple[0] and loc[1] == destination_tuple[1] + 1:
							prev_loc = loc
							del pawn_locs[i]
							break
					for i in range(len(pawn_locs)):
						loc = pawn_locs[i]
						if loc[0] == destination_tuple[0] and loc[1] == 7 and destination_tuple[1] == 5:
							prev_loc = loc
							del pawn_locs[i]
							break
				else:
					letter = black_move[0]
					file_num = LETTER_TO_NUM[letter]
					for i in range(len(pawn_locs)):
						loc = pawn_locs[i]
						if loc[0] == file_num and loc[1] == destination_tuple[1] + 1:
							prev_loc = loc
							del pawn_locs[i]
							break
					if cur_board[convert_tup(destination_tuple)] == "e ":
						en_passant = True
						captured_square = convert_tup((destination_tuple[0], destination_tuple[1] + 1))
						cur_board[captured_square] = "e "
						cur_locs["white"]["pawn"].remove(captured_square)

				if "=" not in black_move:
					cur_locs["black"]["pawn"].append(destination_tuple)
					cur_board[convert_tup(prev_loc)] = "e "
					cur_board[convert_tup(destination_tuple)] = "BP"

				else:
					cur_board[convert_tup(prev_loc)] = "e "
					if "Q" in black_move:
						cur_locs["black"]["queen"].append(destination_tuple)
						cur_board[convert_tup(destination_tuple)] = "BQ"
					elif "R" in black_move:
						cur_locs["black"]["rook"].append(destination_tuple)
						cur_board[convert_tup(destination_tuple)] = "BR"
					elif "B" in black_move:
						cur_locs["black"]["bishop"].append(destination_tuple)
						cur_board[convert_tup(destination_tuple)] = "BB"
					elif "N" in black_move:
						cur_locs["black"]["knight"].append(destination_tuple)
						cur_board[convert_tup(destination_tuple)] = "BN"


			if black_move == "0-0":
				cur_locs["black"]["rook"].remove((8, 8))
				cur_locs["black"]["rook"].append((6, 8))
				cur_locs["black"]["king"] = [(7, 8)]
				cur_board[0][7] = "e "
				cur_board[0][4] = "e "
				cur_board[0][6] = "BK"
				cur_board[0][5] = "BR"

			if black_move == "0-0-0":
				cur_locs["black"]["rook"].remove((1, 8))
				cur_locs["black"]["rook"].append((4, 8))
				cur_locs["black"]["king"] = [(3, 8)]
				cur_board[0][0] = "e "
				cur_board[0][4] = "e "
				cur_board[0][2] = "BK"
				cur_board[0][3] = "BR"

			if "x" in black_move and not en_passant:
				for piece in cur_locs["white"].keys():
					for i in range(len(cur_locs["white"][piece])):
						loc = cur_locs["white"][piece][i]
						if loc == destination_tuple:
							del cur_locs["white"][piece][i]
							break

		for piece in cur_locs["white"].keys():
			for loc in cur_locs["white"][piece]:
				if piece != "all":
					white_data[piece][convert_tup(loc)] += 1
			for loc in cur_locs["black"][piece]:
				if piece != "all":
					black_data[piece][convert_tup(loc)] += 1

	for piece in white_data.keys():
		white_data[piece] = white_data[piece].astype("int")
		black_data[piece] = black_data[piece].astype("int")

	return white_data, black_data
 

def generate_captures_heatmap(move_list):
	heatmap_data = np.zeros((8,8))
	for move in move_list:
		move = move[0]
		if "x" in move:
			destination = re.search("[a-h][1-8]", move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			heatmap_data[convert_tup(destination_tuple)] += 1
	return heatmap_data


def calculate_trade_statistics(white_move_list, black_move_list):
	white_captures = 0
	black_captures = 0
	white_recaptures = 0
	black_recaptures = 0

	for move_num in range(len(white_move_list)):
		white_move = white_move_list[move_num][0]
		if "x" in white_move:
			white_captures += 1
			print("wc", white_captures)
			black_move = black_move_list[move_num - 1][0]
			if "x" in black_move:
				white_capture_loc = re.search("[a-h][1-8]", white_move).group()
				black_capture_loc = re.search("[a-h][1-8]", black_move).group()
				if white_capture_loc == black_capture_loc:
					white_recaptures += 1
					print("wr", white_recaptures)

	for move_num in range(len(black_move_list)):
		black_move = black_move_list[move_num][0]
		if "x" in black_move:
			black_captures += 1
			print("bc", black_captures)
			white_move = white_move_list[move_num][0]
			if "x" in white_move:
				black_capture_loc = re.search("[a-h][1-8]", black_move).group()
				white_capture_loc = re.search("[a-h][1-8]", white_move).group()
				if white_capture_loc == black_capture_loc:
					black_recaptures += 1
					print("br", black_recaptures)

	white_capture_percent = white_captures/len(white_move_list)
	black_capture_percent = black_captures/len(black_move_list)
	white_recapture_percent = white_recaptures/white_captures
	black_recapture_percent = black_recaptures/black_captures

	return white_capture_percent, black_capture_percent, white_recapture_percent, black_recapture_percent



def convert_tup(tup):
	return (8 - tup[1], tup[0] - 1)









	


