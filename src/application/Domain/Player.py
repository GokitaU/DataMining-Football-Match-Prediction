import logging

import src.util.SQLLite as SQLLite
import src.util.Cache as Cache

import src.application.Domain.Match as Match
import src.application.Domain.Player_Attributes as Player_Attributes


log = logging.getLogger(__name__)

class Player(object):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "Player <id: "+str(self.id)+", player_api_id:"+str(self.player_api_id)+", player_name:"+str(self.player_name)\
               +", player_fifa_api_id:"+str(self.player_fifa_api_id)+", birthday:"+str(self.birthday)\
               +", height:"+str(self.height)+", weight:"+str(self.weight)+">";

    def get_last_player_attributes(self):
        max_date = "0000-00-00"
        last_player_attributes = None

        for player_attributes in self.get_player_attributes():
            if player_attributes.date > max_date:
                max_date = player_attributes.date
                last_player_attributes = player_attributes

        return last_player_attributes

    def get_player_attributes(self, date=None):
        return Player_Attributes.read_by_player_fifa_api_id(self.player_fifa_api_id)

    def save_player_attributes(self, player_attributes):
        Player_Attributes.write_player_attributes(self, player_attributes)

    def set_api_id(self, player_api_id, persist=True):
        self.player_api_id = player_api_id
        if persist:
            update(self)

def read_all():
    players = []
    for p in SQLLite.read_all("Player"):
        player = Player(p["id"])
        for attribute, value in p.items():
            player.__setattr__(attribute, value)
        players.append(player)
    return players

def read_by_api_id(player_api_id):
    '''
    Read a player by its api_id
    :param player_api_id:
    :return:
    '''
    try:
        return Cache.get_element(player_api_id, "PLAYER_BY_API_ID")
    except KeyError:
        pass

    filter = {"player_api_id": player_api_id}
    try:
        sqllite_row = SQLLite.get_connection().select("Player", **filter)[0]
    except IndexError:
        return None
    player = Player(sqllite_row["id"])
    for attribute, value in sqllite_row.items():
        player.__setattr__(attribute, value)

    Cache.add_element(player.player_fifa_api_id, player, "PLAYER_BY_FIFA_API_ID")
    Cache.add_element(player.player_api_id, player, "PLAYER_BY_API_ID")
    Cache.add_element(player.player_name, player, "PLAYER_BY_NAME")
    return player


def read_by_fifa_api_id(player_fifa_api_id):
    '''
       Read a player by its team_fifa_api_id
       :param player_api_id:
       :return:
       '''
    try:
        return Cache.get_element(player_fifa_api_id, "PLAYER_BY_FIFA_API_ID")
    except KeyError:
        pass

    filter = {"player_fifa_api_id": player_fifa_api_id}
    try:
        sqllite_row = SQLLite.get_connection().select("Player", **filter)[0]
    except IndexError:
        return None

    player = Player(sqllite_row["id"])
    for attribute, value in sqllite_row.items():
        player.__setattr__(attribute, value)

    Cache.add_element(player.player_fifa_api_id, player, "PLAYER_BY_FIFA_API_ID")
    Cache.add_element(player.player_api_id, player, "PLAYER_BY_API_ID")
    Cache.add_element(player.player_name, player, "PLAYER_BY_NAME")
    return player


def read_by_name(player_name):
    '''
    Read a player by its name
    :param player_api_id:
    :return:
    '''
    filter = {"player_name": player_name}

    players = []
    for p in SQLLite.get_connection().select("Player", **filter):
        player = Player(p["id"])
        for attribute, value in p.items():
            player.__setattr__(attribute, value)
        players.append(player)

    return players


def read_by_team_api_id(team_api_id, season=None):
    '''
    Return list of players that play in the team identified my team_api_id
    if season is set, consider only that season
    :param team_api_id:
    :param season:
    :return:
    '''

    if not season:
        season = ""
    try:
        return Cache.get_element(str(team_api_id)+"_"+season, "PLAYER_BY_TEAM_API_ID")
    except KeyError:
        pass
    players = []
    players_api_id = Match.read_players_api_id_by_team_api_id(team_api_id, season)
    for player_api_id in players_api_id:
        try:
            player = Cache.get_element(player_api_id, "PLAYER_BY_API_ID")
        except KeyError:
            filter = {"player_api_id": player_api_id}
            sqllite_row = SQLLite.get_connection().select("Player", **filter)[0]
            player = Player(sqllite_row["id"])
            for attribute, value in sqllite_row.items():
                player.__setattr__(attribute, value)
            Cache.add_element(player_api_id, player, "PLAYER_BY_API_ID")
        players.append(player)

    Cache.add_element(str(team_api_id)+"_"+season, players, "PLAYER_BY_TEAM_API_ID")
    return players


def write_new_player(player_name, player_fifa_api_id, birthday, height, weight):
    SQLLite.get_connection().insert("Player", {"player_name":player_name,
                                             "player_fifa_api_id":player_fifa_api_id,
                                             "birthday":birthday,
                                             "height":height,
                                              "weight":weight})
    return read_by_fifa_api_id(player_fifa_api_id)


def update(player):
    SQLLite.get_connection().update("Player", player)


