# Persönlicher Budgetplaner (Konsole)

## 📝 Analysis

**Problem:**
Als Teilzeit-Student hat man viel zu erledigen und muss den Überblick über Studium, Arbeit und Privatleben behalten. So kann es kommen, dass man den Überblick über seine finanzielle Lage verliert. 

**Scenario:**
Durch einen persönlicher Budget-Planner in App-Format kann man ganz einfach und von überall einen Einblick in seine Finanzen erhalten. Auch ist der Budget-Planner individuell anpassbar. 

**User stories:**
1. Als User möchte ich, dass die App Passwort geschützt **`Test1234`** ist.
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
- Show Menu (from `menu.txt`)
- Create Order (choose pizzas)
- Show Current Order and Total
- Print Invoice (to `invoice_xxx.txt`)



## ✅ Project Requirements

### 1. Interaktive App (d.h. Verarbeitung von Benutzereingaben über die Konsole) 

- Password eingeben 
- Passwort ändern 
- Einnahmen und Ausgaben angeben & anpassen 
- Budget-Kategorie bearbeiten 
- Budgetlimit/Finanzziel setzten & anpassen 



### 2. Validierung von Daten (Check von Eingabedaten auf Datentyp oder Format) 

**Passwort:**
Check von Eingabedate auf true und Komplexitätsvorgaben. Komplexitätsvorgaben für das Passwort sind:  
- Mind. 8 Zeichen 
- Gross- und Kleinschreibung 
- Mind. eine Zahl 
- Mind. ein Sonderzeichen 

Nach drei falschen Anmeldeversuchen wird das System automatisch beendet. Bei einer Passwortänderung wird zusätzlich geprüft, dass das neue Passwort ==! mit dem altem Passwort übereinstimmt.
*--> Rückführung zum Hauptmenü*

**Hauptmenü:**
Wenn User eine Option wählt, wird geprüft, ob die Eingabe (Option Nr.) existiert und der Datentyp stimmt. 
*Von App abmelden = System beenden*

**Budget-Kategorien:**
Wenn User eine Kategorie bearbeiten will, wird geprüft, ob die Eingabe (Kategorie Nr.) existiert und der Datentyp stimmt.  
*--> Rückführung zum Hauptmenü*

**Budgetlimit & Finanzziele:** 
Wenn User ein Limit/Ziel bearbeiten oder erstellen will, wird geprüft, ob die Eingabe (Kategorie Nr.) existiert und der Datentyp stimmt. 
*--> Rückführung zum Hauptmenü*

**Budgetanalyse / Vergleich:**
Wenn User eine Kategorie mit dem Vormonat vergleichen will, wird geprüft, ob die Eingabe (Kategorie Nr.) existiert und der Datentyp stimmt. 
*--> Rückführung zum Hauptmenü* 



### 3. Dateiverarbeitung (Lesen & Schreiben von Daten) 

**Erst Eingabe:** 
- Eingaben erfolgen über die Konsole.
- Daten werden in einer JSON-Datei (`budget_daten.json`) gespeichert.
- Standardkategorien wie Lebensmittel, Studium und Freizeit sind vordefiniert, können aber geändert werden.

Ausgabetyp
Betrag
Monat & Jahr vom Kauf

**Spätere Bearbeitung (Manipulation):**
- Beim Neustart der Anwendung wird die JSON-Datei eingelesen.
- Alle Änderungen und Ergänzungen aus der vorherigen Nutzung (neue Kategorien, Einträge, Limits oder Ziele) werden automatisch geladen und stehen wieder zur Verfügung.
- Dadurch bleibt der aktuelle Stand der Budgetverwaltung erhalten und kann weiter bearbeitet oder erweitert werden.

**Passwortverschlüsselung:**
- Das Passwort wird vor der Speicherung mit bcrypt gehasht. Dadurch stellen wir sicher, dass sensible Nutzerdaten auch bei einem Datenleck geschützt bleiben.



## ⚙️ Implementation

### Technology
- Python 3.13 *(29.11.2025)*
- Environment: GitHub Codespaces
- 1 externe Bibliotheken

### How to Run
1. Open the repository in **GitHub Codespaces**
2. Open the **Terminal**
3. Run:
	```bash
	python3 main.py
	```


### Libraries Used

**Externe Bibliotheken:**
- `bcrypt`: für die Passwortverschlüsselung eingesetzt. Das Passwort wird vor der Speicherung mit einem Hash versehen, sodass sensible Nutzerdaten auch bei einem Datenleck geschützt bleiben.
Installation über `pip install bcrypt`.

**Interne Bibliotheken:**
- `json`: zum Speichern und Laden strukturierter Daten im JSON-Format (`budget_daten.json`).
- `os`: für Betriebssystemfunktionen wie Pfadprüfung, Dateiexistenz und Programmbeendigung
- `threading`: ermöglicht das Setzen von Timern für Inaktivitäts-Logout und parallele Abläufe
- `sys`: Für Systemfunktionen wie das Beenden des Programms (`sys.exit`)

Diese Bibliotheken wurden gewählt, da sie eine einfache und zugleich effiziente Lösung für Datei­verwaltungsaufgaben in einer Konsolenanwendung bieten.



## 👥 Team & Contributions

| Name       | Contribution                                 |
|------------|----------------------------------------------|
| Nina P.    | Passwort-Logik (Login, Validierung, Passwort ändern und speichern), Statistikteil (50%), README |
| Paola P.   | Menüstruktur & Logik (Kategorien, Budgetlimits/Finanzziele,Validierung), JSON-Dateiverarbeitung (schreiben/lesen), Main-Funktion, README |
| Sarah K.   | Inaktivitäts-Handling, Statistikteil (50%) |



## 🤝 Contributing

- Use this repository as a starting point by importing it into your own GitHub account.  
- Work only within your own copy — do not push to the original template.  
- Commit regularly to track your progress.



## 📝 License

This project is provided for **educational use only** as part of the Programming Foundations module.  
[MIT License](LICENSE)
