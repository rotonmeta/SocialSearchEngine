import json
from .models import Category


def get_start_json():
    with open('Score_evaluator/facebook-page-categories.json') as json_file:
        data = json_file.read()
    _json_file = json.loads(data)
    return _json_file['data']


def recursive_parent(json, parent_id, list):
    for elem in json:
        if parent_id is not None:
            list.append(Category(id=elem['id'], name=elem['name'], parent=Category(id=parent_id)))
        else:
            list.append(Category(id=elem['id'], name=elem['name'], parent=None))

        print('added ' + elem['name'])

        if 'fb_page_categories' in elem.keys():
            recursive_parent(elem['fb_page_categories'], elem['id'], list)


def populate_db():
    json = get_start_json()
    categories = []
    recursive_parent(json, None, categories)

    Category.objects.bulk_create(categories)

