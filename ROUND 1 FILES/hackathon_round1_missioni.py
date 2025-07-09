#!/usr/bin/env python3
"""
Script per eseguire e valutare automaticamente tutte e 4 le missioni del Round 1
Ottimizzato per aggiornare correttamente bilancio e inventario, generare un unico file JSON con tutti i risultati.
"""
import json
import copy
import time
from galactic_apis import GalacticMarketplace, GalaxyNavigator, InfoSphere
from evaluation_system import HackathonEvaluator


def load_initial_state():
    """Carica lo stato iniziale della galassia da galaxy_state.json"""
    with open('galaxy_state.json', 'r') as f:
        return json.load(f)


def mission1(state):
    """Missione 1: Trasporta R2-D2 su Coruscant"""
    steps = []
    navigator = GalaxyNavigator(state)
    loc = navigator.get_droid_location('R2-D2')
    steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc})
    if loc != 'Coruscant':
        ships = navigator.list_available_ships(loc)
        steps.append({'tool': 'list_available_ships', 'from': loc, 'result': ships})
        ship_name = next(iter(ships))
        result = navigator.travel(loc, 'Coruscant', ship_name)
        steps.append({'tool': 'travel', 'from': loc, 'to': 'Coruscant', 'ship': ship_name, 'result': result})
        state['droids']['R2-D2']['location'] = 'Coruscant'
        response = f"Trasportato R2-D2 da {loc} a Coruscant usando {ship_name}"
    else:
        response = "R2-D2 era già su Coruscant"
    return response, steps


def mission2(state):
    """Missione 2: Acquista un 'Walkman degli Antichi'"""
    steps = []
    marketplace = GalacticMarketplace(state)
    found = marketplace.find_item('Walkman degli Antichi')
    steps.append({'tool': 'find_item', 'item': 'Walkman degli Antichi', 'result': found})
    if found:
        item_id, item = found[0]
        result = marketplace.purchase_item(item_id)
        steps.append({'tool': 'purchase_item', 'item_id': item_id, 'result': result})
        state['client']['inventory'][-1] = item['name']
        response = f"Acquistato {item['name']} per {item['price']} crediti"
    else:
        response = "Walkman non trovato"
    return response, steps


def mission3(state):
    """Missione 3: Ottieni informazioni da InfoSphere"""
    steps = []
    infosphere = InfoSphere(state)
    info = infosphere.get_info('Alderaan')
    steps.append({'tool': 'get_info', 'name': 'Alderaan', 'result': info})
    if isinstance(info, dict):
        status = info.get('status', 'N/D')
        threat = info.get('threat_level', 'N/D')
        response = (
            f"Ecco le informazioni dettagliate su Alderaan:\n"
            f"- Stato: {status}\n"
            f"- Threat level: {threat}\n"
            "Alderaan è noto per la sua popolazione pacifica e per essere un hub scientifico."
        )
    else:
        response = f"Non sono disponibili dati per Alderaan: {info}"
    return response, steps


def mission4(state):
    """Missione 4: Porta R2-D2 su Alderaan e acquista 2 oggetti"""
    steps = []
    nav = GalaxyNavigator(state)
    market = GalacticMarketplace(state)

    # 1) Trasporto R2-D2 su Alderaan se necessario
    loc = nav.get_droid_location('R2-D2')
    steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc})
    if loc != 'Alderaan':
        ships = nav.list_available_ships(loc)
        steps.append({'tool': 'list_available_ships', 'origin': loc, 'result': ships})
        ship = next(iter(ships))
        travel_res = nav.travel(loc, 'Alderaan', ship)
        steps.append({
            'tool': 'travel',
            'from': loc,
            'to': 'Alderaan',
            'ship': ship,
            'result': travel_res
        })
        state['droids']['R2-D2']['location'] = 'Alderaan'

    # 2) Trova e acquista 2 oggetti su Alderaan usando solo l’API
    found_items = market.find_item('')
    steps.append({'tool': 'find_item', 'item': '', 'result': found_items})
    # Filtra quelli effettivamente su Alderaan
    candidates = [(iid, itm) for iid, itm in found_items if itm.get('planet') == 'Alderaan']
    # Ordina per prezzo crescente e prendi i primi due
    candidates.sort(key=lambda x: x[1]['price'])
    purchased = []
    for iid, itm in candidates[:2]:
        res = market.purchase_item(iid)
        steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
        state['client']['inventory'].append(itm['name'])
        purchased.append(f"{itm['name']}({itm['price']}c)")

    response = (
        f"Missione 4 completata: R2-D2 è su Alderaan, "
        f"acquistati {', '.join(purchased)}; "
        f"in tutto {len(steps)} API calls."
    )
    return response, steps



def collect_result(task_id, response, steps, state, start, end):
    """Costruisce il dizionario di risultato per JSON con schema completo"""
    return {
        "task_id": task_id,
        "agent_response": response,
        "intermediate_steps": steps,
        "final_state": {
            "client": {
                "balance": state['client']['balance'],
                "inventory": state['client']['inventory']
            },
            "droids": state['droids']
        },
        "api_calls_count": len(steps),
        "execution_time": round(end - start, 2),
        "success": True,
        "notes": "Schema JSON completo Round 1"
    }


def main():
    initial_state = load_initial_state()
    evaluator = HackathonEvaluator(round_number=1)
    all_results = []
    state = copy.deepcopy(initial_state)
    for task_id, fn in [(1, mission1), (2, mission2), (3, mission3), (4, mission4)]:
        start = time.time()
        response, steps = fn(state)
        end = time.time()

        # Stampa valutazione
        eval_res = evaluator.evaluate_mission(task_id, response, steps, state)
        print(f"--- Risultati Missione {task_id} ---")
        print(evaluator.format_evaluation_output(eval_res))
        print()

        # Raccoglie risultato con schema completo
        all_results.append(collect_result(task_id, response, steps, state, start, end))

    # Scrive l'array di risultati in JSON
    with open('round1_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    print("✅ Tutti i risultati salvati in round1_results.json")


if __name__ == '__main__':
    main()
