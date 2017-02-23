#CS122: Group Project - Chess Heatmaps
#
#Names: Will Simkins, Natalie Gray, Steven Cooklev
#github username: wsimkins
#github password: NSFWpassword1
#

import bs4
import re
import sqlite3 as sql


def clean_data(html_input_file, html_output_file):
	'''
	Cleans a given html_file and outputs a new html_file with annotations removed
	'''

	html = open(html_input_file, "r") 
	text = html.read()
	soup = bs4.BeautifulSoup(text, "lxml")
	movelists = soup.find_all("p")
	for all_moves_of_game in movelists:
		moves = all_moves_of_game.find_all("b")
		''.join(str(x) for x in moves)
		re.sub("<b>", '', moves)
		re.sub("</b>", '', moves)

	html_output_file.write(text)


def create_db(html_file, output_file):
	'''
	Given an html file containing information about chess games, creates 
	a games database and a moves database in SQL with this information.
	'''


	conn = sql.connect(output_file, timeout=10)
	c = conn.cursor()
	
	# initializes both SQL tables
	# NOTE REMOVED PRIMARY KEY FROM GAME ID BECAUSE I GOT UNIQUE CONSTRAINT FAILED -WILL
	c.execute('''CREATE TABLE IF NOT EXISTS games (gameid text, white_player text, 
		black_player text, white_rating integer, black_rating integer, result text, 
		ECO text, year integer, num_move integer)''')
	c.execute('''CREATE TABLE IF NOT EXISTS moves (gameid text, move text, color text, move_num integer)''')

	html = open(html_file, "r", encoding='ISO-8859-1')
	# html.seek(4121)
	# 'utf-8' codec can't decode byte 0xe9 in position 321564766: invalid continuation byte
	text = html.read()

	soup = bs4.BeautifulSoup(text, "html.parser")
	
	# extracts all headers and movelists from the html file
	headers = soup.find_all("h3")
	movelists = soup.find_all("p")


	for i in range(len(headers)):
		header = headers[i].text
		movelist = movelists[i] # removed .text in order to remove annotations - Steven
		clean_moves = movelist.find_all("b")

		# Check each game for annotations and remove the annotations
		if not clean_moves:
			movelist = movelist.text
		else:
			clean_moves = ''.join(str(x) for x in clean_moves)
			clean_moves = re.sub("<b>", '', clean_moves)
			clean_moves = re.sub("</b>", '', clean_moves)
			# clean_moves = clean_moves.strip("\n") # I don't think the strip here is necessary?
			movelist = clean_moves

		# extracts gameid from the header
		gameid = re.search("\d+", header).group()
		
		# extracts player names from the header
		players = re.findall("[A-Za-z][A-Za-z\s,]*[A-Za-z]", header)
		white_player = players[0].lower()
		black_player = players[1].lower()

		# extracts elos of both players or None if the elo is not listed
		white_rating = re.search("[A-Za-z]\s\(\d{3,4}\)\s-", header)
		if white_rating:
			white_rating = int(white_rating.group()[3:-3])
		else:
			white_rating = -1

		black_rating = re.search("[A-Za-z]\s\(\d{3,4}\)\s\[", header)
		if black_rating:
			black_rating = int(black_rating.group()[3:-3])

		else:
			black_rating = -1

		# extracts result from the movelist or none if the result is not listed
		result = re.search("1-0|0-1|1/2-1/2", movelist)
		if result:
			result = result.group()
		else:
			result = "no_result"

		# extracts opening code from the header
		ECO = re.search("[A-E]\d{2}", header)
		if ECO:
			ECO = ECO.group()
		else:
			ECO = "no_eco"

		# extracts the year from the header
		year = int(header[-5:-1])

		# extracts a list of white move, black move pairs from the movelist
		moves = re.findall("\.[^.]+", movelist)
		moves = [move[1:] for move in moves]

		# calculates the number of moves in the game
		num_moves = len(moves)

		# inserts all data into games table for the current header and movelist
		c.execute("INSERT INTO games VALUES " + \
			str((gameid, white_player, black_player, white_rating, 
				black_rating, result, ECO, year, num_moves)))
		
		# separates the list of moves into strings representing individual moves
		# and then inserts these moves into the moves table
		for i in range(len(moves)):
			split_move = moves[i].split()
			white_move = split_move[0].strip()
			black_move = split_move[1].strip()
			c.execute("INSERT INTO moves VALUES " + \
				str((gameid, white_move, "white", i+1))) 

			# removes the result from the list of black moves if the game ended
			# in a white move
			if not black_move[-4:] == "1-0 " or black_move[-4:] == "0-1 " or black_move[-4:] == "1/2 ":
				c.execute("INSERT INTO moves VALUES " + \
					str((gameid, black_move, "black", i+1))) 

		# inserts all data into games table for the current header and movelist
		c.execute("INSERT INTO games VALUES " + \
			str((gameid, white_player, black_player, white_rating, 
				black_rating, result, ECO, year, num_moves)))
		
		# separates the list of moves into strings representing individual moves
		# and then inserts these moves into the moves table
		for i in range(len(moves)):
			split_move = moves[i].split()
			white_move = split_move[0].strip()
			black_move = split_move[1].strip()
			c.execute("INSERT INTO moves VALUES " + \
				str((gameid, white_move, "white", i+1))) 

			# removes the result from the list of black moves if the game ended
			# in a white move
			if not black_move[-4:] == "1-0 " or black_move[-4:] == "0-1 " or black_move[-4:] == "1/2 ":
				c.execute("INSERT INTO moves VALUES " + \
					str((gameid, black_move, "black", i+1))) 

	conn.commit()

	r = c.execute("SELECT move FROM moves WHERE color = ? AND gameid = ? ORDER BY move_num", ("white", "3747750"))
	white_moves = r.fetchall()
	q = c.execute("SELECT move FROM moves WHERE color = ? AND gameid = ? ORDER BY move_num", ("black", "3747750"))
	black_moves = q.fetchall()
	s = c.execute("SELECT move FROM moves WHERE color = ? AND gameid = ? ORDER BY move_num", ("white", "3747751"))
	white_moves2 = s.fetchall()
	t = c.execute("SELECT move FROM moves WHERE color = ? AND gameid = ? ORDER BY move_num", ("black", "3747751"))
	black_moves2 = t.fetchall()
	a = c.execute("SELECT move FROM moves WHERE color = ? AND gameid = ? ORDER BY move_num", ("white", "3747752"))
	white_moves3 = a.fetchall()
	b = c.execute("SELECT move FROM moves WHERE color = ? AND gameid = ? ORDER BY move_num", ("black", "3747752"))
	black_moves3 = b.fetchall()
	return white_moves, black_moves, white_moves2, black_moves2, white_moves3, black_moves3 

