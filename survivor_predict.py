import os
import json
import requests
import numpy as np
import chalk
import statistics
import diskcache as dc
from datetime import datetime
from scipy import stats
from dotenv import load_dotenv
load_dotenv()


# z_score(game_odds) * 2
#   + z_score(strength_of_schedule)
#   + z_score(inverse_championship_odds)


def american_probability(points):
    return 100 / (points + 100)


def moneyline_probability(points):
    return -points / (-points + 100)


def fractional_probability(odds):
    return 1 / (odds + 1)


def decimal_probability(odds):
    return american_probability((odds - 1) *100)


teams = {
    'kc': {
        'locale': 'Kansas City',
        'name': 'Chiefs'
    },
    'ne': {
        'locale': 'New England',
        'name': 'Patriots'
    },
    'no': {
        'locale': 'New Orleans',
        'name': 'Saints'
    },
    'chi': {
        'locale': 'Chicago',
        'name': 'Bears'
    },
    'phi': {
        'locale': 'Philadelphia',
        'name': 'Eagles'
    },
    'lar': {
        'locale': 'Los Angeles',
        'name': 'Rams'
    },
    'lac': {
        'locale': 'Los Angeles',
        'name': 'Chargers'
    },
    'pit': {
        'locale': 'Pittsburgh',
        'name': 'Steelers'
    },
    'cle': {
        'locale': 'Cleveland',
        'name': 'Browns'
    },
    'min': {
        'locale': 'Minnesota',
        'name': 'Vikings'
    },
    'gb': {
        'locale': 'Green Bay',
        'name': 'Packers'
    },
    'dal': {
        'locale': 'Dallas',
        'name': 'Cowboys'
    },
    'sea': {
        'locale': 'Seattle',
        'name': 'Seahawks'
    },
    'jac': {
        'locale': 'Jacksonville',
        'name': 'Jaguars'
    },
    'atl': {
        'locale': 'Atlanta',
        'name': 'Falcons'
    },
    'bal': {
        'locale': 'Baltimore',
        'name': 'Ravens'
    },
    'oak': {
        'locale': 'Oakland',
        'name': 'Raiders'
    },
    'sf': {
        'locale': 'San Francisco',
        'name': '49ers'
    },
    'hou': {
        'locale': 'Houston',
        'name': 'Texans'
    },
    'nyj': {
        'locale': 'New York',
        'name': 'Jets'
    },
    'ind': {
        'locale': 'Indianapolis',
        'name': 'Colts'
    },
    'ten': {
        'locale': 'Tennessee',
        'name': 'Titans'
    },
    'den': {
        'locale': 'Denver',
        'name': 'Broncos'
    },
    'det': {
        'locale': 'Detroit',
        'name': 'Lions'
    },
    'buf': {
        'locale': 'Buffalo',
        'name': 'Bills'
    },
    'tb': {
        'locale': 'Tampa Bay',
        'name': 'Buccaneers'
    },
    'nyg': {
        'locale': 'New York',
        'name': 'Giants'
    },
    'cin': {
        'locale': 'Cincinnati',
        'name': 'Bengals'
    },
    'was': {
        'locale': 'Washington',
        'name': 'Redskins'
    },
    'ari': {
        'locale': 'Arizona',
        'name': 'Cardinals'
    },
    'mia': {
        'locale': 'Miami',
        'name': 'Dolphins'
    },
    'car': {
        'locale': 'Carolina',
        'name': 'Panthers'
    }
}

# http://www.vegasinsider.com/nfl/odds/futures/
super_bowl_odds = {
    'kc': 5/1,
    'ne': 6/1,
    'no': 12/1,
    'chi': 12/1,
    'phi': 12/1,
    'lar': 14/1,
    'lac': 14/1,
    'pit': 18/1,
    'cle': 18/1,
    'min': 20/1,
    'gb': 20/1,
    'dal': 20/1,
    'sea': 20/1,
    'jac': 25/1,
    'atl': 30/1,
    'bal': 40/1,
    'oak': 40/1,
    'sf': 40/1,
    'hou': 50/1,
    'car': 50/1,
    'nyj': 60/1,
    'ind': 80/1,
    'ten': 80/1,
    'den': 80/1,
    'det': 80/1,
    'buf': 100/1,
    'tb': 100/1,
    'nyg': 200/1,
    'cin': 200/1,
    'was': 300/1,
    'ari': 300/1,
    'mia': 500/1,
}


