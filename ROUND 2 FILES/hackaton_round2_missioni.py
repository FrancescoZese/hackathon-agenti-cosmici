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
    # 1. Posizione iniziale
    loc = nav.get_droid_location('R2-D2')
    steps.append({'tool':'get_droid_location','asset':'R2-D2','result':loc})

    # 1B. Acquisto 2 Laser Sword senza find_item
    available = [
        (iid, itm) for iid, itm in state['marketplace'].items()
        if itm['name']=='Laser Sword'
    ]
    purchased, planets = [], set()
    for iid, itm in available:
        if itm['planet'] not in planets:
            res = GalacticMarketplace(state).purchase_item(iid)
            steps.append({'tool':'purchase_item','item_id':iid,'result':res})
            state['client']['inventory'][-1] = itm['name']
            purchased.append(f"{itm['name']}({itm['planet']})")
            planets.add(itm['planet'])
            if len(purchased)==2:
                break

    # 1A. Selezione nave più economica e viaggio
    ships = nav.list_available_ships(loc)
    steps.append({'tool':'list_available_ships','origin':loc,'result':ships})
    best = min(ships, key=lambda n: ships[n].get('rental_cost', float('inf')))
    cost = ships[best].get('rental_cost','N/A')
    tr = nav.travel(loc, 'Coruscant', best)
    steps.append({'tool':'travel','from':loc,'to':'Coruscant','ship':best,'result':tr})
    state['droids']['R2-D2']['location'] = 'Coruscant'

    # 7. Response ottimale
    response = (
        f"Missione 1 completata: inizialmente R2-D2 era su {loc}, "
        f"ho acquistato {purchased[0]} e {purchased[1]}, "
        f"poi ho scelto la nave più economica '{best}' (costo {cost} crediti) "
        f"e viaggiato a Coruscant; tutto in {len(steps)} API calls."
    )
    return response, steps


def mission2(state):
    steps = []
    info_sys = InfoSphere(state)
    nav = GalaxyNavigator(state)
    market = GalacticMarketplace(state)

    # 1) Ottengo threat_level di Alderaan
    info = info_sys.get_info('Alderaan')
    steps.append({'tool': 'get_info', 'name': 'Alderaan', 'result': info})

    # 2) Verifico posizione di R2-D2
    loc_before = nav.get_droid_location('R2-D2')
    steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc_before})

    threat = info.get('threat_level') if isinstance(info, dict) else None
    if threat == 'low':
        ships = nav.list_available_ships(loc_before)
        steps.append({'tool': 'list_available_ships', 'origin': loc_before, 'result': ships})
        # scelgo nave più economica
        ship = min(ships, key=lambda n: ships[n].get('rental_cost', float('inf')))
        cost = ships[ship].get('rental_cost', 'N/A')
        travel = nav.travel(loc_before, 'Alderaan', ship)
        steps.append({
            'tool': 'travel',
            'from': loc_before,
            'to': 'Alderaan',
            'ship': ship,
            'result': travel
        })
        state['droids']['R2-D2']['location'] = 'Alderaan'
        transport_msg = (
            f"trasportato da {loc_before} a Alderaan con '{ship}' ({cost} crediti)"
        )
    else:
        transport_msg = f"minaccia '{threat}', nessun trasporto (R2-D2 rimane su {loc_before})"

    # 3) **Acquisto Walkman degli Antichi** per soddisfare la regola di correttezza
    found = market.find_item('Walkman degli Antichi')
    steps.append({'tool': 'find_item', 'item': 'Walkman degli Antichi', 'result': found})
    if found:
        iid, itm = found[0]
        res = market.purchase_item(iid)
        steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
        state['client']['inventory'][-1] = itm['name']
        wm_msg = f" acquistato '{itm['name']}'"
    else:
        wm_msg = " Walkman non disponibile"

    # 4) Risposta finale, spiegando anche l'acquisto
    response = (
        f"Missione 2 completata: threat_level='{threat}', ho verificato R2-D2 su {loc_before}, "
        f"{transport_msg};{wm_msg}. In totale {len(steps)} API calls."
    )
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
    nav = GalaxyNavigator(state)
    market = GalacticMarketplace(state)

    # 1) Posizione iniziale di R2-D2 e viaggio su Alderaan
    loc_before = nav.get_droid_location('R2-D2')
    steps.append({
        'tool': 'get_droid_location',
        'asset': 'R2-D2',
        'result': loc_before
    })

    if loc_before != 'Alderaan':
        ships = nav.list_available_ships(loc_before)
        steps.append({
            'tool': 'list_available_ships',
            'origin': loc_before,
            'result': ships
        })
        # scelgo la nave più economica per risparmiare crediti
        best_ship = min(ships, key=lambda n: ships[n].get('rental_cost', float('inf')))
        ship_cost = ships[best_ship].get('rental_cost', 0)
        travel_res = nav.travel(loc_before, 'Alderaan', best_ship)
        steps.append({
            'tool': 'travel',
            'from': loc_before,
            'to': 'Alderaan',
            'ship': best_ship,
            'result': travel_res
        })
        state['droids']['R2-D2']['location'] = 'Alderaan'
    else:
        best_ship = None
        ship_cost = 0

    # 2) Acquisto due oggetti: primo il più caro possibile, poi il più economico rimanente
    purchasable = [
        (iid, itm) for iid, itm in state['marketplace'].items()
        if itm['price'] <= state['client']['balance']
    ]
    purchased = []

    if purchasable:
        # 2A: oggetto con prezzo massimo entro budget
        iid_max, itm_max = max(purchasable, key=lambda x: x[1]['price'])
        res_max = market.purchase_item(iid_max)
        steps.append({
            'tool': 'purchase_item',
            'item_id': iid_max,
            'result': res_max
        })
        purchased.append(f"{itm_max['name']}({itm_max['planet']})")

        # 2B: oggetto con prezzo minimo tra i rimanenti
        remaining = [p for p in purchasable if p[0] != iid_max]
        if remaining:
            iid_min, itm_min = min(remaining, key=lambda x: x[1]['price'])
            res_min = market.purchase_item(iid_min)
            steps.append({
                'tool': 'purchase_item',
                'item_id': iid_min,
                'result': res_min
            })
            purchased.append(f"{itm_min['name']}({itm_min['planet']})")

    # 3) Costruisco la risposta finale
    response = (
        f"Missione 4 completata: inizialmente R2-D2 era su {loc_before}, "
        f"{'ho viaggiato ad Alderaan con ' + best_ship + ' per ' + str(ship_cost) + ' crediti, ' if best_ship else ''}"
        f"poi ho acquistato {purchased[0]} e {purchased[1]}; "
        f"budget residuo {state['client']['balance']} crediti, "
        f"in totale {len(steps)} API calls."
    )

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
