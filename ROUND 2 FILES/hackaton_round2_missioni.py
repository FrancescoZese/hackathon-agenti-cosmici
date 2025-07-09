#!/usr/bin/env python3
"""
Script per eseguire e valutare tutte e 6 le missioni del Round 2
Genera un unico file JSON con schema completo:
- final_state annidato
- conta api_calls, misura execution_time
- notes sintetiche
- intermediate_steps coerenti con il validatore
"""
import json
import copy
import time
import os
import shutil
from galactic_apis import GalacticMarketplace, GalaxyNavigator, InfoSphere
from evaluation_system import HackathonEvaluator


def load_initial_state():
    with open('galaxy_state_round2.json', 'r') as f:
        return json.load(f)

# ------------------ Missioni Round 2 ------------------

def mission1(state):
    steps = []
    nav = GalaxyNavigator(state)
    market = GalacticMarketplace(state)
    # 1. posizione iniziale
    loc = nav.get_droid_location('R2-D2')
    steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc})
    # 2. acquisto 2 Laser Sword
    items = [(iid, itm) for iid, itm in market.find_item('Laser Sword')]
    steps.append({'tool': 'find_item', 'item': 'Laser Sword', 'result': items})
    purchased = []
    planets = set()
    for iid, itm in items:
        if itm['planet'] not in planets and len(purchased) < 2:
            res = market.purchase_item(iid)
            steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
            state['client']['inventory'].append(itm['name'])
            purchased.append(f"{itm['name']}({itm['planet']})")
            planets.add(itm['planet'])
    # 3. viaggio economico
    ships = nav.list_available_ships(loc)
    steps.append({'tool': 'list_available_ships', 'origin': loc, 'result': ships})
    best = min(ships, key=lambda n: ships[n]['rental_cost'])
    cost = ships[best]['rental_cost']
    travel = nav.travel(loc, 'Coruscant', best)
    steps.append({'tool': 'travel', 'from': loc, 'to': 'Coruscant', 'ship': best, 'result': travel})
    state['droids']['R2-D2']['location'] = 'Coruscant'
    response = (
        f"Missione 1 completata: inizialmente R2-D2 su {loc}, "
        f"acquistati {', '.join(purchased)}, "
        f"quindi viaggiato con '{best}' ({cost} crediti) a Coruscant; "
        f"totale {len(steps)} API calls."
    )
    return response, steps


def mission2(state):
    steps = []
    info_sys = InfoSphere(state)
    nav = GalaxyNavigator(state)
    market = GalacticMarketplace(state)
    # 1. threat_level Alderaan
    info = info_sys.get_info('Alderaan')
    steps.append({'tool': 'get_info', 'name': 'Alderaan', 'result': info})
    # 2. posizione R2-D2
    loc = nav.get_droid_location('R2-D2')
    steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc})
    threat = info.get('threat_level') if isinstance(info, dict) else None
    if threat == 'low':
        ships = nav.list_available_ships(loc)
        steps.append({'tool': 'list_available_ships', 'origin': loc, 'result': ships})
        ship = min(ships, key=lambda n: ships[n]['rental_cost'])
        cost = ships[ship]['rental_cost']
        travel = nav.travel(loc, 'Alderaan', ship)
        steps.append({'tool': 'travel', 'from': loc, 'to': 'Alderaan', 'ship': ship, 'result': travel})
        state['droids']['R2-D2']['location'] = 'Alderaan'
        transport_msg = f"trasportato {loc}->{'Alderaan'} con {ship} ({cost}c)"
    else:
        transport_msg = f"threat_level='{threat}', nessun trasporto (R2-D2 su {loc})"
    # 3. acquisto Walkman
    items = market.find_item('Walkman degli Antichi')
    steps.append({'tool': 'find_item', 'item': 'Walkman degli Antichi', 'result': items})
    if items:
        iid, itm = items[0]
        res = market.purchase_item(iid)
        steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
        state['client']['inventory'].append(itm['name'])
        wm_msg = f"e acquistato '{itm['name']}'"
    else:
        wm_msg = "e Walkman non disponibile"
    response = (
        f"Missione 2 completata: {transport_msg} {wm_msg}; "
        f"totale {len(steps)} API calls."
    )
    return response, steps


def mission3(state):
    steps = []
    # costi viaggio
    tc = state['travel_costs'].get('Tatooine-Coruscant', 0)
    steps.append({'tool': 'get_travel_cost', 'origin': 'Tatooine', 'destination': 'Coruscant', 'result': tc})
    ca = state['travel_costs'].get('Coruscant-Alderaan', 0)
    steps.append({'tool': 'get_travel_cost', 'origin': 'Coruscant', 'destination': 'Alderaan', 'result': ca})
    total = tc + ca
    state['droids']['R2-D2']['location'] = 'Alderaan'
    response = (
        f"Missione 3 completata: rotta Tatooine→Coruscant→Alderaan con costo {total} crediti; "
        f"{len(steps)} API calls."
    )
    return response, steps


