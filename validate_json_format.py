#!/usr/bin/env python3
"""
🔍 Validatore Format JSON - Hackathon Agenti Cosmici 2025

Script di utilità per validare i file JSON prima della submission.
Verifica formato, campi obbligatori e struttura dei dati.
"""

import json
import os
import argparse
import sys
from pathlib import Path

def validate_json_format(filename):
    """Valida formato JSON prima della submission"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📄 Validando {filename}...")
        
        # Controlla campi obbligatori
        required_fields = ['task_id']
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Campi obbligatori mancanti: {', '.join(missing_fields)}")
            return False
        
        # Controlla task_id
        task_id = data.get('task_id')
        if not isinstance(task_id, int) or task_id < 1:
            print(f"❌ task_id deve essere un numero intero >= 1, trovato: {task_id}")
            return False
        
        # Controlla presenza di almeno un campo response
        response_fields = ['agent_response', 'response', 'output', 'result', 'answer']
        has_response = any(field in data for field in response_fields)
        
        if not has_response:
            print(f"❌ Nessun campo response trovato. Aggiungi almeno uno di: {', '.join(response_fields)}")
            return False
        
        # Controlla api_calls_count se presente
        if 'api_calls_count' in data:
            api_calls = data['api_calls_count']
            if not isinstance(api_calls, int) or api_calls < 0:
                print(f"❌ api_calls_count deve essere un numero intero >= 0, trovato: {api_calls}")
                return False
        
        # Controlla intermediate_steps se presente
        if 'intermediate_steps' in data:
            steps = data['intermediate_steps']
            if not isinstance(steps, list):
                print(f"❌ intermediate_steps deve essere una lista, trovato: {type(steps)}")
                return False
        
        # Verifica final_state se presente
        if 'final_state' in data:
            final_state = data['final_state']
            if not isinstance(final_state, dict):
                print(f"❌ final_state deve essere un dizionario, trovato: {type(final_state)}")
                return False
        
        print(f"✅ {filename} è valido")
        return True
    
    except json.JSONDecodeError as e:
        print(f"❌ Errore JSON in {filename}: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore generico nel file {filename}: {e}")
        return False

def extract_task_id_from_filename(filename):
    """Estrae task_id dal nome del file"""
    import re
    
    # Pattern per riconoscere task_id
    patterns = [
        r'mission_(\d+)\.json',
        r'missione_(\d+)\.json',
        r'task_(\d+)\.json',
        r'round\d+_mission_(\d+)\.json',
        r'round\d+_task_(\d+)\.json'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            return int(match.group(1))
    
    return None

def suggest_improvements(filename):
    """Suggerisce miglioramenti per il file JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        suggestions = []
        
        # Suggerisce task_id dal filename se manca
        if 'task_id' not in data:
            task_id = extract_task_id_from_filename(filename)
            if task_id:
                suggestions.append(f"Aggiungi 'task_id': {task_id} (rilevato dal nome file)")
        
        # Suggerisce campi per valutazione più accurata
        if 'api_calls_count' not in data and 'intermediate_steps' not in data:
            suggestions.append("Aggiungi 'api_calls_count' o 'intermediate_steps' per valutazione efficienza")
        
        if 'final_state' not in data:
            suggestions.append("Aggiungi 'final_state' per valutazione accurata dello stato finale")
        
        if 'agent_response' not in data and 'response' in data:
            suggestions.append("Usa 'agent_response' invece di 'response' per maggiore chiarezza")
        
        if suggestions:
            print(f"💡 Suggerimenti per {filename}:")
            for suggestion in suggestions:
                print(f"  - {suggestion}")
        
        return suggestions
        
    except Exception as e:
        print(f"❌ Errore durante analisi suggerimenti: {e}")
        return []

def validate_directory(directory, pattern="*.json"):
    """Valida tutti i file JSON in una directory"""
    from glob import glob
    
    pattern_path = os.path.join(directory, pattern)
    json_files = glob(pattern_path)
    
    if not json_files:
        print(f"❌ Nessun file JSON trovato in {directory} con pattern {pattern}")
        return False
    
    print(f"🔍 Validando {len(json_files)} file in {directory}...")
    
    valid_files = 0
    invalid_files = 0
    
    for filename in json_files:
        is_valid = validate_json_format(filename)
        if is_valid:
            valid_files += 1
        else:
            invalid_files += 1
            suggest_improvements(filename)
    
    print(f"\n📊 Risultati validazione:")
    print(f"  ✅ File validi: {valid_files}")
    print(f"  ❌ File non validi: {invalid_files}")
    print(f"  📊 Totale: {len(json_files)}")
    
    return invalid_files == 0

def create_example_json(task_id, filename):
    """Crea un file JSON di esempio"""
    example_data = {
        "task_id": task_id,
        "agent_response": f"Missione {task_id} completata con successo. Descrivi qui il risultato della tua missione.",
        "intermediate_steps": [
            {
                "tool": "get_asset_location",
                "asset": "R2-D2",
                "result": "Tatooine"
            },
            {
                "tool": "book_travel",
                "asset": "R2-D2", 
                "destination": "Coruscant",
                "ship": "StarHopper",
                "result": {"success": True, "cost": 520}
            }
        ],
        "final_state": {
            "client": {
                "balance": 3480,
                "inventory": ["Laser Sword"]
            },
            "droids": {
                "R2-D2": {
                    "location": "Coruscant"
                }
            }
        },
        "api_calls_count": 2,
        "success": True
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(example_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Esempio creato: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Validatore format JSON per Hackathon Agenti Cosmici')
    parser.add_argument('--file', type=str, help='Valida un file specifico')
    parser.add_argument('--directory', type=str, help='Valida tutti i file in una directory')
    parser.add_argument('--pattern', type=str, default='*.json', help='Pattern per file da validare')
    parser.add_argument('--create-example', type=int, help='Crea un file di esempio per task_id specificato')
    parser.add_argument('--output', type=str, help='Nome file per esempio (default: mission_X.json)')
    
    args = parser.parse_args()
    
    if args.create_example:
        task_id = args.create_example
        filename = args.output or f'mission_{task_id}.json'
        create_example_json(task_id, filename)
        return
    
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ File non trovato: {args.file}")
            sys.exit(1)
        
        is_valid = validate_json_format(args.file)
        if not is_valid:
            suggest_improvements(args.file)
            sys.exit(1)
        
    elif args.directory:
        if not os.path.exists(args.directory):
            print(f"❌ Directory non trovata: {args.directory}")
            sys.exit(1)
        
        is_valid = validate_directory(args.directory, args.pattern)
        if not is_valid:
            sys.exit(1)
    
    else:
        # Valida directory corrente
        current_dir = '.'
        print(f"🔍 Validando directory corrente: {current_dir}")
        is_valid = validate_directory(current_dir)
        if not is_valid:
            sys.exit(1)
    
    print(f"\n🎉 Validazione completata con successo!")

if __name__ == "__main__":
    main() 