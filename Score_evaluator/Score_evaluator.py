import threading
from .models import Category, CategoryScore, Sum
from django.db.models import Q
from allauth.socialaccount.models import SocialAccount
from statsmodels.stats.weightstats import DescrStatsW
from numpy import column_stack
import math
from django import db


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
    to_add = CategoryScore(user=user, category=cat, likes=personal_likes, real_value=real)
    object_list.append(to_add)


def calculate_similarity(solr, user):
    user1_id = user.id
    users = solr.search(q='doc_type:user AND -user_id:' + user1_id, rows=200, wt='python')
    user1_vector, not_useful = get_vector_tf_idf(user1_id)

    threads = []
    for user2 in users:
        print('Calculating similarity for ' + user2['user_name'])
        thread = threading.Thread(target=_similarity_helper_2,
                                  args=(user1_id, user2['user_id'], user1_vector, solr))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    db.connections.close_all()


def _similarity_helper(user1_id, user2_id, solr):
    user1_vector = get_vector_tf(user1_id)
    user2_vector = get_vector_tf(user2_id)
    data = column_stack((user1_vector, user2_vector))

    result = DescrStatsW(data)[1][0]

    print('Pearson similarity ' + str(result))


def _similarity_helper_2(user1_id, user2_id, user1_vector, solr):
    query = 'doc_type:score AND users:({} AND {})'.format(user1_id, user2_id)
    solr.delete(q=query)

    user2_vector, depth_vector = get_vector_tf_idf(user2_id)
    data = column_stack((user1_vector, user2_vector))

    # result = DescrStatsW(data).corrcoef[1][0]
    result2 = DescrStatsW(data, weights=depth_vector).corrcoef[1][0]

    mutual_friends = get_mutual_friends(user1_id, user2_id, solr)

    new_score = [{
        'doc_type': 'score',
        'users': [user1_id, user2_id],
        'similarity': result2,
        'mutual_friends': mutual_friends,
        'friends_count': len(mutual_friends)
    }]

    solr.add(new_score)
    solr.commit()

    # print('Pearson similarity ' + str(user2_id) + ' ' + str(result))
    print('DescrStatsW ' + str(user2_id) + ' ' + str(result2))


def _similarity_helper_limited(user1_id, user2_id, solr):
    user1_vector, user2_vector, weight_vector = get_vector_limited(user1_id, user2_id)

    data = column_stack((user1_vector, user2_vector))
    result = DescrStatsW(data)[1][0]
    result2 = DescrStatsW(data, weights=weight_vector).corrcoef[1][0]

    print('Pearson similarity ' + str(user2_id) + ' ' + str(result))
    print('DescrStatsW ' + str(user2_id) + ' ' + str(result2))


def get_vector_limited(user1_id, user2_id):
    inner_qs = CategoryScore.objects\
        .filter(Q(likes__gt=0), Q(user__uid=user1_id) | Q(user__uid=user2_id))\
        .values('category_id')

    #FIRST USER
    user1_likes = CategoryScore.objects.filter(category__id__in=inner_qs, user__uid=user1_id)\
        .values('likes', 'category__id').order_by('category__id')
    n1_likes = user1_likes.aggregate(Sum('likes')).get('likes__sum')

    tf1 = [u['likes'] / n1_likes for u in user1_likes]
    #END FIRST USER
    #SECOND USER
    user2_likes = CategoryScore.objects.filter(category__id__in=inner_qs, user__uid=user2_id) \
        .values('likes').order_by('category__id')
    n2_likes = user2_likes.aggregate(Sum('likes')).get('likes__sum')

    tf2 = [u['likes'] / n2_likes for u in user2_likes]
    #END SECOND USER

    categories = user1_likes.values('category__id')

    cat_likes = CategoryScore.objects.filter(category__id__in=categories).values('category_id') \
        .annotate(likes_sum=Sum('likes')) \
        .values('category_id', 'likes_sum') \
        .order_by('category_id')

    total_likes = cat_likes.aggregate(total_likes=Sum('likes_sum')).get('total_likes')

    idf = [math.log(total_likes / (1 + c['likes_sum'])) for c in cat_likes]

    return tf1, tf2, idf


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
    # print('tf ' + str(user_id) + str(tf))
    cat_likes = CategoryScore.objects.values('category_id') \
        .annotate(likes_sum=Sum('likes')) \
        .values('category_id', 'category__depth', 'likes_sum') \
        .order_by('category_id')
    total_likes = CategoryScore.objects.all().aggregate(total_likes=Sum('likes')).get('total_likes')

    idf = [math.log(total_likes / (1 + c['likes_sum'])) for c in cat_likes]
    # print('idf ' + str(user_id) + str(idf))

    # tf_idf = [a*b for a, b in zip(tf, idf)]
    # print('tf-idf ' +str(user_id) + str(tf_idf))

    # ma = max(tf_idf)
    # mi = min(tf_idf)

    # normalized_vector = [(x - mi) / (ma - mi) for x in tf_idf]

    # depth_vector = [c['category__depth'] for c in cat_likes]
    #
    # idf_depth = [a*b for a, b in zip(idf, depth_vector)]

    return tf, idf
    #return normalized_vector, depth_vector


