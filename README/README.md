# 🌌 Hackathon Agenti Cosmici 2025

Un hackathon di programmazione avanzata dove i partecipanti sviluppano agenti intelligenti per navigare in una galassia virtuale, completando missioni complesse attraverso API galattiche.

## 🎯 Cos'è l'Hackathon Agenti Cosmici?

Un'avventura epica di coding dove dovrai:
- 🤖 **Sviluppare agenti autonomi intelligenti** per missioni spaziali
- 🔧 **Implementare API galattiche** per interagire con l'universo virtuale  
- 🌟 **Completare missioni** di complessità crescente attraverso 3 round
- 🚀 **Ottimizzare strategie** di navigazione, trading e gestione risorse
- ⚡ **Gestire risorse limitate** (crediti, tempo, API calls)
- 🏆 **Competere** con altri sviluppatori su scala globale

## 🌟 Round dell'Hackathon

### 🟢 **Round 1: Addestramento Cosmico**
**Obiettivo**: Apprendere le basi dell'interazione galattica
- **Missioni**: 4 task di difficoltà base-media
- **Focus**: Navigation, Trading, Resource Management
- **Peso Valutazione**: 60% correttezza, 20% efficienza, 20% qualità

### 🟡 **Round 2: Esploratore Galattico**  
**Obiettivo**: Sviluppare strategie avanzate e algoritmi intelligenti
- **Missioni**: 6 task di complessità crescente
- **Focus**: Optimization, Multi-step coordination, Advanced algorithms
- **Peso Valutazione**: 50% correttezza, 30% efficienza, 20% qualità

### 🔴 **Round 3: Maestro degli Agenti**
**Obiettivo**: Sfide expert-level con coordinazione multi-agente
- **Missioni**: 5 task di complessità livello expert
- **Focus**: Advanced AI strategies, Complex optimization, Multi-agent coordination
- **Peso Valutazione**: 40% correttezza, 40% efficienza, 20% qualità

## 🚀 Quick Start

### 1. Setup Ambiente
```bash
git clone <repository-url>
cd hackathon-agenti-cosmici

# Setup automatico
python setup_hackathon.py

# Attiva ambiente
source hackathon_env/bin/activate  # Linux/Mac
hackathon_env\Scripts\activate     # Windows

# Test sistema
python -c "from galactic_apis import switch_to_round; print(switch_to_round(1))"
```

### 2. Scegli la Tua Modalità

#### 📓 **Modalità Notebook** (Consigliata per iniziare)
```bash
jupyter notebook hackathon_round1_missioni.ipynb
```
- ✅ Esecuzione e valutazione integrate
- ✅ Perfetta per sviluppo e debug
- ✅ Guida step-by-step inclusa

#### 📄 **Modalità JSON** (Per sistemi avanzati)
```bash
python evaluate_json_missions.py --round 1
```
- ✅ Ideale per automazione e CI/CD
- ✅ Supporta batch processing di migliaia di submission
- ✅ Perfetta per competizioni su larga scala

**🎯 Entrambe le modalità usano lo stesso sistema di valutazione e producono risultati identici!**

### 3. Crea il File `galactic_apis.py`

**❗ IMPORTANTE**: Prima di iniziare le missioni, devi creare il file `galactic_apis.py` con le classi per interagire con la galassia virtuale.

#### 🛒 **GalacticMarketplace** - Sistema di Trading
Deve permettere di:
- Cercare oggetti nel marketplace galattico
- Acquistare oggetti da diversi pianeti
- Gestire il budget e l'inventario
- Calcolare costi di trasporto

#### 🚀 **GalaxyNavigator** - Sistema di Navigazione
Deve permettere di:
- Trovare la posizione corrente di droidi e asset
- Prenotare viaggi tra pianeti
- Gestire flotte di navi disponibili
- Ottimizzare rotte e costi

