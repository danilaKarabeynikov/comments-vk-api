import requests
import pandas as pd
import cryptography
import pymysql.connections
from config import token, version, host, user, password, db_name, port


def take_comments(domain):
    count_post = 1
    count_comments = 30
    sort = 'desc'
    thread_items_count = 20
    all_comments = []
    post_data = []
    for offset_posts in range(0, 9):
        response1 = requests.get('https://api.vk.com/method/wall.get',
                        params={
                            'access_token': token,
                            'v': version,
                            'domain': domain,
                            'offset': offset_posts,
                            'count': count_post,
                        }
                        )
        _post = response1.json()['response']['items']
        post_data.extend(_post)
        post_id = response1.json()['response']['items'][0]['id']
        owner_id = response1.json()['response']['items'][0]['owner_id']
        response2 = requests.get('https://api.vk.com/method/wall.getComments',
                        params={
                            'access_token': token,
                            'v': version,
                            'owner_id': owner_id,
                            'post_id': post_id,
                            'count': count_comments,
                            'sort': sort,
                            'thread_items_count': thread_items_count
                        })
        comments_data = response2.json()['response']['items']
        all_comments.extend(comments_data)
        for i in range(len(comments_data)):
            reposts_data = response2.json()['response']['items'][i]['thread']['items']
            all_comments.extend(reposts_data)
    return post_data, all_comments


def file_writer(file_name, comments_and_post_data):
    data = pd.DataFrame()
    for post in comments_and_post_data[0]:
        posts = pd.DataFrame([[post['id'],
                            post['owner_id'],
                            post['date'],
                            post['text'],
                            post['comments']['count'],
                            post['likes']['count'],
                            post['reposts']['count'],
                            post['views']['count']]], columns=['post_id', 'owner_id', 'date', 'text', 'comments', 'likes', 'reposts', 'views']
                            )
        data = data.append(posts)
    for comment in comments_and_post_data[1]:
        if 'reply_to_comment' in comment:
            recomments = pd.DataFrame([[comment['id'],
                                comment['post_id'],
                                comment['from_id'],
                                comment['text'],
                                comment['date'],
                                comment['reply_to_comment']
                                ]], columns=['comment_id', 'post_id', 'from_id', 'text', 'date', 'reply_to_comment']
                                )
            data = data.append(recomments)
        else:
            comments = pd.DataFrame([[comment['id'],
                                comment['post_id'],
                                comment['from_id'],
                                comment['text'],
                                comment['date']
                                ]], columns=['comment_id', 'post_id', 'from_id', 'text', 'date'])
            data = data.append(comments)
    data.to_csv(file_name + '.csv', index=False, sep=';')



def enc(txt):
    txt.replace('"', '').replace('\n', '').replace('\\', '')
    txt = txt.encode('cp1251', errors='ignore')
    txt = txt.decode('cp1251', errors='ignore')

    return str(txt)


def database_writer(domain, post_id=None):
    try:

        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )

        print("successfully connected...")
        print('#' * 20)

        try:

            count_post = 1
            count_comments = 30
            sort = 'desc'
            thread_items_count = 10
            for offset_posts in range(0, 5):
                response1 = requests.get('https://api.vk.com/method/wall.get',
                                         params={
                                             'access_token': token,
                                             'v': version,
                                             'domain': domain,
                                             'offset': offset_posts,
                                             'count': count_post,
                                         }
                                         )
                _post = response1.json()['response']['items']
                post_id1 = str(response1.json()['response']['items'][0]['id'])
                owner_id = str(response1.json()['response']['items'][0]['owner_id'])
                date = str(response1.json()['response']['items'][0]['date'])
                comments_count = str(response1.json()['response']['items'][0]['comments']['count'])
                likes_count = str(response1.json()['response']['items'][0]['likes']['count'])
                reposts_count = str(response1.json()['response']['items'][0]['reposts']['count'])
                views_count = str(response1.json()['response']['items'][0]['views']['count'])
                textt = enc(response1.json()['response']['items'][0]['text'])
                text = str('"') + textt.replace('"', '').replace('\n', '').replace('\\', '') + str('"')
                with connection.cursor() as cursor:
                    insert_query1 = 'replace into `vkdb`.`posts`( idposts, ownerid, date, text, countOfComments,countOfLikes, countOfReposts, countOfViews)' \
                                    ' values('+ post_id1 + ',' + owner_id + ',' + date + ',' + text + ',' + comments_count + ',' + likes_count + ',' + reposts_count + ',' + views_count + ');'
                    cursor.execute(insert_query1)

                response2 = requests.get('https://api.vk.com/method/wall.getComments',
                                         params={
                                             'access_token': token,
                                             'v': version,
                                             'owner_id': owner_id,
                                             'post_id': post_id1,
                                             'count': count_comments,
                                             'sort': sort,
                                             'thread_items_count': thread_items_count
                                         })

                for i in range(count_comments):
                    with connection.cursor() as cursor:
                        tttext = enc(response2.json()['response']['items'][i]['text'])
                        text1 = str('"') + tttext.replace('"', '').replace('\n', '').replace('\\', '') + str('"')
                        insert_query2 = 'replace into `vkdb`.`comments` ' \
                                    '( idcomments, idposts, fromID, date, text' \
                                    ') values( ' + str(response2.json()['response']['items'][i]['id'])+',' +\
                                     str(response2.json()['response']['items'][i]['post_id']) + ',' +\
                                     str(response2.json()['response']['items'][i]['from_id']) + ',' +\
                                    str(response2.json()['response']['items'][i]['date']) + ',' +\
                                     text1 + ');'
                        cursor.execute(insert_query2)
                    countK = response2.json()['response']['items'][i]['thread']['count']
                    k = 0
                    for k in range(countK):
                        with connection.cursor() as cursor:
                            ttext = enc(response2.json()['response']['items'][i]['thread']['items'][k]['text'])
                            text2 = str('"') + ttext.replace('\n', '').replace('\\', '')
                            insert_query3 = "replace into `vkdb`.`comments` " \
                                    "( idcomments, idposts, fromID, date, text, idrecomments" \
                                    ") values( " + str(response2.json()['response']['items'][i]['thread']['items'][k]['id']) + "," + \
                                    str(response2.json()['response']['items'][i]['thread']['items'][k]['post_id']) + "," +\
                                    str(response2.json()['response']['items'][i]['thread']['items'][k]['from_id']) + "," +\
                                    str(response2.json()['response']['items'][i]['thread']['items'][k]['date']) + "," + \
                                    str('"') + text2.replace('"', '') + str('"') + "," +\
                                    str(response2.json()['response']['items'][i]['thread']['items'][k]['reply_to_comment']) + ");"

                            cursor.execute(insert_query3)
                    connection.commit()

        finally:
            connection.close()
    except Exception as ex:
        print(k, i, countK)
        print("Connection refused...")
        print(ex)

if __name__=="__main__":
    database_writer('spacelordrock')
