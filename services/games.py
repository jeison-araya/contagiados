
from datetime import datetime

from bson.objectid import ObjectId
from utility.mongo_driver import get_db
from utility.util import isBlank


def get_all_games(filter):
    """Gets the filtered list of games headers.
    Args:
        filter (dict): Filter of the list.
    Returns:
        games headers (list, dict): Filtered list or dict (if find_one is True)
                                    of games headers.
    """
    db = get_db()

    _filter = _parse_filter(filter)
    _fields = {'_id': 1, 'name': 1}
    
    return _parse_gamesheaders(db.games.find(_filter, _fields))


def get_game_by_id(gameId, name, password):
    """Extract information for an arbitrary game.

    Args:
        gameId (str): Id of the game.
        name (str): Name of the player.
        password (str): Password of the game.
    """
    db = get_db()
        
    _filter = {'_id': ObjectId(gameId)}
    game = _parse_game(db.games.find_one(_filter))

    if game is None:
        raise ValueError('Invalid Game\'s id.', 404)
    if not (name in game.get('players')):
        raise ValueError('You are not part of the players list.', 403)
    if game.get('password') != password:
        # TODO check if necessary.
        raise ValueError('Invalid game password.', 403)

    return game


def create(owner, name, password):
    """Creates and saves an game into a database.
    Args:
        owner (str): Owner's name of the game.
        name (str): Name of the game.
        password (str): Password of the game.
    Returns:
        game (dict): Created game.
    """
    db = get_db()

    check_owner(owner)
    check_name(name)

    result = db.games.insert_one({
        'name': name,
        'owner': owner,
        'password': password,
        'players': [owner],
        'psychos': [],
        'psychosWin': [],
        'status': 'Lobby',
        'rounds': [],
        'updated_at': datetime.now(),
    })
    
    _filter = {'_id': result.inserted_id}
    game = _parse_game(db.games.find_one(_filter))

    return game


def join_game(gameId, name, password):
    """Add player to an arbitrary game.

    Args:
        gameId (str): Id of the game.
        name (str): Name of the player.
        password (str): Password of the game.
    """
    db = get_db()
    
    game = _parse_game(db.games.find_one({'_id': ObjectId(gameId)}))
    
    if game is None:
        raise ValueError('Invalid Game\'s id.', 404)
    if password != game.get('password'):
        raise ValueError('Invalid game password.', 403)
    if game.get('status') != 'Lobby' or len(game.get('players')) >= 10:
        raise ValueError('Game has already started or is full.', 406)
    if name in game.get('players'):
        raise ValueError('You are already part of this game.', 409)
    
    result = db.games.update_one(
        {'_id': ObjectId(gameId)}, 
        {'$push': {'players': name }, 
         '$set': {'updated_at': datetime.now()
        }})

    return result.matched_count == 1
    
    

def _parse_filter(filter):
    """Parses the filter.
    Args:
        filter (dict): Search filter.
    Returns:
        dict: Filter parsed.
    """
    _filter = {}
    
    if filter is None:
        return _filter
    
    for key in filter:
        if key in ['gameId', 'owner', 'status']:
            value = filter[key]
            if key == 'gameId':
                _filter['_id'] = ObjectId(value)
            else:
                _filter[key] = value

    return _filter


def _parse_game(game):  
    if game is None:
        return game
    
    return {
        'gameId': str(game['_id']),
        'name': game['name'],
        'owner': game['owner'],
        'password': game['password'],
        'players': game['players'],
        'psychos': game['psychos'],
        'psychosWin': game['psychosWin'],
        'status': game['status'],
        'rounds': game['rounds']}


def _parse_gamesheaders(games):
    """Parses a games documents into formated dict.
    Args:
        games (dict): game from database.
    Returns:
        dict: parsed game.
    """
    if games is None:
        return games
    
    return [{
        'gameId': str(game['_id']),
        'name': game['name']
    } for game in games]


def check_owner(owner):
    """Checks if the owner is valid.
    Args:
        owner (str): owner of the game.
    Raises:
        ValueError: Raised when the owner is empty.
    """
    if isBlank(owner):
        raise ValueError('The owner\'s name is in not provided.')


def check_name(name):
    """Checks if the name is valid.
    Args:
        name (str): name of the game.
    Raises:
        ValueError: Raised when the name is empty.
    """
    if isBlank(name):
        raise ValueError('The game\'s name is in not provided.')

