#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time, random, requests, json

instagram_url = 'https://www.instagram.com'
login_route = '%s/accounts/login/ajax/' % (instagram_url)
logout_route = '%s/accounts/logout/' % (instagram_url)
profile_route = '%s/%s/?__a=1'
query_route = '%s/graphql/query/' % (instagram_url)
unfollow_route = '%s/web/friendships/%s/unfollow/'

session = requests.Session()

connected_username = ""

def banner():
    print '''
        ____           __             _  __      __  __      ____      ____             
       /  _/___  _____/ /_____ _     | |/ /     / / / /___  / __/___  / / /___ _      __
       / // __ \/ ___/ __/ __ `/_____|   /_____/ / / / __ \/ /_/ __ \/ / / __ \ | /| / /
     _/ // / / (__  ) /_/ /_/ /_____/   /_____/ /_/ / / / / __/ /_/ / / / /_/ / |/ |/ / 
    /___/_/ /_/____/\__/\__,_/     /_/|_|     \____/_/ /_/_/  \____/_/_/\____/|__/|__/  
    '''
    print('Please remember: to avoid ban, don\'t use this program more than 3 times a day!\n')

def login():
    session.headers.update({
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Host': 'www.instagram.com',
        'Origin': 'https://www.instagram.com',
        'Referer': 'https://www.instagram.com/',
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36'),
        'X-Instagram-AJAX': '1',
        'X-Requested-With': 'XMLHttpRequest'
    })
    session.cookies.update({
        'ig_pr': '1',
        'ig_vw': '1920',
    })
    reponse = session.get(instagram_url)
    session.headers.update({
        'X-CSRFToken': reponse.cookies['csrftoken']
    })

    while True:
        print('Wait...Connecting...')
        time.sleep(random.randint(2, 4))
        
        global connected_username
        connected_username = raw_input("Please insert username: ")
        password = raw_input("Please insert password: ")

        post_data = {
            'username': connected_username,
            'password': password
        }

        reponse = session.post(login_route, data=post_data, allow_redirects=True)
        reponse_data = json.loads(reponse.text)

        if reponse_data['authenticated']:
            session.headers.update({
                'X-CSRFToken': reponse.cookies['csrftoken']
            })
            return
            
        print('Error: wrong username/password. Please try again.\n')

# Not so useful, it's just to simulate human actions better
def get_user_profile(username):
    response = session.get(profile_route % (instagram_url, username))
    response = json.loads(response.text)

    return response['graphql']['user']

def get_follows_list():
    follows_list = []

    follows_post = {
        'query_id': 17874545323001329,
        'variables': {
            'id': session.cookies['ds_user_id'],
            'first': 20
        }
    }
    follows_post['variables'] = json.dumps(follows_post['variables'])
    response = session.get(query_route, params=follows_post)
    response = json.loads(response.text)
    
    i=0

    for edge in response['data']['user']['edge_follow']['edges']:
        i=i+1
        follows_list.append(edge['node'])

    while response['data']['user']['edge_follow']['page_info']['has_next_page'] and i<135:
        i=i+1
        time.sleep(random.randint(2, 3))

        follows_post = {
            'query_id': 17874545323001329,
            'variables': {
                'id': session.cookies['ds_user_id'],
                'first': 10,
                'after': response['data']['user']['edge_follow']['page_info']['end_cursor']
            }
        }
        follows_post['variables'] = json.dumps(follows_post['variables'])
        response = session.get(query_route, params=follows_post)
        response = json.loads(response.text)

        for edge in response['data']['user']['edge_follow']['edges']:
            follows_list.append(edge['node'])

    return follows_list

def unfollow(user):
    response = session.post(unfollow_route % (instagram_url, user['id']))
    response = json.loads(response.text)

    if response['status'] != 'ok':
        print('ERROR: {}'.format(unfollow.text))
        sys.exit('\nMight be unfollowing too fast, quit to prevent ban...')

def logout():
    print('\nLogging out...')
    while True:
        post_data = {
            'csrfmiddlewaretoken': session.cookies['csrftoken']
        }

        logout = session.post(logout_route, data=post_data)

        if logout.status_code == 200:
            return

def main():
    banner()
    login()
    
    time.sleep(random.randint(2, 3))

    connected_user = get_user_profile(connected_username)
    
    print('\nYou\'re now logged as {}'.format(connected_user['username']))
    print('You have {} followers'.format(connected_user['edge_followed_by']['count']))
    print('You are following {} users'.format(connected_user['edge_follow']['count']))
    
    time.sleep(random.randint(2, 3))

    max_unfollow_num = connected_user['edge_follow']['count']
    if max_unfollow_num>135:
        max_unfollow_num = 135
    print('\nBuilding follows list... (maybe require a lot, max {} minutes)\n'.format(max_unfollow_num*3/60))
    follows_list = get_follows_list()
    
    while True:
        unfollow_num = int(input('How many user do you want to unfollow? (Max {}): '.format(max_unfollow_num)))
        if unfollow_num<=max_unfollow_num and unfollow_num>=0:
            break
        print('You didn\'t respect max number. Please try again. To avoid ban, you can\'t unfollow more than 135 profiles per hour.')
        
        print('\nBegin to unfollow users...')

        i=0
        for user in follows_list:
            if i>=unfollow_num:
                break
            i=i+1
            time.sleep(random.randint(2, 3))

            print("(%d/%d) Unfollowing %s" % (i, unfollow_num, user['username']))
            unfollow(user)

    time.sleep(random.randint(2, 3))
    connected_user = get_user_profile(connected_username)
    print('\nFinished! You are now following {} users'.format(connected_user['edge_follow']['count']))

    logout()
    sys.exit(0)

if __name__ == "__main__":
    main()