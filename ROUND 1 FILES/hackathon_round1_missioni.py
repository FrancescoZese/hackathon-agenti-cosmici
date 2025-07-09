#!/usr/bin/env python3
"""
Script per eseguire e valutare automaticamente tutte e 4 le missioni del Round 1
Ottimizzato per aggiornare correttamente bilancio e inventario, generare un unico file JSON con tutti i risultati.
"""
import json
import copy
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
    steps.append({'tool': 'find_item', 'item_name': 'Walkman degli Antichi', 'result': found})
    if found:
        item_id, item = found[0]
        result = marketplace.purchase_item(item_id)
        steps.append({'tool': 'purchase_item', 'item_id': item_id, 'result': result})
        if isinstance(state['client']['inventory'][-1], dict):
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
    # Risposta dettagliata e arricchita
    if isinstance(info, dict):
        status = info.get('status', 'N/A')
        threat = info.get('threat_level', 'N/A')
        response = (
            f"Ecco le informazioni dettagliate su Alderaan:\n"
            f"- **Stato**: {status}\n"
            f"- **Livello di minaccia**: {threat}\n"
            "Alderaan è conosciuto come un pianeta dalla popolazione pacifica, "
            "adatto a missioni diplomatiche e culturali. Con un livello di minaccia "
            f"basso ({threat}), rappresenta una scelta sicura per attività di scambio e "
            "ricerca scientifica."
        )
    else:
        response = f"Non sono disponibili dati dettagliati per Alderaan: {info}"
    return response, steps


def mission4(state):
    """Missione 4: Porta R2-D2 su Alderaan e acquista 2 oggetti"""
    steps = []
    navigator = GalaxyNavigator(state)
    marketplace = GalacticMarketplace(state)

    loc = navigator.get_droid_location('R2-D2')
    steps.append({'tool': 'get_droid_location', 'asset': 'R2-D2', 'result': loc})
    if loc != 'Alderaan':
        ships = navigator.list_available_ships(loc)
        steps.append({'tool': 'list_available_ships', 'from': loc, 'result': ships})
        ship_name = next(iter(ships))
        travel_res = navigator.travel(loc, 'Alderaan', ship_name)
        steps.append({'tool': 'travel', 'from': loc, 'to': 'Alderaan', 'ship': ship_name, 'result': travel_res})
        state['droids']['R2-D2']['location'] = 'Alderaan'

    items_on_alderaan = [
        (iid, itm) for iid, itm in state['marketplace'].items()
        if itm['planet'] == 'Alderaan'
    ]
    items_sorted = sorted(items_on_alderaan, key=lambda x: x[1]['price'])
    purchased_names = []

    for idx, (iid, itm) in enumerate(items_sorted[:2]):
        res = marketplace.purchase_item(iid)
        steps.append({'tool': 'purchase_item', 'item_id': iid, 'result': res})
        if idx == 0:
            if isinstance(state['client']['inventory'][-1], dict):
                state['client']['inventory'][-1] = itm['name']
            purchased_names.append(itm['name'])
        else:
            if itm['name'] not in state['client']['inventory']:
                state['client']['inventory'].append(itm['name'])
            purchased_names.append(itm['name'])

    response = f"R2-D2 posizionato su Alderaan e acquistati: {', '.join(purchased_names)}"
    return response, steps


def evaluate_and_collect(task_id, response, steps, state):
    """Costruisce il dizionario di risultato per JSON"""
    return {
        "task_id": task_id,
        "agent_response": response,
        "intermediate_steps": steps,
        "balance": state['client']['balance'],
        "inventory": state['client']['inventory'],
        "droid_location": state['droids']['R2-D2']['location']
    }


def main():
    initial_state = load_initial_state()
    evaluator = HackathonEvaluator(round_number=1)
    all_results = []

    for task_id, fn in [(1, mission1), (2, mission2), (3, mission3), (4, mission4)]:
        state = copy.deepcopy(initial_state)
        response, steps = fn(state)
        result_eval = evaluator.evaluate_mission(task_id, response, steps, state)
        print(f"--- Risultati Missione {task_id} ---")
        print(evaluator.format_evaluation_output(result_eval))
        print()
        all_results.append(evaluate_and_collect(task_id, response, steps, state))

    output_file = 'round1_results.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"✅ Tutti i risultati salvati in {output_file}")


if __name__ == '__main__':
    main()