#### 🔍 **InfoSphere** - Database Galattico
Deve permettere di:
- Cercare informazioni su pianeti, droidi e oggetti
- Accedere a dati storici e report
- Analizzare trend e statistiche galattiche

#### 📋 **Suggerimenti di Implementazione**
```python
# Esempio di struttura (da implementare)
class GalacticMarketplace:
    def __init__(self, galaxy_state_file):
        # Carica stato galattico
        pass
    
    def find_item(self, item_name):
        # Cerca oggetti nel marketplace
        pass
    
    def purchase_item(self, item_id):
        # Acquista oggetto
        pass

# Stessa logica per le altre classi...
```

**💡 Suggerimento**: Studia i file nella cartella `ROUND X FILES/` per capire la struttura dei dati galattici!

## 🎮 Esempio Fac-Simile Missione

### Missione Tipo: "Gestione Droidi e Risorse"
**Obiettivo**: "Trova un droide specifico e spostalo su un pianeta target. Poi acquista oggetti diversi ottimizzando i costi."

#### Strategia Vincente:
1. 🔍 Localizza l'asset usando le API di navigazione
2. 🚀 Confronta costi di trasporto tra diverse navi
3. ✈️ Esegui il trasporto più economico
4. 🛒 Scansiona il marketplace per trovare le migliori offerte
5. 💰 Ottimizza gli acquisti considerando costi di trasporto

#### Risultato Tipo:
- **Punteggio**: 85-95% (strategia efficace)
- **API Calls**: 8-15 (range ottimale)
- **Budget**: utilizzo intelligente delle risorse

## 🏗️ Struttura del Progetto

```
hackathon-agenti-cosmici/
├── 📓 NOTEBOOK PRINCIPALI
│   ├── hackathon_round1_missioni.ipynb    # Round 1: Addestramento
│   ├── hackathon_round2_missioni.ipynb    # Round 2: Esploratore
│   └── hackathon_round3_multi_agenti.ipynb # Round 3: Maestro
│
├── 🔧 SISTEMA DI VALUTAZIONE
│   ├── evaluation_system.py               # Core valutazione
│   ├── evaluate_json_missions.py          # Valutazione JSON
│   └── validate_json_format.py            # Validatore JSON
│
├── 📊 DATI DELL'UNIVERSO
│   ├── ROUND 1 FILES/                     # Stato galattico Round 1
│   ├── ROUND 2 FILES/                     # Stato galattico Round 2  
│   └── ROUND 3 FILES/                     # Stato galattico Round 3
│
├── 🧪 ESEMPI E TEST
│   ├── example_mission_result.json        # Esempio formato JSON
│   └── galactic_apis.py                   # ❗ DA CREARE
│
└── 📚 DOCUMENTAZIONE
    ├── README.md                          # Questo file
    ├── EVALUATION_SYSTEM_README.md        # Dettagli valutazione
    ├── GUIDE_EVALUATION_JSON.md           # Guida formato JSON
    └── README_SETUP.md                    # Setup dettagliato
```

## 📊 Sistema di Valutazione

### Metriche di Punteggio
- **🎯 Correttezza**: Hai raggiunto l'obiettivo della missione?
- **⚡ Efficienza**: Hai ottimizzato il numero di API calls?
- **✨ Qualità**: Il tuo codice è elegante e ben strutturato?

### Livelli di Performance
- 🌟 **LEGGENDARIO** (90%+): Strategia quasi perfetta
- 🥇 **ECCELLENTE** (80-89%): Implementazione molto solida  
- 🥈 **OTTIMO** (70-79%): Buona strategia ben eseguita
- 🥉 **BUONO** (60-69%): Approccio valido con margini di miglioramento
- 🔶 **SUFFICIENTE** (50-59%): Obiettivi base raggiunti

## 🏆 Criteri di Vittoria

### Determinazione del Vincitore
Il **team o partecipante vincitore** sarà determinato secondo questi criteri:

