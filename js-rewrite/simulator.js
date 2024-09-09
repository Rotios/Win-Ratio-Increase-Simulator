

function simulate(statistics, simulation_id, original_stats, options) {
    const start_time = Date.now();

    let wins = original_stats.wins;
    let ties = original_stats.ties ?? 0;
    let losses = original_stats.losses;
    let battles = original_stats.battles;

    let battle_diff = 0;

    let percent = wins/battles;

    
    while (percent < (options.target_percentage/100) && battle_diff < options.max_simulated_battles) {
        battle_diff += 1;
        battles += 1;
        let rand = Math.random();
        if (rand <= (options.average_tierate / 100))
            ties += 1
        else if (rand <= (options.average_winrate / 100))
            wins += 1
        else
            losses += 1
        
        percent = wins/battles
    }

    statistics[simulation_id] = {
        'original_stats': original_stats,
        'new_stats': {
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'total_battles': battles,
        },
        'battles_simulated': battle_diff,
        'percent': percent,
        'simulation_number': simulation_id,
        'total_time': time.time() - start_time
    }
}

simulate([], 0, {wins: 5, losses: 5, ties: 1, battles: 11}, {target_percentage: 60, max_simulated_battles: 100, average_tierate: 0, average_winrate: 70})