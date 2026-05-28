from django.shortcuts import render


def vykazy_index(request):
	return render(request, "vykazy/index.html")
