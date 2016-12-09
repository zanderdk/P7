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
        return HttpResponse(_get_pool_pairs())
    else:
        return HttpResponse(_get_pool_pairs(count))

@csrf_exempt
def partial_pool(request, count):
    if (request.method != 'GET'):
        return HttpResponse(status = 405)
    return HttpResponse(_get_pool_pairs(int(count)))

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



