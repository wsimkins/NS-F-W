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
    Validates results
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
        return [player.replace(".", ",") for player in list(col)]

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

# builds dropdowns based on either a set list of options or from the choices found in the
# relevant csv file. 
PLAYERS = _build_dropdown([None] + _load_res_column('player_list.csv'))
RESULTS = _build_dropdown([None] + _load_res_column('result_list.csv'))
ECOS = _build_dropdown([None] + ["A00-A39", "A40-A99", "B00-B19", "B20-B99", "C00-C19", "C20-C99", "D00-D69", "D70-E99"])
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
        return values

class RatingsRange(IntegerRange):
    def compress(self, values):
        super(RatingsRange, self).compress(values)
        return values


class YearRange(IntegerRange):
    def compress(self, values):
        super(YearRange, self).compress(values)
        return values

class MoveNumberRange(IntegerRange):
    def compress(self, values):
        super(MoveNumberRange, self).compress(values)
        return values

RANGE_WIDGET = forms.widgets.MultiWidget(widgets=(forms.widgets.NumberInput,
                                                  forms.widgets.NumberInput))


class SearchForm(forms.Form):
    """
    Form class which includes all the specifications for the heatmaps. A 
    combination of ranged specifications (years, move numbers, player ratings)
    and dropdown menus (result, ecos, player names, color, piece, annotations, 
    and heatmap type).
    """
    years = YearRange(
                label='Year(s)',
                help_text='1858-2013',
                widget=RANGE_WIDGET,
                required=False)
    num_move = MoveNumberRange(
                label='Move Numbers',
                help_text='maximum 300 moves',
                widget=RANGE_WIDGET,
                required=False)
    ratings_b = RatingsRange(
                label='Black Player Rating (Elo)',
                help_text='maximum 3000',
                widget=RANGE_WIDGET,
                required=False)
    ratings_w = RatingsRange(
                label='White Player Rating (Elo)',
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

class SearchFormCompare(forms.Form):
    """
    Identical options to the SearchForm class, but with different variable names so 
    that when making a comparison heatmap the argument dictionaries for heatmap 1
    and heatmap 2 have distinct keys 
    """
    years_c = YearRange(
                label='Year(s)',
                help_text='1858-2013',
                widget=RANGE_WIDGET,
                required=False)
    num_move_c = MoveNumberRange(
                label='Move Numbers',
                help_text='maximum 300 moves',
                widget=RANGE_WIDGET,
                required=False)
    ratings_b_c = RatingsRange(
                label='Black Player Rating (Elo)',
                help_text='maximum 3000',
                widget=RANGE_WIDGET,
                required=False)
    ratings_w_c = RatingsRange(
                label='White Player Rating (Elo)',
                help_text='maximum 3000',
                widget=RANGE_WIDGET,
                required=False)
    result_c = forms.ChoiceField(label='Result', choices=RESULTS, required=False)
    ecos_c = forms.ChoiceField(label='Opening Category', choices=ECOS, required=False)
    player_w_c = forms.ChoiceField(label='White Player Name', choices=PLAYERS, required=False)
    player_b_c = forms.ChoiceField(label='Black Player Name', choices=PLAYERS, required=False)
    color_c = forms.ChoiceField(label='Color', choices=COLORS, required=True)
    piece_c = forms.ChoiceField(label='Piece', choices=PIECES, required=True)
    annotation_c = forms.ChoiceField(label='Display Counts', choices=ANNOTATION, required=True)
    map_type_c = forms.ChoiceField(label='Heatmap Type', choices=MAP_TYPE, required=True)

def info(request):
    """
    Displays the information page. 
    """
    return render(request, 'info.html')

def home(request):
    """
    Displays the homepage, with links and the menu for a single heatmap. 
    """
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
    """
    Displays single heatmaps based on user input. 
    """
    context = {}
    d = request.POST.dict()
    # creation of an arguments dictionary that will be fed into
    # generate_heatmap_from_user_input
    args = {}
    if d.get("years_0", False):
        args['year_min'] = d["years_0"]
    if d.get("years_1", False):
        args['year_max'] = d["years_1"]
    if d.get("num_move_0", False):
        args['num_move_min'] = d["num_move_0"]
    if d.get("num_move_1", False):
        args['num_move_max'] = d["num_move_1"]
    if d.get("ratings_w_0", False):
        args['white_rating_min'] = d["ratings_w_0"]
    if d.get("ratings_w_1", False):
        args['white_rating_max'] = d["ratings_w_1"]
    if d.get("ratings_b_0", False):
        args['black_rating_min'] = d["ratings_b_0"]
    if d.get("ratings_b_1", False):
        args['black_rating_max'] = d["ratings_b_1"]
    if d.get("ecos", False):
        args['ECO'] = d["ecos"]
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

    a, b = queries.generate_heatmap_from_user_input(args)
    context["stats1"] = a
    context["stats2"] = b
    # displays an error page when the specifications do not match any games
    # and there is no heatmap to display
    if not a:
        return render(request, '404.html')
    return render(request, 'heatmap_display.html', context)

def heatmap_comp_menu(request):
    """
    Displays the menu for comparison heatmaps 
    """
    context = {}
    res = None
    if request.method == 'GET':
        # create form instances and populate it with data from the request:
        form1 = SearchForm(request.GET)
        form2 = SearchFormCompare(request.GET)
        
    else:
        form1 = SearchForm()
        form2 = SearchFormCompare()

    context['form1'] = form1
    context['form2'] = form2
    return render(request, 'heatmap_comp_menu.html', context)


def heatmap_display_comp(request):
    """
    Displays comparison heatmaps based on user input
    """
    context = {}

    d = request.POST.dict()
    d_c = request.POST.dict()

    # creation of the arguments dictionary for heatmap 1
    args = {}
    if d.get("years_0", False):
        args['year_min'] = d["years_0"]
    if d.get("years_1", False):
        args['year_max'] = d["years_1"]
    if d.get("num_move_0", False):
        args['num_move_min'] = d["num_move_0"]
    if d.get("num_move_1", False):
        args['num_move_max'] = d["num_move_1"]
    if d.get("ratings_w_0", False):
        args['white_rating_min'] = d["ratings_w_0"]
    if d.get("ratings_w_1", False):
        args['white_rating_max'] = d["ratings_w_1"]
    if d.get("ratings_b_0", False):
        args['black_rating_min'] = d["ratings_b_0"]
    if d.get("ratings_b_1", False):
        args['black_rating_max'] = d["ratings_b_1"]
    if d.get("ecos", False):
        args['ECO'] = d["ecos"]
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

    # creation of the comparison arguments dictionary, or the dictionary
    # for heatmap 2. 
    args_c = {}
    if d_c.get("years_c_0", False):
        args_c['year_min'] = d_c["years_c_0"]
    if d_c.get("years_c_1", False):
        args_c['year_max'] = d_c["years_c_1"]
    if d_c.get("num_move_c_0", False):
        args_c['num_move_min'] = d_c["num_move_c_0"]
    if d_c.get("num_move_c_1", False):
        args_c['num_move_max'] = d_c["num_move_c_1"]
    if d.get("ratings_w_c_0", False):
        args_c['white_rating_min'] = d_c["ratings_w_c_0"]
    if d.get("ratings_w_c_1", False):
        args_c['white_rating_max'] = d_c["ratings_w_c_1"]
    if d.get("ratings_b_c_0", False):
        args_c['black_rating_min'] = d_c["ratings_b_c_0"]
    if d.get("ratings_b_c_1", False):
        args_c['black_rating_max'] = d_c["ratings_b_c_1"]
    if d_c.get("ecos_c", False):
        args_c['ECO'] = d_c["ecos_c"]
    if d_c.get("result_c", False):
        args_c['result'] = d_c["result_c"]
    if d_c.get("player_w_c", False):
        args_c['white_player'] = d_c["player_w_c"]
    if d_c.get("player_b_c", False):
        args_c['black_player'] = d_c["player_b_c"]
    if d_c.get("color_c", False):
        args_c['color'] = d_c["color_c"]
    if d_c.get("piece_c", False):
        args_c['piece'] = d_c["piece_c"]
    if d_c.get("annotation_c", False):
        args_c["annotation"] = d_c["annotation_c"]
    if d_c.get("map_type_c", False):
        args_c['heatmap_type'] = d_c["map_type_c"]
    
    # statistics are returned by generate_comparison_from_user_input and stored
    a,b,c,d,e,f = queries.generate_comparison_from_user_input([args, args_c])

    # if there were no games to generate one of the heatmaps, directs to 
    # an error page
    if not a:
        return render(request, '405.html')
    if not b:
        return render(request, '406.html')
    
    # adds the statistics to the context
    context["stats1"] = a
    context["stats2"] = b
    context["stats3"] = c
    context["stats4"] = d
    context["stats5"] = e
    context["stats6"] = f
    
    # displays the comparison heatmaps
    return render(request, 'heatmap_display_comp.html', context)

