from .FbIndexManager import *
from Score_evaluator.Score_evaluator import *
from Score_evaluator.helpers import *
import time
import datetime


def index_data(user, solr, IndexManager):
    print('Indicizzando dati: ', user.token)
    try:
        # is_new_user = IndexManager.index_user()
        # if is_new_user:
        #     IndexManager.takeANDindexPages()
        #     IndexManager.takeANDindexPosts()
        #create_db_rows(solr, user)
        #remove_sparsity(user)
        calculate_similarity(solr, user)


    except Exception as ex:
        print(ex)
    print('finito!')
    return


