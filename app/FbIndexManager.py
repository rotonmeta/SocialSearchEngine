import threading
import io
from webpreview import *
from PIL import Image
import requests


def id_list_page(solr):
    response = solr.search(q='doc_type:content AND type:facebook_page', rows=pow(10, 6), wt='python')
    response2 = solr.search(q='doc_type:page', rows=pow(10, 6), wt='python')
    pages_list = []
    pages_link = []
    for page in response:
        link = str(page['link'])
        if link not in pages_link:
            pages_link.append(link)
        else:
            continue
        string = ''
        for page_user in response2:
            if page['link'] == page_user['link']:
                if str(page_user['user_id']) not in string:
                    string = string + ' ' + str(page_user['user_id'])
        doc = {}
        for key in page.keys():
            if str(key) == 'id' or 'version' in str(key):
                continue
            if str(key) == 'category_list':
                l = []
                for cat in page[key]:
                    l.append(cat)
                doc.update({str(key): l})
                continue
            try:
                doc.update({str(key): str(page[key])})
            except:
                try:
                    doc.update({str(key): page[key]})
                except:
                    doc.update({str(key): str(page[key])})

        doc.update({'user_id': string})
        pages_list.append(doc)
    query = 'doc_type:content AND type:facebook_page'
    solr.delete(q=query)
    solr.add(pages_list)


def web_description(doc):
    try:
        title, description, image = web_preview(doc['link'])
        doc.update({'description': description})
        doc.update({'image': image})
    except:
        doc.update({'description': 'None'})
        doc.update({'image': 'None'})


def pageUpdater(_list, page, header):
    for h in header:
        page.update(h)
    page.update({'page_id': page['id']})
    del page['id']
    page.update({'image': page['picture']['data']['url']})
    del page['picture']
    catListToAdd = []
    for cat in page['category_list']:
        catListToAdd.append(cat['id'])
    page.update({'category_list': catListToAdd})
    if 'about' in page.keys():
        page.update({'description': page['about']})
        del page['about']
    elif 'description' in page.keys():
        pass
    else:
        page.update({'description': '__null__'})
    _list.append(page)
    #print(page)


def postUpdater(postsToAdd, post, headerList):
    for h in headerList:
        post.update(h)

    if 'message' in post.keys():
        pass
    else:
        post.update({'message': '__null__'})

    if post['type'] == 'video':

        if 'source' in post.keys():
            if 'autoplay=1' in post['source']:
                post.update({'type': 'video_link'})
                del post['source']

        if 'full_picture' in post.keys() and 'description' in post.keys():
            post.update({'image': post['full_picture']})
        else:
            web_description(post)

    elif post['type'] == 'photo':
        if 'full_picture' in post.keys():
            post.update({'image': post['full_picture']})
            del post['full_picture']
            image_size(post)
        else:
            pass

    elif post['type'] == 'link':

        if 'full_picture' in post.keys() and 'description' in post.keys():
            post.update({'image': post['full_picture']})
        else:
            web_description(post)

    postsToAdd.append(post)
    #print(post)


def image_size(doc):
    try:
        image_content = requests.get(doc['image']).content
        image_stream = io.BytesIO(image_content)
        img = Image.open(image_stream)
        doc.update({'width': img.width})
        doc.update({'height': img.height})
        doc.update({'aspect_ratio': float(img.width) / img.height})
    except:
        doc.update({'width': 0}) #MODIFICATO da RM: era __null__ invece di 0, per tutte e 3
        doc.update({'height': 0})
        doc.update({'aspect_ratio': 0})


