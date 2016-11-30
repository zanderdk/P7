from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import os
from django.conf import settings
import simplejson as json
import math

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


def full_pool(request):
    return HttpResponse(_get_pool_pairs())

def partial_pool(request, count):
    return HttpResponse(_get_pool_pairs(int(count)))