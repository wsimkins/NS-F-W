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


NOPREF_STR = 'No preference'
RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'res')
COLUMN_NAMES = dict(
        player='player',
        rating='rating',
        result='result',
        ECO='ECO',
        year='year',
        num_move='number of Moves',
        color='color',
        piece="piece",
)


def _valid_result(res):
    """
    Validates results returned by ????????????????????????
    """
    (HEADER, RESULTS) = [0,1]
    ok = (isinstance(res, (tuple, list)) and 
            len(res) == 2 and
            isinstance(res[HEADER], (tuple, list)) and
            isinstance(res[RESULTS], (tuple, list)))
    if not ok:
        return False

    n = len(res[HEADER])
    def _valid_row(row):
        return isinstance(row, (tuple, list)) and len(row) == n
    return reduce(and_, (_valid_row(x) for x in res[RESULTS]), True)

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
RESULTS = _build_dropdown([None] + _load_res_column('result_list.csv'))

eco_list = []
for let in ["A", "B", "C", "D", "E"]:
    for num in range(100):
        if num < 10:
            num = "0" + str(num)
        eco_list.append(let + str(num))

ECOS = _build_dropdown([None] + eco_list)
YEARS = _build_dropdown([None] + _load_res_column('year_list.csv'))
NUM_MOVES = _build_dropdown([None] + _load_res_column('num_move_list.csv'))
PIECES = _build_dropdown([None] + ["King", "Queen", "Rook", "Knight", "Bishop", "Pawn", "All"])
COLORS = _build_dropdown([None] + ["white", "black"])


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


class SearchForm(forms.Form):
    years = YearRange(
                label='Year(s)',
                help_text='1475-2013',
                widget=RANGE_WIDGET,
                required=False)
    num_move = MoveNumberRange(
                label='Move Numbers',
                help_text='maximum 300 moves',
                widget=RANGE_WIDGET,
                required=False)
    ratings = RatingsRange(
                label='Player Ratings (Elo)',
                help_text='maximum 3000',
                widget=RANGE_WIDGET,
                required=False)
    results = forms.ChoiceField(label='Result', choices=RESULTS, required=False)
    ecos = forms.ChoiceField(label='ECO (opening)', choices=ECOS, required=False)
    players = forms.ChoiceField(label='Player Name', choices=PLAYERS, required=False)
    color = forms.ChoiceField(label='Color', choices=COLORS, required=False)
    piece = forms.ChoiceField(label='Piece', choices=PIECES, required=False)


def home(request):
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():

            # Convert form data to an args dictionary for heatmaps.py
            args = {}
            years = form.cleaned_data['years']
            if years:
                args['year_lower'] = years[0]
                args['year_upper'] = years[1]

            num_move = form.cleaned_data['num_move']
            if num_move:
                args['moves_lower'] = num_move[0]
                args['moves_upper'] = num_move[1]

            ratings = form.cleaned_data['ratings']
            if ratings:
                args['rating_lower'] = ratings[0]
                args['rating_upper'] = ratings[1]

            ecos = form.cleaned_data['ecos']
            if ecos:
                args['ecos'] = ecos

            results = form.cleaned_data['results']
            if results:
                args['results'] = results

            players = form.cleaned_data['players']
            if players:
                args['players'] = players

            color = form.cleaned_data['color']
            if color:
                args['color'] = color

            piece = form.cleaned_data['piece']
            if piece:
                args['piece'] = piece

            res = None
    else:
        form = SearchForm()

    # Handle different responses of res
    if res is None:
        context['result'] = None
    elif isinstance(res, str):
        context['result'] = None
        context['err'] = res
        result = None
        cols = None
    else:
        columns, result = res

        # Wrap in tuple if result is not already
        if result and isinstance(result[0], str):
            result = [(r,) for r in result]

        context['result'] = result
        context['num_results'] = len(result)
        context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]

    context['form'] = form
    return render(request, 'menu.html', context)

