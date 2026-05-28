from django.shortcuts import render


def maturity(request):
	return render(request, "imp/index.html")


def practical_maturity(request):
	return render(request, "imp/prakticke_maturity.html")


def schedules(request):
	return render(request, "imp/rozpisy.html")