def create_matchup(teams, sites):
    odds_a = 0
    odds_b = 0

    for site in sites:
        odds_a += site['odds']['h2h'][0]
        odds_b += site['odds']['h2h'][1]

    return {
        'favorite': team_to_abbr(teams[0] if odds_a < odds_b else teams[1]),
        'underdog': team_to_abbr(teams[1] if odds_a < odds_b else teams[0]),
        'probability': decimal_probability((odds_a if odds_a < odds_b else odds_b) / len(sites))
    }


def team_to_abbr(team):
    for abbr, maybe in teams.items():
        if team.strip() == f"{maybe['locale']} {maybe['name']}":
            return abbr
    raise KeyError(f'Team not found in teams dictionary: {team}')


def parse_odds(odds_data):
    seen = set()
    next_odds_data = []

    for d in odds_data:
        if d['sites_count'] > 0 and d['teams'][0] not in seen and d['teams'][1] not in seen:
            next_odds_data.append(d)
            seen.add(d['teams'][0])
            seen.add(d['teams'][1])

    return [
        create_matchup(data['teams'], data['sites'])
        for data in next_odds_data
    ]


def get_game_odds():
    cache = dc.Cache('tmp')
    key = datetime.now().strftime("NFL-%Y-%m-%d-%H").encode()

    if cache.get(key):
        return json.loads(cache[key].decode())

    # Calls Rapid API with your API key
    rapid_response = requests.get(
        'https://odds.p.rapidapi.com/v1/odds',
        params={
            'sport': 'americanfootball_nfl',
            'region': 'us',
            'mkt': 'h2h'
        },
        headers={
            'X-RapidAPI-Host': 'odds.p.rapidapi.com',
            'X-RapidAPI-Key': os.getenv('RAPID_API_KEY')
        }
    )

    cache.clear()
    game_odds = rapid_response.json()['data']
    cache[key] = json.dumps(game_odds).encode()
    return game_odds


if __name__ == '__main__':
    game_odds = parse_odds(get_game_odds())

    # Strength of remaining schedule
    sos = {
        'kc': 0.520,
        'ne': 0.473,
        'no': 0.488,
        'chi': 0.520,
        'phi': 0.477,
        'lar': 0.473,
        'lac': 0.502,
        'pit': 0.496,
        'cle': 0.484,
        'min': 0.512,
        'gb': 0.504,
        'dal': 0.504,
        'sea': 0.479,
        'jac': 0.531,
        'atl': 0.518,
        'bal': 0.496,
        'oak': 0.539,
        'sf': 0.510,
        'hou': 0.527,
        'car': 0.502,
        'nyj': 0.473,
        'ind': 0.518,
        'ten': 0.514,
        'den': 0.537,
        'det': 0.496,
        'buf': 0.480,
        'tb': 0.508,
        'nyg': 0.473,
        'cin': 0.473,
        'was': 0.469,
        'ari': 0.508,
        'mia': 0.500,
    }
    # sorts matchups by odds
    game_odds = sorted(game_odds, key=lambda v: v['probability'] * -1)
    # creates numpy arrays from matchups, strength of schedule, etc
    game_odds_arr = np.array([matchup['probability'] for matchup in game_odds])
    sos_arr = np.array([sos[matchup['favorite']] for matchup in game_odds])
    champion_odds_arr = np.array([
        1 - fractional_probability(super_bowl_odds[matchup["favorite"]])
        for matchup in game_odds
    ])
    # calculates z-scores for each metric
    game_z = stats.zscore(game_odds_arr)
    sos_z = stats.zscore(sos_arr)
    champion_z = stats.zscore(champion_odds_arr)
    j_score = []
    # calculates the j-score ;-P
    for i, matchup in enumerate(game_odds):
        j_score.append((matchup, (game_z[i] * 2) + sos_z[i] + champion_z[i]))
    # prints the results
    for i, (matchup, z) in enumerate(sorted(j_score, key=lambda v: v[1] * -1), 1):
        print(f'[{i}]', chalk.blue(teams[matchup['favorite']]['name']))
        print(chalk.green(f'  JScore={round(z, 3)}'))
        print(f'  Game={round(matchup["probability"] * 100, 3)}%')
        print(f'  Championship={round(fractional_probability(super_bowl_odds[matchup["favorite"]]) * 100, 3)}%')

