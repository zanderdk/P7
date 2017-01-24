from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import os
from django.conf import settings
import simplejson as json
import math
from rest_framework import status
from rest_framework.response import Response
from getNgrams import getNgrams
from getPageTextFromDBpedia import getPageTextFromDBpedia
from getTitleMatches import getTitleMatches
from testLinks import testLinks


# Create your views here.

def _get_pool_pairs(MaxCount = math.inf):
    counter = 0
    output = []
    with open(os.path.join(settings.PROJECT_ROOT, 'pool')) as csvPool:
        for row in csvPool:
            if MaxCount <= counter:
                break
            source, target = row.split()
            output.append({"source": source, "target": target})
            counter += 1
    return json.dumps(output, sort_keys = True)

@csrf_exempt
def full_pool(request):
    if (request.method != 'GET'):
        return HttpResponse(status = 405)
    try:
        count = int(request.GET['max'])
    except Exception:
        return HttpResponse(_get_pool_pairs(), content_type="application/json")
    else:
        return HttpResponse(_get_pool_pairs(count), content_type="application/json")

@csrf_exempt
def partial_pool(request, count):
    if (request.method != 'GET'):
        return HttpResponse(status = 405)
    return HttpResponse(_get_pool_pairs(int(count)), content_type="application/json")

@csrf_exempt
def link_checked(request):
    if (request.method != 'POST'):
        return HttpResponse("Request must be POST", status = 405)

    try:
        source = request.POST['source']
        target = request.POST['target']
        status = request.POST['status']
        if(not(status == "good" or status == "bad")):
            raise KeyError("status should be 'good' or 'bad'")
    except Exception:
        return HttpResponse("You messed up the POST request", status = 400)
    else:
        with open(os.path.join(settings.PROJECT_ROOT, 'reviews'), 'a') as reviews:
            reviews.write(source + " " + target + " " + status + "\n")
        return HttpResponseRedirect('links/', "Review Accepted")


@csrf_exempt
def check_page(request):
    if (request.method != 'GET'):
        return HttpResponse("Request must be GET", status = 405)

    try:
        title = str(request.GET['title'])
    except Exception:
        return HttpResponse("You messed up the GET request", status = 400)
    else:
        text = getPageTextFromDBpedia(title)
        nGrams = getNgrams(text, 3)
        matchingTitles = getTitleMatches(nGrams)
        result = testLinks(title, matchingTitles)
        #jsonRes = toJSON(result)
        return HttpResponse(result, content_type="application/json")