class FbIndexManager:

    def __init__(self, user, solr):
        self.user = user
        self.solr = solr

    def index_posts(self):
        print('starting post index')

        graph = self.user.graph
        user_id = str(self.user.id)
        name = str(self.user.name)
        profPic = str(self.user.profPic)

        getter = graph.get_object(id='me',
                                    fields='posts.limit(1000){name,description,source,'
                                           'message,type,id,link,full_picture,created_time}')

        if 'posts' not in getter.keys():
            return
        graphPosts = getter['posts']['data']

        while True:
            if 'paging' in getter.keys() and 'next' in getter['paging'].keys():
                getter = requests.get(getter['paging']['next']).json()
                graphPosts.extend(getter['data'])
                #print('if')
            elif 'posts' in getter.keys() and 'next' in getter['posts']['paging'].keys():
                getter = requests.get(getter['posts']['paging']['next']).json()
                graphPosts.extend(getter['data'])
                #print('else')
            else:
                #print('break')
                break

        # 2) CREO UNA LISTA DI ELEMENTI DA AGGIUNGERE
        headerList = []
        headerList.append({'doc_type': 'content'})
        headerList.append({'user_id': user_id})
        headerList.append({'user_name': name})
        headerList.append({'user_profile_picture': profPic})

        solrPosts = self.solr.search(q='doc_type:content AND -type:page AND user_id:' + user_id, rows=100000, wt='python')
        solrPostsIdList = []
        graphPostsIdList = []
        for post in graphPosts:
            graphPostsIdList.append(post['id'])

        for solrPost in solrPosts:
            if solrPost['id'] not in graphPostsIdList:
                self.solr.delete(q='doc_type:post AND user_id:' + user_id + ' AND id:' + solrPost['id'])
            else:
                solrPostsIdList.append(solrPost['id'])
        self.solr.commit()

        postsToAdd = []
        threads = []
        for post in graphPosts:
            if post['id'] in solrPostsIdList:
                continue
            elif (post['type'] == 'status') or ('link' not in post.keys()):
                del post
                continue
            else:
                thread = threading.Thread(target=postUpdater, args=(postsToAdd, post, headerList))
                thread.start()
                threads.append(thread)
        for t in threads:
            t.join()

        self.solr.add(postsToAdd)
        self.solr.commit()

        print('POST INDICIZZATI')

    def index_pages(self):
        print('inizia pages')

        # 1) SCARICO I DATI IN UN FILE JSON
        graph = self.user.graph
        user_id = self.user.id

        getter = graph.get_object(id='me',
                                    fields='likes.limit(99){created_time,location,picture.height(480){url},'
                                           'name,about,description,fan_count,category_list,link,id}')
        if 'likes' not in getter.keys():
            return
        graphPages = getter['likes']['data']

        while True:
            try:
                if 'paging' in getter.keys() and 'next' in getter['paging'].keys():
                    getter = requests.get(getter['paging']['next']).json()
                    graphPages.extend(getter['data'])
                elif 'likes' in getter.keys() and 'next' in getter['likes']['paging'].keys():

                    getter = requests.get(getter['likes']['paging']['next']).json()
                    graphPages.extend(getter['data'])
                else:
                    break
            except:
                pass

        # 2) CREO UNA LISTA DI ELEMENTI DA AGGIUNGERE

        headerList = []
        headerList.append({'doc_type': 'content'})
        headerList.append({'type': 'page'})
        headerList.append({'user_id': user_id})

        solrPages = self.solr.search(q='doc_type:content AND type:page AND user_id:' + user_id, rows=100000, wt='python')
        solrPagesIdList = []
        graphPagesIdList = []
        for page in graphPages:
            if page['id'] not in graphPagesIdList:
                graphPagesIdList.append(page['id'])
            else:
                del page

        for solrPage in solrPages:
            if solrPage['page_id'] not in graphPagesIdList:
                self.solr.delete(q='doc_type:page AND user_id:' + user_id + ' AND page_id:' + solrPage['page_id'])
            else:
                solrPagesIdList.append(solrPage['page_id'])
        self.solr.commit()

        pagesToAdd = []
        threads = []
        for page in graphPages:
            if page['id'] in solrPagesIdList:
                continue
            else:
                thread = threading.Thread(target=pageUpdater, args=(pagesToAdd, page, headerList))
                thread.start()
                threads.append(thread)

        for t in threads:
            t.join()

        self.solr.add(pagesToAdd)
        self.solr.commit()

        print('PAGINE INDICIZZATE')

    def index_user(self):
        result = self.solr.search(q='doc_type:user AND user_id:' + self.user.id)
        if not result:
            user_document = [{'doc_type': 'user',
                              'user_id': self.user.id,
                              'user_name': self.user.name}]

            self.solr.add(user_document)
            self.solr.commit()
            return True
        return False
