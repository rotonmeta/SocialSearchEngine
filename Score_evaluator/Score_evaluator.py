import json
import threading
from .models import Category, CategoryScore
from allauth.socialaccount.models import SocialAccount
from scipy.stats import pearsonr


def user_page_score(solr, user):
    user_id = user.id
    user = SocialAccount.objects.get(uid=user_id)
    user_likes = solr.search(q='type:page AND user_id:' + user_id, fl='page_id, category_list, fan_count', rows=2000, wt='python')
    fb_category_list = Category.objects.all()

    threads = []
    user_category_score = []
    for cat in fb_category_list:
        thread = threading.Thread(target=_user_page_helper, args=(user_category_score, user_likes, cat, user))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    CategoryScore.objects.bulk_create(user_category_score)
    Category.objects.bulk_update(fb_category_list, ['likes'])
    print('fine create')


def calculate_similarity(solr, user):
    user_id = user.id
    user_scores = CategoryScore.objects.filter(user__uid=user_id).values('score').order_by('category__id')
    array = [u['score'] for u in user_scores]

    users = solr.search(q='doc_type:user AND -user_id:' + user_id, rows=200, wt='python')

    threads = []
    for user in users:
        print(str(user))
        thread = threading.Thread(target=_similarity_helper, args=(array, user))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()


def _user_page_helper(object_list, user_likes, cat, user):
    cat_count = 0
    cat_likes = cat.likes
    for page in user_likes:
        for category_id in page['category_list']:
            if cat.id == category_id:
                cat_count = cat_count + 1
                cat_likes = cat_likes + page['fan_count']
    adjusted_count = cat_count/len(user_likes)
    #category = Category(id=cat['id'])
    cat.likes = cat_likes
    to_add = CategoryScore(user=user, category=cat, score=adjusted_count)
    object_list.append(to_add)
    #print(str(cat['name']))


def _similarity_helper(array1, user2):
    user2_scores = CategoryScore.objects.filter(user__uid=user2['user_id']).values('score').order_by(
        'category__id')
    array2 = [u['score'] for u in user2_scores]
    result = pearsonr(array1, array2)
    print('Pearson similarity ' + str(result))


def sparsity_remover():
    pass






# def update_user_page_score(solr, user):
#     user_id = user.id
#     queryset = CategoryScore.objects.filter(user__uid=user_id)
#     objects = [entry for entry in queryset]
#     user_likes = solr.search(q='type:page AND user_id:' + user_id, fl='page_id, category_list', rows=2000, wt='python')
#
#     threads = []
#     user_category_score = []
#     for obj in objects:
#         thread = threading.Thread(target=_user_page_update_helper, args=(user_category_score, user_likes, obj))
#         thread.start()
#         threads.append(thread)
#
#     for t in threads:
#         t.join()
#
#     CategoryScore.objects.bulk_update(user_category_score, ['score'])
#     print('fine update')



# def _user_page_update_helper(object_list, user_likes, obj):
#     time.sleep(1)
#     cat_count = 0
#     for page in user_likes:
#         for category_id in page['category_list']:
#             if obj.category.id == category_id:
#                 cat_count = cat_count + 1
#     adjusted_score = cat_count/len(user_likes)
#     if obj.score != adjusted_score:
#         obj.score = adjusted_score
#         object_list.append(obj)