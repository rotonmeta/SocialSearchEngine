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


def web_description(_list, doc, link):
    try:
        title, description, image = web_preview(link)
        doc.update({'description': description})
        doc.update({'image': image})
    except:
        doc.update({'description': '__null__'})
        doc.update({'image': 'None'})
    _list.append(doc)
    print(doc)


def image_size(_list, doc, link):
    try:
        image_content = requests.get(link).content
        image_stream = io.BytesIO(image_content)
        img = Image.open(image_stream)
        doc.update({'width': img.width})
        doc.update({'height': img.height})
        doc.update({'aspect_ratio': float(img.width) / img.height})
    except:
        doc.update({'width': 0}) #MODIFICATO da RM: era __null__ invece di 0, per tutte e 3
        doc.update({'height': 0})
        doc.update({'aspect_ratio': 0})
    _list.append(doc)


class FbIndexManager():
    solr = 'istanza di solr'

    def __init__(self, solr):
        self.solr = solr
        #todo:aggiungi graph qui

    def token_is_valid(self, token):
        url = 'https://graph.facebook.com/me?access_token=' + str(token)
        r = requests.get(url)
        if r.status_code == 400:
            print('token non valido')
            return 0
        return 1

    def takeANDindexPosts(self, token):
        print('starting post index')
        if self.token_is_valid(token) == 0:
            return
        # 1) SCARICO I DATI IN UN FILE JSON
        graph = facebook.GraphAPI(access_token=token)
        getter = graph.get_object(id='me',
                                    fields='name,posts.limit(999999){status_type,story_tags,name,place,'
                                           'reactions{id},source,message,type,id,link,full_picture,created_time},id')
        user_id = getter['id']
        name = getter['name']

        if 'posts' not in getter.keys():
            return
        tmp_json = getter['posts']['data']

        while True:
            if 'paging' in getter.keys() and 'next' in getter['paging'].keys():
                getter = requests.get(getter['paging']['next']).json()
                tmp_json.extend(getter['data'])
            elif 'posts' in getter.keys() and 'next' in getter['posts']['paging'].keys():
                getter = requests.get(getter['posts']['paging']['next']).json()
                tmp_json.extend(getter['data'])
            else:
                break

        # 2) CREO UNA LISTA DI ELEMENTI DA AGGIUNGERE
        List = []
        List.append({'doc_type': 'post'})
        List.append({'user_id': str(user_id)})
        response = self.solr.search(q='doc_type:post AND user_id:' + str(user_id), rows=100000, wt='python')
        posts_id_list = []
        Posts = []

        for tmp in tmp_json:
            Posts.append(str(tmp['id']))

        if response is not []:  # aggiunto da rm
            for post in response:
                if str(post['id']) not in Posts:
                    self.solr.delete(q='doc_type:post AND user_id:' + str(user_id) + ' AND id:' + str(post['id']))
                posts_id_list.append(post['id'])

        # 3) FORMATTO E AGGIUNGO GLI ELEMENTI DELLA LISTA AL FILE JSON

        Posts = []
        sd = 0
        for tmp in tmp_json:
            print(str(sd))
            if tmp['type'] == 'status':
                del tmp
                continue
            tmp.update({'data': str(tmp['created_time'])})
            del tmp['created_time']

            if 'place' in tmp.keys():
                if 'id' in tmp['place']:
                    place = tmp['place']
                    tmp.update({'place_id': place['id']})
                else: #aggiunto da rm
                    tmp.update({'place_id': '__null__'})
                del tmp['place']

            if 'reactions' in tmp.keys():
                tmp.update({'likes_users_id': tmp['reactions']['data']})
                del tmp['reactions']

            if 'story_tags' in tmp.keys():
                string = ''
                for j in range(0, len(tmp['story_tags'])):
                    if 'type' in tmp['story_tags'][j].keys():   #aggiunto da rm
                        if tmp['story_tags'][j]['type'] == 'user':
                            string = string + tmp['story_tags'][j]['id'] + ' '
                del tmp['story_tags']
                tmp.update({'tags_users_id': string})

            for j in range(0, len(List)):
                tmp.update(List[j])

            found = 0
            for page in posts_id_list:
                if str(tmp['id']) == str(page):
                    found = 1
                    break
            if found == 0:
                Posts.append(tmp)

        # 4) INDICIZZO IN SOLR
        #     E AGGIORNO CONTENUTI
        self.solr.add(Posts)
        self.solr.commit()
        print('post aggiunti')

        self.takeANDindexPlaces(token)
        response = self.solr.search(q='doc_type:profile_picture AND user_id:' + str(user_id), rows=10, wt='python')
        profPic = response.docs[0]['link2']
        link_list = []
        nome = str(graph.get_object(id='me')['name'])

        doc_list = []
        threads = []
        Contents = []
        print('inizia aggiunta post come content')
        for post in Posts:
            doc = {}
            doc.update({'doc_type': 'content'})
            doc.update({'type': post['type']})
            doc.update({'user_id': user_id})
            doc.update({'user_name': name})
            doc.update({'user_profile_picture': profPic})
            doc.update({'data': post['data']})

            if post['type'] == 'link':
                if 'status_type' in post.keys():
                    if 'mobile_status' in post['status_type']:
                        continue
            if ('name' in post.keys()) and (post['type'] != 'photo') and (post['name'] not in nome):
                doc.update({'name': post['name']})

            if 'message' in post.keys():
                doc.update({'message': post['message']})

            elif post['type'] != 'status':
                doc.update({'message': '__null__'})

            else:
                continue

            if 'place_id' in post.keys():
                response = self.solr.search(q='doc_type:place AND place_id:' + str(post['place_id']), rows=1,
                                            wt='python')
                for place in response:
                    if 'name' in place.keys():
                        doc.update({'place_name': place['name']})
                    doc.update({'city': place['city']})
                    doc.update({'country': place['country']})

            if post['type'] == 'video':

                response = self.solr.search(q='doc_type:content AND link:"' + post['link'] + '"', rows=100000,
                                            wt='python')
                if 'source' in post.keys():

                    if 'autoplay=1' in str(post['source']):

                        doc.update({'type': 'video_link'})
                        doc.update({'link': post['link']})
                    else:
                        doc.update({'link': post['source']})

                    if len(response) == 0 and doc['link'] not in link_list:
                        if 'autoplay=1' in str(post['source']):
                            thread = threading.Thread(target=web_description, args=(doc_list, doc, post['link']))
                            thread.start()
                            threads.append(thread)
                            #except threading.ThreadError as ex:
                            #    threads[0].join()
                            #    print('join after number of threads exceeded. Error: ' + str(ex))

                        else:
                            doc.update({'image': post['full_picture']})
                            Contents.append(doc)
                        link_list.append(doc['link'])

                else:
                    doc.update({'link': post['link']})
                    doc.update({'image': post['full_picture']})
                    if len(response) == 0 and doc['link'] not in link_list:
                        Contents.append(doc)
                        link_list.append(doc['link'])

            elif post['type'] == 'photo':
                doc.update({'image': post['full_picture']})
                try:
                    response = self.solr.search(q='doc_type:content AND image:"' + doc['image'] + '"', rows=100000,
                                                wt='python')
                except Exception as ex:
                    print('Errore nella ricerca su solr' + str(ex))
                    continue

                if len(response) == 0 and doc['image'] not in link_list:
                    thread = threading.Thread(target=image_size, args=(doc_list, doc, doc['image']))
                    #try:
                    thread.start()
                    threads.append(thread)
                    #except threading.ThreadError as ex:
                    #    threads[0].join()
                    #    print('join after number of threads exceeded. Error: ' + str(ex))

                    link_list.append(doc['image'])

            #elif post['type'] == 'status':
            #    try:
            #        response = self.solr.search(q='doc_type:content AND message:"' + doc['message'].replace(':', ';') + '"', rows=100000,
            #                                wt='python')
            #    except Exception as ex:
            #        print('Errore nella ricerca su solr' + str(ex))
            #        continue

            #    if len(response) == 0 and doc['message'] not in link_list:
            #        Contents.append(doc)
            #        link_list.append(doc['message'])

            elif post['type'] == 'link':
                if 'link' in post.keys(): #aggiunto da rm
                    doc.update({'link': post['link']})
                    try:
                        response = self.solr.search(q='doc_type:content AND link:"' + doc['link'] + '"', rows=100000,
                                                wt='python')
                    except:
                        print('Errore nella ricerca su solr')
                        continue

                    if len(response) == 0 and doc['link'] not in link_list:
                        thread = threading.Thread(target=web_description, args=(doc_list, doc, post['link'],))
                        #try:
                        thread.start()
                        threads.append(thread)
                        #except threading.ThreadError as ex:
                        #    threads[0].join()
                        #    print('join after number of threads exceeded. Error: ' + str(ex))

                        link_list.append(doc['link'])
                else:
                    doc.update({'link': '__null__'})

            for t in threads:
                t.join()

        for doc in doc_list:
            Contents.append(doc)

        self.solr.add(Contents)
        self.solr.commit()
        query = 'doc_type:content AND type:(facebook_page or link) -description:*'
        self.solr.delete(q=query)
        self.solr.commit()
        print('POST INDICIZZATI')

    def takeANDindexPages(self, token):
        if self.token_is_valid(token) == 0:
            return

        print('inizia pages')

        # 1) SCARICO I DATI IN UN FILE JSON
        graph = facebook.GraphAPI(access_token=token)
        getter = graph.get_object(id='me',
                                    fields='likes.limit(999999){created_time,description,location,'
                                           'name,fan_count,category_list,link,genre,id},id')
        if 'likes' not in getter.keys():
            return
        tmp_json = getter['likes']['data']
        user_id = getter['id']

        while True:
            if 'paging' in getter.keys() and 'next' in getter['paging'].keys():
                getter = requests.get(getter['paging']['next']).json()
                tmp_json.extend(getter['data'])
            elif 'likes' in getter.keys() and 'next' in getter['likes']['paging'].keys():
                getter = requests.get(getter['likes']['paging']['next']).json()
                tmp_json.extend(getter['data'])
            else:
                break

        cat_getter = graph.get_object(id='me',
                                      fields='music.limit(999999),television.limit(999999),movies.limit(999999),books.limit(999999)')

        categories = cat_getter.copy()

        for key in cat_getter.keys():
            if key == 'id':
                break
            tmp_cat_getter = cat_getter.copy()
            while True:
                if 'paging' in tmp_cat_getter.keys() and 'next' in tmp_cat_getter['paging'].keys():
                    tmp_cat_getter = requests.get(tmp_cat_getter['paging']['next']).json()
                    categories[str(key)]['data'].extend(tmp_cat_getter['data'])
                elif str(key) in tmp_cat_getter.keys() and 'next' in tmp_cat_getter[str(key)]['paging'].keys():
                    tmp_cat_getter = requests.get(tmp_cat_getter[str(key)]['paging']['next']).json()
                    categories[str(key)]['data'].extend(tmp_cat_getter['data'])
                else:
                    break

        Music_id = []
        Movies_id = []
        Books_id = []
        TV_id = []
        if 'music' in categories.keys():
            for i in categories['music']['data']:
                Music_id.append(str(i['id']))
        if 'books' in categories.keys():
            for i in categories['books']['data']:
                Books_id.append(str(i['id']))
        if 'television' in categories.keys():
            for i in categories['television']['data']:
                TV_id.append(str(i['id']))
        if 'movies' in categories.keys():
            for i in categories['movies']['data']:
                Movies_id.append(str(i['id']))

        # 2) CREO UNA LISTA DI ELEMENTI DA AGGIUNGERE

        List = []
        List.append({'doc_type': 'page'})
        List.append({'user_id': user_id})
        response = self.solr.search(q='doc_type:page AND user_id:' + str(user_id), rows=100000, wt='python')
        posts_id_list = []
        Pages = []
        for tmp in tmp_json:
            Pages.append(str(tmp['id']))

        for page in response:
            if str(page['page_id']) not in Pages:
                self.solr.delete(
                    q='doc_type:page AND user_id:' + str(user_id) + ' AND page_id:' + str(page['page_id']))
            posts_id_list.append(page['page_id'])

        # 3) FORMATTO E AGGIUNGO 'DOC_TYPE' E 'USER_ID' AL FILE JSON
        Pages = []
        for tmp in tmp_json:
            category_list = []
            if str(tmp['id']) in Music_id:
                tmp.update({'type': 'music'})
            elif str(tmp['id']) in TV_id:
                tmp.update({'type': 'television'})
            elif str(tmp['id']) in Books_id:
                tmp.update({'type': 'book'})
            elif str(tmp['id']) in Movies_id:
                tmp.update({'type': 'movie'})
            else:
                tmp.update({'type': 'generic'})
            tmp.update({'page_id': tmp['id']})
            del tmp['id']
            if 'created_time' in tmp.keys():
                tmp.update({'data': str(tmp['created_time'])})
                del tmp['created_time']
            else:
                tmp.update({'data': '__null__'})
            if 'category_list' in tmp.keys():
                for cat in tmp['category_list']:
                    category_list.append(cat['name'])
            if 'genre' not in tmp.keys():
                tmp.update({'genre': '__null__'})
            if 'location' in tmp.keys():
                if 'city' in tmp['location'].keys():
                    tmp.update({'city': tmp['location']['city']})
                if 'country' in tmp['location'].keys():
                    tmp.update({'country': tmp['location']['country']})
                del tmp['location']
            tmp.update({'category_list': category_list})
            for j in range(0, len(List)):
                tmp.update(List[j])

            found = 0
            for page in posts_id_list:
                if str(tmp['page_id']) == str(page):
                    found = 1
                    break
            if found == 0:
                Pages.append(tmp)
        self.solr.add(Pages)
        self.solr.commit()

        # 4) INDICIZZO IN SOLR
        #   E AGGIORNO CONTENUTI
        doc_list = []
        threads = []
        Contents = []

        for post in Pages: #aggiunto da RM. era Pages
            doc = {}
            doc.update({'doc_type': 'content'})
            doc.update({'type': 'facebook_page'})
            doc.update({'link': post['link']})
            doc.update({'name': post['name']})
            doc.update({'category_list': post['category_list']})
            doc.update({'genre': post['genre']})

            thread = threading.Thread(target=web_description, args=(doc_list, doc, post['link']))
            #try:
            thread.start()
            threads.append(thread)
            #except Exception as ex:
            #    threads[0].join()
            #    print('join after number of threads exceeded. Error: ' + str(ex))

        for t in threads:
            t.join()
        for doc in doc_list:
            Contents.append(doc)

        self.solr.add(Contents)
        self.solr.commit()
        id_list_page(self.solr)

        print('PAGINE INDICIZZATE')

    def takeANDindexFriends(self, token):
        if self.token_is_valid(token) == 0:
            return
        print('inizia friends')

        # 1) SCARICO I DATI IN UN FILE JSON
        graph = facebook.GraphAPI(access_token=token)
        tmp_json = graph.get_object(id='me', fields='friends.limit(99999){id},id')

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
                        'user_id': tmp_json['id'],
                        'friends_id': id_friends,
                        'friends_count': tmp_json['friends']['summary']['total_count'],
                        }])
        self.solr.commit()

        print('LISTA AMICI INDICIZZATA')

    def takeANDindexAge(self, token):
        if self.token_is_valid(token) == 0:
            return
        print('inizia age')

        # 1) SCARICO I DATI IN UN FILE JSON
        graph = facebook.GraphAPI(access_token=token)
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
                        'user_id': tmp_json['id'],
                        'age': age,
                        }])
        self.solr.commit()

        print('ETA INDICIZZATA')

    def takeANDindexProfPic(self, token):
        if self.token_is_valid(token) == 0:
            return

        # 1) SCARICO I DATI IN UN FILE JSON
        graph = facebook.GraphAPI(access_token=token)
        tmp_json = graph.get_object(id='me', fields='albums{name,photos{images}}')
        if 'albums' not in tmp_json.keys():
            return
        user_id = tmp_json['id']
        tmp_json = tmp_json['albums']['data']
        for a in tmp_json:
            if a['name'] == "Profile Pictures":
                album = a
                break

        query = 'doc_type:profile_picture AND user_id:' + str(user_id)
        self.solr.delete(q=query)

        image = album['photos']['data'][0]['images'][0]['source']
        middle = int(len(album['photos']['data'][0]['images']) - len(album['photos']['data'][0]['images']) / 4.0)
        image2 = album['photos']['data'][0]['images'][middle]['source']
        self.solr.add([{'doc_type': 'profile_picture',
                        'user_id': user_id,
                        'link': image,
                        'link2': image2,
                        }])

        self.solr.commit()

        print('PROFPIC INDICIZZATA')

    def takeANDindexPlaces(self, token):
        if self.token_is_valid(token) == 0:
            return
        print('inizia places')

        # 1) SCARICO I DATI IN UN FILE JSON
        graph = facebook.GraphAPI(access_token=token)
        tmp_json = graph.get_object(id='me', fields='posts{place,created_time},tagged_places,id')

        # 2) CREO UNA LISTA DI ELEMENTI DA AGGIUNGERE
        List = []
        List.append({'doc_type': 'place'})
        user_id = tmp_json['id']
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
