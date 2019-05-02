# -*- coding: utf-8 -*-
from .functions import *


def p(V):
    l = []
    for i in V:
        if i['place_id'] in l:
            continue
        else:
            l.append(i['place_id'])
        if 'name' not in i.keys():
            print(i['place_id'], i['city'], occurrences(V, 'place_id', i['place_id']))
        else:
            print(i['city'], occurrences(V, 'place_id', i['place_id']))


def cosine_similarity_places(A, B, cat, coeff):
    tmp_A = []
    for place in A:
        if place[cat] not in tmp_A:
            tmp_A.append(place[cat])
    for place in B:
        if place[cat] not in tmp_A:
            tmp_A.append(place[cat])
    tmp = tmp_A[:]
    tmp_A = []
    for place in tmp:
        tmp_A.append({cat: place, 'occurrences': 0})
    tmp_B = tmp_A[:]

    for i in range(0, len(tmp_A)):
        for a in A:
            if tmp_A[i][cat] == a[cat]:
                tmp_A[i] = {cat: a[cat], 'occurrences': tmp_A[i]['occurrences'] + 1}

    for i in range(0, len(tmp_B)):
        for b in B:
            if tmp_B[i][cat] == b[cat]:
                tmp_B[i] = {cat: b[cat], 'occurrences': tmp_B[i]['occurrences'] + 1}

    score = 0.0
    norm = 0.0

    for i in range(0, len(tmp_B)):
        if min(tmp_A[i]['occurrences'], tmp_B[i]['occurrences']) > 0:
            coeff[0] += coeff[0]
            score += min(tmp_A[i]['occurrences'], tmp_B[i]['occurrences'])
        else:
            norm += 1

    if int(norm + score) == 0:
        coeff[0] = 0
        return 0
    return score / (norm + score)


def update_vector(vector, cat, found_list):
    A = []  # rimuovo i duplicati dai vettori

    for a in vector:
        if (a not in A) and (a[cat] not in found_list):
            A.append(a)

    vector = A
    for a in vector:  # cancello la categoria analizzata da ogni elemento dei vettori
        del a[cat]
    return vector


def places_score(solr, userA_id, userB_id):
    placesA = solr.search(q='doc_type:place AND user_id:' + str(userA_id), rows=pow(10, 6), wt='python')
    placesB = solr.search(q='doc_type:place AND user_id:' + str(userB_id), rows=pow(10, 6), wt='python')
    tmp_A = []
    tmp_B = []

    for i in placesA:
        tmp_A.append({'place_id': i['place_id'], 'city': i['city'], 'country': i['country']})

    for i in placesB:
        tmp_B.append({'place_id': i['place_id'], 'city': i['city'], 'country': i['country']})

    if len(tmp_A) + len(tmp_B) == 0:
        return 0
    score = 0
    # ////////////   PRIMO CICLO: CONFRONTO place_id

    found_list = []  # lista delle corripondenze trovate
    cat = 'place_id'
    coeff1 = [1.0]

    similarity = cosine_similarity_places(tmp_A, tmp_B, cat, coeff1)
    score = score + coeff1[0] * similarity

    for a in tmp_A:
        if (a in tmp_B) and (a[cat] not in found_list):
            found_list.append(a[cat])

    # AGGIORNAMENTO DEI VETTORI
    tmp_A = update_vector(tmp_A, cat, found_list)
    tmp_B = update_vector(tmp_B, cat, found_list)

    # ////////////   SECONDO CICLO: CONFRONTO city

    found_list = []
    cat = 'city'
    coeff2 = [0.5]

    similarity = cosine_similarity_places(tmp_A, tmp_B, cat, coeff2)
    score = score + coeff2[0] * similarity
    for a in tmp_A:
        if (a in tmp_B) and (a[cat] not in found_list):
            found_list.append(a[cat])

    # AGGIORNAMENTO DEI VETTORI
    tmp_A = update_vector(tmp_A, cat, found_list)
    tmp_B = update_vector(tmp_B, cat, found_list)

    # ////////////   TERZO CICLO: CONFRONTO country

    cat = 'country'
    coeff3 = [0.25]
    similarity = cosine_similarity_places(tmp_A, tmp_B, cat, coeff3)
    score = score + coeff3[0] * similarity
    if (coeff1[0] + coeff2[0] + coeff3[0]) == 0:
        score = 0.0
    else:
        score = score / (coeff1[0] + coeff2[0] + coeff3[0])

    return score


def update_places_score(solr, usersID_list):
    docs_list = []
    for i in range(0, len(usersID_list)):
        for j in range(i + 1, len(usersID_list)):
            a = usersID_list[i]
            b = usersID_list[j]
            query = "(userA:" + str(a) + " AND userB:" + str(b) + ") OR (userB:" + str(a) + " AND userA:" + str(b) + ")"
            try:
                solr.delete(q="type:places_score AND (" + query + ")")
            except:
                print('primo aggiornamento')
            score = places_score(solr, a, b)
            new_doc = {"doc_type": 'score', 'type': "places_score", "userA": a, "userB": b, "score": score}
            docs_list.append(new_doc)
    solr.add(docs_list)
