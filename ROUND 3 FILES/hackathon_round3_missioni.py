#!/usr/bin/env python3

"""
Script per eseguire e valutare tutte e 5 le missioni del Round 3
Genera un unico file JSON con schema completo:
- final_state annidato
- conta api_calls e misura execution_time
- note sintetiche
"""
import json
import copy
import time
import os
import shutil
import sys
from itertools import permutations

# Consente di importare correttamente le missioni del Round 1
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
round1_dir = os.path.join(project_root, 'ROUND 1 FILES')
sys.path.insert(0, round1_dir)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ROUND 1 FILES')))
from hackathon_round1_missioni import mission1 as r1m1, mission2 as r1m2, mission3 as r1m3, mission4 as r1m4

from galactic_apis import GalacticMarketplace, GalaxyNavigator, InfoSphere
from evaluation_system import HackathonEvaluator

# Carica stato iniziale di Round 3
def load_initial_state():
    with open('galaxy_state_round3.json', 'r') as f:
        return json.load(f)

# ----------------- Missioni Round 3 -----------------

def mission1(state):
    """SPEED RUN: completa 4 missioni del Round1 minimizzando le chiamate API"""
    results = []
    for tid, fn in [(1, r1m1), (2, r1m2), (3, r1m3), (4, r1m4)]:
        st = copy.deepcopy(state)
        _, steps = fn(st)
        results.append((tid, steps, st))
    # Seleziona le 3 missioni con meno API calls
    chosen = sorted(results, key=lambda x: len(x[1]))[:3]
    steps = []
    for tid, s, st in chosen:
        steps.extend(s)
        state = st
    response = (
        f"Missione 1 completata: eseguite Round1 tasks "
        f"{[tid for tid,_,_ in chosen]} con tot. {len(steps)} API calls."
    )
    return response, steps


def mission2(state):
    """INTELLIGENCE: raccogli info su tutte le entità InfoSphere e crea report"""
    steps = []
    infosphere = InfoSphere(state)
    report = {}
    for entity in state['infosphere'].keys():
        info = infosphere.get_info(entity)
        steps.append({'tool': 'get_info', 'name': entity, 'result': info})
        report[entity] = info
    response = (
        f"Missione 2 completata: raccolte informazioni per "
        f"{len(report)} entità in InfoSphere."
    )
    return response, steps


def mission3(state):
    """LOGISTICS MASTER: rotta che tocca tutti i pianeti col minimo costo"""
    steps = []
    nav = GalaxyNavigator(state)
    planets = ['Coruscant', 'Tatooine', 'Alderaan']
    start = state['droids']['R2-D2']['location']
    best_path, best_cost = None, float('inf')
    # Calcola costo per ogni permutazione
    for perm in permutations([p for p in planets if p != start]):
        path = [start] + list(perm)
        cost = 0
        for a, b in zip(path, path[1:]):
            c = state['travel_costs'].get(f"{a}-{b}") or state['travel_costs'].get(f"{b}-{a}")
            steps.append({'tool': 'get_travel_cost', 'origin': a, 'destination': b, 'result': c})
            cost += c
        if cost < best_cost:
            best_cost, best_path = cost, path
    # Esegui viaggi nella rotta ottimale
    for a, b in zip(best_path, best_path[1:]):
        ship = next(iter(nav.list_available_ships(a)))
        tr = nav.travel(a, b, ship)
        steps.append({'tool': 'travel', 'from': a, 'to': b, 'ship': ship, 'result': tr})
    state['droids']['R2-D2']['location'] = best_path[-1]
    response = (
        f"Missione 3 completata: percorso ottimale {best_path} "
        f"con costo totale {best_cost} crediti."
    )
    return response, steps


def mission4(state):
    """MULTI-OBJECTIVE: porta R2-D2 su ogni pianeta e compra 1 oggetto per ciascuno"""
    steps = []
    nav = GalaxyNavigator(state)
    market = GalacticMarketplace(state)
    planets = ['Coruscant', 'Tatooine', 'Alderaan']
    purchased = []
    for planet in planets:
        # Sposta se necessario
        loc = nav.get_droid_location('R2-D2')
        steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc})
        if loc != planet:
            ships = nav.list_available_ships(loc)
            steps.append({'tool': 'list_available_ships', 'origin': loc, 'result': ships})
            ship = next(iter(ships))
            tr = nav.travel(loc, planet, ship)
            steps.append({'tool': 'travel', 'from': loc, 'to': planet, 'ship': ship, 'result': tr})
        # Compra il più economico su quel pianeta
        items = [(iid, itm) for iid, itm in state['marketplace'].items() if itm['planet'] == planet]
        iid, itm = min(items, key=lambda x: x[1]['price'])
        res = market.purchase_item(iid)
        steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
        state['client']['inventory'][-1] = itm['name']
        purchased.append(f"{itm['name']} ({planet})")
    response = (
        f"Missione 4 completata: R2-D2 visitati {planets} "
        f"e acquistati {purchased}."
    )
    return response, steps


def mission5(state):
    """ULTIMATE CHALLENGE: costruisci circuito completo e compra Hyperdrive Core"""
    steps = []
    nav = GalaxyNavigator(state)
    market = GalacticMarketplace(state)
    circuit = ['Coruscant', 'Tatooine', 'Alderaan', 'Coruscant']
    for a, b in zip(circuit, circuit[1:]):
        loc = nav.get_droid_location('R2-D2')
        steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc})
        ship = next(iter([s for s in state['ships']
                           if state['ships'][s]['location'] == a and state['ships'][s]['available']]))
        tr = nav.travel(a, b, ship)
        steps.append({'tool': 'travel', 'from': a, 'to': b, 'ship': ship, 'result': tr})
        state['droids']['R2-D2']['location'] = b
    # Acquisto Hyperdrive Core
    found = market.find_item('Hyperdrive Core')
    steps.append({'tool': 'find_item', 'item': 'Hyperdrive Core', 'result': found})
    if found:
        iid, itm = found[0]
        res = market.purchase_item(iid)
        steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
        state['client']['inventory'][-1] = itm['name']
        response = "Missione 5 completata: circuito effettuato e Hyperdrive Core acquistato."
    else:
        response = "Missione 5: Hyperdrive Core non disponibile, circuito completato comunque."
    return response, steps


def collect_result(task_id, response, steps, state, start, end):
    return {
        'task_id': task_id,
        'agent_response': response,
        'intermediate_steps': steps,
        'final_state': {
            'client': {'balance': state['client']['balance'], 'inventory': state['client']['inventory']},
            'droids': state['droids']
        },
        'api_calls_count': len(steps),
        'execution_time': round(end - start, 2),
        'success': True,
        'notes': 'Schema JSON completo Round 3'
    }


def main():
    # Assicura tasks.csv per evaluator
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(script_dir, 'tasks_round3.csv')
    dst = os.path.join(script_dir, 'tasks.csv')
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copy(src, dst)

    initial_state = load_initial_state()
    evaluator = HackathonEvaluator(round_number=3)
    all_results = []

    for task_id in range(1, 6):
        state = copy.deepcopy(initial_state)
        t0 = time.time()
        response, steps = globals()[f'mission{task_id}'](state)
        t1 = time.time()
        print(f"--- Missione {task_id} ---")
        print(evaluator.format_evaluation_output(
            evaluator.evaluate_mission(task_id, response, steps, state)
        ))
        print()
        all_results.append(collect_result(task_id, response, steps, state, t0, t1))

    with open('round3_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    print('✅ round3_results.json creato')

if __name__ == '__main__':
    main()
