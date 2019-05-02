# -*- coding: utf-8 -*-
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse
from allauth.socialaccount.models import SocialToken
from .Index_new_user_data import *
from .models import *
from .forms import *
import datetime
import facebook
import pysolr
import threading


solr_string = 'https://solr.socialsearch.blog/solr/demo3/'
solr = pysolr.Solr(solr_string)
IndexManager = FbIndexManager(solr)


def open_file(request):
    if 'name' not in request.GET.keys():
        return redirect('/')
    name = str(request.GET.__getitem__('name'))
    for key in request.GET.keys():
        if str(key) != 'name' and str(key) != '_type_':
            name = name + '&' + key + '=' + request.GET.__getitem__(key)
    if not request.user.is_anonymous:
        thread = threading.Thread(target=update_file_history,
                                  args=(request.user.username, name, request.GET.__getitem__('_type_'), solr, 0,))
        thread.start()
    return redirect(name)


def history(request):
    print(request.user.username)
    if request.user.is_anonymous:
        return redirect('/')
    if 'delete' in request.GET.keys():
        solr.delete(q='doc_type:history AND user:' + str(request.user.username))
        solr.commit()
        return render(request, 'app/history.html', {'history': []})
    response = solr.search(q='doc_type:history AND user:' + str(request.user.username), sort='num desc', rows=1000000,
                           wt='python')
    history = []
    for result in response:
        s = Search()
        s.title = result['title']
        s.time = result['time']
        s.type = result['type']
        s.f = result['f']
        history.append(s)
    return render(request, 'app/history.html', {'history': history})


def welcome(request):
    try:
        print('thread di welcome')
        token = SocialToken.objects.filter(account__user=request.user, account__provider='facebook').first()
        thread = threading.Thread(target=index_data, args=(token, solr, IndexManager, 0))
        thread.start()
        return render(request, 'app/results_list.html')
    except:
        print('errore')
        return render(request, 'app/results_list.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def results_list(request):
    print(request.GET)
    logged = not request.user.is_anonymous
    if 'click_index' in request.GET.keys():
        if logged:
            user_name = request.user.get_full_name()
        else:
            user_name = 'not logged'
        doc = [{"doc_type": 'history',
                "user_name": user_name,
                "query": request.GET.__getitem__('query'),
                "filter": request.GET.__getitem__('filter'),
                "click_index": request.GET.__getitem__('click_index'),
                "data": str(datetime.datetime.now())[:19]}]
        solr.add(doc)
        solr.commit()

    if logged:

        token = SocialToken.objects.filter(account__user=request.user, account__provider='facebook').first()
        IndexManager.takeANDindexProfPic(token)
        graph = facebook.GraphAPI(access_token=token)
        tmp_json = graph.get_object(id='me', fields='albums{name,id,photos{images}}')

        user_id = str(tmp_json['id'])
        try:
            tmp_json = tmp_json['albums']['data']
        except:
            return render(request, 'app/results_list.html', {'profpic': 0, 'solr': solr_string})

        for a in tmp_json:
            if a['name'] == "Profile Pictures":
                album = a
                break
        profpic = album['photos']['data'][0]['images'][0]['source']

        response = solr.search(q='doc_type:score -score:0 AND (userA:' + user_id + ' OR userB:' + user_id + ')',
                               rows=pow(10, 6), wt='python')

        score_list = []
        for i in response:
            doc = {}
            if str(i['userA']) == user_id:
                second_user = i['userB']
            else:
                second_user = i['userA']
            doc.update({'user_id': str(second_user)})
            doc.update({'score': i['score']})

            if 'places_' in str(i['type']):
                type = 'place'

            elif 'age_' in str(i['type']):
                type = 'age'

            elif 'books_' in str(i['type']):
                type = 'book'

            elif 'music_' in str(i['type']):
                type = 'music'

            elif 'television_' in str(i['type']):
                type = 'TV'

            elif 'movies_' in str(i['type']):
                type = 'movie'

            elif 'generic_' in str(i['type']):
                type = 'page'

            doc.update({'type': type})
            score_list.append(doc)

        thread = threading.Thread(target=index_data, args=(token, solr, IndexManager, 0))
        thread.start()

        return render(request, 'app/results_list.html',
                      {'profpic': profpic, 'user_id': user_id, 'score_list': score_list, 'solr': solr_string})

    return render(request, 'app/results_list.html', {'profpic': 0, 'solr': solr_string})
