import requests, praw, re, config
from datetime import datetime

r = praw.Reddit(client_id=config.reddit_id,
                client_secret=config.reddit_secret,
                username=config.reddit_user,
                password=config.reddit_pass,
                user_agent=config.reddit_agent)


def hattrick():

    # for post in r.subreddit('hockey').new(limit=2000):
    for post in r.subreddit('hockey').search('hat trick', sort='new'):
        if re.search(r'hat.?trick', str(post.title).lower()) and not any(x in  str(post.title).lower() for x in ['?', 'gordie howe', 'til ']):
            print(f"\n{post.title} {post.shortlink}\n")
            try:
                name = re.match(r'[A-Z]\w+ [A-Z]\w+', post.title)[0]
                url = 'https://api.nhle.com/stats/rest/en/skater/summary'
                params = {
                    'isAggregate': 'False',
                    'isGame': 'True',
                    'sort': '[{"property":"gameDate","direction":"DESC"}]',
                    'start': '0',
                    'limit': '50',
                    'factCayennneExp': 'gamesPlayed>=1',
                    'cayenneExp': f'gameTypeId=2 and seasonId=20192020 and skaterFullName likeIgnoreCase "{name}"'
                }
                data = requests.get(url, params=params)
                games = data.json()['data']
                for game in games:
                    if game['goals'] >= 3:
                        player_id = game['playerId']
                        apiurl = 'https://statsapi.web.nhl.com/api/v1/game/'
                        livedata = requests.get(f"{apiurl}{game['gameId']}/feed/live").json()['liveData']['plays']['allPlays']
                        content = requests.get(f"{apiurl}{game['gameId']}/content").json()['media']['milestones']['items']

                        for item in livedata:
                            if item['result']['event'] == 'Goal' and item['players'][0]['player']['id'] == player_id:
                                for goal in [x for x in content if x['title'] == 'Goal' and x['statsEventId'] == str(item['about']['eventId'])]:
                                    print(f"[{goal['description']}]({goal['highlight']['playbacks'][3]['url']})\n")
                        print(20*'-')
                        break
            except TypeError:
                date = datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d')
                print('TYPE ERROR')
                url = 'https://api.nhle.com/stats/rest/en/skater/summary'
                params = {
                    'isAggregate': 'False',
                    'isGame': 'True',
                    'sort': '[{"property":"goals","direction":"DESC"}]',
                    'start': '0',
                    'limit': '50',
                    'factCayenneExp': 'gamesPlayed>=1',
                    'cayenneExp': f'gameDate="{date}"'
                }
                data = requests.get(url, params=params)
                games = data.json()['data']
                for game in games:
                    if game['goals'] >= 3:
                        if game['lastName'] in post.title:
                            player_id = game['playerId']
                            apiurl = 'https://statsapi.web.nhl.com/api/v1/game/'
                            livedata = requests.get(f"{apiurl}{game['gameId']}/feed/live").json()['liveData']['plays'][
                                'allPlays']
                            content = requests.get(f"{apiurl}{game['gameId']}/content").json()['media']['milestones'][
                                'items']

                            for item in livedata:
                                if item['result']['event'] == 'Goal' and item['players'][0]['player']['id'] == player_id:
                                    for goal in [x for x in content if x['title'] == 'Goal' and x['statsEventId'] == str(item['about']['eventId'])]:
                                        print(f"[{goal['description']}]({goal['highlight']['playbacks'][3]['url']})\n")
                            print(20*'-')
                        # break

hattrick()