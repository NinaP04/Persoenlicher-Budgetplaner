# Persönlicher Budgetplaner (Konsole)
---

## 📝 Analyse
---

**Problem:**
Als Teilzeit-Student hat man viel zu erledigen und muss den Überblick über Studium, Arbeit und Privatleben behalten. So kann es kommen, dass man den Überblick über seine finanzielle Lage verliert.

**Scenario:**
Durch einen persönlicher Budget-Planner in App-Format kann man ganz einfach und von überall einen Einblick in seine Finanzen erhalten. Auch ist der Budget-Planner individuell anpassbar.

**User stories:**
1. Als User möchte ich, dass die App Passwort geschützt ist (Passwort bei Erstnutzung: **`Test1234!`**).
2. Als User möchte ich jederzeit mein Passwort in der App ändern können.
3. Als User möchte ich automatisch ausgeloggt werden bei Inaktivität.
4. Als User möchte ich, meine Einnahmen und Ausgaben erfassen & anpassen können.
5. Als User möchte ich mein Budget in mehrere Kategorien unterteilen, um den Überblick zu behalten.
6. Als User möchte ich die Budget-Kategorien anpassen, hinzufügen und löschen können.
7. Als User möchte ich ein Budgetlimit für jede Kategorie festlegen können.
8. Als User möchte ich eine Warnung erhalten, wenn ich mein Budget überschreite.
9. Als User möchte ich bei Erreichen eines finanziellen Zieles benachrichtigt werden.
10. Als User möchte ich, die Daten vom aktuellen Monat mit denen der Vormonate vergleichen können.

**Use cases:**
- Hauptmenü anzeigen (Bedienung aller Funktionen)
- Budget-Kategorien verwalten (Kategorien und Einträge anzeigen, erstellen, bearbeiten und löschen)
- Finanzkontrolle pro Kategorie (Budgetlimit und Sparziel setzen, anzeigen, ändern, entfernen)
- Passwort ändern (Benutzerpasswort aktualisieren, Sicherheitsregeln prüfen)
- Daten speichern und Programm beenden (Eingaben werden dauerhaft gesichert und das Programm wird sauber beendet)
- Ausgabe von Statistik (Visualisierung) als PGN-Datei (`finanzziele_diagramm.png` & `monats_summen_diagramm.png`)

<br>

## ✅ Projektanforderungen
---

### 1. Interaktive App (Benutzereingaben über die Konsole)

- Password eingeben
- Passwort ändern
- Einnahmen und Ausgaben angeben & anpassen
- Budget-Kategorie bearbeiten
- Budgetlimit/Finanzziel setzten & anpassen
- (Erhalt von Monatsauswertungen)

### 2. Validierung von Daten (Prüfung von Eingabedaten auf Datentyp oder Format)

- **Passwort setzten:** Bei einer Passwortänderung wird zusätzlich geprüft, dass das neue Passwort ==! mit dem altem Passwort übereinstimmt. <br> Komplexitätsvorgaben für das Passwort sind:
    - Mindestens 8 Zeichen
    - Maximal 20 Zeichen
    - Mindestens ein Grossbuchstabe
    - Mindestens ein Kleinbuchstabe
    - Mindestens eine Zahl
    - Mindestens ein Sonderzeichen: `$, @, #, %, !, ?, &, *` <br>


- **Anmeldeversuchen:** Nach drei falschen Anmeldeversuchen wird das System automatisch beendet. <br>
*--> Von App abmelden = System beenden*

- **Hauptmenü:** Wenn User eine Option wählt, wird geprüft, ob die Eingabe (Option Nr.) existiert und der Datentyp stimmt.<br>
*--> Aufforderung zur erneuten Eingabe*

- **Budget-Kategorien:** Wenn User eine Kategorie bearbeiten will, wird geprüft, ob die Eingabe (Kategorie Nr.) existiert und der Datentyp stimmt.<br>
*--> Rückführung zum Hauptmenü*

- **Budgetlimit & Finanzziele:** Wenn User ein Limit/Ziel bearbeiten oder erstellen will, wird geprüft, ob die Eingabe (Kategorie Nr.) existiert und der Datentyp stimmt.<br>
*--> Rückführung zum Hauptmenü*

- **Budgetanalyse / Vergleich:** Wenn User eine Kategorie mit dem Vormonat vergleichen will, wird geprüft, ob die Eingabe (Kategorie Nr.) existiert und der Datentyp stimmt.<br>
*--> Rückführung zum Hauptmenü*

### 3. Dateiverarbeitung (Lesen & Schreiben von Daten)

**Erst Eingabe:**
- Eingaben (Ausgabetyp, Betrag, Monat & Jahr vom Kauf) erfolgen über die Konsole.
- Daten werden in einer JSON-Datei (`budget_daten.json`) gespeichert.
- Standardkategorien wie Lebensmittel, Studium und Freizeit sind vordefiniert, können aber geändert werden.

