from django.shortcuts import render


def temataky_index(request):
	return render(request, "temataky/index.html")
