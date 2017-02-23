#CS122: Group Project - Chess Heatmaps
#
#Names: Will Simkins, Natalie Gray, Steven Cooklev
#github username: wsimkins
#github password: NSFWpassword1

import bs4
import re
import sqlite3 as sql


def clean_data(html_input_file, html_output_file):
	'''
	Cleans a given html_file and outputs a new html_file
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


def create_database(html_file, output_file):
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

	html = open(html_file, "r")
	text = html.read()

	soup = bs4.BeautifulSoup(text, "lxml")
	
	# extracts all headers and movelists from the html file
	headers = soup.find_all("h3")
	movelists = soup.find_all("p")

	for i in range(len(headers)):
		header = headers[i].text
		movelist = movelists[i].text

		# extracts gameid from the header
		gameid = re.search("\d+", header).group()
		
		# extracts player names from the header
		players = re.findall("[A-Za-z][A-Za-z\s,]*[A-Za-z]", header)
		white_player = players[0]
		black_player = players[1]

		# extracts elos of both players or None if the elo is not listed
		white_rating = re.search("[A-Za-z]\s\(\d{3,4}\)\s-", header)
		if white_rating:
			white_rating = int(white_rating.group()[3:-3])

		black_rating = re.search("[A-Za-z]\s\(\d{3,4}\)\s\[", header)
		if black_rating:
			black_rating = int(black_rating.group()[3:-3])

		# extracts result from the movelist
		result = re.search("1-0|0-1|1/2-1/2", movelist).group()

		# extracts opening code from the header
		ECO = re.search("[A-E]\d{2}", header).group()

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


	conn.commit()

	r = c.execute("SELECT DISTINCT move FROM moves WHERE color = ? AND gameid = ? ORDER BY move_num", ("white", "3747763"))
	white_moves = r.fetchall()
	q = c.execute("SELECT DISTINCT move FROM moves WHERE color = ? AND gameid = ? ORDER BY move_num", ("black", "3747763"))
	black_moves = q.fetchall()
	s = c.execute("SELECT DISTINCT move FROM moves WHERE color = ? AND gameid = ? ORDER BY move_num", ("white", "3747764"))
	white_moves2 = s.fetchall()
	t = c.execute("SELECT DISTINCT move FROM moves WHERE color = ? AND gameid = ? ORDER BY move_num", ("black", "3747764"))
	black_moves2 = t.fetchall()
	return white_moves, black_moves, white_moves2, black_moves2 










