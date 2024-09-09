import time
import random
from statistics import mean
from threading import Thread
import json
import random
from statistics import mean
from threading import Thread
from types import SimpleNamespace
import os

def simulate(sim_statistics, simulation_num, original_stats, options):
    start_time = time.time()

    wins = original_stats.wins
    battles = original_stats.battles
    ties = original_stats.ties
    losses = original_stats.losses

    battle_diff = 0
    percent = wins/battles
    while (percent < (options.target_percentage/100) and battle_diff < options.max_simulated_battles):
        battle_diff += 1
        battles += 1
        rand = random.random()
        if rand <= (options.average_tierate / 100):
            ties += 1
        elif rand <= (options.average_winrate / 100):
            wins += 1
        else:    
            losses += 1
        
        percent = wins/battles

    print("Completed Simulation Run:", simulation_num if simulation_num >= 10 else '0' + str(simulation_num), "Battles Simulated:", battle_diff)

    sim_statistics[simulation_num] = {
        'original_stats': original_stats.__dict__,
        'new_stats': {
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'total_battles': battles,
        },
        'battles_simulated': battle_diff,
        'percent': percent,
        'simulation_number': simulation_num,
        'total_time': time.time() - start_time
    }

def run_individual_threads(total_battles, total_wins, num_simulations, sim_statistics, total_losses, options):
    threads = []

    for i in range(0, num_simulations):
        original_stats = SimpleNamespace(**{
            'wins': total_wins,
            'losses': total_losses,
            'ties': 0,
            'battles': total_battles,
        })

        new_t = Thread(target=simulate, args=(sim_statistics, i, original_stats, options))
        new_t.start()

        threads.append(new_t)

    for thread in threads:
        thread.join()

def validate_event(event):
    keys = ['averageWinrate', 'totalBattles', 'totalWins', 'targetPercentage']

    for k in keys:
        if k not in event and not event.get('isTest', False):
            raise ValueError('Must provide all of the following properties: {}. Missing key was {}.'.format(json.dumps(keys), k))


def handle_event(event):
    t0 = time.time()

    validate_event(event)
    average_winrate = event.get('averageWinrate', 70)
    total_battles = event.get('totalBattles', 10000)
    total_wins = event.get('totalWins', 5000)
    target_percentage = event.get('targetPercentage', 60)

    max_simulated_battles = total_battles * total_battles

    if max_simulated_battles < 1000:
        max_simulated_battles = 1000

    num_simulations = os.environ.get('MAX_SIMULATIONS', 1000)

    if num_simulations > event.get('simulations', num_simulations):
        num_simulations = event['simulations']

    sim_statistics = [0] * num_simulations

    if total_wins/total_battles > target_percentage/100:
        print("Wins already greater than target percentage!") 
        raise ValueError('Wins already greater than target percentage!')

    total_losses = total_battles - total_wins

    options = SimpleNamespace(
            max_simulated_battles = max_simulated_battles,
            average_winrate = average_winrate,
            target_percentage = target_percentage,
            average_tierate = 0
        )

    run_individual_threads(total_battles, total_wins, num_simulations, sim_statistics, total_losses, options)
    
    num_diff_battles = [stats['battles_simulated'] for stats in sim_statistics if stats['battles_simulated'] > 0]

    avg_battles_required = mean(num_diff_battles)
    max_battles_required = max(num_diff_battles)
    min_battles_required = min(num_diff_battles)

    sim_times = [stat['total_time'] for stat in sim_statistics]
    avg_sim_time = mean(sim_times)
    total_statistics = {
        'total_time': time.time() - t0,
        'average_sim_time': avg_sim_time,
        'average_win_rate': average_winrate,
        'target_win_rate': target_percentage,
        'average_battles_required': avg_battles_required,
        'max_battles_required': max_battles_required,
        'min_battles_required': min_battles_required,
        'original_information': {
            'wins': total_wins,
            'losses': total_losses,
            'battles': total_battles,
            'original_winrate': total_wins/total_battles
        },
        'num_simulations': num_simulations,
        'max_allowed_battles': max_simulated_battles
    }

    if event.get('isDetailed', False):
        total_statistics['sim_statistics'] = sim_statistics
    else:
        total_statistics['sim_statistics'] = sim_statistics[:100]

    print("Returning total statistics of " + json.dumps(total_statistics))
    return total_statistics

