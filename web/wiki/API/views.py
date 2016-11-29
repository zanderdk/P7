from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import os
from django.conf import settings
import json

# Create your views here.

def full_pool(request):

    output = ""
    with open(os.path.join(settings.PROJECT_ROOT, 'pool')) as csvPool:
        for row in csvPool:
            output += row   

    latest_question_list = range(1,10)
    return HttpResponse(output)