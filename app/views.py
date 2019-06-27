from django.shortcuts import render
from allauth.socialaccount.models import SocialToken
from .Index_new_user_data import *
import pysolr
import threading
from .FbUser import *


solr_string = 'https://solr.socialsearch.blog/solr/demo3/'
solr = pysolr.Solr(solr_string)


def results_list(request):
    logged = not request.user.is_anonymous
    if logged:
        token = SocialToken.objects.filter(account__user=request.user, account__provider='facebook').first()

        # check if token is valid
        url = 'https://graph.facebook.com/me?access_token=' + str(token)
        r = requests.get(url)
        if r.status_code == 400:
            print('Token non valido.')
            return render(request, 'app/results_list.html', {'profpic': 0, 'solr': solr_string})

        # inizializza i dati dell'utente loggato
        user = FbUser(token)
        user.initialize()

        index_manager = FbIndexManager(user, solr)
        thread = threading.Thread(target=index_data, args=(user, solr, index_manager))
        thread.start()

        score_list = solr.search(q='doc_type:score AND users:{}'.format(user.id),
                                 sort='similarity desc', rows=200, wt='json').docs

        return render(request, 'app/results_list.html',
                      {'profpic': user.profPic, 'user_id': user.id, 'score_list': score_list, 'solr': solr_string})

    return render(request, 'app/results_list.html', {'profpic': 0, 'solr': solr_string})
