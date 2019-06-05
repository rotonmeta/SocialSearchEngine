import json
from .models import Category


def populate_mysql_categories():
    with open('Score_evaluator/facebook-page-categories.json') as json_file:
        data = json_file.read()
    fb_category_list = json.loads(data)

    categories = []
    for cat in fb_category_list:
        categories.append(Category(id=cat['id'], name=cat['name']))

    Category.objects.bulk_create(categories)
