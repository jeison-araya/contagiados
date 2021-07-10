from flask import Flask, request, jsonify
from flask_restful import Api
from decouple import config

from services import games as games_service

app = Flask(__name__)
api = Api(app)


@app.route('/game')
def list_all_games():
    return jsonify(games_service.get_all_games(filter=_build_filter(request.args)))


@app.route('/game/create', methods=['POST'])
def create_game():
    owner = request.headers.get('name')
    
    name = request.json.get('name')
    password = request.json.get('password')
    
    try:
        return jsonify(games_service.create(owner=owner,
                                    name=name,
                                    password=password))
    except ValueError as e:
        return ({'error': str(e)}, 406)


@app.route('/game/<gameId>')
def game_by_id(gameId):
    name = request.headers.get('name')
    password = request.headers.get('password')
    
    try:
        return jsonify(games_service.get_game_by_id(gameId=gameId,
                                                    name=name,
                                                    password=password))
    except ValueError as e:
        
        error, status_code = e.args
        return ({'error': error}, status_code)


@app.route('/game/<gameId>/join', methods=['PUT'])
def join_game(gameId):
    name = request.headers.get('name')
    password = request.headers.get('password')
    
    try:
        updated = games_service.join_game(gameId=gameId,
                                              name=name,
                                              password=password)
        
        if updated:
            return jsonify({'message': 'Operation successful'})
        else: 
            return ({'error': 'Operation failed'}, 500)
            
    except ValueError as e:
        
        error, status_code = e.args
        return ({'error': error}, status_code)
    
    
def _build_filter(args):
    filter_key = args.get('filter')
    filter_value = args.get('filterValue')
    
    return {filter_key: filter_value} if filter_key and filter_value else None


def run():
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    run()