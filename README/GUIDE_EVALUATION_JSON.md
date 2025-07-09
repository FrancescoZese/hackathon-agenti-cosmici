# 📄 Guida Completa: Valutazione JSON - Hackathon Agenti Cosmici 2025

## 🎯 Introduzione

La **modalità JSON** è una nuova funzionalità che permette di valutare i risultati delle missioni salvati in file JSON separati. Questa modalità è perfetta per:

- ✅ **Sistemi automatizzati** e pipeline CI/CD
- ✅ **Batch processing** di migliaia di submission
- ✅ **Competizioni su larga scala** con migliaia di partecipanti
- ✅ **Archivio e analisi** dei risultati storici
- ✅ **Flessibilità** nella struttura dei dati

## 🚀 Caso d'Uso: Esempio di Implementazione

### Esempio Generico di Missione
**Tipo**: "Gestione Droidi e Acquisti Multi-Pianeta"
**Obiettivo**: Ottimizzare trasporti e acquisti in una galassia virtuale

**Strategia tipo**:
- ✅ **Ricerca efficiente**: Localizzazione asset con minimo numero di chiamate
- ✅ **Ottimizzazione costi**: Confronto prezzi e costi trasporto
- ✅ **Acquisti intelligenti**: Diversificazione pianeti per massimizzare efficienza

### File di Esempio Forniti
```
example_mission_result.json                 # Formato JSON di esempio
hackathon_results_example.json              # Esempio risultati aggregati
```

## 📁 Formati File JSON Supportati

### 1. Formato Completo (Raccomandato)
Il formato più ricco che garantisce la valutazione più accurata:

```json
{
  "task_id": 1,
  "agent_response": "Missione completata con successo. Ho localizzato il droide target, l'ho trasportato sul pianeta richiesto e ho completato tutti gli obiettivi secondari ottimizzando l'uso delle risorse.",
  "intermediate_steps": [
    {
      "tool": "get_asset_location",
      "asset": "TARGET_DROID",
      "result": "STARTING_PLANET"
    },
    {
      "tool": "get_ships",
      "result": [
        {
          "name": "SHIP_NAME",
          "type": "transport",
          "rental_cost": 400,
          "speed": "medium",
          "cost_per_unit": 1.5
        }
      ]
    },
    {
      "tool": "calculate_travel_cost",
      "origin": "STARTING_PLANET",
      "destination": "TARGET_PLANET",
      "ship": "SHIP_NAME",
      "result": 520
    },
    {
      "tool": "book_travel",
      "asset": "TARGET_DROID",
      "destination": "TARGET_PLANET",
      "ship": "SHIP_NAME",
      "result": {
        "success": true,
        "cost": 520,
        "new_location": "TARGET_PLANET"
      }
    },
    {
      "tool": "search_marketplace",
      "item": "TARGET_ITEM",
      "result": [
        {
          "id": "item_001",
          "name": "TARGET_ITEM",
          "price": 500,
          "planet": "PLANET_A",
          "description": "Descrizione oggetto"
        },
        {
          "id": "item_002",
          "name": "TARGET_ITEM",
          "price": 500,
          "planet": "PLANET_B",
          "description": "Descrizione oggetto alternativo"
        }
      ]
    },
    {
      "tool": "purchase_item",
      "item_id": "item_001",
      "planet": "PLANET_A",
      "result": {
        "success": true,
        "cost": 500,
        "item_name": "TARGET_ITEM"
      }
    },
    {
      "tool": "purchase_item",
      "item_id": "item_002",
      "planet": "PLANET_B",
      "result": {
        "success": true,
        "cost": 500,
        "item_name": "TARGET_ITEM"
      }
    }
  ],
  "final_state": {
    "client": {
      "balance": 3480,
      "inventory": ["TARGET_ITEM", "TARGET_ITEM"]
    },
    "droids": {
      "TARGET_DROID": {
        "location": "TARGET_PLANET"
      }
    }
  },
  "api_calls_count": 10,
  "execution_time": 35.7,
  "success": true,
  "notes": "Strategia ottimizzata per bilanciare costi e efficienza"
}
```

