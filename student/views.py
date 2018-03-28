from django.shortcuts import render
from django.http.response import HttpResponse


def test(request):
    return HttpResponse('Test page in student app')