**Spätere Bearbeitung (Manipulation):**
- Beim Neustart der Anwendung wird die JSON-Datei eingelesen. Alle Änderungen und Ergänzungen aus der vorherigen Nutzung (neue Kategorien, Einträge, Limits oder Ziele) werden automatisch geladen und stehen wieder zur Verfügung.
- Dadurch bleibt der aktuelle Stand der Budgetverwaltung erhalten und kann weiter bearbeitet oder erweitert werden.
- Statistik / Visualisierung (`finanzziele_diagramm.png` & `monats_summen_diagramm.png`)

**Passwortverschlüsselung:**
- Das Passwort wird vor der Speicherung mit bcrypt gehasht. Dadurch stellen wir sicher, dass sensible Nutzerdaten auch bei einem Datenleck geschützt bleiben.

<br>

## ⚙️ Implementation
---

### Technologie

- Python 3.13
- Environment: GitHub Codespaces
- 3 externe Bibliotheken (die letzten Versionen -> jeweils Stand 13.12.2025)

### Ausführung

1. Open the repository in **GitHub Codespaces**
2. Open the **Terminal**
3. Run:
	```bash
	python3 main.py
	```

 ### Verwendete Bibliotheken

**Externe Bibliotheken:**
- `bcrypt`: für die Passwortverschlüsselung eingesetzt. Das Passwort wird vor der Speicherung mit einem Hash versehen, sodass sensible Nutzerdaten auch bei einem Datenleck geschützt bleiben. Installation über `pip install bcrypt`.
- `numpy`: für mathematische Operationen und effiziente Arbeit mit Arrays und numerischen Daten. Installation über `pip install numpy`.
- `matplotlib.pyplot`: zum Erstellen von Diagrammen und Visualisierungen (z.B. Balken‑ oder Liniendiagramme). Installation über `pip install matplotlib`.

**Interne Bibliotheken:**
- `json`: zum Speichern und Laden strukturierter Daten im JSON-Format (`budget_daten.json`).
- `os`: für Betriebssystemfunktionen wie Pfadprüfung, Dateiexistenz und Programmbeendigung
- `threading`: ermöglicht das Setzen von Timern für Inaktivitäts-Logout und parallele Abläufe
- `sys`: für Systemfunktionen wie das Beenden des Programms (`sys.exit`)
- `re`: reguläre Ausdrücke zum Validieren und Bearbeiten von Texteingaben (z.B. Zahlen, Passwörter).
- `base64`: zum Kodieren und Dekodieren von Daten in Base64‑Format (z.B. für sichere Speicherung).
- `bcrypt`: für sichere Passwort‑Hashing‑Funktionen und Authentifizierung.

Diese Bibliotheken wurden gewählt, da sie eine einfache und zugleich effiziente Lösung für Datei­verwaltungsaufgaben in einer Konsolenanwendung bieten.

### Repository Struktur

```text
budget-tracker/
├── `README.md`              # Projektbeschreibung, Installationsanleitung und Nutzungshinweise (diese Datei).
├── `main.py`                # Login, Menüführung und zentrale Steuerung.
├── `statistic.py`           # Statistische Visusliserung mit Balkendiagramme.
├── `financ_control`         # Budgetlimits und Finanzziele setzen, ändern, löschen.
├── `category_manager.py`    # Anzeigen, Umbenennen, Hinzufügen, Bearbeiten, Löschen von Kategorien.
├── `utils.py`               # Inaktivitäts-Timer mit Logout, Validierung (Betrag & Datum).
├── `daten_handler.py`       # Konstanten und Standardwerte (Standard-Kategorien, Maximale Budgetlimits etc.), das Erstellen, Laden und Speichern der JSON-Daten.
└── `auth.py`                # Passwort-Hashing, Login, Passwort ändern und Validierung.
```

## 👥 Team & Contributions
---


| Name       | Contribution                                                                                                                                                 |
|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Nina P.    | Passwort-Logik (Login, Validierung, Passwort ändern und speichern), Statistikteil-Visualisierung, README (Aufsetzung)                                        |
| Paola P.   | Menüstruktur & Logik (Kategorien, Budgetlimits/Finanzziele,Validierung), JSON-Dateiverarbeitung (schreiben/lesen), Main-Funktion, README (Weiterbearbeitung) |
| Sarah K.   | Inaktivitäts-Handling, Statistikteil-Datenverarbeitung                                                                                                       |

## 🤝 Contributing
---

- Verwende dieses Repository als Ausgangspunkt, indem du es in dein eigenes GitHub-Konto importierst.
- Arbeite ausschließlich in deiner eigenen Kopie, keine Änderungen am Original-Template pushen.
- Führe regelmässige Commits durch, um deinen Fortschritt zu dokumentieren.

## 📝 Lizenz
---

Dieses Projekt wird **ausschließlich zu Ausbildungszwecken** im Rahmen des Moduls Grundlagen Programmieren bereitgestellt.
MIT License