### 2. Formato Minimo (Supportato)
Il formato essenziale che funziona comunque:

```json
{
  "task_id": 1,
  "response": "Missione completata: R2-D2 su Coruscant, 2 Laser Sword acquistate",
  "api_calls_count": 12,
  "balance": 3480,
  "inventory": ["Laser Sword", "Laser Sword"],
  "droid_location": "Coruscant"
}
```

### 3. Formato Automatico (Riconosciuto)
Il sistema riconosce automaticamente questi campi:

```json
{
  "agent_response": "Missione completata",
  "tool_calls": 12,
  "final_balance": 3480,
  "items_purchased": ["Laser Sword", "Laser Sword"],
  "R2-D2_location": "Coruscant"
}
```

## 🏆 Pattern di Nomi File Supportati

### Nomi Riconosciuti Automaticamente
Il sistema riconosce questi pattern:

```
✅ mission_1.json, mission_2.json, mission_3.json
✅ missione_1.json, missione_2.json, missione_3.json
✅ task_1.json, task_2.json, task_3.json
✅ round1_mission_1.json, round2_task_3.json
✅ team_alpha_mission_1.json, student_123_task_2.json
```

### Esempi per Diversi Contesti
```bash
# Università
student_12345_mission_1.json
student_12345_mission_2.json

# Aziende
team_engineering_task_1.json
team_marketing_task_2.json

# Competizioni
participant_001_round1_mission_1.json
participant_001_round2_mission_3.json
```

## 🔧 Utilizzo del Sistema

### 1. Via Command Line (Consigliato)

#### Valutazione Standard
```bash
# Valuta tutte le missioni del Round 2
python evaluate_json_missions.py --round 2

# Output esempio:
# 🚀 Valutazione Round 2 iniziata...
# ✅ mission_1.json: 85.0/100 (85.0%)
# ✅ mission_2.json: 92.0/100 (92.0%)
# 📊 Risultati salvati in: hackathon_results_round2.json
```

#### Valutazione Personalizzata
```bash
# Valuta pattern specifico
python evaluate_json_missions.py --round 2 --pattern "task_*.json"

# Valuta directory specifica
python evaluate_json_missions.py --round 2 --directory "./team_submissions/"

# Output personalizzato
python evaluate_json_missions.py --round 2 --output "my_results.json"

# Modalità debug
python evaluate_json_missions.py --round 2 --debug
```

### 2. Via Python API

#### Valutazione Completa
```python
from evaluate_json_missions import JSONMissionEvaluator

# Inizializza evaluator
evaluator = JSONMissionEvaluator(round_number=2)

# Valuta tutte le missioni
results = evaluator.evaluate_all_missions()

# Salva risultati
evaluator.save_aggregated_results(results)

# Mostra riepilogo
print(f"Missioni valutate: {len(results)}")
for mission, result in results.items():
    print(f"{mission}: {result['score']}/{result['max_score']} ({result['percentage']:.1f}%)")
```

#### Valutazione Singola Missione
```python
# Valuta una missione specifica
result = evaluator.evaluate_mission_from_json("mission_1.json")

print(f"Punteggio: {result['score']}/{result['max_score']}")
print(f"Percentuale: {result['percentage']:.1f}%")
print(f"Breakdown:")
print(f"  - Correttezza: {result['breakdown']['correctness']['score']}/{result['breakdown']['correctness']['max']}")
print(f"  - Efficienza: {result['breakdown']['efficiency']['score']}/{result['breakdown']['efficiency']['max']}")
print(f"  - Qualità: {result['breakdown']['quality']['score']}/{result['breakdown']['quality']['max']}")
```

## 🔍 Estrazione Dati Intelligente

