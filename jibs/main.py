import time
from multiprocessing import Process

import pandas as pd
import vk

COLUMNS = ['albums', 'alcohol', 'audios', 'bdate', 'city', 'country',
           'first_name', 'followers', 'followers_count', 'friends',
           'groups',
           'has_mobile', 'has_photo', 'langs', 'last_name', 'life_main',
           'notes',
           'pages', 'people_main', 'photos', 'political', 'relation',
           'schools',
           'sex', 'smoking', 'trending', 'uid', 'universities',
           'user_videos',
           'videos', "position", "wall_posts"]
TOKEN2 = "2ed69dafcf2a5560d335a66c1c79390ca50998126e7f9ee6150236ec98c54f4f3f7b7ea78ead865d7831e"
TOKEN1 = "b6b413f28280562c93c2ccf504f03cc220bdafeaee0756b46c58aed76917daac1b994ad79078c54359153"
TOKEN3 = "b8bcf0884b412aae9113bcc7de00a6a961d0b329026f19d62a1e562a4e09d28ef216936a478ecfbf28368"


def main():
    Process(target=runparallel, args=("Data science", TOKEN1,)).start()
    Process(target=runparallel, args=("Робототехник", TOKEN2,)).start()
    Process(target=runparallel, args=("ERP", TOKEN3)).start()


def runparallel(position, token):
    session = vk.Session(
        access_token=token)
    vk_api = vk.API(session)
    test_get = 1000

    def worker2(id, position, dataframe):
        print("get {} from {}".format(id, position))

        js = vk_api.users.get(user_ids=id,
                              fields="bdate, city,counters,country, followers_count, has_mobile, has_photo, personal,relation,schools,sex,trending,universities")

        counters_keys = ["photos", "videos", "audios", "albums", "notes", "friends", "groups", "user_videos",
                         "followers", "pages"]
        simple_keys = ["uid", "city", "country", "has_photo", "has_mobile", "trending", "followers_count", "sex",
                       "relation", "universities", "schools", "political", "people_main", "life_main",
                       "smoking", "alcohol", "langs", "bdate", "position", "wall_posts"]

        # init
        dict_js = {}

        for ke in counters_keys:
            dict_js[ke] = -1
        for ke in simple_keys:
            dict_js[ke] = -1

        dict_js.update(js[0])
        dict_js["uid"] = id

        for ke in counters_keys:
            if ke in dict_js["counters"]:
                dict_js[ke] = dict_js["counters"][ke]

        dict_js.pop('counters')
        if dict_js['universities'] != -1:
            dict_js["universities"] = len(dict_js["universities"])
        if dict_js['schools'] != -1:
            dict_js["schools"] = len(dict_js["schools"])
        if 'personal' in dict_js:
            if 'langs' in dict_js['personal']:
                dict_js["langs"] = len(dict_js['personal']["langs"])
            if 'people_main' in dict_js['personal']:
                dict_js["people_main"] = dict_js['personal']["people_main"]
            if 'life_main' in dict_js['personal']:
                dict_js["life_main"] = dict_js['personal']["life_main"]
            if 'smoking' in dict_js['personal']:
                dict_js["smoking"] = dict_js['personal']["smoking"]
            if 'alcohol' in dict_js['personal']:
                dict_js["alcohol"] = dict_js['personal']["alcohol"]
            if 'political' in dict_js['personal']:
                dict_js["political"] = dict_js['personal']["political"]
            dict_js.pop('personal')

        if 'relation_partner' in dict_js:
            dict_js.pop('relation_partner')

        dict_js["position"] = position

        print(dict_js)

        js = vk_api.wall.get(owner_id=id, count=1)
        dict_js['wall_posts'] = js[0]

        dataframe.loc[len(dataframe.index)] = [dict_js[i] for i in COLUMNS]
        print(len(dataframe.index))

    with open("{}_0.csv".format(position)) as f:
        position_df = pd.DataFrame.from_csv(f)
        dataframe = pd.DataFrame(index=[0], columns=COLUMNS)
        for index, row in position_df.iterrows():
            if index % 10 == 0:
                dataframe.to_csv("{}/{}.csv".format(position, index))
            worker2(row["uid"], position, dataframe)
            time.sleep(0.5)
