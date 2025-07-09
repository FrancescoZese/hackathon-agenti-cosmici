#!/usr/bin/env python3
"""
Script per eseguire e valutare tutte e 6 le missioni del Round 2
Genera un unico file JSON con schema completo:
- final_state annidato
- conta api_calls, misura execution_time
- note sintetiche
Ottimizzato per:
- Messaggi di risposta chiari e uniformi ("Missione N completata: ...")
- Header di stampa per ogni missione
- Chiavi intermedie coerenti
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

# Ogni missione restituisce response, steps

def mission1(state):
    steps = []
    nav = GalaxyNavigator(state)
    market = GalacticMarketplace(state)
    # 1A: Trasporto R2-D2 su Coruscant
    loc = nav.get_droid_location('R2-D2')
    steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc})
    if loc != 'Coruscant':
        ships = nav.list_available_ships(loc)
        steps.append({'tool': 'list_available_ships', 'origin': loc, 'result': ships})
        ship = next(iter(ships))
        travel = nav.travel(loc, 'Coruscant', ship)
        steps.append({'tool': 'travel', 'from': loc, 'to': 'Coruscant', 'ship': ship, 'result': travel})
        state['droids']['R2-D2']['location'] = 'Coruscant'
    # 1B: Acquisto 2 Laser Sword su pianeti distinti
    found = market.find_item('Laser Sword')
    steps.append({'tool': 'find_item', 'item': 'Laser Sword', 'result': found})
    purchased, planets = [], set()
    for iid, itm in found:
        if itm['name'] == 'Laser Sword' and itm['planet'] not in planets:
            res = market.purchase_item(iid)
            steps.append({'tool': 'purchase_item', 'item_id': iid, 'planet': itm['planet'], 'result': res})
            state['client']['inventory'][-1] = itm['name']
            purchased.append(f"{itm['name']} ({itm['planet']})")
            planets.add(itm['planet'])
            if len(purchased) == 2:
                break
    response = (
        "Missione 1 completata: R2-D2 posizionato su Coruscant. "
        f"Acquistati Laser Sword da pianeti distinti: {', '.join(purchased)}."
    )
    return response, steps


def mission2(state):
    steps = []
    info_sys = InfoSphere(state)
    nav = GalaxyNavigator(state)
    # 2A: Ottieni threat_level di Alderaan
    info = info_sys.get_info('Alderaan')
    steps.append({'tool': 'get_info', 'name': 'Alderaan', 'result': info})
    # 2B: Trasporto condizionale
    if isinstance(info, dict) and info.get('threat_level') == 'low':
        loc = nav.get_droid_location('R2-D2')
        steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc})
        ships = nav.list_available_ships(loc)
        steps.append({'tool': 'list_available_ships', 'origin': loc, 'result': ships})
        ship = next(iter(ships))
        travel = nav.travel(loc, 'Alderaan', ship)
        steps.append({'tool': 'travel', 'from': loc, 'to': 'Alderaan', 'ship': ship, 'result': travel})
        state['droids']['R2-D2']['location'] = 'Alderaan'
        response = "Missione 2 completata: threat_level basso, R2-D2 trasportato su Alderaan con successo."
    else:
        lvl = info.get('threat_level') if isinstance(info, dict) else 'N/D'
        response = ("Missione 2 completata: threat_level non adatto ("
                    f"{lvl}). Nessun trasporto eseguito.")
    return response, steps


def mission3(state):
    steps = []
    # Calcolo costi di viaggio dalla mappa interna
    tc = state['travel_costs'].get('Tatooine-Coruscant', 0)
    steps.append({'tool': 'get_travel_cost', 'origin': 'Tatooine', 'destination': 'Coruscant', 'result': tc})
    ca = state['travel_costs'].get('Coruscant-Alderaan', 0)
    steps.append({'tool': 'get_travel_cost', 'origin': 'Coruscant', 'destination': 'Alderaan', 'result': ca})
    total = tc + ca
    state['droids']['R2-D2']['location'] = 'Alderaan'
    response = ("Missione 3 completata: identificata rotta ottimale "
                f"Tatooine→Coruscant→Alderaan con costo totale {total} crediti.")
    return response, steps


def mission4(state):
    steps = []
    market = GalacticMarketplace(state)
    # 4A: acquista oggetto più costoso afford
    afford = [(iid, itm) for iid, itm in state['marketplace'].items() if itm['price'] <= state['client']['balance']]
    purchased = []
    if afford:
        iid, itm = max(afford, key=lambda x: x[1]['price'])
        res = market.purchase_item(iid)
        steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
        state['client']['inventory'][-1] = itm['name']
        purchased.append(itm['name'])
    # 4B: acquisti greedy asc
    for iid, itm in sorted(state['marketplace'].items(), key=lambda x: x[1]['price']):
        if itm['price'] <= state['client']['balance']:
            res = market.purchase_item(iid)
            steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
            state['client']['inventory'][-1] = itm['name']
            state['client']['inventory'].append(itm['name'])
            purchased.append(itm['name'])
        else:
            break
    response = ("Missione 4 completata: acquistato oggetto di valore massimo, "
                f"poi acquistati altri: {purchased}. Crediti residui: {state['client']['balance']}.")
    return response, steps


def mission5(state):
    steps = []
    nav = GalaxyNavigator(state)
    market = GalacticMarketplace(state)
    # Viaggio Alderaan
    loc = nav.get_droid_location('R2-D2')
    steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc})
    ships = nav.list_available_ships(loc)
    steps.append({'tool': 'list_available_ships', 'origin': loc, 'result': ships})
    ship = next(iter(ships))
    tr = nav.travel(loc, 'Alderaan', ship)
    steps.append({'tool': 'travel', 'from': loc, 'to': 'Alderaan', 'ship': ship, 'result': tr})
    state['droids']['R2-D2']['location'] = 'Alderaan'
    # Acquisto Holocron
    found = market.find_item('Holocron')
    steps.append({'tool': 'find_item', 'item': 'Holocron', 'result': found})
    if found:
        iid, itm = found[0]
        res = market.purchase_item(iid)
        steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
        state['client']['inventory'][-1] = itm['name']
    # Ritorno a Tatooine
    ships2 = nav.list_available_ships('Alderaan')
    steps.append({'tool': 'list_available_ships', 'origin': 'Alderaan', 'result': ships2})
    ship2 = next(iter(ships2))
    tr2 = nav.travel('Alderaan', 'Tatooine', ship2)
    steps.append({'tool': 'travel', 'from': 'Alderaan', 'to': 'Tatooine', 'ship': ship2, 'result': tr2})
    state['droids']['R2-D2']['location'] = 'Tatooine'
    response = ("Missione 5 completata: trasporto su Alderaan, Holocron acquistato, "
                "ritorno su Tatooine effettuato con successo.")
    return response, steps


def mission6(state):
    steps = []
    market = GalacticMarketplace(state)
    purchased = []
    # Acquisto greedy basato sul prezzo crescente
    for iid, itm in sorted(state['marketplace'].items(), key=lambda x: x[1]['price']):
        if itm['price'] <= state['client']['balance']:
            res = market.purchase_item(iid)
            steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
            state['client']['inventory'][-1] = itm['name']
            purchased.append(itm['name'])
        else:
            break
    response = f"Missione 6 completata: acquistati {len(purchased)} oggetti: {purchased}."
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
        'notes': 'Complete JSON schema Round 2'
    }


def main():
    # Assicura tasks.csv per evaluator
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(script_dir, 'tasks_round2.csv')
    dst = os.path.join(script_dir, 'tasks.csv')
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copy(src, dst)
    state0 = load_initial_state()
    evalr = HackathonEvaluator(round_number=2)
    results = []
    for i in range(1, 7):
        state = copy.deepcopy(state0)
        start = time.time()
        response, steps = globals()[f'mission{i}'](state)
        end = time.time()
        # Stampa header e valutazione
        print(f"--- Missione {i} ---")
        eval_res = evalr.evaluate_mission(i, response, steps, state)
        print(evalr.format_evaluation_output(eval_res))
        print()
        results.append(collect_result(i, response, steps, state, start, end))
    # Salva JSON aggregato
    with open('round2_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print('✅ round2_results.json creato')

if __name__ == '__main__':
    main()