### Strategie di Fallback
Il sistema usa strategie multiple per estrarre i dati:

#### 1. Riconoscimento Campi Standard
```python
# Cerca questi campi in ordine di preferenza:
response_fields = [
    "agent_response",      # Preferito
    "response",
    "output",
    "result",
    "answer",
    "conclusion"
]
```

#### 2. Riconoscimento API Calls
```python
# Cerca questi campi:
api_call_fields = [
    "api_calls_count",     # Preferito
    "tool_calls",
    "calls_made",
    "api_calls",
    "total_calls"
]
```

#### 3. Riconoscimento Stato Finale
```python
# Cerca questi campi:
final_state_fields = [
    "final_state",         # Preferito
    "end_state",
    "galaxy_state",
    "state",
    "final_galaxy_state"
]
```

### Esempio di Ricostruzione Automatica
```python
# Se non trova final_state, prova a ricostruirlo:
def reconstruct_final_state(data):
    reconstructed = {}
    
    # Cerca balance
    if "balance" in data:
        reconstructed["client"] = {"balance": data["balance"]}
    
    # Cerca inventory
    if "inventory" in data:
        reconstructed["client"]["inventory"] = data["inventory"]
    
    # Cerca posizioni droidi
    if "droid_location" in data:
        reconstructed["droids"] = {"R2-D2": {"location": data["droid_location"]}}
    
    return reconstructed
```

## 🚀 Funzionalità Avanzate

### Batch Processing
```bash
# Valuta centinaia di file contemporaneamente
find ./submissions -name "*.json" | xargs python evaluate_json_missions.py --round 2 --file

# Parallelo con GNU parallel
find ./submissions -name "*.json" | parallel python evaluate_json_missions.py --round 2 --file {}
```

### Integrazione CI/CD

#### GitHub Actions
```yaml
name: Evaluate Hackathon Submissions
on:
  push:
    paths:
      - 'submissions/*.json'

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Evaluate Round 1
        run: |
          python evaluate_json_missions.py --round 1 --directory submissions/
      
      - name: Evaluate Round 2
        run: |
          python evaluate_json_missions.py --round 2 --directory submissions/
      
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: hackathon-results
          path: hackathon_results_from_json_*.json
```

#### Jenkins Pipeline
```groovy
pipeline {
    agent any
    
    stages {
        stage('Evaluate Submissions') {
            steps {
                script {
                    def rounds = [1, 2, 3]
                    rounds.each { round ->
                        sh "python evaluate_json_missions.py --round ${round} --directory ./submissions/"
                    }
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'hackathon_results_*.json', fingerprint: true
            }
        }
    }
}
```

## 🎯 Analisi dei Risultati

### Struttura Output Standard
```json
{
  "mission_1": {
    "task_id": 1,
    "score": 85.0,
    "max_score": 100,
    "percentage": 85.0,
    "breakdown": {
      "correctness": {
        "score": 60,
        "max": 60,
        "percentage": 100.0
      },
      "efficiency": {
        "score": 15,
        "max": 20,
        "percentage": 75.0
      },
      "quality": {
        "score": 10,
        "max": 20,
        "percentage": 50.0
      }
    },
    "details": {
      "api_calls": 8,
      "optimal_calls": 6,
      "efficiency_ratio": 0.75,
      "objectives_met": [
        "Target droid moved to destination",
        "Required items purchased",
        "Budget optimized"
      ]
    }
  },
  "mission_2": {
    "task_id": 2,
    "score": 92.0,
    "max_score": 100,
    "percentage": 92.0,
    "breakdown": {
      "correctness": {
        "score": 60,
        "max": 60,
        "percentage": 100.0
      },
      "efficiency": {
        "score": 18,
        "max": 20,
        "percentage": 90.0
      },
      "quality": {
        "score": 14,
        "max": 20,
        "percentage": 70.0
      }
    },
    "details": {
      "api_calls": 6,
      "optimal_calls": 6,
      "efficiency_ratio": 1.0,
      "objectives_met": [
        "All objectives completed",
        "Optimal resource usage",
        "Clean implementation"
      ]
    }
  },
  "summary": {
    "total_score": 177.0,
    "total_max_score": 200,
    "overall_percentage": 88.5,
    "missions_completed": 2,
    "missions_evaluated": 2,
    "average_score": 88.5
  }
}
```

