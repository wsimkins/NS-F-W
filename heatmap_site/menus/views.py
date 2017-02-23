from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import FormView
from .models import Piece_color_selection
from .forms import Piece_color_selection_form

class Menu_Page(FormView):
	template_name = 'menu.html'
	success_url = '/NSFW/'
	form_class = Piece_color_selection_form

	def form_valid(self, form):
		return HttpResponse("this should probably be a heatmap")