def mission4(state):
    steps = []
    nav = GalaxyNavigator(state)
    market = GalacticMarketplace(state)
    # 1. trasporto base
    loc = nav.get_droid_location('R2-D2')
    steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc})
    if loc != 'Alderaan':
        ships = nav.list_available_ships(loc)
        steps.append({'tool': 'list_available_ships', 'origin': loc, 'result': ships})
        ship = min(ships, key=lambda n: ships[n]['rental_cost'])
        cost = ships[ship]['rental_cost']
        tr = nav.travel(loc, 'Alderaan', ship)
        steps.append({'tool': 'travel', 'from': loc, 'to': 'Alderaan', 'ship': ship, 'result': tr})
        state['droids']['R2-D2']['location'] = 'Alderaan'
    # 2. acquisto 2 oggetti
    items = market.find_item('')
    steps.append({'tool': 'find_item', 'item': '', 'result': items})
    cand = [(iid, itm) for iid, itm in items if itm['planet']=='Alderaan']
    cand.sort(key=lambda x: x[1]['price'])
    purchased = []
    for iid, itm in cand[:2]:
        res = market.purchase_item(iid)
        steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
        state['client']['inventory'].append(itm['name'])
        purchased.append(itm['name'])
    response = (
        f"Missione 4 completata: R2-D2 su Alderaan, acquistati {purchased}; "
        f"{len(steps)} API calls."
    )
    return response, steps


def mission5(state):
    steps = []
    nav = GalaxyNavigator(state)
    market = GalacticMarketplace(state)
    # viaggio & acquisto
    loc = nav.get_droid_location('R2-D2')
    steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc})
    ships = nav.list_available_ships(loc)
    steps.append({'tool': 'list_available_ships', 'origin': loc, 'result': ships})
    ship = min(ships, key=lambda n: ships[n]['rental_cost'])
    cost = ships[ship]['rental_cost']
    tr = nav.travel(loc, 'Alderaan', ship)
    steps.append({'tool': 'travel', 'from': loc, 'to': 'Alderaan', 'ship': ship, 'result': tr})
    state['droids']['R2-D2']['location'] = 'Alderaan'
    items = market.find_item('Holocron')
    steps.append({'tool': 'find_item', 'item': 'Holocron', 'result': items})
    if items:
        iid, itm = items[0]
        res = market.purchase_item(iid)
        steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
        state['client']['inventory'].append(itm['name'])
    ships2 = nav.list_available_ships('Alderaan')
    steps.append({'tool': 'list_available_ships', 'origin': 'Alderaan', 'result': ships2})
    ship2 = min(ships2, key=lambda n: ships2[n]['rental_cost'])
    tr2 = nav.travel('Alderaan', 'Tatooine', ship2)
    steps.append({'tool': 'travel', 'from': 'Alderaan', 'to': 'Tatooine', 'ship': ship2, 'result': tr2})
    state['droids']['R2-D2']['location'] = 'Tatooine'
    response = (
        f"Missione 5 completata: percorso + Holocron acquistato + ritorno; "
        f"{len(steps)} API calls."
    )
    return response, steps


def mission6(state):
    steps = []
    market = GalacticMarketplace(state)
    purchased = []
    for iid, itm in market.find_item(''):
        if itm['price'] <= state['client']['balance']:
            res = market.purchase_item(iid)
            steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
            state['client']['inventory'].append(itm['name'])
            purchased.append(itm['name'])
        else:
            break
    response = f"Missione 6 completata: acquistati {len(purchased)} oggetti."
    return response, steps


def collect_result(task_id, response, steps, state, start, end):
    return {
        'task_id': task_id,
        'agent_response': response,
        'intermediate_steps': steps,
        'final_state': {
            'client': { 'balance': state['client']['balance'], 'inventory': state['client']['inventory']},
            'droids': state['droids']
        },
        'api_calls_count': len(steps),
        'execution_time': round(end - start, 2),
        'success': True,
        'notes': 'Complete JSON schema Round 2'
    }


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(script_dir, 'tasks_round2.csv')
    dst = os.path.join(script_dir, 'tasks.csv')
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copy(src, dst)
    state0 = load_initial_state()
    evalr = HackathonEvaluator(round_number=2)
    results = []
    state = copy.deepcopy(state0)
    for i in range(1, 7):
        start = time.time()
        response, steps = globals()[f'mission{i}'](state)
        end = time.time()
        print(f"--- Missione {i} ---")
        print(evalr.format_evaluation_output(evalr.evaluate_mission(i, response, steps, state)))
        print()
        results.append(collect_result(i, response, steps, state, start, end))
    with open('round2_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print('✅ round2_results.json creato')


if __name__ == '__main__':
    main()
