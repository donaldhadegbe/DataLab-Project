# Created on Fri Sep 13 21:04:12 2019
# @author: Donald HADEGBE, Big thank to Gustavo Saidler

# 'pip install --ignore-installed instagramAPI' à renseigner dans l'invit de commande _
# pour installer la librairie InstagramAPI
from InstagramAPI import InstagramAPI
from matplotlib import pyplot as plt
import numpy
import time
import pandas as pd
from pandas.io.json import json_normalize
import copy
# Se connecter à son compte instagram en passant  l'API d'instagram (non-officiel "


def login_to_instagram(username, password):
    api = InstagramAPI(username, password)
    api.login()

    return api

api = login_to_instagram('Data__Lab', 'Mc2i2020')


def get_my_posts(api):
    #Recuperer toutes les publications sur un compte
    my_posts = []
    has_more_posts = True
    max_id = ''

    while has_more_posts:
        api.getUserFeed(641259147, maxid=max_id)
        if api.LastJson['more_available'] is not True:
            has_more_posts = False  # stop condition

        max_id = api.LastJson.get('next_max_id', '')
        my_posts.extend(api.LastJson['items'])  # merge lists

        time.sleep(0.5)  # slows down to avoid flooding

        if has_more_posts:
            print(str(len(my_posts)) + ' posts retrieved so far...')

    print('Total posts retrieved: ' + str(len(my_posts)))

    return my_posts


my_posts = get_my_posts(api)


def get_posts_likers(api, my_posts):
    # Recuperer tous les likers sur un compte

    likers = []

    print('wait %.1f minutes' % (len(my_posts) * 2 / 60.))
    for i in range(len(my_posts)):
        m_id = my_posts[i]['id']
        api.getMediaLikers(m_id)

        likers += [api.LastJson]

        # Include post_id in likers dict list
        likers[i]['post_id'] = m_id

        time.sleep(2)
    print('done')

    return likers


likers = get_posts_likers(api, my_posts)


def get_posts_commenters(api, my_posts):
    # Retrieve all commenters on all posts

    commenters = []

    print('wait %.1f minutes' % (len(my_posts) * 2 / 60.))
    for i in range(len(my_posts)):
        m_id = my_posts[i]['id']
        api.getMediaComments(m_id)

        commenters += [api.LastJson]

        # Include post_id in commenters dict list
        commenters[i]['post_id'] = m_id

        time.sleep(2)
    print('done')

    return commenters


commenters = get_posts_commenters(api, my_posts)


def posts_likers_to_df(likers):
    # Transforms likers list of dicts into pandas DataFrame'''

    # Normalize likers by getting the 'users' list and the post_id of each like
    df_likers = json_normalize(likers, 'users', ['post_id'])

    # Add 'content_type' column to know the rows are likes
    df_likers['content_type'] = 'like'

    return df_likers


df_likers = posts_likers_to_df(likers)


def posts_commenters_to_df(commenters_):
    # Transforms commenters list of dicts into pandas DataFrame
    commenters = copy.deepcopy(commenters_)
    # Include username and full_name of commenter in 'comments' list of dicts
    for i in range(len(commenters)):
        if len(commenters[i]['comments']) > 0:  # checks if there is any comment on the post
            for j in range(len(commenters[i]['comments'])):
                # Puts username/full_name one level up
                commenters[i]['comments'][j]['username'] = commenters[i]['comments'][j]['user']['username']
                commenters[i]['comments'][j]['full_name'] = commenters[i]['comments'][j]['user']['full_name']

    # Create DataFrame
    # Normalize commenters to have 1 row per comment, and gets 'post_id' from parent
    df_commenters = json_normalize(commenters, 'comments', 'post_id')

    # Get rid of 'user' column as we already handled it above
    del df_commenters['user']

    return df_commenters


df_commenters = posts_commenters_to_df(commenters)

print(df_likers)
print(df_commenters)

Export_likers = df_commenters.to_csv (r'C:\Users\i7 gaming\PycharmProjects\D&A Club Projects\DataLab Project\Usecase Sephora\IG Data Analysis\Data\Export_likers.csv', index = None, header=True)
Export_comments = df_commenters.to_csv (r'C:\Users\i7 gaming\PycharmProjects\D&A Club Projects\DataLab Project\Usecase Sephora\IG Data Analysis\Data\Export_comments.csv', index = None, header=True)

print('Total posts: ' + str(len(my_posts)))
print('---------')
print('Total likes on profile: ' + str(df_likers.shape[0])) #shape[0] represents number of rows
print('Distinct users that liked your posts: ' +str(df_likers.username.nunique())) # nunique() will count distinct values of a col
print('---------')
print('Total comments on profile: ' + str(df_commenters.shape[0]))
print('Distinct users that commented your posts: ' +str(df_commenters.username.nunique()))

" liker bar plot"
df_likers.username.value_counts()[:10].plot(kind='bar', title='Top 10 media likers', grid=True, figsize=(12,6))
plt.show()
" liker pie plot "
df_likers.username.value_counts()[:10].plot(kind='pie', title='Top 10 media likers distribution', autopct='%1.1f%%', figsize=(12,6))
plt.show()
"top ten comments"
df_commenters['username'].value_counts()[:10].plot(kind='bar', figsize=(12,6), title='Top 10 post commenters')
plt.show()
# Converts date from unix time to YYYY-MM-DD hh24:mm:ss
df_commenters.created_at = pd.to_datetime(df_commenters.created_at, unit='s')
plt.show()
df_commenters.created_at_utc = pd.to_datetime(df_commenters.created_at_utc, unit='s')
plt.show()
df_commenters.created_at.dt.weekday.value_counts().sort_index().plot(kind='bar', figsize=(12,6), title='Comments per day of the week (0 - Sunday, 6 - Saturday)')
plt.show()
"comments per hour of the day "
df_commenters.created_at.dt.hour.value_counts().sort_index().plot(kind='bar', figsize=(12,6))
plt.show()
# Create a column to show when a a comment was created at France Time
df_commenters['created_at_fr'] = df_commenters.created_at_utc.dt.tz_localize('UTC').dt.tz_convert('Europe/Paris')
plt.show()
df_commenters.created_at_fr.dt.hour.value_counts().sort_index().plot(kind='bar', figsize=(12,6))
plt.show()