# query_dict = {white_player: games.white_player = ?}
# add levenshtein distance for names
# have not added gameid to dictionaries and search query
# add join statements

games_inputs_select = {'white_player': 'games.white_player = ?', 'black_player': 'games.black_player = ?',
					'result': 'games.result = ?', 'ECO': 'games.ECO = ?',
					'year_min': 'games.year >= ?', 'year_max': 'games.year <= ?',
					'num_moves_min': 'games.num_moves >= ?', 'num_moves_max': 'games.num_moves <= ?',
					'white_rating_min': 'games.white_rating >= ?', 'white_rating_max': 'games.white_rating <= ?',
					'black_rating_min': 'games.black_rating >= ?', 'black_rating_max': 'games.black_rating >= ?'}

games_input_dict = {'result': None, 'ECO': None, 
				'year_min': None, 'year_max': None,
				'num_moves_min': None, 'num_moves_max': None,
				'white_player': None, 'black_player': None, 	
				'white_rating_min': None, 'white_rating_max': None, 
				'black_rating_min': None, 'black_rating_max': None}

input_dict_sample_1 = {'result': '1-0', 'year_min': 1998, 'white_rating_min': 2000, 'white_rating_max': 2400}

def query_table_games(db_filename, input_dict):

	conn = sql.connect(db_filename)
	c = conn.cursor()
	s =  "SELECT * FROM games;"

	if input_dict:
		s = s.rstrip(";")
		s += " WHERE "
		arg_list = []

	for key, value in input_dict.items():
		arg_list.append(value)
		s += str(games_inputs_select[key]) + ' AND '
	s = s.rstrip(" AND ")
	s += ";"

	r = c.execute(s, arg_list)
	return(r.fetchall())
	conn.close()

moves_inputs_select = {'move': 'moves.move = ?', 'color': 'moves.color = ?', 
					'num_moves_min': 'moves.move_num >= ?', 'num_moves_max': 'moves.move_num >= ?'}

def query_table_moves(db_filename, input_dict):

	conn = sql.connect(db_filename)
	c = conn.cursor()

	s =  "SELECT * FROM moves;"

	if input_dict:
		s = s.rstrip(";")
		s += " WHERE "
		arg_list = []

	for key, value in input_dict.items():
		arg_list.append(value)
		s += str(moves_inputs_select[key]) + ' AND '
	s = s.rstrip(" AND ")
	s += ";"

	r = c.execute(s, arg_list)
	return(r.fetchall())
	conn.close()


'''
	r = c.execute("SELECT move FROM moves WHERE color = ? ORDER BY move_num", ("white",))
	white_moves = r.fetchall()
	q = c.execute("SELECT move FROM moves WHERE color = ? AND substr(move, 1, 1) = ? ORDER BY move_num", ("white", "B"))
	bishop_moves = q.fetchall()
	return white_moves, bishop_moves
'''
