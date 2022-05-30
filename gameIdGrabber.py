# broad search this time
import csv
from queue import Queue
from typing import List
import time
import pandas as pd

import RequestSender

KEY = "RGAPI-25a51237-2c61-4367-b99e-60f2531f7cae"
IDS_FILE = "data/gameids.csv"
INFO_FILE = "data/gameinfo.csv"

QUEUE_TYPE = "400"
START_ID = "NA1_4323613385"
SEED_IDS = [
    "NA1_4323613385",
    "NA1_4323585320",
    "NA1_4321260841",
    "NA1_4321204992",
    "NA1_4315813266",
    "NA1_4315757319",
    "NA1_4312753168",
    "NA1_4311479389",
    "NA1_4308431256",
    "NA1_4308386473",
    "NA1_4308421073",
    "NA1_4308363999",
    "NA1_4292963642",
    "NA1_4292918871",
    "NA1_4291918838",
    "NA1_4291945051",
    "NA1_4291040284",
    "NA1_4290735518",
    "NA1_4290722226",
    "NA1_4290075007"
]  # from ohm
MATCH_V5_URL = "https://americas.api.riotgames.com/lol/match/v5/matches/<MATCHID>?api_key=<API_KEY>"
PAST_MATCHES_URL = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/<PUUID>/ids?queue=" + QUEUE_TYPE + "&start=0&count=<COUNT>&api_key=<API_KEY> "


def get_match_v5(matchid):
    url = MATCH_V5_URL
    variables = {"API_KEY": KEY, "MATCHID": matchid}
    game_json = RequestSender.send_request(url, variables=variables).json()
    return game_json


# use this with match_v5
def grab_participant_infos(game_json):
    ret_lst = []
    for participant in game_json["info"]["participants"]:
        ret_lst.append([participant["summonerName"], participant["championName"], participant["teamId"]])
    return ret_lst


def grab_puuids(game_json):
    return game_json["metadata"]["participants"]


def grab_participant_past_game(puuid) -> List[str]:
    variables = {"API_KEY": KEY, "PUUID": puuid, "COUNT": "5"}
    url = PAST_MATCHES_URL
    return RequestSender.send_request(url, variables=variables).json()


def write_to_csv(games: List, file_path):
    with open(file_path, 'a', newline="", encoding="utf-8") as file:
        writist = csv.writer(file, lineterminator="\n")
        for game in games:
            if not isinstance(game, list):
                writist.writerow([game])
            else:
                writist.writerow(game)


def get_game_ids(n_games, start):
    game_queue = Queue()
    game_queue.put(start)
    gameids = []
    while len(gameids) < n_games and game_queue.qsize() != 0:
        # get new id
        current_id = game_queue.get()

        # get match info for id
        time.sleep(100 / 120)
        print("GRABBER: SENDING MATCHV5")
        m_v5 = get_match_v5(current_id)

        # grab puuids, go thru participants
        for participant in grab_puuids(m_v5):
            # grab past 2 games for each
            time.sleep(100 / 120)
            print("GRABBER: GETTING PAST GAMES")
            past_games = grab_participant_past_game(participant)

            # add to game queue now
            for game in past_games:
                if game not in gameids:
                    game_queue.put(game)
                else:
                    print("found duplicate game")

            # add to gameids list and remove duplicates
            gameids += past_games
            gameids = list(set(gameids))

        print("Got", len(gameids), "games")
    gameids = list(set(gameids))
    print("WRITING", len(gameids), "TO FILE")
    print("GAME QUEUE SIZE:", game_queue.qsize())
    write_to_csv(gameids, IDS_FILE)


def get_game_user_champs(gameid):
    time.sleep(100 / 120)
    match_v5 = get_match_v5(gameid)
    return grab_participant_infos(match_v5)


def get_game_users_champs(id_list):
    ret_list = []
    i = 0
    for gameid in id_list:
        write_list = [get_game_user_champs(gameid)]

        i += 1
        try:
            print("Writing", i, "games")
            write_to_csv(write_list, INFO_FILE)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    # get_game_ids(1000, START_ID)
    game_ids = pd.read_csv(IDS_FILE)
    game_ids = game_ids.values.flatten().tolist()
    game_ids = list(set(game_ids))
    print("GOING TO GET GAMES", len(game_ids))
    get_game_users_champs(game_ids)