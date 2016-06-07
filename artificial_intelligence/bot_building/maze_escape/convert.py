# coding=utf-8
import json
import os

TARGET = 'allmoves.json'
DUMP = 'allmoves-fixed.json'
BASE_PATH = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(BASE_PATH, TARGET)) as f:
    games = json.load(f)

for i, game in enumerate(games):
    for key, value in game.items():
        try:
            game[key] = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass

with open(os.path.join(BASE_PATH, DUMP), 'w') as f:
    json.dump(games, f, sort_keys=True, indent=2)
