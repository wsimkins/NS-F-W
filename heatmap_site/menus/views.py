from django.shortcuts import render
from django.http import HttpResponse
from django import forms
import json
import traceback
from io import StringIO
import sys
import csv
import os
from django.views.generic import FormView
from .models import Piece_color_selection
from .forms import Piece_color_selection_form

NOPREF_STR = 'No preference'
RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'res')
COLUMN_NAMES = dict(
	    player='Player Name'
	    rating='Rating'
	    result='Result'
	    ECO='ECO'
	    year='Year'
	    num_move='Number of Moves'
)


def _valid_result(res):
	"""
	Validates results returned by ????????????????????????
	"""

def _load_column(filename, col=0):
	"""
	Loads single column from CSV file
	"""
	with open(filename) as f:
		col = list(zip(*csv.reader(f)))[0]
		return list(col)

def _load_res_column(filename, col=0):
	"""
	Load column from resource directory
	"""
	return _load_column(os.path.join(RES_DIR, filename), col=col)

def _build_dropdown(options):
	"""
	Converts a list to (value, caption) tuples
	"""
	return [(x, x) if x is not None else ('', NOPREF_STR) for x in options]

PLAYERS = _build_dropdown([None] + _load_res_column('player_list.csv'))
RATINGS = _build_dropdown([None] + _load_res_column('rating_list.csv'))
RESULTS = _build_dropdown([None] + _load_res_column('result_list.csv'))
ECOS = _build_dropdown([None] + _load_res_column('ECO_list.csv'))
YEARS = _build_dropdown([None] + _load_res_column('year_list.csv'))
NUM_MOVES = _build_dropdown([None] + _load_res_column('num_move_list.csv'))

class IntegerRange(forms.MultiValueField):
	def __init__(self, *args, **kwargs):
        fields = (forms.IntegerField(),
                  forms.IntegerField())
        super(IntegerRange, self).__init__(fields=fields,
                                           *args, **kwargs)

    def compress(self, values):
        if values and (values[0] is None or values[1] is None):
            raise forms.ValidationError('Must specify both lower and upper '
                                        'bound, or leave both blank.')

        return values

class RatingsRange(IntegerRange):
	def compress(self, values):
	        super(RatingsRange, self).compress(values)
	        for v in values:
	            if not (0 <= v <= 3000):
	                raise forms.ValidationError('Ratings bounds must be in the range 0 to 3000.')
	        if values and (values[1] < values[0]):
	            raise forms.ValidationError('Lower bound must not exceed upper bound.')
	        return values


class YearRange(IntegerRange):
	 def compress(self, values):
        super(YearRange, self).compress(values)
        for v in values:
            if not (1475 <= v <= 2013):
	                raise forms.ValidationError('Year bounds must be in the range 1475 to 2013.')
        if values and (values[1] < values[0]):
            raise forms.ValidationError('Lower bound must not exceed upper bound.')
        return values

class MoveNumberRange(IntegerRange):
	 def compress(self, values):
        super(MoveNumberRange, self).compress(values)
        for v in values:
            if not (0 <= v <= 300):
	                raise forms.ValidationError('Move number bounds must be in the range 0 to 300.')
        if values and (values[1] < values[0]):
            raise forms.ValidationError('Lower bound must not exceed upper bound.')
        return values

RANGE_WIDGET = forms.widgets.MultiWidget(widgets=(forms.widgets.NumberInput,
                                                  forms.widgets.NumberInput))

class PlayerNames(forms.MultiValueField):
	def __init__(self, *args, **kwargs):
        fields = (forms.IntegerField(),
                  forms.ChoiceField(label='Building', choices=PLAYERS, required=False),)
        super(BuildingWalkingTime, self).__init__(
                                           fields=fields,
                                           *args, **kwargs)

class ResultOptions(for)

















class Menu_Page(FormView):
	template_name = 'menu.html'
	success_url = '/NSFW/'
	form_class = Piece_color_selection_form

	def form_valid(self, form):
		return HttpResponse("this should probably be a heatmap")
