from Score_evaluator.Score_evaluator import *


def index_data(user, solr, index_manager):
    print('Indexing data of ', user.name)
    try:
        is_new_user = index_manager.index_user()
        if is_new_user:
            index_manager.index_pages()
            create_db_rows(solr, user)
            index_manager.index_posts()
        calculate_similarity(solr, user)

    except Exception as ex:
        print(ex)
        index_data(user, solr, index_manager)
    print('Indexing finished!')
    return


