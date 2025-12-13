"""
Hilfsfunktionen-Modul für Budget-Tracker
Enthält Validierungs- und Utility-Funktionen
"""

import threading
import os
from datetime import datetime


# Maximale Budgetlimite für Studenten
MAX_BUDGET_LIMIT = 2000.0


def validiere_datum(datum_str):
    """
    Validiert ob ein Datum im Format DD.MM.YYYY gültig ist.

    Args:
        datum_str (str): Datum als String im Format DD.MM.YYYY

    Returns:
        bool: True wenn Datum gültig ist, sonst False
    """
    try:
        datetime.strptime(datum_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def validiere_positiven_betrag(betrag, max_wert=None):
    """
    Validiert ob ein Betrag positiv (>=0) und
    optional unter einem Maximum liegt.

    Args:
        betrag (float): Zu validierender Betrag
        max_wert (float, optional): Maximaler erlaubter Wert

    Returns:
        bool: True wenn Betrag gültig ist, sonst False
    """
    if betrag < 0:
        print("\n\033[31mFehler: Der Betrag darf nicht negativ sein!\033[0m")
        return False
    if max_wert is not None and betrag > max_wert:
        print(
            f"\n\033[31mFehler: Der Betrag darf maximal "
            f"{max_wert:.2f} CHF betragen!\033[0m")
        return False
    return True


def inaktivität_wrapper(timeout, daten_speichern_func):
    """
    Erstellt eine Wrapper-Funktion für input() mit
    automatischem Logout bei Inaktivität.

    Args:
        timeout (int): Zeit in Sekunden bis zum automatischen Logout
        daten_speichern_func (callable): Funktion zum Speichern der Daten

    Returns:
        function: Wrapper-Funktion die input() mit Timer kombiniert
    """

    def logout():
        print("\n\n\033[31mDu wurdest wegen Inaktivität ausgeloggt! \033[0m")
        daten_speichern_func()
        os._exit(0)

    def timed_input_func(prompt):
        timer = threading.Timer(timeout, logout)
        timer.start()
        try:
            eingabe = input(prompt)
            timer.cancel()
            return eingabe
        except BaseException as e:
            timer.cancel()
            print(f"\n\n\033[31mEingabe abgebrochen oder Fehler aufgetreten: "
                  f"{e}\033[0m")
            daten_speichern_func()
            os._exit(0)

    return timed_input_func
