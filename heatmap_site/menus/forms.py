from django import forms
from .models import Piece_color_selection

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

class Piece_color_selection_form(forms.ModelForm):
	error_css_class = 'error'
	color = forms.ChoiceField(choices=COLOR_CHOICES, required=True)
	piece = forms.ChoiceField(choices=PIECE_CHOICES, required=True)
	class Meta:
		model = Piece_color_selection
		fields = ['color', 'piece']