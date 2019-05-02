# -*- coding: utf-8 -*-


def age_distance(solr, userA_id, userB_id):
    ageA = solr.search(q='doc_type:age AND user_id:' + str(userA_id), rows=pow(10, 6), wt='python')
    ageB = solr.search(q='doc_type:age AND user_id:' + str(userB_id), rows=pow(10, 6), wt='python')

    if len(ageA) == 0 or len(ageB) == 0:
        return 'none'

    for year in ageA:
        A = year['age']
    for year in ageB:
        B = year['age']

    try:
        distance = abs(int(A) - int(B))
    except:
        distance = abs(int(A) - int(B))
    return distance


def update_age_distance(solr, usersID_list):
    docs_list = []

    for i in range(0, len(usersID_list)):
        for j in range(i + 1, len(usersID_list)):
            a = usersID_list[i]
            b = usersID_list[j]
            query = "(userA:" + str(a) + " AND userB:" + str(b) + ") OR (userB:" + str(a) + " AND userA:" + str(b) + ")"
            try:
                solr.delete(q="type:age_distance AND (" + query + ")")
            except:
                print('primo aggiornamento')
                score = age_distance(solr, a, b)
                if str(score) == 'none':
                    continue
                new_doc = {"doc_type": 'score', 'type': "age_distance", "userA": a, "userB": b, "score": score}
                docs_list.append(new_doc)
        solr.add(docs_list)
