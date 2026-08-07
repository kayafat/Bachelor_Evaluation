# Prototypische Umsetzung eines MetaHuman-basierten Dozenten für interaktive Prüfungsvorbereitung in einer Unreal-Engine-Lernumgebung (Evaluation)

## Projektbasis

Dieses Repository enthält die Materialien und Ergebnisdaten der im Rahmen der
Bachelorarbeit durchgeführten Gestenevaluation. Untersucht wurde die
Gestenauswahl der Sprachmodelle **llama3.1:8B** und **llama3.1:70B** unter
vergleichbaren Testbedingungen.

Die Evaluation wurde über das
[Backend](https://github.com/kayafat/Backend_Bachelor) ausgeführt. Das Skript
`run_gesture_eval.py` ruft die dort enthaltene Datei `langchain_query.py` auf,
verarbeitet die erzeugten Antwortsegmente und bewertet die tatsächlich
verwendeten Gesten.

Das [Unreal-Engine-Frontend](https://github.com/kayafat/Frontend_Bachelor)
wird für die automatisierte Evaluation nicht direkt benötigt. Es verwendet
die geprüfte Gestenauswahl jedoch im Gesamtsystem für die Animation des
MetaHuman-basierten Dozenten.

---

# Inhalt des Repositories

| Datei | Beschreibung |
|---|---|
| `run_gesture_eval.py` | Automatisierte Durchführung und Bewertung der Gestenevaluation |
| `test_cases.csv` | 50 englischsprachige Testfälle aus acht kommunikativen Kategorien |
| `gesture_eval_results_llama8b.csv` | 150 Testläufe des Modells llama3.1:8B |
| `gesture_eval_results_llama70b.csv` | 150 Testläufe des Modells llama3.1:70B |
| `PromptFuerEvaluation.pdf` | Prompt zur unabhängigen Berechnung und Überprüfung der Ergebnisdaten |

---

## Evaluationsaufbau

Jeder der 50 Testfälle wurde mit beiden Sprachmodellen jeweils dreimal
ausgeführt. Daraus ergeben sich **150 Testläufe pro Modell** und insgesamt
**300 Testläufe**.

Vor jedem Testlauf wird der bisherige Gesprächsverlauf gelöscht. Bewertet
werden nur die Gesten, die entsprechend der Anzahl der erzeugten
Antwortsegmente tatsächlich verwendet werden. Falls für ein Antwortsegment
keine Geste vorliegt, ergänzt das Evaluationsskript die Standardgeste
`talk_pose`.

Die zentralen Bewertungsgrößen sind:

- die Match-Rate der verwendeten Gesten,
- das Vorhandensein mindestens einer passenden Geste,
- die Übereinstimmung der ersten verwendeten Geste,
- ungültige oder unangemessen starke Gesten,
- der automatische Score von 0 bis 2.

---

## Verwendung mit dem Backend

Für eine erneute Ausführung müssen sich das Evaluationsskript und die
Testfalldatei im Ordner `evaluation` des Backend-Projekts befinden:

```text
Backend_Bachelor
├── langchain_query.py
├── history.txt
├── knowledge_base
└── evaluation
    ├── run_gesture_eval.py
    └── test_cases.csv
```

In `langchain_query.py` wird zunächst das gewünschte Sprachmodell ausgewählt.
Zusätzlich wird in `run_gesture_eval.py` die passende Modellbezeichnung
gesetzt: `MODEL_LABEL = "llama8b"` oder `MODEL_LABEL = "llama70b"`

Die Evaluation wird aus dem Hauptverzeichnis des Backends gestartet:

```bat
py -3.10 evaluation/run_gesture_eval.py
```

Während der Ausführung müssen die in der Backend-Dokumentation beschriebenen
Dienste, insbesondere die Ollama-Verbindung zum DACHS-Cluster, verfügbar sein.

---

## Auszüge aus den CSV-Dateien

Die folgenden Tabellen zeigen jeweils drei Einträge. Bei den Ergebnisdateien
werden nur ausgewählte Spalten dargestellt; die vollständigen CSV-Dateien
enthalten zusätzliche Angaben zu Antworten, Gesten, Validierung und Bewertung.

### `test_cases.csv`

| id | category | input | expected_gestures | strong_allowed |
|---:|---|---|---|---|
| 1 | `greeting` | Hello, can you hear me? | `hello_pose`&#124;`acknowledging_pose`&#124;`head_nod_yes`&#124;`talk_pose`&#124;`talk_pose2`&#124;`talk_pose3` | `hello_pose`&#124;`head_nod_yes` |
| 2 | `greeting` | Hi, are you ready to help me learn today? | `hello_pose`&#124;`acknowledging_pose`&#124;`head_nod_yes`&#124;`talk_pose`&#124;`talk_pose2`&#124;`talk_pose3` | `hello_pose`&#124;`head_nod_yes` |
| 3 | `greeting` | Good morning, can we start the lesson? | `hello_pose`&#124;`acknowledging_pose`&#124;`head_nod_yes`&#124;`talk_pose`&#124;`talk_pose2`&#124;`talk_pose3` | `hello_pose`&#124;`head_nod_yes` |
| … | … | … | … | … |

### `gesture_eval_results_llama8b.csv`

| test_id | category | used_gestures | match_rate | auto_score |
|---:|---|---|---:|---:|
| 1 | `greeting` | `talk_pose`&#124;`head_nod_yes`&#124;`arm_gesture` | 0.67 | 2 |
| 2 | `greeting` | `hello_pose`&#124;`talk_pose`&#124;`head_nod_yes` | 1.00 | 2 |
| 3 | `greeting` | `hello_pose`&#124;`talk_pose`&#124;`arm_gesture`&#124;`head_nod_yes` | 0.75 | 2 |
| … | … | … | … | … |

### `gesture_eval_results_llama70b.csv`

| test_id | category | used_gestures | match_rate | auto_score |
|---:|---|---|---:|---:|
| 1 | `greeting` | `hello_pose`&#124;`talk_pose` | 1.00 | 2 |
| 2 | `greeting` | `hello_pose`&#124;`acknowledging_pose`&#124;`talk_pose` | 1.00 | 2 |
| 3 | `greeting` | `hello_pose`&#124;`acknowledging_pose`&#124;`talk_pose` | 1.00 | 2 |
| … | … | … | … | … |

---

## Prompt zur unabhängigen Auswertung

Die Datei
[PromptFuerEvaluation.pdf](./PromptFuerEvaluation.pdf)
enthält den vollständigen Prompt, mit dem die Rohdaten unabhängig geprüft und
die Kennzahlen der Gestenevaluation erneut berechnet wurden.

Der Prompt fordert unter anderem die Rekonstruktion der Match-Rate, die Prüfung
der Score-Regeln sowie die getrennte Berechnung der Gesamt- und
Kategorieergebnisse. Die PDF stellt die im Repository dokumentierte Fassung
des Auswertungsauftrags dar.

Die zugehörige geteilte Auswertung ist ergänzend unter folgendem Link
verfügbar: [ChatGPT-Prompt](https://chatgpt.com/share/6a698126-1bfc-83eb-8105-6c5a3283c005)

---

## Zugehörige Repositories

- [Backend](https://github.com/kayafat/Backend_Bachelor)
- [Unreal-Engine-Frontend](https://github.com/kayafat/Frontend_Bachelor)

---

>### Autor
>- **Fatih Kaya**
>- Bachelorarbeit, Hochschule Esslingen
