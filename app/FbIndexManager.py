# -*- coding: utf-8 -*-
import facebook
import threading
import io
from webpreview import *
from PIL import Image
from .functions import *
import requests

#ToDO: use fb graph to get the results after the 100th. Use paging['next'] to get other 100 results and so on
#ToDo: try catch in tutti i response, e prova a migliorare il catch( except Exception as e)
#todo: modificaare classe Fbindexmanager in modo che prenda in input il token ed esegua facebook.graphAPI(token)..
#todo: ..cosi lo esegue solo una volta e non istanzia la classe se il token non è valido.


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
    if 'about' in page.keys():
        page.update({'description': page['about']})
        del page['about']
    elif 'description' in page.keys():
        pass
    else:
        page.update({'description': '__null__'})
    _list.append(page)
    print(page)


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
    print(post)


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

    def takeANDindexPosts(self):
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
                print('if')
            elif 'posts' in getter.keys() and 'next' in getter['posts']['paging'].keys():
                getter = requests.get(getter['posts']['paging']['next']).json()
                graphPosts.extend(getter['data'])
                print('else')
            else:
                print('break')
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

        # 3) FORMATTO E AGGIUNGO GLI ELEMENTI DELLA LISTA AL FILE JSON

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

    def takeANDindexPages(self):
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

        # 3) FORMATTO E AGGIUNGO 'DOC_TYPE' E 'USER_ID' AL FILE JSON
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
        # 4) INDICIZZO IN SOLR
        #   E AGGIORNO CONTENUTI

        print('PAGINE INDICIZZATE')

    def takeANDindexFriends(self):
        print('inizia friends')

        # 1) SCARICO I DATI IN UN FILE JSON
        graph = self.user.graph
        user_id = self.user.id

        tmp_json = graph.get_object(id='me', fields='friends.limit(5000){id},id')

        if len(tmp_json['friends']['data']) == 0:
            id_friends = 0
            print('no friends')
        else:
            id_friends = []
            for friend in tmp_json['friends']['data']:
                id_friends.append(friend['id'])

        query = 'doc_type:friends_list AND user_id:' + str(tmp_json['id'])
        self.solr.delete(q=query)
        self.solr.add([{'doc_type': 'friends_list',
                        'user_id': user_id,
                        'friends_id': id_friends,
                        'friends_count': tmp_json['friends']['summary']['total_count'],
                        }])
        self.solr.commit()

        print('LISTA AMICI INDICIZZATA')

    def takeANDindexAge(self):
        print('inizia age')

        # 1) SCARICO I DATI IN UN FILE JSON
        graph = self.user.graph
        user_id = self.user.id

        tmp_json = graph.get_object(id='me', fields='id,birthday')
        if 'birthday' not in tmp_json.keys():
            return
        index = 0
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        string = str(tmp_json['birthday'])
        for i in range(0, len(string)):
            if string[i] not in numbers:
                index = i
        try:
            age = int(string[index + 1:])
        except:
            return
        query = 'doc_type:age AND user_id:' + str(tmp_json['id'])
        print('add age to solr')
        self.solr.delete(q=query)
        self.solr.add([{'doc_type': 'age',
                        'user_id': user_id,
                        'age': age,
                        }])
        self.solr.commit()

        print('ETA INDICIZZATA')

    def takeANDindexProfPic(self):
        # 1) SCARICO I DATI IN UN FILE JSON

        user_id = self.user.id
        profPic = self.user.profPic
        self.solr.add([{'doc_type': 'profile_picture',
                        'user_id': user_id,
                        'link': profPic,
                        }])

        self.solr.commit()

        print('PROFPIC INDICIZZATA')

    def takeANDindexPlaces(self):
        print('inizia places')

        # 1) SCARICO I DATI IN UN FILE JSON
        graph = self.user.graph
        user_id = self.user.id

        tmp_json = graph.get_object(id='me', fields='posts{place,created_time},tagged_places,id')

        # 2) CREO UNA LISTA DI ELEMENTI DA AGGIUNGERE
        List = []
        List.append({'doc_type': 'place'})
        List.append({'user_id': user_id})
        tmp_json2 = []

        if 'posts' not in tmp_json.keys():
            return
        tmp_json1 = tmp_json['posts']['data']
        for tmp in tmp_json1:
            if 'place' not in tmp.keys():
                continue
            place = tmp['place']
            tmp.update({'place_id': place['id']})
            tmp.update({'name': place['name']})
            place = place['location']
            if 'city' not in place.keys():
                tmp_place = get_place(place['latitude'], place['longitude'])
                place.update({'city': tmp_place[0]})
                place.update({'country': tmp_place[1]})
            del place['latitude']
            del place['longitude']
            tmp.update(place)
            del tmp['place']
            del tmp['id']
            for j in range(0, len(List)):
                tmp.update(List[j])
            tmp_json2.append(tmp)

        dates_list = []
        for place in tmp_json2:
            dates_list.append(place['created_time'])

        if 'tagged_places' not in tmp_json.keys():
            return
        tmp_json1 = tmp_json['tagged_places']['data']
        for tmp in tmp_json1:
            if tmp['created_time'] in dates_list:
                continue
            place = tmp['place']
            tmp.update({'place_id': place['id']})
            tmp.update({'created_time': str(tmp['created_time'])})
            tmp.update({'name': place['name']})
            place = place['location']
            if 'city' not in place.keys():
                tmp_place = get_place(place['latitude'], place['longitude'])
                place.update({'city': tmp_place[0]})
                place.update({'country': tmp_place[1]})
            del place['latitude']
            del place['longitude']
            tmp.update(place)
            del tmp['place']
            del tmp['id']
            for j in range(0, len(List)):
                tmp.update(List[j])
            tmp_json2.append(tmp)

        # 4) INDICIZZO IN SOLR
        query = 'doc_type:place AND user_id:' + str(user_id)
        self.solr.delete(q=query)

        self.solr.add(tmp_json2)
        self.solr.commit()

        print('LUOGHI INDICIZZATI')
