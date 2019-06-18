import threading
from .models import Category, CategoryScore, Sum
from allauth.socialaccount.models import SocialAccount
from scipy.stats import pearsonr
from numpy import column_stack
from statsmodels.stats.weightstats import DescrStatsW
import math


def create_db_rows(solr, user):
    user_id = user.id
    user = SocialAccount.objects.get(uid=user_id)
    user_likes = solr.search(q='type:page AND user_id:' + user_id, fl='page_id, category_list', rows=2000, wt='python')
    fb_category_list = Category.objects.all()

    threads = []
    user_category_score = []
    for cat in fb_category_list:
        thread = threading.Thread(target=_db_helper, args=(user_category_score, user_likes, cat, user))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    CategoryScore.objects.bulk_create(user_category_score)
    Category.objects.bulk_update(fb_category_list, ['likes'])
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
    cat.likes = cat.likes + personal_likes
    to_add = CategoryScore(user=user, category=cat, likes=personal_likes, real_value=real)
    object_list.append(to_add)


def remove_sparsity(user):
    updated_categories = []
    updated_category_scores = []

    cat_scores = CategoryScore.objects.select_related('category__parent__parent').filter(user__uid=user.id)
        #.values('category_id', 'likes', 'category__parent_id')
    cat_scores_gt_0 = cat_scores.filter(likes__gt=0)

    for elem in cat_scores_gt_0:
        recursive_sparsity(elem, cat_scores, updated_categories, updated_category_scores)

    Category.objects.bulk_update(updated_categories, ['likes'])
    CategoryScore.objects.bulk_update(updated_category_scores, ['likes'])


def recursive_sparsity(child, category_scores, update_cat_list, update_cat_score_list):
    parent_id = child.category.parent_id

    if parent_id is not None:
        parent = category_scores.get(category_id=parent_id)
        parent.likes = parent.likes + child.likes
        cat_parent = Category.objects.get(id=parent_id)
        cat_parent.likes = cat_parent.likes + child.likes

        update_cat_list.append(cat_parent)
        update_cat_score_list.append(parent)

        recursive_sparsity(parent, category_scores, update_cat_list, update_cat_score_list)


def calculate_similarity(solr, user):
    user1_id = user.id
    users = solr.search(q='doc_type:user AND -user_id:' + user1_id, rows=200, wt='python')

    threads = []
    for user2 in users:
        print('Calculating similarity for ' + user2['user_name'])
        thread = threading.Thread(target=_similarity_helper_2, args=(user1_id, user2['user_id'], solr))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()


def _similarity_helper(user1_id, user2_id, solr):
    user1_vector = get_vector_tf(user1_id)
    user2_vector = get_vector_tf(user2_id)

    result = pearsonr(user1_vector, user2_vector)

    print('Pearson similarity ' + str(result))


def _similarity_helper_2(user1_id, user2_id, solr):
    query = 'doc_type:score AND users:({} AND {})'.format(user1_id, user2_id)
    solr.delete(q=query)

    user1_vector, depth_vector = get_vector_limited(user1_id)
    user2_vector, depth_vector = get_vector_limited(user2_id)

    result = pearsonr(user1_vector, user2_vector)[0]
    data = column_stack((user1_vector, user2_vector))
    result2 = DescrStatsW(data, weights=depth_vector).corrcoef

    mutual_friends = get_mutual_friends(user1_id, user2_id, solr)

    new_score = [{
        'doc_type': 'score',
        'users': [user1_id, user2_id],
        'score': result,
        'mutual_friends': mutual_friends
    }]

    solr.add(new_score)
    solr.commit()

    print('Pearson similarity ' + str(result))
    print('DescrStatsW ' + str(result2[1][0]))


def get_vector_limited(user_id):
    inner_qs = CategoryScore.objects.filter(likes__gt=0).values('category_id')
    user_likes = CategoryScore.objects.filter(category__id__in=inner_qs, user__uid=user_id)\
        .values('likes').order_by('category__id')
    n_likes = user_likes.aggregate(Sum('likes')).get('likes__sum')

    tf = [u['likes'] / n_likes for u in user_likes]

    liked_categories = CategoryScore.objects.filter(category__id__in=inner_qs, user__uid=user_id)\
        .values('category__id')

    cat_likes = Category.objects.filter(id__in=liked_categories).values('likes', 'depth').order_by('id')
    total_likes = cat_likes.aggregate(Sum('likes')).get('likes__sum')

    idf = [math.log(total_likes / (1 + c['likes'])) for c in cat_likes]

    tf_idf = [a*b for a, b in zip(tf, idf)]

    ma = max(tf_idf)
    mi = min(tf_idf)

    normalized_vector = [(x - mi) / (ma - mi) for x in tf_idf]

    depth_vector = [c['depth'] for c in cat_likes]

    return normalized_vector, depth_vector


def get_vector_tf(user_id):
    user_likes = CategoryScore.objects.filter(user__uid=user_id).values('likes').order_by('category__id')
    n_likes = CategoryScore.objects.filter(user__uid=user_id).aggregate(Sum('likes')).get('likes__sum')
    tf = [u['likes'] / n_likes for u in user_likes]

    ma = max(tf)
    mi = min(tf)

    normalized_vector = [(x - mi) / (ma - mi) for x in tf]

    return normalized_vector


def get_vector_tf_idf(user_id):
    user_likes = CategoryScore.objects.filter(user__uid=user_id).values('likes').order_by('category__id')
    n_likes = CategoryScore.objects.filter(user__uid=user_id).aggregate(Sum('likes')).get('likes__sum')

    tf = [u['likes'] / n_likes for u in user_likes]

    cat_likes = Category.objects.all().values('likes', 'depth').order_by('id')
    total_likes = Category.objects.all().aggregate(Sum('likes')).get('likes__sum')

    idf = [math.log(total_likes / (1 + c['likes'])) for c in cat_likes]

    tf_idf = [a*b for a, b in zip(tf, idf)]

    ma = max(tf_idf)
    mi = min(tf_idf)

    normalized_vector = [(x - mi) / (ma - mi) for x in tf_idf]

    depth_vector = [c['depth'] for c in cat_likes]

    return normalized_vector, depth_vector


def friends_in_common(solr, _user):
    user_id = _user.id

    user = solr.search(q='doc_type:user AND user_id:' + user_id, wt='python').docs[0]
    other_users = solr.search(q='doc_type:user AND -user_id:' + user_id, rows=100, wt='python')
    #user_likes = solr.search(q='type:page AND user_id:' + user_id, fl='page_id, category_list', rows=2000, wt='python')

    threads = []
    print("Friends in common for " + user['user_name'] + ": ")
    for other_user in other_users:
        thread = threading.Thread(target=friends_helper, args=(user, other_user))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()


def friends_helper(user, other_user):
    user_friend_list = user['friends_list']
    other_friend_list = other_user['friends_list']

    intersection = [friend for friend in user_friend_list if friend in other_friend_list]

    print("    with " + other_user['user_name'] + ": " + str(len(intersection)) + " friends.")


def get_mutual_friends(user1, user2, solr):
    users = solr.search(q='doc_type:user AND (user_id:{} OR user_id:{})'.format(user1, user2), rows=2, wt='python').docs
    user1_friend_list = users[0]['friends_list']
    user2_friend_list = users[1]['friends_list']

    mutual_friends = [friend for friend in user1_friend_list if friend in user2_friend_list]

    return mutual_friends



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