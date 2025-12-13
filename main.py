"""
Budget-Tracker Hauptprogramm (ohne Klasse),
koordiniert alle Module und stellt das Hauptmenü bereit
"""

from data_handler import daten_laden, daten_speichern
from auth import passwort_login, passwort_ändern
from category_manager import (
    anzeigen_kategorien,
    neue_kategorie_hinzufügen,
    kategorie_bearbeiten,
    kategorie_löschen
)
from finance_control import finanzkontrolle
from statistic import statistik_menü
from utils import inaktivität_wrapper


# Globale Variablen
budget_kategorien = {}
budget_limits = {}
finanzziele = {}
benutzer_passwort = {}
timed_input = None


def daten_speichern_wrapper():
    """Wrapper-Funktion zum Speichern aller Daten."""
    daten_speichern(
        budget_kategorien,
        budget_limits,
        finanzziele,
        benutzer_passwort)


def hauptmenü():
    """Zeigt das Hauptmenü an und verarbeitet Benutzerauswahlen."""
    global budget_kategorien, budget_limits, finanzziele
    global benutzer_passwort, timed_input

    timed_input = inaktivität_wrapper(120, daten_speichern_wrapper)

    while True:
        print("\n\n\033[1mKategorien Menü\033[0m")
        print("1. Kategorien anzeigen")
        print("2. Neue Kategorie hinzufügen")
        print("3. Kategorie bearbeiten")
        print("4. Kategorie löschen")
        print("5. Finanzkontrolle")
        print("6. Passwort ändern")
        print("7. Statistik anzeigen")
        print("8. App beenden")

        auswahl = timed_input("\n\033[34mWähle eine Option (1-8):\033[0m")

        if auswahl == "1":
            anzeigen_kategorien(
                budget_kategorien,
                timed_input
            )

        elif auswahl == "2":
            budget_kategorien = neue_kategorie_hinzufügen(
                budget_kategorien,
                timed_input
            )
            daten_speichern_wrapper()

        elif auswahl == "3":
            budget_kategorien = kategorie_bearbeiten(
                budget_kategorien,
                budget_limits,
                timed_input
            )
            daten_speichern_wrapper()

        elif auswahl == "4":
            budget_kategorien = kategorie_löschen(
                budget_kategorien,
                timed_input
            )
            daten_speichern_wrapper()

        elif auswahl == "5":
            budget_limits, finanzziele = finanzkontrolle(
                budget_kategorien,
                budget_limits,
                finanzziele,
                timed_input,
                daten_speichern_wrapper
            )

        elif auswahl == "6":
            benutzer_passwort = passwort_ändern(
                benutzer_passwort,
                timed_input,
                daten_speichern_wrapper
            )

        elif auswahl == "7":
            statistik_menü(
                budget_kategorien,
                budget_limits,
                finanzziele,
                timed_input
            )

        elif auswahl == "8":
            print("\n\033[32mProgramm beendet.\033[0m")
            break

        else:
            print("\n\033[31mUngültige Eingabe:"
                  "Bitte wähle eine Zahl zwischen 1-8.\033[0m")


def main():
    """Hauptfunktion des Programms."""
    global budget_kategorien, budget_limits, finanzziele, benutzer_passwort

    # Daten laden
    (budget_kategorien,
     budget_limits,
     finanzziele,
     benutzer_passwort) = daten_laden()

    # Login durchführen
    passwort_login(benutzer_passwort, daten_speichern_wrapper)

    # Hauptmenü starten
    hauptmenü()

    # Beim Beenden speichern
    daten_speichern_wrapper()


if __name__ == "__main__":
    main()
