"""
📊 Sistema di Valutazione Automatico - Hackathon Agenti Cosmici
"""

import json
import pandas as pd
import os
from typing import Dict, List, Tuple
from datetime import datetime


class HackathonEvaluator:
    """Sistema di valutazione per le missioni dell'hackathon"""
    
    def __init__(self, round_number: int = 1):
        self.round_number = round_number
        self.load_configurations()
    
    def load_configurations(self):
        """Carica le configurazioni per il round attuale"""
        self.scoring_weights = {
            1: {"correctness": 60, "efficiency": 20, "quality": 20},  # Learning focus
            2: {"correctness": 50, "efficiency": 30, "quality": 20},  # Efficiency focus  
            3: {"correctness": 40, "efficiency": 40, "quality": 20}   # Expert efficiency
        }
        
        self.max_api_calls = {
            1: {"excellent": 3, "good": 5, "acceptable": 8},
            2: {"excellent": 5, "good": 8, "acceptable": 12},
            3: {"excellent": 8, "good": 12, "acceptable": 15}
        }
    
    def get_max_scores_for_round(self, max_score: int) -> Dict[str, float]:
        """
        Calcola automaticamente i punteggi massimi per ogni componente
        basandosi sui pesi del round corrente
        
        Args:
            max_score: Punteggio massimo totale per la missione
            
        Returns:
            Dict con i punteggi massimi per correctness, efficiency, quality
        """
        weights = self.scoring_weights[self.round_number]
        
        return {
            "correctness_max": max_score * (weights["correctness"] / 100),
            "efficiency_max": max_score * (weights["efficiency"] / 100),
            "quality_max": max_score * (weights["quality"] / 100)
        }
    
    def format_evaluation_output(self, evaluation_result: Dict) -> str:
        """
        Formatta automaticamente l'output di valutazione con i valori massimi corretti
        
        Args:
            evaluation_result: Risultato della valutazione da evaluate_mission
            
        Returns:
            Stringa formattata con i risultati
        """
        max_scores = self.get_max_scores_for_round(evaluation_result['max_score'])
        
        output = []
        output.append("📊 RISULTATI VALUTAZIONE:")
        output.append(f"   🎯 Correttezza: {evaluation_result['correctness']:.1f}/{max_scores['correctness_max']:.0f}")
        output.append(f"   ⚡ Efficienza: {evaluation_result['efficiency']:.1f}/{max_scores['efficiency_max']:.0f}")
        output.append(f"   ✨ Qualità: {evaluation_result['quality']:.1f}/{max_scores['quality_max']:.0f}")
        output.append(f"   📊 Totale: {evaluation_result['total_score']:.1f}/{evaluation_result['max_score']}")
        output.append(f"   📈 Percentuale: {evaluation_result['percentage']:.1f}%")
        
        return "\n".join(output)
    
    def evaluate_mission(self, task_id: int, agent_response: str, 
                        intermediate_steps: List, final_state: Dict) -> Dict:
        """
        Valuta una singola missione
        
        Args:
            task_id: ID della missione
            agent_response: Risposta finale dell'agente
            intermediate_steps: Passi intermedi (tool calls)
            final_state: Stato finale del galaxy_state.json
            
        Returns:
            Dict con punteggi dettagliati
        """
        
        # Carica task details con auto-detection
        task_file_options = [
            f'ROUND {self.round_number} FILES/tasks.csv' if self.round_number == 1 else f'ROUND {self.round_number} FILES/tasks_round{self.round_number}.csv',
            'ROUND 1 FILES/tasks.csv',  # Fallback
            'ROUND 2 FILES/tasks_round2.csv',
            'ROUND 3 FILES/tasks_round3.csv',
            'tasks.csv'  # Fallback legacy
        ]
        
        task_file = None
        for file_path in task_file_options:
            if os.path.exists(file_path):
                task_file = file_path
                break
        
        if not task_file:
            raise FileNotFoundError(f"⚠️ Nessun file tasks trovato per il round {self.round_number}")
        
        tasks_df = pd.read_csv(task_file)
        task_row = tasks_df[tasks_df['task_id'] == task_id].iloc[0]
        max_score = task_row['max_score']
        
        # Calcola i 3 componenti del punteggio
        correctness_score = self._evaluate_correctness(task_id, final_state, max_score)
        efficiency_score = self._evaluate_efficiency(intermediate_steps, max_score)
        quality_score = self._evaluate_quality(agent_response, max_score)
        
        # Calcola i valori massimi per questo round
        max_scores = self.get_max_scores_for_round(max_score)
        
        # 🛡️ SICUREZZA: Assicurati che i punteggi non superino mai i limiti massimi
        correctness_score = min(correctness_score, max_scores["correctness_max"])
        efficiency_score = min(efficiency_score, max_scores["efficiency_max"])
        quality_score = min(quality_score, max_scores["quality_max"])
        
        # I pesi sono già applicati nei singoli componenti, quindi sommiamo direttamente
        total_score = correctness_score + efficiency_score + quality_score
        
        # 🛡️ SICUREZZA FINALE: Il punteggio totale non deve mai superare il massimo
        total_score = min(total_score, max_score)
        
        return {
            "task_id": task_id,
            "max_score": max_score,
            "correctness": correctness_score,
            "efficiency": efficiency_score,
            "quality": quality_score,
            "total_score": round(total_score, 2),
            "percentage": round((total_score / max_score) * 100, 1),
            "api_calls_used": len(intermediate_steps),
            "evaluation_details": self._get_evaluation_details(task_id, final_state, intermediate_steps),
            # 🌟 NUOVO: Includi i valori massimi calcolati automaticamente
            "max_scores": max_scores
        }
    
    def _evaluate_correctness(self, task_id: int, final_state: Dict, max_score: int) -> float:
        """Valuta se la missione è stata completata correttamente"""
        
        # Calcola il punteggio massimo per correttezza
        max_correctness_score = max_score * (self.scoring_weights[self.round_number]["correctness"] / 100)
        
        # Regole di valutazione per task specifici
        correctness_rules = {
            # Round 1
            1: lambda state: self._check_droid_location(state, "Coruscant"),
            2: lambda state: self._check_inventory_contains(state, "Walkman degli Antichi"),
            3: lambda state: True,  # Info task - sempre corretto se chiamato
            4: lambda state: self._check_droid_location(state, "Alderaan") and len(state['client']['inventory']) >= 2,
            
            # Round 2 examples
            5: lambda state: self._check_droid_location(state, "Tatooine") and self._check_inventory_contains(state, "Holocron"),
            
            # Round 3 specific rules
            6: lambda state: self._check_multi_objective_round3(state),
            8: lambda state: self._check_ultimate_challenge_round3(state),
        }
        
        # Fallback per task non definiti
        if task_id not in correctness_rules:
            return min(max_correctness_score * 0.6, max_correctness_score)  # 60% se non riusciamo a valutare
        
        # Esegui valutazione
        is_correct = correctness_rules[task_id](final_state)
        
        if is_correct:
            # 🌟 BONUS: Se la missione era già completata dall'inizio, dai punteggio pieno
            if self._was_mission_already_completed(task_id, final_state):
                return max_correctness_score
            else:
                return max_correctness_score
        else:
            # Partial credit se almeno ha provato
            if self._has_attempted_task(final_state):
                return min(max_correctness_score * 0.3, max_correctness_score)
            else:
                return 0
    
    def _evaluate_efficiency(self, intermediate_steps: List, max_score: int) -> float:
        """Valuta l'efficienza basata sul numero di API calls"""
        api_calls = len(intermediate_steps)
        thresholds = self.max_api_calls[self.round_number]
        max_efficiency_score = max_score * (self.scoring_weights[self.round_number]["efficiency"] / 100)
        
        # 🌟 BONUS: Se ha fatto 0 API calls (missione già completata), dai punteggio pieno
        if api_calls == 0:
            return min(max_efficiency_score, max_efficiency_score)
        
        # 🎯 OTTIMALE: Se ha fatto solo 1-2 API calls (controllo intelligente), dai punteggio pieno
        if api_calls <= 2:
            return min(max_efficiency_score, max_efficiency_score)
        
        # Valutazione standard
        if api_calls <= thresholds["excellent"]:
            return min(max_efficiency_score, max_efficiency_score)
        elif api_calls <= thresholds["good"]:
            return min(max_efficiency_score * 0.8, max_efficiency_score)
        elif api_calls <= thresholds["acceptable"]:
            return min(max_efficiency_score * 0.6, max_efficiency_score)
        else:
            return min(max_efficiency_score * 0.3, max_efficiency_score)
    
    def _evaluate_quality(self, agent_response: str, max_score: int) -> float:
        """Valuta la qualità della risposta"""
        max_quality_score = max_score * (self.scoring_weights[self.round_number]["quality"] / 100)
        
        if not agent_response:
            return min(max_quality_score * 0.1, max_quality_score)  # Minimo se nessuna risposta
        
        response_length = len(agent_response)
        response_lower = agent_response.lower()
        
        # 🌟 BONUS: Riconosce risposte intelligenti per casi ottimali
        optimal_responses = [
            "già" in response_lower and any(word in response_lower for word in ["coruscant", "posizione", "lì"]),
            "completata" in response_lower or "finita" in response_lower,
            "non serve" in response_lower or "non necessario" in response_lower,
        ]
        
        # Criteri di qualità standard
        has_explanation = any(word in response_lower for word in 
                            ["ho", "prima", "poi", "quindi", "perché", "così", "analisi", "piano"])
        has_numbers = any(char.isdigit() for char in agent_response)
        mentions_cost = any(word in response_lower for word in 
                          ["crediti", "costo", "prezzo", "budget"])
        mentions_location = any(word in response_lower for word in 
                              ["coruscant", "tatooine", "alderaan", "posizione", "dove"])
        
        quality_factors = [
            response_length > 30,          # Risposta sufficientemente lunga
            has_explanation,               # Spiega il processo
            has_numbers,                  # Include dettagli numerici
            mentions_cost,                # Gestisce aspetti economici
            mentions_location,            # Menziona pianeti/posizioni
            response_length < 500,        # Non troppo prolissa
            any(optimal_responses)        # 🌟 BONUS: Risposta intelligente per caso ottimale
        ]
        
        quality_ratio = sum(quality_factors) / len(quality_factors)
        
        # 🎯 BONUS EXTRA: Se ha riconosciuto il caso ottimale, dai punteggio pieno
        if any(optimal_responses):
            quality_ratio = max(quality_ratio, 0.9)  # Almeno 90% se riconosce il caso ottimale
        
        return min(max_quality_score * quality_ratio, max_quality_score)
    
    def _check_droid_location(self, state: Dict, expected_location: str) -> bool:
        """Controlla se il droide è nella posizione corretta"""
        return state.get('droids', {}).get('R2-D2', {}).get('location') == expected_location
    
    def _check_inventory_contains(self, state: Dict, item_name: str) -> bool:
        """Controlla se l'inventario contiene un oggetto specifico"""
        inventory = state.get('client', {}).get('inventory', [])
        return item_name in inventory
    
    def _check_multi_objective_round3(self, state: Dict) -> bool:
        """
        Controlla se la Missione 6 Round 3 è stata completata correttamente:
        - R2-D2 deve essere stato su ogni pianeta almeno una volta
        - Deve essere stato comprato almeno 1 oggetto per ogni pianeta
        
        Nota: Per ora implementiamo una verifica semplificata basata sull'inventario
        """
        inventory = state.get('client', {}).get('inventory', [])
        marketplace = state.get('marketplace', {})
        
        # Raggruppa oggetti per pianeta
        items_by_planet = {}
        for item_id, item_info in marketplace.items():
            planet = item_info.get('planet', '')
            if planet not in items_by_planet:
                items_by_planet[planet] = []
            items_by_planet[planet].append(item_info.get('name', ''))
        
        # Verifica che ci sia almeno un oggetto per ogni pianeta nell'inventario
        planets = ['Coruscant', 'Tatooine', 'Alderaan']
        for planet in planets:
            planet_items = items_by_planet.get(planet, [])
            has_item_from_planet = any(item in inventory for item in planet_items)
            if not has_item_from_planet:
                return False
        
        return True
    
    def _check_ultimate_challenge_round3(self, state: Dict) -> bool:
        """
        Controlla se l'Ultimate Challenge (Missione 8) è stata completata correttamente.
        
        Criterio di successo: La missione è considerata completata se dimostra 
        padronanza del sistema multi-agente attraverso:
        - Coordinamento strategico (droidi posizionati su pianeti diversi)
        - Intelligence gathering (informazioni raccolte)
        - Resource management (budget gestito responsabilmente)
        - Strategic acquisitions (oggetti acquisiti)
        
        Essendo una missione aperta, la valutazione è generosa se si dimostra 
        tentativo di coordinamento multi-agente complesso.
        """
        # Verifica coordinamento multi-agente
        droids = state.get('droids', {})
        if not droids:
            return False
        
        # Controlla che i droidi siano posizionati strategicamente
        droid_locations = [droid.get('location') for droid in droids.values()]
        unique_locations = set(droid_locations)
        multi_planet_deployment = len(unique_locations) >= 2
        
        # Verifica resource management: budget non completamente esaurito
        balance = state.get('client', {}).get('balance', 0)
        responsible_budget_management = balance > 100  # Ha lasciato almeno 100 crediti
        
        # Verifica strategic acquisitions: ha acquisito oggetti
        inventory = state.get('client', {}).get('inventory', [])
        has_strategic_acquisitions = len(inventory) > 5  # Ha almeno 5 oggetti
        
        # Verifica intelligence gathering: ha accessato l'infosphere
        infosphere = state.get('infosphere', {})
        intelligence_available = len(infosphere) > 0
        
        # Criterio di successo: almeno 3 dei 4 requisiti soddisfatti
        criteria_met = [
            multi_planet_deployment,
            responsible_budget_management, 
            has_strategic_acquisitions,
            intelligence_available
        ]
        
        return sum(criteria_met) >= 3
    
    def _has_attempted_task(self, state: Dict) -> bool:
        """Controlla se è stato fatto almeno un tentativo"""
        # Controllo semplice: se il budget è cambiato significa che ha fatto qualcosa
        return state.get('client', {}).get('balance', 3000) != 3000
    
    def _was_mission_already_completed(self, task_id: int, final_state: Dict) -> bool:
        """
        Controlla se la missione era già completata dal principio
        Questo è utile per dare bonus quando l'agente riconosce che non serve fare nulla
        """
        # Controlla se il budget è rimasto invariato (non ha speso nulla)
        initial_balance = self._get_initial_balance_for_round()
        current_balance = final_state.get('client', {}).get('balance', 0)
        
        # Se il budget è invariato E l'obiettivo è raggiunto, era già completata
        return current_balance == initial_balance and self._is_mission_objective_met(task_id, final_state)
    
    def _is_mission_objective_met(self, task_id: int, state: Dict) -> bool:
        """Controlla se l'obiettivo della missione è soddisfatto"""
        objectives = {
            1: lambda s: self._check_droid_location(s, "Coruscant"),
            2: lambda s: self._check_inventory_contains(s, "Walkman degli Antichi"),
            3: lambda s: True,  # Info task
            4: lambda s: self._check_droid_location(s, "Alderaan") and len(s['client']['inventory']) >= 2,
            6: lambda s: self._check_multi_objective_round3(s),
            8: lambda s: self._check_ultimate_challenge_round3(s),
        }
        
        return objectives.get(task_id, lambda s: False)(state)
    
    def _get_initial_balance_for_round(self) -> int:
        """Ottiene il bilancio iniziale per il round corrente"""
        # Questi sono i bilanci iniziali per ogni round
        initial_balances = {
            1: 390,  # Round 1 balance
            2: 500,  # Round 2 balance (esempio)
            3: 700   # Round 3 balance (esempio)
        }
        return initial_balances.get(self.round_number, 1000)
    
    def _get_evaluation_details(self, task_id: int, final_state: Dict, 
                              intermediate_steps: List) -> Dict:
        """Genera dettagli di valutazione per feedback"""
        
        # Safe tool extraction
        tools_used = []
        try:
            # 🔧 FIX: Gestisci entrambi i formati - oggetti LangChain e dict JSON
            for step in intermediate_steps:
                if step is None:
                    continue
                
                # Formato LangChain: step[0].tool
                if hasattr(step, '__len__') and len(step) > 0 and hasattr(step[0], 'tool'):
                    tools_used.append(step[0].tool)
                # Formato dict JSON: step['tool']
                elif isinstance(step, dict) and 'tool' in step:
                    tools_used.append(step['tool'])
                # Formato dict JSON: step['action']
                elif isinstance(step, dict) and 'action' in step:
                    tools_used.append(step['action'])
            
            tools_used = list(set(tools_used))  # Remove duplicates
            
        except (TypeError, AttributeError, IndexError, KeyError):
            tools_used = ["simulated_steps"]  # Fallback for simulation
        
        return {
            "droid_location": final_state.get('droids', {}).get('R2-D2', {}).get('location'),
            "remaining_balance": final_state.get('client', {}).get('balance'),
            "inventory_items": len(final_state.get('client', {}).get('inventory', [])),
            "api_calls": len(intermediate_steps),
            "tools_used": tools_used
        }
    
    def generate_leaderboard(self, all_results: List[Dict]) -> pd.DataFrame:
        """Genera la classifica finale"""
        # Raggruppa per partecipante
        participant_scores = {}
        
        for result in all_results:
            participant = result.get('participant_id', 'Unknown')
            if participant not in participant_scores:
                participant_scores[participant] = {
                    'total_score': 0,
                    'missions_completed': 0,
                    'round_scores': {1: 0, 2: 0, 3: 0}
                }
            
            participant_scores[participant]['total_score'] += result['total_score']
            participant_scores[participant]['missions_completed'] += 1
            participant_scores[participant]['round_scores'][self.round_number] += result['total_score']
        
        # Crea DataFrame per classifica
        leaderboard_data = []
        for participant, scores in participant_scores.items():
            leaderboard_data.append({
                'Participant': participant,
                'Total Score': scores['total_score'],
                'Missions Completed': scores['missions_completed'],
                'Round 1': scores['round_scores'][1],
                'Round 2': scores['round_scores'][2], 
                'Round 3': scores['round_scores'][3],
                'Average Score': scores['total_score'] / max(scores['missions_completed'], 1)
            })
        
        df = pd.DataFrame(leaderboard_data)
        df = df.sort_values('Total Score', ascending=False)
        df['Rank'] = range(1, len(df) + 1)
        
        # Aggiungi titoli
        titles = ["🥇 Cosmic Champion", "🥈 Galaxy Explorer", "🥉 Space Cadet", "🏅 Rookie Agent"]
        df['Title'] = df['Rank'].apply(lambda x: titles[x-1] if x <= len(titles) else "🌟 Agent")
        
        return df[['Rank', 'Participant', 'Title', 'Total Score', 'Missions Completed', 
                  'Round 1', 'Round 2', 'Round 3', 'Average Score']]


