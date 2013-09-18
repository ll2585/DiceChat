#import json, logging
import logging
import simplejson as json

def player_to_json(player):
    info = {}
    attrs = ['name', 'firstdieroll', 'seconddieroll', 'firstdiereroll', 'seconddiereroll', 'scorethisround', 'totalscore', 'passed']
    for attr in attrs:
        info[attr] = getattr(player, attr)
    return info


def game_to_json(game):
    info = {}
    attrs = ['turn', 'phase', 'step']
    for attr in attrs:
        info[attr] = getattr(game, attr)
    info['players'] = []
    info['turn_logs'] = game.turn_logs[-20:]
    for player in game.players:
        info['players'].append(player_to_json(player))
    info['over'] = game.over
    return json.dumps(info)
    
def action_to_json(action):
    return {'class':action.__class__.__name__, 'repr':repr(action)}
    
def decision_to_json(decision):
    info = {}
    info['cls'] = decision.__class__.__name__
    info['player'] = decision.player.name
    if hasattr(decision, 'buildings'):
        info['buildings'] = []
        for building in decision.buildings:
            info['buildings'].append(building_to_json(building))
    if hasattr(decision, 'tracks'):
        info['tracks'] = []
        for track in decision.tracks:
            info['tracks'].append(get_track_name(track))
    if hasattr(decision, 'actions'):
        info['actions'] = []
        for action in decision.actions:
            info['actions'].append(action_to_json(action))
    return info
