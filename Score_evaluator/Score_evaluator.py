import threading
from .models import Category, CategoryScore, Sum
from allauth.socialaccount.models import SocialAccount
from scipy.stats import pearsonr
import math


def create_db_rows(solr, user):
    user_id = user.id
    user = SocialAccount.objects.get(uid=user_id)
    user_likes = solr.search(q='type:page AND user_id:' + user_id, fl='page_id, category_list, fan_count', rows=2000, wt='python')
    fb_category_list = Category.objects.all()

    threads = []
    user_category_score = []
    for cat in fb_category_list:
        thread = threading.Thread(target=_db_helper, args=(user_category_score, user_likes, cat, user))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    Category.objects.bulk_update(fb_category_list, ['likes'])
    CategoryScore.objects.bulk_create(user_category_score)
    print('fine create')


def _db_helper(object_list, user_likes, cat, user):
    personal_likes = 0
    real = False
    for page in user_likes:
        for category_id in page['category_list']:
            if cat.id == category_id:
                personal_likes = personal_likes + 1
    if personal_likes is not 0:
        real = True
    total_likes = cat.likes + personal_likes
    cat.likes = total_likes
    to_add = CategoryScore(user=user, category=cat, likes=total_likes, real_value=real)
    object_list.append(to_add)


def remove_sparsity(user):
    categories = Category.objects.all()
    category_scores = CategoryScore.objects.filter(user__uid=user.id)

    recursive_sparsity(category_scores)

    Category.objects.bulk_update(categories, ['likes'])
    CategoryScore.objects.bulk_update(category_scores, ['likes'])


def recursive_sparsity(category_scores):
    for parent in category_scores:
        #if parent.real_value is True:
        _id = parent.category.id
        _likes = parent.likes
        children = Category.objects.filter(parent__id=_id)
        if len(children) is 0:
            continue
        new_likes = math.ceil(_likes / len(children))
        #print('1')
        for child in children:
            #print('2')
            elem = category_scores.get(category=child)
            #print('3')
            if elem.real_value is False:
                #print('4')
                elem.likes = new_likes
                child.likes = new_likes
                #print('5')
                _children = Category.objects.filter(parent__id=child.id)
                child_category_scores = category_scores.filter(category__in=_children)
                #print('6')
                if not child_category_scores:
                    continue
                else:
                    recursive_sparsity(child_category_scores)


def calculate_similarity(solr, user):
    user1_id = user.id
    users = solr.search(q='doc_type:user AND -user_id:' + user1_id, rows=200, wt='python')

    threads = []
    for user2 in users:
        print('Calculating similarity for ' + user2['user_name'])
        thread = threading.Thread(target=_similarity_helper, args=(user1_id, user2['user_id']))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()


def _similarity_helper(user1_id, user2_id):
    user1_vector = get_vector(user1_id)
    user2_vector = get_vector(user2_id)

    result = pearsonr(user1_vector, user2_vector)
    print('Pearson similarity ' + str(result))


def get_vector(user_id):
    user_likes = CategoryScore.objects.filter(user__uid=user_id).values('likes').order_by('category__id')
    n_likes = CategoryScore.objects.filter(user__uid=user_id).aggregate(Sum('likes')).get('likes__sum')
    tf = [u['likes'] / n_likes for u in user_likes]
    print('tf ' + str(tf))

    cat_likes = Category.objects.all().values('likes').order_by('id')
    total_likes = Category.objects.all().aggregate(Sum('likes')).get('likes__sum')

    idf = [math.log(total_likes / c['likes']) if c['likes'] else 0 for c in cat_likes]
    print('idf ' + str(idf))

    tf_idf = [a*b for a, b in zip(tf, idf)]
    print(tf_idf)

    ma = max(tf_idf)
    print('max ' + str(ma))
    mi = min(tf_idf)
    print('min ' + str(mi))

    normalized_vector = [(x - mi) / (ma - mi) for x in tf_idf]
    print(normalized_vector)

    return normalized_vector




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