def quick_evaluate_current_state(task_id: int, round_number: int = 1, 
                                 agent_response: str = None, 
                                 intermediate_steps: List = None) -> Dict:
    """
    Funzione helper per valutare velocemente lo stato attuale
    
    Args:
        task_id: ID della missione
        round_number: Numero del round
        agent_response: Risposta reale dell'agente (opzionale)
        intermediate_steps: Passi intermedi reali dell'agente (opzionale)
    """
    evaluator = HackathonEvaluator(round_number)
    
    # 🔍 Auto-detect del file di stato per il round corrente
    state_file_options = [
        f'ROUND {round_number} FILES/galaxy_state.json' if round_number == 1 else f'ROUND {round_number} FILES/galaxy_state_round{round_number}.json',
        'ROUND 1 FILES/galaxy_state.json',  # Fallback
        'ROUND 2 FILES/galaxy_state_round2.json',
        'ROUND 3 FILES/galaxy_state_round3.json',
        'galaxy_state.json'  # Fallback legacy
    ]
    
    state_file = None
    for file_path in state_file_options:
        if os.path.exists(file_path):
            state_file = file_path
            break
    
    if not state_file:
        raise FileNotFoundError(f"⚠️ Nessun file di stato trovato per il round {round_number}. Controllare che le cartelle ROUND siano presenti.")
    
    # Carica stato attuale
    print(f"📁 Caricando stato da: {state_file}")
    with open(state_file, 'r') as f:
        final_state = json.load(f)
    
    # Usa dati reali se forniti, altrimenti usa fallback
    if agent_response is None:
        agent_response = "Missione completata. Ho eseguito le azioni richieste."
    
    if intermediate_steps is None:
        # 🔧 FIX: Invece di simulare sempre 3, usa 1 per default (più realistico)
        intermediate_steps = [None]  # 1 API call simulata invece di 3
        print("⚠️ Usando 1 API call simulata (dati reali non forniti)")
    else:
        print(f"✅ Usando {len(intermediate_steps)} API calls reali")
    
    result = evaluator.evaluate_mission(task_id, agent_response, intermediate_steps, final_state)
    
    print(f"🎯 Valutazione Missione {task_id}")
    print(f"📊 Punteggio Totale: {result['total_score']}/{result['max_score']} ({result['percentage']}%)")
    print(f"✅ Correttezza: {result['correctness']}")
    print(f"⚡ Efficienza: {result['efficiency']} (API calls: {result['api_calls_used']})")
    print(f"🎨 Qualità: {result['quality']}")
    
    return result


