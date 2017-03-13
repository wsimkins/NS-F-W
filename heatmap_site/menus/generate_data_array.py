#CS122: Group Project - Chess Heatmaps
# for generating heatmaps
#Names: Will Simkins, Natalie Gray, Steven Cooklev


import numpy as np
import re


LETTER_TO_NUM = {"a":1, "b":2, "c":3, "d":4, "e":5, "f":6, "g":7, "h":8}
PIECE_TO_LETTER = {"rook":"R", "knight":"N", "bishop":"B", "queen":"Q", "king":"K", "pawn":"P"}
KNIGHT_DIFFS = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]



def generate_moved_to_data(move_list, color, piece):
	'''
	Given a list of moves, the color which made those moves, and the piece 
	(or all) that made those moves, generates a numpy array
	containing counts for each square on a chess board representing the number
	of the times that square was moved to in move_list as well as the % of
	moves which were made to the kingside

	Inputs:
		move_list: a list of chess moves
		color: "white" or "black" depending on which color the moves in 
			move_list were made by
		piece: a string representing the piece that the moves in move_list
			were made by (could be "all")

	Returns:
		an 8x8 numpy array containing counts representing the number of times
			each square was moved to in move_list
		a float represnting the % of moves in move_list which were made to the 
			kingside
	'''
	heatmap_data = np.zeros((8,8))
	kingside = 0

	for move_tup in move_list:
		move = move_tup[0]
		destination_tuples = []

		# uses regex to search each move for a destination such as "e5" or "a1"
		destination = re.search("[a-h][1-8]", move)
		if destination:
			destination = destination.group()
			destination_tuples = [(LETTER_TO_NUM[destination[0]], int(destination[1]))]

			# increments kingside by 1 if the destination is on the kingside
			if destination_tuples[0][0] >= 5:
				kingside += 1

		# handles kingside and queenside castling
		elif move == "0-0":
			kingside += 1
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

	return np.rot90(heatmap_data).astype("int"), kingside




