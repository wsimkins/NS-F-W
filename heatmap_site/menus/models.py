from __future__ import unicode_literals

from django.db import models

COLOR_CHOICES = (
	('white', 'white'),
	('black', 'black')
)

PIECE_CHOICES = (
	("K", "K"),
	('Q', 'Q'),
	('R', 'R'),
	('B', 'B'),
	('N', 'N'),
	('P', 'P'),
	('all', 'all')
	)

class Piece_color_selection(models.Model):
	color = models.CharField(max_length=6, choices=COLOR_CHOICES)
	piece = models.CharField(max_length=3, choices=PIECE_CHOICES)