# 🌟 NUOVA FUNZIONE: Display automatico risultati valutazione
def display_evaluation_results(evaluation_result: Dict, round_number: int = None):
    """
    Mostra i risultati di valutazione con valori massimi calcolati automaticamente
    
    Args:
        evaluation_result: Risultato da evaluate_mission() 
        round_number: Numero del round (se None, lo deduce dal risultato)
    """
    
    # Se round_number non è specificato, prova a dedurlo
    if round_number is None:
        # Potrebbe essere incluso nel risultato, altrimenti usa default
        round_number = getattr(evaluation_result, 'round_number', 1)
    
    # Usa la funzione format_evaluation_output se disponibile
    if 'max_scores' in evaluation_result:
        max_scores = evaluation_result['max_scores']
        print("📊 RISULTATI VALUTAZIONE:")
        print(f"   🎯 Correttezza: {evaluation_result['correctness']:.1f}/{max_scores['correctness_max']:.0f}")
        print(f"   ⚡ Efficienza: {evaluation_result['efficiency']:.1f}/{max_scores['efficiency_max']:.0f}")
        print(f"   ✨ Qualità: {evaluation_result['quality']:.1f}/{max_scores['quality_max']:.0f}")
        print(f"   📊 Totale: {evaluation_result['total_score']:.1f}/{evaluation_result['max_score']}")
        print(f"   📈 Percentuale: {evaluation_result['percentage']:.1f}%")
    else:
        # Fallback: calcola i valori massimi al volo
        evaluator = HackathonEvaluator(round_number=round_number)
        max_scores = evaluator.get_max_scores_for_round(evaluation_result['max_score'])
        
        print("📊 RISULTATI VALUTAZIONE:")
        print(f"   🎯 Correttezza: {evaluation_result['correctness']:.1f}/{max_scores['correctness_max']:.0f}")
        print(f"   ⚡ Efficienza: {evaluation_result['efficiency']:.1f}/{max_scores['efficiency_max']:.0f}")
        print(f"   ✨ Qualità: {evaluation_result['quality']:.1f}/{max_scores['quality_max']:.0f}")
        print(f"   📊 Totale: {evaluation_result['total_score']:.1f}/{evaluation_result['max_score']}")
        print(f"   📈 Percentuale: {evaluation_result['percentage']:.1f}%")


# 🚀 NUOVA FUNZIONE: Valutazione corretta per agenti LangChain
def evaluate_agent_result(task_id: int, round_number: int, agent_result: Dict) -> Dict:
    """
    Valuta il risultato di un agente LangChain con dati completi
    
    Args:
        task_id: ID della missione
        round_number: Numero del round  
        agent_result: Risultato completo da agent_executor.invoke()
                     deve contenere 'output' e 'intermediate_steps'
    """
    return quick_evaluate_current_state(
        task_id=task_id,
        round_number=round_number,
        agent_response=agent_result.get('output', ''),
        intermediate_steps=agent_result.get('intermediate_steps', [])
    )


# Esempio di uso
if __name__ == "__main__":
    # Test valutazione
    result = quick_evaluate_current_state(1, 1)
    print("\n📋 Dettagli valutazione:")
    print(json.dumps(result, indent=2)) 