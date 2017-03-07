import sqlite3
import csv

def generate_lists():

#destination: cp cooklev /heatmap_site/res
	connection = sqlite3.connect("mega_sample.db")
	c = connection.cursor()

	# gets lists of unique values from sql database
	player_w = c.execute('''SELECT DISTINCT white_player FROM games''').fetchall()
	player_b = c.execute('''SELECT DISTINCT black_player FROM games''').fetchall()
	player = list(set(player_w + player_b))
	player.sort()

	result = c.execute('''SELECT DISTINCT result FROM games''').fetchall()
	ECO = c.execute('''SELECT DISTINCT ECO FROM games''').fetchall()
	year = c.execute('''SELECT DISTINCT year FROM games''').fetchall()
	num_move = c.execute('''SELECT DISTINCT num_move FROM games''').fetchall()

	connection.close()

	# write lists of unique values to file
	f = open('player_list.csv', 'w')
	w = csv.writer(f, delimiter="|")
	for row in player:
		w.writerow([row[0].replace(",", ". ").title()])
	f.close

	f = open('result_list.csv', 'w')
	w = csv.writer(f, delimiter="|")
	for row in result:
		w.writerow(row)
	f.close

	f = open('ECO_list.csv', 'w')
	w = csv.writer(f, delimiter="|")
	for row in ECO:
		w.writerow(row)
	f.close

	f = open('year_list.csv', 'w')
	w = csv.writer(f, delimiter="|")
	for row in year:
		w.writerow(row)
	f.close

	f = open('num_move_list.csv', 'w')
	w = csv.writer(f, delimiter="|")
	for row in num_move:
		w.writerow(row)
	f.close



