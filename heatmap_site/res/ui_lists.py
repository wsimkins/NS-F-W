import sqlite3
import csv

def generate_lists():

	connection = sqlite3.connect(??????????????)
	c = connection.cursor()

	# gets lists of unique values from sql database
	player = c.execute('''SELECT DISTINCT white_player AND black_player FROM games''').fetchall()
	rating = c.execute('''SELECT DISTINCT white_rating AND black_rating FROM games'''). fetchall()
	result = c.execute('''SELECT DISTINCT result FROM games''').fetchall()
	ECO = c.execute('''SELECT DISTINCT ECO FROM games''').fetchall()
	year = c.execute('''SELECT DISTINCT year FROM games''').fetchall()
	num_move = c.execute('''SELECT DISTINCT num_move FROM games''').fetchall()

	connection.close()

	# write lists of unique values to file
	f = open('player_list.csv', 'wb')
	w = csv.writer(f, delimiter="|")
	for row in player:
		w.writerow(row)
	f.close

	f = open('rating_list.csv', 'wb')
	w = csv.writer(f, delimiter="|")
	for row in rating:
		w.writerow(row)
	f.close

	f = open('result_list.csv', 'wb')
	w = csv.writer(f, delimiter="|")
	for row in result:
		w.writerow(row)
	f.close

	f = open('ECO_list.csv', 'wb')
	w = csv.writer(f, delimiter="|")
	for row in ECO:
		w.writerow(row)
	f.close

	f = open('year_list.csv', 'wb')
	w = csv.writer(f, delimiter="|")
	for row in year:
		w.writerow(row)
	f.close

	f = open('num_move_list.csv', 'wb')
	w = csv.writer(f, delimiter="|")
	for row in num_move:
		w.writerow(row)
	f.close



