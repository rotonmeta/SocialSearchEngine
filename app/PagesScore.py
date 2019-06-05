import pysolr
from surprise import *
from surprise.model_selection import cross_validate

def raccomender_simulator(self, solr):
    dataCsv = solr.search(q="type: page",fl="user_id, page_id", wt="csv")
    reader = Reader(line_format='user_id page_id category_list', sep=',')
    data = Dataset.load_from_df(dataCsv, reader)
    cross_validate(BaselineOnly(), data, verbose=True)
