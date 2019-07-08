import threading
import pysolr
import math

solr = pysolr.Solr('https://solr.socialsearch.blog/solr/demo3/')


def test(v=1):
    users = solr.search(q='doc_type:user', fl='user_name, user_id', rows=50, wt='python')

    threads = []
    ndcg_values = []

    if v == 1:
        target_function = nDCG
    elif v == 2:
        target_function = nDCG_friends
    else:
        print('Error: v can only be 1 or 2!')
        return

    for user in users:
        thread = threading.Thread(target=target_function, args=(user, ndcg_values))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    ndcg_sum = 0
    for elem in ndcg_values:
        elem_value = list(elem.values())[0]
        ndcg_sum = ndcg_sum + elem_value
        if elem_value == 0:
            ndcg_values.remove(elem)

    average_ndcg = ndcg_sum / len(ndcg_values)

    # print(ndcg_values)
    print('Average nDCG: ' + str(average_ndcg))


def nDCG(user, ndcg_values):
    reference_scores = solr.search(q='doc_type:score AND users:{}'.format(user['user_id']),
                         fl='users, similarity, friends_count',
                         sort='friends_count desc, similarity desc',
                         rows=50, wt='python')

    r = 10
    for score in reference_scores:
        if r >= 0:
            score.update({'ranking': r})
            r = r - 1
        else:
            score.update({'ranking': 0})

    predicted_scores = sorted(reference_scores, key=lambda s: s['similarity'], reverse=True)

    #print('Predicted scores: ' + str(predicted_scores))

    ndcg = DCG(predicted_scores)/DCG(reference_scores)

    print('nDCG of ' + user['user_name'] + ': ' + str(ndcg))

    ndcg_values.append({user['user_name']: ndcg})


def nDCG_friends(user, ndcg_values):
    reference_scores = solr.search(q='doc_type:score AND users:{}'.format(user['user_id']),
                                   fl='users, similarity, friends_count',
                                   sort='friends_count desc',
                                   rows=50, wt='python')

    for score in reference_scores:
            if 'friends_count' in score.keys():
                score.update({'ranking': score['friends_count']})
            else:
                score.update({'ranking': 0})

    predicted_scores = sorted(reference_scores, key=lambda s: s['similarity'], reverse=True)

    #print('Predicted scores: ' + str(predicted_scores))

    ndcg = (DCG(predicted_scores) / DCG(reference_scores)) if DCG(reference_scores) != 0 else 0

    print('nDCG_friends of ' + user['user_name'] + ': ' + str(ndcg))

    ndcg_values.append({user['user_name']: ndcg})


def DCG(ranking, k=10):
    _list = list(ranking)[:k]

    dcg = 0
    for i in range(k):
        dcg = dcg + (_list[i]['ranking'] / math.log(i+2, 2))

    return dcg



