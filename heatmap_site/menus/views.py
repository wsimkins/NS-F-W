from django.shortcuts import render
from django.http import HttpResponse
from django import forms
import json
import traceback
from io import StringIO
import sys
import csv
import os
import queries
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
        annotation="annotation"
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
ANNOTATION = _build_dropdown([None] + ["yes", "no"])
MAP_TYPE = _build_dropdown([None] + ["time spent", "moved to", "captures"])


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
    result = forms.ChoiceField(label='Result', choices=RESULTS, required=False)
    ecos = forms.ChoiceField(label='ECO (opening)', choices=ECOS, required=False)
    player_w = forms.ChoiceField(label='White Player Name', choices=PLAYERS, required=False)
    player_b = forms.ChoiceField(label='Black Player Name', choices=PLAYERS, required=False)
    color = forms.ChoiceField(label='Color', choices=COLORS, required=True)
    piece = forms.ChoiceField(label='Piece', choices=PIECES, required=True)
    annotation = forms.ChoiceField(label='Display Counts', choices=ANNOTATION, required=True)
    map_type = forms.ChoiceField(label='Heatmap Type', choices=MAP_TYPE, required=True)



def home(request):
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        
    else:
        form = SearchForm()

    context['form'] = form
    return render(request, 'menu.html', context)

def heatmap_display(request):
    context = {}
    d = request.POST.dict()
    print(d)
    args = {}
    if d.get("years_0", False):
        args['year_min'] = d["years_0"]
        args['year_max'] = d["years_1"]

    if d.get("num_move_0", False):
        args['num_move_min'] = d["num_move_0"]
        args['num_move_max'] = d["num_move_1"]

    if d.get("ratings_0", False):
        args['rating_min'] = d["ratings_0"]
        args['rating_max'] = d["ratings_1"]

    if d.get("ecos", False):
        args['ecos'] = d["ecos"]

    if d.get("result", False):
        args['result'] = d["result"]

    if d.get("player_w", False):
        args['white_player'] = d["player_w"]

    if d.get("player_b", False):
        args['black_player'] = d["player_b"]

    if d.get("color", False):
        args['color'] = d["color"]

    if d.get("piece", False):
        args['piece'] = d["piece"]

    if d.get("annotation", False):
        args["annotation"] = d["annotation"]

    if d.get("map_type", False):
        args['heatmap_type'] = d["map_type"]

    context['stats'] = queries.generate_heatmap_from_user_input(args)
    return render(request, 'heatmap_display.html', context)

def heatmap_display_comp(request):
    context = {}

    # NOT SURE IF THIS IS THE CORRECT WAY, CAN I GENERATE TWO STARTING DICTIONARIES?
    d1 = request.POST.dict()
    d2 = request.POST.dict()


    args_1 = {}
    if d.get("years_0", False):
        args_1['year_min'] = d["years_0"]
        args_1['year_max'] = d["years_1"]
    if d.get("num_move_0", False):
        args_1['num_move_min'] = d["num_move_0"]
        args_1['num_move_max'] = d["num_move_1"]
    if d.get("ratings_0", False):
        args_1['rating_min'] = d["ratings_0"]
        args_1['rating_max'] = d["ratings_1"]
    if d.get("ecos", False):
        args_1['ecos'] = d["ecos"]
    if d.get("result", False):
        args_1['result'] = d["result"]
    if d.get("player_w", False):
        args_1['white_player'] = d["player_w"]
    if d.get("player_b", False):
        args_1['black_player'] = d["player_b"]
    if d.get("color", False):
        args_1['color'] = d["color"]
    if d.get("piece", False):
        args_1['piece'] = d["piece"]
    if d.get("annotation", False):
        args_1["annotation"] = d["annotation"]
    if d.get("map_type", False):
        args_1['heatmap_type'] = d["map_type"]

    args_2 = {}
    if d.get("years_0", False):
        args_2['year_min'] = d["years_0"]
        args_2['year_max'] = d["years_1"]
    if d.get("num_move_0", False):
        args_2['num_move_min'] = d["num_move_0"]
        args_2['num_move_max'] = d["num_move_1"]
    if d.get("ratings_0", False):
        args_2['rating_min'] = d["ratings_0"]
        args_2['rating_max'] = d["ratings_1"]
    if d.get("ecos", False):
        args_2['ecos'] = d["ecos"]
    if d.get("result", False):
        args_2['result'] = d["result"]
    if d.get("player_w", False):
        args_2['white_player'] = d["player_w"]
    if d.get("player_b", False):
        args_2['black_player'] = d["player_b"]
    if d.get("color", False):
        args_2['color'] = d["color"]
    if d.get("piece", False):
        args_2['piece'] = d["piece"]
    if d.get("annotation", False):
        args_2["annotation"] = d["annotation"]
    if d.get("map_type", False):
        args_2['heatmap_type'] = d["map_type"]
    
    context['stats'] = queries.generate_comparison_from_user_input([args_1, args_2])

    return render(request, 'heatmap_display_comp.html', context)