1. **🎯 Criterio Principale**: Numero di missioni risolte correttamente
   - Vince chi ha completato il maggior numero di missioni con successo
   - Una missione è considerata "risolta" se ottiene almeno il 60% di correttezza

2. **⚖️ Criterio di Parità**: Confronto percentuali per singola missione
   - In caso di parità nel numero di missioni risolte
   - Si confrontano le percentuali di ogni singola missione nell'ordine
   - Vince chi ottiene la percentuale più alta nella prima missione diversa

### Esempio di Calcolo
```
Team A: 5 missioni risolte (85%, 92%, 78%, 88%, 95%)
Team B: 5 missioni risolte (85%, 92%, 82%, 88%, 90%)

Confronto:
- Missione 1: 85% = 85% → Parità
- Missione 2: 92% = 92% → Parità  
- Missione 3: 78% < 82% → Team B vince

🏆 Vincitore: Team B (82% > 78% nella Missione 3)
```

### Ordine di Confronto
Il confronto avviene nell'ordine delle missioni:
1. **Round 1**: Missioni 1, 2, 3, 4
2. **Round 2**: Missioni 1, 2, 3, 4, 5, 6  
3. **Round 3**: Missioni 1, 2, 3, 4, 5, 6, 7, 8

### Classifiche Multiple
- **🥇 Vincitore Assoluto**: Miglior performance complessiva
- **🏅 Vincitore Round 1**: Migliore nei task introduttivi
- **🏅 Vincitore Round 2**: Migliore nell'ottimizzazione
- **🏅 Vincitore Round 3**: Migliore nel multi-agente
- **⚡ Premio Efficienza**: Minor numero di API calls utilizzate
- **🎨 Premio Creatività**: Soluzioni più innovative

## 🛠️ Funzionalità Avanzate

### Per Sviluppatori Singoli
```bash
# Valutazione rapida
python evaluate_json_missions.py --round 1

# Validazione file
python validate_json_format.py --file mission_1.json
```

### Per Competizioni su Larga Scala
```bash
# Batch processing migliaia di submission
find ./submissions -name "*.json" | xargs python evaluate_json_missions.py --round 1

# Integrazione CI/CD
python evaluate_json_missions.py --round $ROUND --directory $SUBMISSION_DIR
```

### Per Team e Università
```bash
# Valutazione per classe
python evaluate_json_missions.py --round 2 --directory "./class_submissions/"

# Generazione leaderboard
python generate_leaderboard.py --results results_*.json
```

## 🎯 Obiettivi di Apprendimento

Al termine dell'hackathon avrai acquisito competenze in:
- 🧠 **Intelligenza Artificiale**: Algoritmi di decision-making
- 🔧 **Ingegneria del Software**: API design e integrazione
- ⚡ **Ottimizzazione**: Resource management e performance tuning
- 🚀 **Problem Solving**: Analisi di problemi complessi multi-step
- 📊 **Data Management**: Gestione stati complessi e persistenza dati

## 🔗 Risorse e Guide

- **[🔧 Setup Ambiente](README_SETUP.md)** - Installazione e configurazione dettagliata
- **[📊 Sistema Valutazione](EVALUATION_SYSTEM_README.md)** - Come funziona la valutazione
- **[📄 Modalità JSON](GUIDE_EVALUATION_JSON.md)** - Guida completa formato JSON
- **[🧪 Formato JSON](example_mission_result.json)** - Esempio di formato risultato

## 🎉 Inizia la Tua Avventura!

1. **🛠️ Setup**: Clona il repo e configura l'ambiente
2. **📚 Studia**: Leggi le guide e esplora i dati galattici
3. **🔧 Implementa**: Crea il file `galactic_apis.py` con le tre classi
4. **🚀 Testa**: Inizia con il Round 1 per imparare le basi
5. **🏆 Competi**: Affronta round più complessi e ottimizza le strategie

**Che la Forza sia con te, giovane Padawan Developer! 🌟**

---

*© 2025 Hackathon Agenti Cosmici - Powered by Datapizza* 