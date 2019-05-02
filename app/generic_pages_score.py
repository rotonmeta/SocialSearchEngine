# -*- coding: utf-8 -*-
from .functions import *


def print_vect(V):
    l = []
    for i in V:
        if i['page_id'] in l:
            continue
        else:
            l.append(i['page_id'])
        if 'name' not in i.keys():
            print(i['page_id'], occurrences(V, 'page_id', i['page_id']))
        else:
            print(i['name'], occurrences(V, 'page_id', i['page_id']))


def similarity_generic_pages(A, B, cat, coeff):
    tmp = []
    tmp_A = []
    for a in A:
        if a[cat] not in tmp:
            tmp_A.append({'name': a['name'], cat: a[cat], 'fan_count': a['fan_count'], 'likes': 0})
            tmp.append(a[cat])

    for b in B:
        if b[cat] not in tmp:
            tmp_A.append({'name': b['name'], cat: b[cat], 'fan_count': b['fan_count'], 'likes': 0})
            tmp.append(b[cat])
    tmp_B = tmp_A[:]

    for i in range(0, len(tmp_A)):
        for a in A:
            if tmp_A[i][cat] == a[cat]:
                tmp_A[i] = {'name': tmp_A[i]['name'], cat: tmp_A[i][cat], 'fan_count': tmp_A[i]['fan_count'],
                            'likes': tmp_A[i]['likes'] + 1}

    for i in range(0, len(tmp_B)):
        for b in B:
            if tmp_B[i][cat] == b[cat]:
                tmp_B[i] = {'name': tmp_B[i]['name'], cat: tmp_B[i][cat], 'fan_count': tmp_B[i]['fan_count'],
                            'likes': tmp_B[i]['likes'] + 1}

    if cat == 'page_id':  # per page_id calcolo un indice di jaccard
        intersect = 0.0
        union = 0.0
        for i in range(0, len(tmp_B)):
            union += 1.0 / len(str(tmp_A[i]['fan_count']))
            if tmp_B[i]['likes'] == tmp_A[i]['likes']:
                coeff[0] += coeff[0]
                intersect += 1.0 / len(str(tmp_A[i]['fan_count']))
        if int(union) == 0:
            coeff[0] = 0
            return union
        return intersect / union

    score = 0.0
    norm = 0.0

    for i in range(0, len(tmp_B)):
        if min(tmp_A[i]['likes'], tmp_B[i]['likes']) > 0:
            coeff[0] += coeff[0]
            score += min(tmp_A[i]['likes'], tmp_B[i]['likes'])
        else:
            norm += 1

    if int(norm + score) == 0:
        coeff[0] = 0
        return 0
    return score / (norm + score)


def update_vector(vector, cat, found_list):
    A = []
    for a in vector:
        if a[cat] not in found_list:
            for c in a['category_list']:
                A.append({'name': a['name'], 'category': c, 'fan_count': 1})
    return A


def generic_pages_score(solr, userA_id, userB_id):
    pagesA = solr.search(q='doc_type:page AND type:generic AND user_id:' + str(userA_id), rows=pow(10, 6), wt='python')
    pagesB = solr.search(q='doc_type:page AND type:generic AND user_id:' + str(userB_id), rows=pow(10, 6), wt='python')
    tmp_A = []
    tmp_B = []

    for i in pagesA:
        tmp_A.append(
            {'page_id': i['page_id'], 'name': i['name'], 'genre': i['genre'], 'category_list': i['category_list'],
             'fan_count': i['fan_count']})

    for i in pagesB:
        tmp_B.append(
            {'page_id': i['page_id'], 'name': i['name'], 'genre': i['genre'], 'category_list': i['category_list'],
             'fan_count': i['fan_count']})

    score = 0.0

    # ////////////   PRIMO CICLO: CONFRONTO place_id

    found_list = []  # lista delle corripondenze trovate
    cat = 'page_id'
    coeff1 = [1.0]
    similarity = similarity_generic_pages(tmp_A, tmp_B, cat, coeff1)
    score = score + coeff1[0] * similarity

    for a in tmp_A:
        found = 0
        for b in tmp_B:
            if a[cat] == b[cat]:
                found = 1
                break
        if found == 1 and (a[cat] not in found_list):
            found_list.append(a[cat])

    # AGGIORNAMENTO DEI VETTORI
    tmp_A = update_vector(tmp_A, cat, found_list)
    tmp_B = update_vector(tmp_B, cat, found_list)
    # ////////////   SECONDO CICLO: CONFRONTO city
    cat = 'category'
    coeff2 = [0.2]
    similarity = similarity_generic_pages(tmp_A, tmp_B, cat, coeff2)
    score = score + coeff2[0] * similarity

    if (coeff1[0] + coeff2[0]) == 0:
        score = 0.0
    else:
        score = score / (coeff1[0] + coeff2[0])
    return score


def update_generic_pages_score(solr, usersID_list):
    docs_list = []
    for i in range(0, len(usersID_list)):
        for j in range(i + 1, len(usersID_list)):
            a = usersID_list[i]
            b = usersID_list[j]
            query = "(userA:" + str(a) + " AND userB:" + str(b) + ") OR (userB:" + str(a) + " AND userA:" + str(b) + ")"
            try:
                solr.delete(q="type:generic_pages_score AND (" + query + ")")
            except:
                print ('primo aggiornamento')
            score = generic_pages_score(solr, a, b)
            new_doc = {"doc_type": 'score', 'type': "generic_pages_score", "userA": a, "userB": b, "score": score}
            docs_list.append(new_doc)
    solr.add(docs_list)
