import json
import pysolr
from app.FbUser import FbUser
from .models import Category
from allauth.socialaccount.models import SocialToken
from .Score_evaluator import *
import time


def get_start_json():
    with open('Score_evaluator/facebook-page-categories.json') as json_file:
        data = json_file.read()
    _json_file = json.loads(data)
    return _json_file['data']


def recursive_parent(_json, parent_id, _list, depth):
    for elem in _json:
        if parent_id is not None:
            _list.append(Category(id=elem['id'], name=elem['name'], parent=Category(id=parent_id), depth=depth))
        else:
            _list.append(Category(id=elem['id'], name=elem['name'], parent=None, depth=depth))

        print('added ' + elem['name'])

        if 'fb_page_categories' in elem.keys():
            recursive_parent(elem['fb_page_categories'], elem['id'], _list, depth+1)


def populate_db():
    _json = get_start_json()
    categories = []
    recursive_parent(_json=_json, parent_id=None, _list=categories, depth=1)

    Category.objects.bulk_create(categories)


def update_all_similarities():
    tokens = SocialToken.objects.all()
    solr = pysolr.Solr('https://solr.socialsearch.blog/solr/demo3/')

    for elem in tokens:
        user = FbUser(elem.token)
        user.initialize()
        print("aggiorno dati di " + user.name)
        calculate_similarity(solr, user)
        #time.sleep(5)


