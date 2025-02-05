def track_statistics(picks):
    stats = {}
    for pick in picks:
        sport = pick['sport']
        result = pick['result']
        if sport not in stats:
            stats[sport] = {'total': 0, 'won': 0, 'lost': 0}
        stats[sport]['total'] += 1
        if result == 'Won':
            stats[sport]['won'] += 1
        elif result == 'Lost':
            stats[sport]['lost'] += 1
    return stats 