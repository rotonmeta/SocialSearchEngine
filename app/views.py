from .Index_new_user_data import index_data
from .FbIndexManager import FbIndexManager
from .FbUser import FbUser
from django.shortcuts import render
from allauth.socialaccount.models import SocialToken
import pysolr
import threading


solr_string = 'https://solr.socialsearch.blog/solr/demo3/'
solr = pysolr.Solr(solr_string)


def results_list(request):
    if request.user.is_anonymous:
        return render(request, 'app/results_list.html', {'profpic': 0})

    if not request.session.get('search_done'):
        initialize_context(request)

    context = request.session['context']
    return render(request, 'app/results_list.html', context)


def initialize_context(request):
    token = SocialToken.objects.filter(account__user=request.user, account__provider='facebook').first()

    # inizializza i dati dell'utente loggato
    user = FbUser(token)
    user.initialize()

    index_manager = FbIndexManager(user, solr)
    thread = threading.Thread(target=index_data, args=(user, solr, index_manager))
    thread.start()

    score_list = solr.search(q='doc_type:score AND users:{}'.format(user.id),
                             fl='users, similarity',
                             sort='similarity desc',
                             rows=200, wt='json').docs

    # session variables to use in other view/template
    context = {'profpic': user.profPic, 'user_id': user.id, 'user_name': user.name,
               'score_list': score_list, 'solr': solr_string}

    request.session['context'] = context
    request.session['search_done'] = True
    request.session['similarity_done'] = False

