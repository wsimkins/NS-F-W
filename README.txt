CS 122 Final Project: Chess Heatmaps

Authors: Will Simkins, Steven Cooklev, Natalie Gray

heatmap_site:
	heatmaps.py: cleans data from html and creates the database
	menus:
        generate_data_array.py: generates the necessary data arrays for the type
            of heatmap requested, used in queries.py
        mini.db: database containing information from 1,525 chess games. 
        queries.py: creates a query for the database based on user input and 
            outputs the requested heatmaps as .png images. 
	res:
	    mini.db: database which needs to be connected to ui_lists.py in order
	        to populate the CSV files in res correctly
	    ui_lists.py: populates the CSV files in res with specific lists taken
	        from the database. move_num, player, ECO, result, and year list
	        csv files. Must be run and have its function called when you want
	        to use a new database. (ex: switch from mini.db to mega.db)
	static: contains the heatmap images and main.css
proposal: directory containing original project proposal
README.txt: this file

* note: the database used (in this case mini.db) must be connected to both 
      generate_data_array.py and ui_lists.py. If you wish to change the database
      used both connections must be updated. 