### Analisi Avanzata
```python
# Carica e analizza risultati
import json

with open('hackathon_results_example.json', 'r') as f:
    results = json.load(f)

# Statistiche per mission
for mission, data in results.items():
    if mission != 'summary':
        print(f"\n📊 {mission}:")
        print(f"  Score: {data['score']}/{data['max_score']} ({data['percentage']:.1f}%)")
        print(f"  Breakdown:")
        for component, scores in data['breakdown'].items():
            print(f"    - {component.title()}: {scores['score']}/{scores['max']} ({scores['percentage']:.1f}%)")
```

## 🔧 Troubleshooting

### Problema: File non riconosciuto
```bash
# Sintomo
FileNotFoundError: No missions found for round 2

# Soluzione
# 1. Verifica nome file
ls mission_*.json

# 2. Usa pattern esplicito
python evaluate_json_missions.py --round 2 --pattern "*.json"

# 3. Specifica task_id nel JSON
{
  "task_id": 1,
  "response": "..."
}
```

### Problema: Stato finale non trovato
```bash
# Sintomo
KeyError: 'final_state' or Warning: Using fallback for final_state

# Soluzione
# Aggiungi final_state completo:
{
  "task_id": 1,
  "final_state": {
    "client": {
      "balance": 3480,
      "inventory": ["Laser Sword", "Laser Sword"]
    },
    "droids": {
      "R2-D2": {
        "location": "Coruscant"
      }
    }
  }
}
```

### Problema: API calls non conteggiati
```bash
# Sintomo
Efficiency score = 0 or Warning: No API calls information

# Soluzione
# Aggiungi conteggio API calls:
{
  "task_id": 1,
  "api_calls_count": 12
}

# O fornisci intermediate_steps dettagliati
{
  "task_id": 1,
  "intermediate_steps": [
    {"tool": "get_asset_location", "result": "..."},
    {"tool": "book_travel", "result": "..."}
  ]
}
```

### Debug Mode
```bash
# Abilita debug dettagliato
python evaluate_json_missions.py --round 2 --debug

# Output debug mostra:
# 🔍 Debug: Extracting data from mission_1.json
# 🔍 Debug: Found task_id: 1
# 🔍 Debug: Found agent_response: "Missione completata..."
# 🔍 Debug: Found api_calls_count: 12
# 🔍 Debug: Reconstructing final_state from partial data
```

## 🎨 Personalizzazioni

### Criteri di Valutazione Custom
```python
class CustomJSONEvaluator(JSONMissionEvaluator):
    def _calculate_custom_bonus(self, data):
        """Calcola bonus personalizzati"""
        bonus = 0
        
        # Bonus per creatività
        if self._is_creative_solution(data):
            bonus += 10
        
        # Bonus per efficienza estrema
        if data.get('api_calls_count', 0) < 5:
            bonus += 5
        
        return bonus
    
    def evaluate_mission_from_json(self, filename):
        result = super().evaluate_mission_from_json(filename)
        
        # Aggiungi bonus custom
        with open(filename, 'r') as f:
            data = json.load(f)
        
        bonus = self._calculate_custom_bonus(data)
        result['score'] += bonus
        result['custom_bonus'] = bonus
        
        return result
```

### Format Personalizzati
```python
# Supporta format JSON completamente custom
class FlexibleJSONEvaluator(JSONMissionEvaluator):
    def _extract_data_from_json(self, data):
        """Estrae dati da format personalizzato"""
        
        # Mapping per format aziendali
        if 'corporate_mission_result' in data:
            return self._extract_corporate_format(data)
        
        # Mapping per format universitari
        if 'student_submission' in data:
            return self._extract_student_format(data)
        
        # Fallback a estrazione standard
        return super()._extract_data_from_json(data)
```

