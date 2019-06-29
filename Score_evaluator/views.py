from django.shortcuts import render


def similarity(request):
    return render(request, 'Score_evaluator/similarity.html')