def get_mutual_friends(user1, user2, solr):
    mutual_friends = []
    users = solr.search(q='doc_type:user AND (user_id:{} OR user_id:{})'.format(user1, user2), rows=2, wt='python').docs
    if 'friends_list' not in users[0].keys() or 'friends_list' not in users[1].keys():
        return mutual_friends

    user1_friend_list = users[0]['friends_list']
    user2_friend_list = users[1]['friends_list']

    mutual_friends = [friend for friend in user1_friend_list if friend in user2_friend_list]

    return mutual_friends


# def remove_sparsity(user):
#     updated_categories = []
#     updated_category_scores = []
#
#     cat_scores = CategoryScore.objects.select_related('category__parent__parent').filter(user__uid=user.id)
#         #.values('category_id', 'likes', 'category__parent_id')
#     cat_scores_gt_0 = cat_scores.filter(likes__gt=0)
#
#     for elem in cat_scores_gt_0:
#         recursive_sparsity(elem, cat_scores, updated_categories, updated_category_scores)
#
#     Category.objects.bulk_update(updated_categories, ['likes'])
#     CategoryScore.objects.bulk_update(updated_category_scores, ['likes'])
#
#
# def recursive_sparsity(child, category_scores, update_cat_list, update_cat_score_list):
#     parent_id = child.category.parent_id
#
#     if parent_id is not None:
#         parent = category_scores.get(category_id=parent_id)
#         parent.likes = parent.likes + child.likes
#         cat_parent = Category.objects.get(id=parent_id)
#         cat_parent.likes = cat_parent.likes + child.likes
#
#         update_cat_list.append(cat_parent)
#         update_cat_score_list.append(parent)
#
#         recursive_sparsity(parent, category_scores, update_cat_list, update_cat_score_list)


# def friends_in_common(solr, _user):
#     user_id = _user.id
#
#     user = solr.search(q='doc_type:user AND user_id:' + user_id, wt='python').docs[0]
#     other_users = solr.search(q='doc_type:user AND -user_id:' + user_id, rows=100, wt='python')
#     #user_likes = solr.search(q='type:page AND user_id:' + user_id, fl='page_id, category_list', rows=2000, wt='python')
#
#     threads = []
#     print("Friends in common for " + user['user_name'] + ": ")
#     for other_user in other_users:
#         thread = threading.Thread(target=friends_helper, args=(user, other_user))
#         thread.start()
#         threads.append(thread)
#
#     for t in threads:
#         t.join()
#
#
# def friends_helper(user, other_user):
#     user_friend_list = user['friends_list']
#     other_friend_list = other_user['friends_list']
#
#     intersection = [friend for friend in user_friend_list if friend in other_friend_list]
#
#     print("    with " + other_user['user_name'] + ": " + str(len(intersection)) + " friends.")


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