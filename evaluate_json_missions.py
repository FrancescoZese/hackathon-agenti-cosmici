#!/usr/bin/env python3
"""
🔄 Evaluation Bridge - Valutazione da File JSON Separati
Sistema per valutare risultati salvati in file JSON individuali per ogni missione.
"""

import json
import os
import glob
from typing import Dict, List, Optional
from datetime import datetime
from evaluation_system import HackathonEvaluator, display_evaluation_results


class JSONMissionEvaluator:
    """
    Valuta risultati salvati in file JSON separati per ogni missione
    """
    
    def __init__(self, round_number: int = 1):
        self.round_number = round_number
        self.evaluator = HackathonEvaluator(round_number)
        self.results_cache = {}
    
    def find_mission_files(self, directory: str = ".", pattern: str = None) -> List[str]:
        """
        Trova tutti i file JSON delle missioni
        
        Args:
            directory: Directory di ricerca
            pattern: Pattern personalizzato (es: "mission_*.json")
        
        Returns:
            Lista dei file JSON trovati
        """
        if pattern is None:
            # Pattern predefiniti più comuni
            patterns = [
                "mission_*.json",
                "missione_*.json", 
                "task_*.json",
                "round*_mission_*.json",
                "round*_task_*.json",
                "*_mission_*.json",
                "*_task_*.json"
            ]
        else:
            patterns = [pattern]
        
        found_files = []
        for pattern in patterns:
            files = glob.glob(os.path.join(directory, pattern))
            found_files.extend(files)
        
        # Rimuovi duplicati e ordina
        found_files = sorted(list(set(found_files)))
        
        print(f"📁 Trovati {len(found_files)} file missione:")
        for file in found_files:
            print(f"   • {file}")
        
        return found_files
    
    def extract_mission_data(self, json_file: str) -> Optional[Dict]:
        """
        Estrae i dati necessari per la valutazione da un file JSON
        
        Args:
            json_file: Path al file JSON della missione
            
        Returns:
            Dict con i dati estratti o None se impossibile
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Estrai task_id dal nome del file o dai dati
            task_id = self._extract_task_id(json_file, data)
            if task_id is None:
                print(f"⚠️ Impossibile determinare task_id per {json_file}")
                return None
            
            # Estrai dati richiesti con fallback intelligenti
            extracted = {
                'task_id': task_id,
                'json_file': json_file,
                'agent_response': self._extract_agent_response(data),
                'intermediate_steps': self._extract_intermediate_steps(data),
                'final_state': self._extract_final_state(data)
            }
            
            return extracted
            
        except Exception as e:
            print(f"❌ Errore leggendo {json_file}: {e}")
            return None
    
    def _extract_task_id(self, json_file: str, data: Dict) -> Optional[int]:
        """Estrae task_id dal nome del file o dai dati"""
        
        # Prova prima dai dati
        if 'task_id' in data:
            return int(data['task_id'])
        if 'mission_id' in data:
            return int(data['mission_id'])
        if 'id' in data:
            return int(data['id'])
        
        # Prova dal nome del file
        import re
        filename = os.path.basename(json_file)
        
        # Pattern comuni: mission_1.json, task_2.json, etc.
        patterns = [
            r'mission_(\d+)',
            r'missione_(\d+)',
            r'task_(\d+)',
            r'round\d+_mission_(\d+)',
            r'round\d+_task_(\d+)',
            r'(\d+)_mission',
            r'(\d+)_task',
            r'(\d+)\.json$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_agent_response(self, data: Dict) -> str:
        """Estrae la risposta dell'agente"""
        
        # Possibili chiavi per la risposta
        response_keys = [
            'agent_response', 'response', 'output', 'result',
            'final_response', 'answer', 'conclusion', 'summary'
        ]
        
        for key in response_keys:
            if key in data and data[key]:
                return str(data[key])
        
        # Fallback: cerca in sottostrutture
        if 'execution' in data and 'response' in data['execution']:
            return str(data['execution']['response'])
        
        if 'agent' in data and 'response' in data['agent']:
            return str(data['agent']['response'])
        
        # Fallback finale
        return "Missione completata automaticamente tramite file JSON."
    
    def _extract_intermediate_steps(self, data: Dict) -> List:
        """Estrae i passi intermedi (tool calls)"""
        
        # Possibili chiavi per gli step intermedi
        step_keys = [
            'intermediate_steps', 'steps', 'tool_calls', 'api_calls',
            'actions', 'execution_steps', 'calls'
        ]
        
        for key in step_keys:
            if key in data and isinstance(data[key], list):
                return data[key]
        
        # Cerca in sottostrutture
        if 'execution' in data and 'steps' in data['execution']:
            return data['execution']['steps']
        
        if 'agent' in data and 'steps' in data['agent']:
            return data['agent']['steps']
        
        # Se c'è un conteggio esplicito di API calls
        if 'api_calls_count' in data:
            count = int(data['api_calls_count'])
            return [None] * count  # Simula il numero di chiamate
        
        if 'tool_calls_count' in data:
            count = int(data['tool_calls_count'])
            return [None] * count
        
        # Fallback: 1 call simulata
        return [None]
    
    def _extract_final_state(self, data: Dict) -> Dict:
        """Estrae lo stato finale"""
        
        # Possibili chiavi per lo stato finale
        state_keys = [
            'final_state', 'state', 'galaxy_state', 'end_state',
            'resulting_state', 'outcome_state'
        ]
        
        for key in state_keys:
            if key in data and isinstance(data[key], dict):
                return data[key]
        
        # Se non c'è stato esplicito, cerca di ricostruirlo
        reconstructed_state = {}
        
        # Cerca informazioni comuni
        if 'balance' in data:
            reconstructed_state['client'] = {'balance': data['balance']}
        
        if 'inventory' in data:
            if 'client' not in reconstructed_state:
                reconstructed_state['client'] = {}
            reconstructed_state['client']['inventory'] = data['inventory']
        
        if 'droid_location' in data:
            reconstructed_state['droids'] = {
                'R2-D2': {'location': data['droid_location']}
            }
        
        if 'r2d2_location' in data:
            reconstructed_state['droids'] = {
                'R2-D2': {'location': data['r2d2_location']}
            }
        
        # Se abbiamo ricostruito qualcosa, usalo
        if reconstructed_state:
            return reconstructed_state
        
        # Fallback: carica dallo stato globale
        return self._load_current_galaxy_state()
    
    def _load_current_galaxy_state(self) -> Dict:
        """Carica lo stato attuale del galaxy_state.json"""
        
        # Opzioni di file di stato per il round corrente
        state_file_options = [
            f'ROUND {self.round_number} FILES/galaxy_state.json' if self.round_number == 1 else f'ROUND {self.round_number} FILES/galaxy_state_round{self.round_number}.json',
            'ROUND 1 FILES/galaxy_state.json',
            'ROUND 2 FILES/galaxy_state_round2.json',
            'ROUND 3 FILES/galaxy_state_round3.json',
            'galaxy_state.json'
        ]
        
        for file_path in state_file_options:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"⚠️ Errore caricando {file_path}: {e}")
                    continue
        
        # Fallback: stato vuoto
        return {
            'client': {'balance': 1000, 'inventory': []},
            'droids': {'R2-D2': {'location': 'Coruscant'}}
        }
    
    def evaluate_mission_file(self, json_file: str, display_results: bool = True) -> Optional[Dict]:
        """
        Valuta una singola missione da file JSON
        
        Args:
            json_file: Path al file JSON della missione
            display_results: Se mostrare i risultati
            
        Returns:
            Risultato della valutazione o None se errore
        """
        print(f"\n🎯 Valutando missione: {json_file}")
        
        # Estrai dati dal file
        mission_data = self.extract_mission_data(json_file)
        if not mission_data:
            return None
        
        # Esegui valutazione
        try:
            result = self.evaluator.evaluate_mission(
                task_id=mission_data['task_id'],
                agent_response=mission_data['agent_response'],
                intermediate_steps=mission_data['intermediate_steps'],
                final_state=mission_data['final_state']
            )
            
            # Aggiungi info sul file sorgente
            result['source_file'] = json_file
            result['round_number'] = self.round_number
            
            # Salva in cache
            self.results_cache[mission_data['task_id']] = result
            
            if display_results:
                display_evaluation_results(result, self.round_number)
                print(f"📁 Fonte: {json_file}")
            
            return result
            
        except Exception as e:
            print(f"❌ Errore valutando {json_file}: {e}")
            return None
    
    def evaluate_all_missions(self, directory: str = ".", pattern: str = None) -> Dict:
        """
        Valuta tutte le missioni trovate in una directory
        
        Args:
            directory: Directory di ricerca
            pattern: Pattern personalizzato per i file
            
        Returns:
            Dict con tutti i risultati
        """
        print(f"\n🔍 Cercando missioni in: {directory}")
        
        # Trova tutti i file missione
        mission_files = self.find_mission_files(directory, pattern)
        
        if not mission_files:
            print("❌ Nessun file missione trovato!")
            return {}
        
        # Valuta ogni missione
        all_results = {}
        successful_evaluations = 0
        
        for json_file in mission_files:
            result = self.evaluate_mission_file(json_file)
            if result:
                all_results[result['task_id']] = result
                successful_evaluations += 1
        
        # Riassunto finale
        print(f"\n📊 RIASSUNTO VALUTAZIONE:")
        print(f"   📁 File trovati: {len(mission_files)}")
        print(f"   ✅ Valutazioni riuscite: {successful_evaluations}")
        print(f"   ❌ Valutazioni fallite: {len(mission_files) - successful_evaluations}")
        
        if all_results:
            # Calcola statistiche
            total_score = sum(r['total_score'] for r in all_results.values())
            max_possible = sum(r['max_score'] for r in all_results.values())
            avg_percentage = sum(r['percentage'] for r in all_results.values()) / len(all_results)
            
            print(f"\n🏆 STATISTICHE FINALI:")
            print(f"   🎯 Punteggio totale: {total_score:.1f}/{max_possible}")
            print(f"   📈 Percentuale media: {avg_percentage:.1f}%")
            print(f"   🚀 Missioni completate: {len(all_results)}")
        
        return all_results
    
    def save_aggregated_results(self, results: Dict, output_file: str = None):
        """
        Salva i risultati aggregati in formato compatibile
        
        Args:
            results: Risultati da evaluate_all_missions
            output_file: File di output (default: hackathon_results_from_json.json)
        """
        if output_file is None:
            output_file = f"hackathon_results_from_json_round{self.round_number}.json"
        
        # Formato compatibile con il sistema esistente
        aggregated = {
            "timestamp": datetime.now().isoformat(),
            "round_number": self.round_number,
            "missions_completed": len(results),
            "individual_scores": {
                f"mission_{task_id}": float(result['total_score'])
                for task_id, result in results.items()
            },
            "detailed_results": {
                str(k): {
                    **v,
                    "total_score": float(v['total_score']),
                    "correctness": float(v['correctness']),
                    "efficiency": float(v['efficiency']),
                    "quality": float(v['quality']),
                    "percentage": float(v['percentage']),
                    "max_score": float(v['max_score'])
                }
                for k, v in results.items()
            },
            "average_score": float(sum(r['percentage'] for r in results.values()) / len(results) if results else 0),
            "total_api_calls": int(sum(r['api_calls_used'] for r in results.values())),
            "total_score": float(sum(r['total_score'] for r in results.values())),
            "max_possible_score": float(sum(r['max_score'] for r in results.values()))
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(aggregated, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Risultati salvati in: {output_file}")
        return output_file


def main():
    """
    Funzione principale per eseguire la valutazione da comando
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Valuta missioni da file JSON separati')
    parser.add_argument('--round', type=int, default=1, help='Numero del round (1-3)')
    parser.add_argument('--directory', type=str, default='.', help='Directory di ricerca')
    parser.add_argument('--pattern', type=str, help='Pattern personalizzato per i file')
    parser.add_argument('--output', type=str, help='File di output per i risultati')
    
    args = parser.parse_args()
    
    # Crea valutatore
    evaluator = JSONMissionEvaluator(args.round)
    
    # Valuta tutte le missioni
    results = evaluator.evaluate_all_missions(args.directory, args.pattern)
    
    # Salva risultati
    if results:
        evaluator.save_aggregated_results(results, args.output)
    else:
        print("❌ Nessun risultato da salvare")


if __name__ == "__main__":
    main() 