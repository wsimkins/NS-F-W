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
	Converts a given html file into a SQL table
	'''
	conn = sql.connect(output_file, timeout=10)
	c = conn.cursor()
	
	c.execute('''CREATE TABLE IF NOT EXISTS games (gameid text PRIMARY KEY, white_player text, 
		black_player text, white_rating integer, black_rating integer, result text, 
		ECO text, year integer)''')
	c.execute('''CREATE TABLE IF NOT EXISTS moves (gameid text, white_moves blob, 
				black_moves blob, num_moves integer)''')

	html = open(html_file, "r")
	text = html.read()

	soup = bs4.BeautifulSoup(text, "lxml")
	headers = soup.find_all("h3")
	movelists = soup.find_all("p")

	for i in range(len(headers)):
		header = headers[i].text
		movelist = movelists[i].text

		gameid = re.search("\d+", header).group()
		
		players = re.findall("[A-Za-z][A-Za-z\s,]*[A-Za-z]", header)
		white_player = players[0]
		black_player = players[1]

		white_rating = re.search("[A-Za-z]\s\(\d{3,4}\)\s-", header)
		if white_rating:
			white_rating = int(white_rating.group()[3:-3])

		black_rating = re.search("[A-Za-z]\s\(\d{3,4}\)\s\[", header)
		if black_rating:
			black_rating = int(black_rating.group()[3:-3])

		result = re.search("1-0|0-1|1/2-1/2", movelist).group()
		ECO = re.search("[A-E]\d{2}", header).group()

		year = int(header[-5:-1])

		c.execute("INSERT INTO games VALUES " + \
			str((gameid, white_player, black_player, white_rating, 
				black_rating, result, ECO, year)))

		moves = re.findall("\.[^.]+", movelist)
		moves = [move[1:] for move in moves]
		white_moves = ""
		black_moves = ""
		for move in moves:
			split_move = move.split()
			white_moves += split_move[0] + " "
			black_moves += split_move[1] + " "

		if(black_moves[-4:] == "1-0 " or black_moves[-4:] == "0-1 "):
			black_moves = black_moves[:-4]
		elif(black_moves[-4:] == "1/2 "):
			black_moves = black_moves[:-8]

		num_moves = len(moves)

		c.execute("INSERT INTO moves VALUES " + \
			str((gameid, white_moves[:-1], black_moves[:-1], num_moves))) 


	conn.commit()

	r = c.execute("SELECT * FROM games JOIN moves ON games.gameid = moves.gameid LIMIT 2")
	print(r.fetchall())

	conn.close()









