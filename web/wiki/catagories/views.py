from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

# Create your views here.

def index(request):
    latest_question_list = range(1,10)
    context = {'latest_question_list':latest_question_list}
    return render(request, 'catagories/index.html', context)

def catagory(request, catagory_name):
	#parse catagory name to database
	#fetch info on that catagory or error
	fromtitles = {"Horse","cats","dogs","humans"}
	context = {'catagory_name':catagory_name, 'titles':fromtitles}
	return render(request, 'catagories/catagory.html', context)