## 🎉 Esempi Pratici per Scenari Reali

### Scenario 1: Hackathon Universitario
```bash
# Setup per corso di 200 studenti
mkdir submissions_AI_2025
cd submissions_AI_2025

# Struttura attesa:
# student_12345_mission_1.json
# student_12345_mission_2.json
# student_67890_mission_1.json

# Valutazione automatica
for round in 1 2 3; do
    echo "🚀 Valutando Round $round..."
    python ../evaluate_json_missions.py --round $round --directory . --output results_round_$round.json
done

# Genera classifica
python ../generate_leaderboard.py --results results_round_*.json
```

### Scenario 2: Competizione Aziendale
```python
# Sistema di valutazione per team aziendali
class CorporateEvaluator:
    def __init__(self):
        self.evaluators = {
            1: JSONMissionEvaluator(1),
            2: JSONMissionEvaluator(2),
            3: JSONMissionEvaluator(3)
        }
    
    def evaluate_team(self, team_name, submission_dir):
        team_results = {}
        
        for round_num in [1, 2, 3]:
            evaluator = self.evaluators[round_num]
            results = evaluator.evaluate_all_missions(directory=submission_dir)
            team_results[f'round_{round_num}'] = results
        
        return self._calculate_team_score(team_results)
```

### Scenario 3: Competizione Mondiale
```bash
# Gestione competizione con migliaia di partecipanti
#!/bin/bash

# Valutazione distribuita
for country in usa europe asia; do
    echo "Processing $country submissions..."
    
    # Valutazione parallela per regione
    find submissions/$country -name "*.json" | \
    parallel --progress -j 8 python evaluate_json_missions.py --round {//} --file {}
    
    # Aggrega risultati regionali
    python aggregate_regional_results.py --region $country
done

# Combina risultati globali
python combine_global_results.py --regions usa europe asia
```

## 📚 Risorse Aggiuntive

### File di Esempio
- `example_mission_result.json` - Formato JSON risultato di esempio
- `hackathon_results_example.json` - Esempio risultati valutazione

### Script di Utilità
```python
# validate_json_format.py
def validate_json_format(filename):
    """Valida formato JSON prima della submission"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Controlla campi obbligatori
        required_fields = ['task_id', 'agent_response']
        for field in required_fields:
            if field not in data:
                print(f"❌ Campo obbligatorio mancante: {field}")
                return False
        
        print(f"✅ {filename} è valido")
        return True
    
    except Exception as e:
        print(f"❌ Errore nel file {filename}: {e}")
        return False
```

### Migrazione da Notebook
```python
# convert_notebook_to_json.py
def convert_notebook_results_to_json(notebook_path, output_path):
    """Converte risultati notebook in formato JSON"""
    
    # Carica notebook
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    # Estrai risultati dalle celle
    results = extract_results_from_notebook(notebook)
    
    # Converte in formato JSON standard
    json_format = {
        "task_id": results['task_id'],
        "agent_response": results['final_response'],
        "intermediate_steps": results['tool_calls'],
        "final_state": results['final_state'],
        "api_calls_count": len(results['tool_calls'])
    }
    
    # Salva
    with open(output_path, 'w') as f:
        json.dump(json_format, f, indent=2)
    
    print(f"✅ Convertito {notebook_path} -> {output_path}")
```

---

**🎯 Con questa guida completa, hai tutte le informazioni necessarie per utilizzare efficacemente il sistema di valutazione JSON. Il sistema è progettato per essere flessibile, robusto e facile da usare sia per singoli sviluppatori che per competizioni su larga scala!**

**🚀 Buona fortuna con le tue missioni galattiche!** 