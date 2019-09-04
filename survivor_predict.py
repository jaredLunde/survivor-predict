import numpy as np
import chalk
import statistics
from scipy import stats


# z_score(game_odds) * 2
#   + z_score(strength_of_schedule)
#   + z_score(inverse_championship_odds)


def american_probability(points):
    return 100 / (points + 100)


def moneyline_probability(points):
    return -points / (-points + 100)


def fractional_probability(odds):
    return 1 / (odds + 1)


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


def create_matchup(favorite, underdog, odds):
    return {
        'favorite': favorite,
        'underdog': underdog,
        'odds': moneyline_probability(odds)
    }


if __name__ == '__main__':
    # Consensus odds from:
    # https://www.sportsline.com/nfl/odds/
    game_odds = [
        create_matchup('chi', 'gb', -166),
        create_matchup('min', 'atl', -198),
        create_matchup('phi', 'was', -439),
        create_matchup('nyj', 'buf', -162),
        create_matchup('bal', 'mia', -322),
        create_matchup('kc', 'jac', -198),
        create_matchup('cle', 'ten', -247),
        create_matchup('lar', 'car', -148),
        create_matchup('sea', 'cin', -445),
        create_matchup('lac', 'ind', -302),
        create_matchup('sf', 'tb', -110),
        create_matchup('det', 'ari', -144),
        create_matchup('dal', 'nyg', -310),
        create_matchup('ne', 'pit', -253),
        create_matchup('no', 'hou', -317),
        create_matchup('den', 'oak', -109)
    ]

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

    game_odds = sorted(game_odds, key=lambda v: v['odds'] * -1)
    game_odds_arr = np.array([matchup['odds'] for matchup in game_odds])
    sos_arr = np.array([sos[matchup['favorite']] for matchup in game_odds])
    champion_odds_arr = np.array([
        1 - fractional_probability(super_bowl_odds[matchup["favorite"]])
        for matchup in game_odds
    ])
    game_z = stats.zscore(game_odds_arr)
    sos_z = stats.zscore(sos_arr)
    champion_z = stats.zscore(champion_odds_arr)
    j_score = []

    for i, matchup in enumerate(game_odds):
        j_score.append((matchup, (game_z[i] * 2) + sos_z[i] + champion_z[i]))

    for i, (matchup, z) in enumerate(sorted(j_score, key=lambda v: v[1] * -1), 1):
        print(f'[{i}]', chalk.blue(teams[matchup['favorite']]['name']))
        print(chalk.green(f'  JScore={round(z, 3)}'))
        print(f'  Game={round(matchup["odds"] * 100, 3)}%')
        print(f'  Championship={round(fractional_probability(super_bowl_odds[matchup["favorite"]]) * 100, 3)}%')

