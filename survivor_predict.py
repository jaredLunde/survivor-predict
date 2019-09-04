import os
import json
import math
import click
import requests
import numpy as np
import chalk
import statistics
import diskcache as dc
from datetime import datetime
from scipy import stats
from dotenv import load_dotenv

load_dotenv()


# z_score(game_odds)
#   + z_score(strength_of_schedule)
#   + z_score(inverse_futuresship_odds) * math.log(17 - week, 10)  # decay function


def american_probability(points):
    return 100 / (points + 100)


def moneyline_probability(points):
    return -points / (-points + 100)


def fractional_probability(odds):
    return 1 / (odds + 1)


def decimal_probability(odds):
    return american_probability((odds - 1) * 100)


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
# TODO: bs4 odds from: https://www.actionnetwork.com/nfl/futures
super_bowl_odds = {
    'kc': 5 / 1,
    'ne': 6 / 1,
    'no': 12 / 1,
    'chi': 12 / 1,
    'phi': 12 / 1,
    'lar': 14 / 1,
    'lac': 14 / 1,
    'pit': 18 / 1,
    'cle': 18 / 1,
    'min': 20 / 1,
    'gb': 20 / 1,
    'dal': 20 / 1,
    'sea': 20 / 1,
    'jac': 25 / 1,
    'atl': 30 / 1,
    'bal': 40 / 1,
    'oak': 40 / 1,
    'sf': 40 / 1,
    'hou': 50 / 1,
    'car': 50 / 1,
    'nyj': 60 / 1,
    'ind': 80 / 1,
    'ten': 80 / 1,
    'den': 80 / 1,
    'det': 80 / 1,
    'buf': 100 / 1,
    'tb': 100 / 1,
    'nyg': 200 / 1,
    'cin': 200 / 1,
    'was': 300 / 1,
    'ari': 300 / 1,
    'mia': 500 / 1,
}


def create_teams(teams, sites):
    odds_a = 0
    odds_b = 0

    for site in sites:
        odds_a += site['odds']['h2h'][0]
        odds_b += site['odds']['h2h'][1]

    return [
        {
            'abbr': team_to_abbr(teams[0]),
            'probability': decimal_probability(odds_a / len(sites))
        },
        {
            'abbr': team_to_abbr(teams[1]),
            'probability': decimal_probability(odds_b / len(sites))
        }
    ]


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

    out = []
    for data in next_odds_data:
        out.extend(create_teams(data['teams'], data['sites']))
    return out


def cache(key):
    disk_cache = dc.Cache(f'tmp/{key}')
    key = datetime.now().strftime(f"{key}-%Y-%m-%d-%H").encode()

    def wrapper(fn):
        def wrapped(*a, **kw):
            if disk_cache.get(key):
                return json.loads(disk_cache[key].decode())
            result = fn(*a, **kw)
            disk_cache.clear()
            disk_cache[key] = json.dumps(result).encode()
            return result

        return wrapped

    return wrapper


@cache('game_odds')
def get_game_odds():
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

    return rapid_response.json()['data']


@click.command()
@click.option("--week", default=1, help="Current week")
def main(week):
    print(chalk.blue(f'NFL Week {week}'), '\n')
    game_odds = parse_odds(get_game_odds())
    # Strength of remaining schedule
    # TODO: bs4 this page
    # https://www.sportsbettingdime.com/nfl/proper-way-to-calculate-strength-of-schedule/
    sos = {
        'kc': 134.5,
        'ne': 117.5,
        'no': 132,
        'chi': 135.5,
        'phi': 123,
        'lar': 127.5,
        'lac': 131,
        'pit': 127,
        'cle': 122.5,
        'min': 133,
        'gb': 130.5,
        'dal': 128.5,
        'sea': 132,
        'jac': 133.5,
        'atl': 135.5,
        'bal': 128,
        'oak': 136.5,
        'sf': 130,
        'hou': 138.5,
        'car': 134.5,
        'nyj': 121,
        'ind': 131,
        'ten': 135,
        'den': 138,
        'det': 131.5,
        'buf': 123,
        'tb': 135,
        'nyg': 124.5,
        'cin': 127.5,
        'was': 128.5,
        'ari': 132.5,
        'mia': 129.5,
    }
    # sorts matchups by odds
    game_odds = sorted(game_odds, key=lambda v: v['probability'] * -1)
    # creates numpy arrays from matchups, strength of schedule, etc
    game_odds_arr = np.array([matchup['probability'] for matchup in game_odds])
    sos_arr = np.array([sos[matchup['abbr']] for matchup in game_odds])
    futures_odds_arr = np.array([
        1 - fractional_probability(super_bowl_odds[matchup["abbr"]])
        for matchup in game_odds
    ])
    # calculates z-scores for each metric
    game_z = stats.zscore(game_odds_arr)
    sos_z = stats.zscore(sos_arr)
    futures_z = stats.zscore(futures_odds_arr)
    j_score = []
    # calculates the j-score ;-P
    for i, team in enumerate(game_odds):
        data = {
            'team': team,
            'game_score': game_z[i] * math.log(week + 4, 2),
            # 'schedule_score': sos_z[i] * math.log(17 - week, 10),
            'futures_score': futures_z[i] * math.log(17 - week, 10)
        }
        j_score.append({
            **data,
            'j_score': data['game_score'] + data['futures_score']
        })

    # prints the results
    for i, data in enumerate(sorted(j_score, key=lambda v: v['j_score'] * -1)):
        team = data['team']
        print(f'[{i + 1}]', chalk.blue(teams[team['abbr']]['name']))
        print(chalk.green(f'  JScore={round(data["j_score"], 3)}'))
        print(f'  Game={round(team["probability"] * 100, 3)}% {chalk.yellow(round(data["game_score"], 3))}')
        # print(f'  Schedule={round(sos_arr[i], 3)} {chalk.yellow(round(data["schedule_score"], 3))}')
        print(f'  Futures={round(fractional_probability(super_bowl_odds[team["abbr"]]) * 100, 3)}% {chalk.yellow(round(data["futures_score"], 3))}')


if __name__ == '__main__':
    main()