def generate_time_spent_data(white_move_list, black_move_list):
	'''
	Given a the white and black moves from a single game of chess, recreates
	the position reached after each move and then increments the position of 
	each piece by 1, so that the total time spent on each square by each piece
	during the game is represented in a numpy array.

	Inputs:
		white_move_list: a list of white moves
		black_move_list: the corresponding list of black 
			moves (from the same game)

	Returns:
		a dictionary whose keys are white pieces and whose values are 8x8 numpy
			arrays where the count in each square represents the total number
			of turns spent on that square by the corresponding piece
		the corresponding dictionary for black pieces
		the % of total white moves that were forward
		the % of total black moves that were forward
	'''
	# initializes the locations of all pieces based off of the starting positions
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

	 # initializes the white and balck return dictionaries
	white_data = {"rook":np.zeros((8,8)), "knight":np.zeros((8,8)), "bishop": np.zeros((8,8)), "queen":np.zeros((8,8)), "king":np.zeros((8,8)), "pawn":np.zeros((8,8))}
	black_data = {"rook":np.zeros((8,8)), "knight":np.zeros((8,8)), "bishop": np.zeros((8,8)), "queen":np.zeros((8,8)), "king":np.zeros((8,8)), "pawn":np.zeros((8,8))}

	# an array representing the current board state of the game
	cur_board = np.array([["BR", "BN", "BB", "BQ", "BK", "BB", "BN", "BR"],
       ["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"],
       ["e ", "e ", "e ", "e ", "e ", "e ", "e ", "e "],
       ["e ", "e ", "e ", "e ", "e ", "e ", "e ", "e "],
       ["e ", "e ", "e ", "e ", "e ", "e ", "e ", "e "],
       ["e ", "e ", "e ", "e ", "e ", "e ", "e ", "e "],
       ["WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP"],
       ["WR", "WN", "WB", "WQ", "WK", "WB", "WN", "WR"]])

	cur_locs = STARTING_SQUARES

	# increments the starting square of each piece by 1 at the beginning of the game
	for piece in white_data.keys():
		white_ss = STARTING_SQUARES["white"][piece]
		black_ss = STARTING_SQUARES["black"][piece]
		for i in range(len(white_ss)):
			white_data[piece][8 - white_ss[i][1]][white_ss[i][0] - 1] = 1
			black_data[piece][8 - black_ss[i][1]][black_ss[i][0] - 1] = 1

	# initializes a dictionary containing two values for each piece:
	# the total number of forward moves and the total number of moves
	wl = len(white_move_list)
	bl = len(black_move_list)
	white_aggression = {"Rook":[0,0], "Knight":[0,0], "Bishop":[0,0], "Queen":[0,0], "King":[0,0], "Pawn":[0,0], "All":[0,wl]}
	black_aggression = {"Rook":[0,0], "Knight":[0,0], "Bishop":[0,0], "Queen":[0,0], "King":[0,0], "Pawn":[0,0], "All":[0,bl]}

	# increments through each pair of white moves and black moves in the game
	for move_num in range(len(white_move_list)):
		en_passant = False
		white_move = white_move_list[move_num][0]
		black_move = None
		if move_num < len(black_move_list):
			black_move = black_move_list[move_num][0]

		# handles white King moves
		if white_move[0] == "K":
			destination = re.search("[a-h][1-8]", white_move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			prev_loc = cur_locs["white"]["king"][0]
			cur_locs["white"]["king"][0] = destination_tuple
			cur_board[convert_tup(prev_loc)] = "e "
			cur_board[convert_tup(destination_tuple)] = "WK"
			
			if determine_aggression(prev_loc, destination_tuple, "white"):
				white_aggression["King"][0] += 1
				white_aggression["All"][0] += 1
			white_aggression["King"][1] += 1

		# handles white Queen moves
		elif white_move[0] == "Q":
			destination = re.search("[a-h][1-8]", white_move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			prev_loc = cur_locs["white"]["queen"][0]
			cur_locs["white"]["queen"][0] = destination_tuple
			cur_board[convert_tup(prev_loc)] = "e " 
			cur_board[convert_tup(destination_tuple)] = "WQ"

			if determine_aggression(prev_loc, destination_tuple, "white"):
				white_aggression["Queen"][0] += 1
				white_aggression["All"][0] += 1
			white_aggression["Queen"][1] += 1

		# handles white Bishop moves
		elif white_move[0] == "B":
			destination = re.search("[a-h][1-8]", white_move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			
			bishop_locs = cur_locs["white"]["bishop"]

			if len(bishop_locs) == 1:
				prev_loc = bishop_locs[0]
				cur_locs["white"]["bishop"] = []
			# if there are two bishops, determines which one could have made
			# the current move
			else:
				for i in range(len(bishop_locs)):
					loc = bishop_locs[i]
					diff = tuple(np.subtract(destination_tuple, loc))
					if diff[1] != 0:
						div = float(diff[0]) / diff[1]
						if div == 1 or div == -1:
							prev_loc = loc
							del bishop_locs[i]
							break


			cur_locs["white"]["bishop"].append(destination_tuple)
			cur_board[convert_tup(prev_loc)] = "e "
			cur_board[convert_tup(destination_tuple)] = "WB"

			if determine_aggression(prev_loc, destination_tuple, "white"):
				white_aggression["Bishop"][0] += 1
				white_aggression["All"][0] += 1
			white_aggression["Bishop"][1] += 1

		# handles white Knight moves
		elif white_move[0] == "N":
			destination = re.search("[a-h][1-8]", white_move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			
			knight_locs = cur_locs["white"]["knight"]
			disambig_let = re.search("[a-h]{2}", white_move)
			disambig_num = re.search("[1-8][a-h]", white_move)
			if len(knight_locs) == 1:
				prev_loc = knight_locs[0]
				cur_locs["white"]["knight"] = [] 
			# if there are two Knights, determines which one could have made
			# the current move
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
				rank_num = int(disambig_num.group()[0])
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
			if determine_aggression(prev_loc, destination_tuple, "white"):
				white_aggression["Knight"][0] += 1
				white_aggression["All"][0] += 1
			white_aggression["Knight"][1] += 1

		# handles white Rook moves
		elif white_move[0] == "R":
			destination = re.search("[a-h][1-8]", white_move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			
			rook_locs = cur_locs["white"]["rook"]
			disambig_let = re.search("[a-h]{2}", white_move)
			disambig_num = re.search("[1-8][a-h]", white_move)
			if len(rook_locs) == 1:
				prev_loc = rook_locs[0]
				cur_locs["white"]["rook"] = [] 
			# if there are two Rooks, determines which one could have made the
			# current move
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
				rank_num = int(LETTER_TO_NUM[disambig_num.group()[1]])
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
							if cur_board[8 - j][loc[0] - 1] != "e ":
								blocked = True
								break
						if not blocked:
							prev_loc = loc
							del rook_locs[i]
							break
					if loc[1] == destination_tuple[1]:
						blocked = False
						for j in range(min(loc[0], destination_tuple[0]) + 1, max(loc[0], destination_tuple[0])):
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

			if determine_aggression(prev_loc, destination_tuple, "white"):
				white_aggression["Rook"][0] += 1
				white_aggression["All"][0] += 1
			white_aggression["Rook"][1] += 1

		# handles white pawn moves
		elif white_move[0].islower():
			destination = re.search("[a-h][1-8]", white_move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			pawn_locs = cur_locs["white"]["pawn"]
			
			# handles pawn moves which are not captures
			if "x" not in white_move:
				moved = False
				for i in range(len(pawn_locs)):
					loc = pawn_locs[i]
					if loc[0] == destination_tuple[0] and loc[1] == destination_tuple[1] - 1:
						prev_loc = loc
						del pawn_locs[i]
						moved = True
						break
				if not moved:
					for i in range(len(pawn_locs)):
						loc = pawn_locs[i]
						if loc[0] == destination_tuple[0] and loc[1] == 2 and destination_tuple[1] == 4:
							prev_loc = loc
							del pawn_locs[i]
							break

			# handles pawn captures
			else:
				letter = white_move[0]
				file_num = LETTER_TO_NUM[letter]
				for i in range(len(pawn_locs)):
					loc = pawn_locs[i]
					if loc[0] == file_num and loc[1] == destination_tuple[1] - 1:
						prev_loc = loc
						del pawn_locs[i]
						break

				# handles en passant
				if cur_board[convert_tup(destination_tuple)] == "e ":
					en_passant = True
					captured_square = convert_tup((destination_tuple[0], destination_tuple[1] - 1))
					cur_board[captured_square] = "e "
					cur_locs["black"]["pawn"].remove((destination_tuple[0], destination_tuple[1] - 1))

			# handles non promoting pawn moves
			if destination_tuple[1] != 8:
				cur_locs["white"]["pawn"].append(destination_tuple)
				cur_board[convert_tup(prev_loc)] = "e "
				cur_board[convert_tup(destination_tuple)] = "WP"

			# handles promotions
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

			
			white_aggression["Pawn"][0] += 1
			white_aggression["All"][0] += 1
			white_aggression["Pawn"][1] += 1

		# handles white kingside castling
		if white_move == "0-0":
			prev_loc = (0,0)
			destination_tuple = (0,0)
			cur_locs["white"]["rook"].remove((8, 1))
			cur_locs["white"]["rook"].append((6, 1))
			cur_locs["white"]["king"] = [(7,1)]
			cur_board[7][7] = "e "
			cur_board[7][4] = "e "
			cur_board[7][6] = "WK"
			cur_board[7][5] = "WR"

			white_aggression["King"][1] += 1
			white_aggression["Rook"][1] += 1

		# handles white queenside castling
		if white_move == "0-0-0":
			prev_loc = (0,0)
			destination_tuple = (0,0)
			cur_locs["white"]["rook"].remove((1, 1))
			cur_locs["white"]["rook"].append((4, 1))
			cur_locs["white"]["king"] = [(3,1)]
			cur_board[7][0] = "e "
			cur_board[7][4] = "e "
			cur_board[7][2] = "WK"
			cur_board[7][3] = "WR"

			white_aggression["King"][1] += 1
			white_aggression["Rook"][1] += 1

		# deletes black pieces that were captured
		if "x" in white_move and not en_passant:
			for piece in cur_locs["black"].keys():
				for i in range(len(cur_locs["black"][piece])):
					loc = cur_locs["black"][piece][i]
					if loc == destination_tuple:
						del cur_locs["black"][piece][i]
						break


		en_passant = False

		# handles black move if there is one 
		# (may not be a black move at the end of the game)
		if black_move:
			# handles black King moves
			if black_move[0] == "K":
				destination = re.search("[a-h][1-8]", black_move).group()
				destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
				prev_loc = cur_locs["black"]["king"][0]
				cur_locs["black"]["king"][0] = destination_tuple
				cur_board[convert_tup(prev_loc)] = "e "
				cur_board[convert_tup(destination_tuple)] = "BK"

				if determine_aggression(prev_loc, destination_tuple, "black"):
					black_aggression["King"][0] += 1
					black_aggression["All"][0] += 1
				black_aggression["King"][1] += 1

			# handles black Queen moves
			elif black_move[0] == "Q":
				destination = re.search("[a-h][1-8]", black_move).group()
				destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
				prev_loc = cur_locs["black"]["queen"][0]
				cur_locs["black"]["queen"][0] = destination_tuple
				cur_board[convert_tup(prev_loc)] = "e " 
				cur_board[convert_tup(destination_tuple)] = "BQ"

				if determine_aggression(prev_loc, destination_tuple, "black"):
					black_aggression["Queen"][0] += 1
					black_aggression["All"][0] += 1
				black_aggression["Queen"][1] += 1

			# handles black bishop moves
			elif black_move[0] == "B":
				destination = re.search("[a-h][1-8]", black_move).group()
				destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
				
				bishop_locs = cur_locs["black"]["bishop"]
				if len(bishop_locs) == 1:
					prev_loc = bishop_locs[0]
					cur_locs["black"]["bishop"] = []
				# if there are two bishops, determines which one could have
				# made the current move
				else:
					for i in range(len(bishop_locs)):
						loc = bishop_locs[i]
						diff = tuple(np.subtract(destination_tuple, loc))
						if diff[1] != 0:
							div = float(diff[0]) / diff[1]
							if div == 1 or div == -1:
								prev_loc = loc
								del bishop_locs[i]
								break

				cur_locs["black"]["bishop"].append(destination_tuple)
				cur_board[convert_tup(prev_loc)] = "e "
				cur_board[convert_tup(destination_tuple)] = "BB"

				if determine_aggression(prev_loc, destination_tuple, "black"):
					black_aggression["Bishop"][0] += 1
					black_aggression["All"][0] += 1
				black_aggression["Bishop"][1] += 1

			# handles black Knight moves
			elif black_move[0] == "N":
				destination = re.search("[a-h][1-8]", black_move).group()
				destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
				
				knight_locs = cur_locs["black"]["knight"]
				disambig_let = re.search("[a-h]{2}", black_move)
				disambig_num = re.search("[1-8][a-h]", black_move)
				if len(knight_locs) == 1:
					prev_loc = knight_locs[0]
					cur_locs["black"]["knight"] = [] 
				# if there are two knights, determines which could have made
				# the current move
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
					rank_num = int(LETTER_TO_NUM[disambig_num.group()[1]])
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

				if determine_aggression(prev_loc, destination_tuple, "black"):
					black_aggression["Knight"][0] += 1
					black_aggression["All"][0] += 1
				black_aggression["Knight"][1] += 1

			# handles black rook moves
			elif black_move[0] == "R":
				destination = re.search("[a-h][1-8]", black_move).group()
				destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
				
				rook_locs = cur_locs["black"]["rook"]
				disambig_let = re.search("[a-h]{2}", black_move)
				disambig_num = re.search("[1-8][a-h]", black_move)
				if len(rook_locs) == 1:
					prev_loc = rook_locs[0]
					cur_locs["black"]["rook"] = [] 
				# if there are two rooks, determines which could have made the 
				# current move
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
					rank_num = int(LETTER_TO_NUM[disambig_num.group()[1]])
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
								if cur_board[8 - j][loc[0] - 1] != "e ":
									blocked = True
									break
							if not blocked:
								prev_loc = loc
								del rook_locs[i]
								break
						elif loc[1] == destination_tuple[1]:
							blocked = False
							for j in range(min(loc[0], destination_tuple[0]) + 1, max(loc[0], destination_tuple[0])):
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

				if determine_aggression(prev_loc, destination_tuple, "black"):
					black_aggression["Rook"][0] += 1
					black_aggression["All"][0] += 1
				black_aggression["Rook"][1] += 1

			# handles black pawn moves
			elif black_move[0].islower():
				destination = re.search("[a-h][1-8]", black_move).group()
				destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
				pawn_locs = cur_locs["black"]["pawn"]
				
				# handles pawn moves which are not captures
				if "x" not in black_move:
					moved = False
					for i in range(len(pawn_locs)):
						loc = pawn_locs[i]
						if loc[0] == destination_tuple[0] and loc[1] == destination_tuple[1] + 1:
							prev_loc = loc
							del pawn_locs[i]
							moved = True
							break

					if not moved:
						for i in range(len(pawn_locs)):
							loc = pawn_locs[i]
							if loc[0] == destination_tuple[0] and loc[1] == 7 and destination_tuple[1] == 5:
								prev_loc = loc
								del pawn_locs[i]
								break
				# handles pawn captures
				else:
					letter = black_move[0]
					file_num = LETTER_TO_NUM[letter]
					for i in range(len(pawn_locs)):
						loc = pawn_locs[i]
						if loc[0] == file_num and loc[1] == destination_tuple[1] + 1:
							prev_loc = loc
							del pawn_locs[i]
							break
					# handles en passant
					if cur_board[convert_tup(destination_tuple)] == "e ":
						en_passant = True
						captured_square = convert_tup((destination_tuple[0], destination_tuple[1] + 1))
						cur_board[captured_square] = "e "
						cur_locs["white"]["pawn"].remove((destination_tuple[0], destination_tuple[1] + 1))

				# handles non promotions
				if destination_tuple[1] != 1:
					cur_locs["black"]["pawn"].append(destination_tuple)
					cur_board[convert_tup(prev_loc)] = "e "
					cur_board[convert_tup(destination_tuple)] = "BP"

				# handles promotions
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

				if determine_aggression(prev_loc, destination_tuple, "black"):
					black_aggression["Pawn"][0] += 1
					black_aggression["All"][0] += 1
				black_aggression["Pawn"][1] += 1

			# handles black kingside castling
			if black_move == "0-0":
				prev_loc = (0,0)
				destination_tuple = (0, 0)
				cur_locs["black"]["rook"].remove((8, 8))
				cur_locs["black"]["rook"].append((6, 8))
				cur_locs["black"]["king"] = [(7, 8)]
				cur_board[0][7] = "e "
				cur_board[0][4] = "e "
				cur_board[0][6] = "BK"
				cur_board[0][5] = "BR"

				black_aggression["Rook"][1] += 1
				black_aggression["All"][1] += 1

			# handles black queenside castling
			if black_move == "0-0-0":
				prev_loc = (0,0)
				destination_tuple = (0, 0)
				cur_locs["black"]["rook"].remove((1, 8))
				cur_locs["black"]["rook"].append((4, 8))
				cur_locs["black"]["king"] = [(3, 8)]
				cur_board[0][0] = "e "
				cur_board[0][4] = "e "
				cur_board[0][2] = "BK"
				cur_board[0][3] = "BR"

				black_aggression["Rook"][1] += 1
				black_aggression["All"][1] += 1

			# handles non en passant captures and deletes the
			# captured white piece
			if "x" in black_move and not en_passant:
				for piece in cur_locs["white"].keys():
					for i in range(len(cur_locs["white"][piece])):
						loc = cur_locs["white"][piece][i]
						if loc == destination_tuple:
							del cur_locs["white"][piece][i]
							break

		# increments the current location of all pieces still on the board
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

	return white_data, black_data, white_aggression, black_aggression
 

def generate_captures_heatmap(move_list):
	'''
	Given a move list, returns an array representing the number of captures
	that occured on each square

	Inputs:
		move_list: a list of chess moves

	Returns:
		an 8x8 numpy array whose entries are counts representing the number of
			captures that occurred on the corresponding square in move_list
	'''
	heatmap_data = np.zeros((8,8))
	for move in move_list:
		move = move[0]
		if "x" in move:
			destination = re.search("[a-h][1-8]", move).group()
			destination_tuple = (LETTER_TO_NUM[destination[0]], int(destination[1]))
			heatmap_data[convert_tup(destination_tuple)] += 1
	return heatmap_data


def calculate_trade_statistics(white_move_lists, black_move_lists, num_moves_white, num_moves_black):
	'''
	Given a list of white move lists and a list of black move lists, calculates
	capture statistics for each color

	Inputs:
		white_move_lists: a list of lists containing white moves
		black_move_lists: a list of lists containing the corresponding black
			moves (from the same games)
		num_moves_white: the total number of moves in white_move_lists
		num_moves_black: the total number of moves in black_move_lists

	Returns:
		a float representing the percentage of white moves which were captures,
		a float representing the percentage of black moves which were captures,
		a float representing the percentage of white captures which were
			recaptures (meaning black made a capture on the same square on
			the previous move),
		a float representing the percentage of black captures which were
			recaptures
	'''
	white_captures = 0
	black_captures = 0
	white_recaptures = 0
	black_recaptures = 0
	
	for i in range(len(white_move_lists)):
		white_move_list = white_move_lists[i]
		black_move_list = black_move_lists[i]

		# goes through each move and determines if it was a capture and, if so,
		# whether it was a recapture
		for move_num in range(len(white_move_list)):
			white_move = white_move_list[move_num][0]
			if "x" in white_move:
				white_captures += 1
				black_move = black_move_list[move_num - 1][0]
				if "x" in black_move:
					white_capture_loc = re.search("[a-h][1-8]", white_move).group()
					black_capture_loc = re.search("[a-h][1-8]", black_move).group()
					if white_capture_loc == black_capture_loc:
						white_recaptures += 1

		for move_num in range(len(black_move_list)):
			black_move = black_move_list[move_num][0]
			if "x" in black_move:
				black_captures += 1
				white_move = white_move_list[move_num][0]
				if "x" in white_move:
					black_capture_loc = re.search("[a-h][1-8]", black_move).group()
					white_capture_loc = re.search("[a-h][1-8]", white_move).group()
					if white_capture_loc == black_capture_loc:
						black_recaptures += 1

	# calculates capture% and recapture% for white and black
	white_capture_percent = float(white_captures)/num_moves_white
	black_capture_percent = float(black_captures)/num_moves_black
	white_recapture_percent = float(white_recaptures)/white_captures
	black_recapture_percent = float(black_recaptures)/black_captures

	return white_capture_percent, black_capture_percent, white_recapture_percent, black_recapture_percent



def convert_tup(tup):
	'''
	converts coordinates as they appear in chess notation to the corresponding
	numpy coordinates
	'''
	return (8 - tup[1], tup[0] - 1)


def determine_aggression(prev_loc, destination_tuple, color):
	'''
	Given the starting and ending location for a move and the color which made
	that move, returns a boolean representing whether or not the move was 
	forward or backward
	'''
	if color == "white":
		if destination_tuple[1] > prev_loc[1]:
			return True
	else:
		if destination_tuple[1] < prev_loc[1]:
			return True
	return False








	


