"""
Datenverwaltungs-Modul für Budget-Tracker
Enthält Funktionen zum Laden und Speichern von Daten
"""

import json
import os
import base64
from auth import hash_passwort


# Standardkategorien beim ersten Start
STANDARD_KATEGORIEN = {
    "Lebensmittel": [
        "01.01.2025 - Nudeln - 2.50 CHF",
        "02.01.2025 - Milch - 1.80 CHF",
        "03.01.2025 - Gipfeli - 1.20 CHF",
        "04.01.2025 - Fisch (Lachs) - 12.90 CHF",
        "05.01.2025 - Brot - 3.50 CHF",
        "06.03.2025 - Käse - 4.80 CHF",
        "07.03.2025 - Eier - 5.20 CHF",
        "08.03.2025 - Äpfel - 3.60 CHF",
        "09.03.2025 - Tomaten - 2.90 CHF",
        "10.04.2025 - Reis - 3.10 CHF",
        "12.04.2025 - Bananen - 2.40 CHF",
        "15.04.2025 - Joghurt - 1.50 CHF",
        "18.04.2025 - Pouletfilet - 9.80 CHF",
        "22.04.2025 - Spinat - 3.20 CHF",
        "25.04.2025 - Mineralwasser - 1.00 CHF",
        "02.05.2025 - Schokolade - 2.90 CHF",
        "05.05.2025 - Orangensaft - 3.80 CHF",
        "09.05.2025 - Hackfleisch - 8.50 CHF",
        "14.05.2025 - Kartoffeln - 4.20 CHF",
        "20.05.2025 - Zwiebeln - 2.10 CHF",
        "28.05.2025 - Butter - 3.70 CHF"
    ],
    "Studium": [
        "01.01.2025 - Semestergebühr - 750 CHF",
        "10.01.2025 - Laptop-Rücklage - 50 CHF",
        "15.01.2025 - Bücher & Skripte - 380 CHF",
        "20.01.2025 - Lernmaterialien - 40 CHF",
        "01.02.2025 - Software-Lizenz - 30 CHF",
        "22.02.2025 - ÖV-Monatsabo - 65 CHF",
        "12.03.2025 - Kopier- und Druckkosten - 18 CHF",
        "20.03.2025 - Laptop-Rücklage - 50 CHF",
        "12.04.2025 - Mensa & Snacks - 22 CHF",
        "15.04.2025 - Kopier- und Druckkosten - 25 CHF",
        "20.05.2025 - Studierendenverein-Beitrag - 20 CHF"
    ],
    "Freizeit": [
        "05.01.2025 - Kinoabend - 20 CHF",
        "12.01.2025 - Bowling - 15 CHF",
        "18.01.2025 - Museumseintritt - 12 CHF",
        "01.02.2025 - Netflix Abo - 18 CHF",
        "05.02.2025 - Fitnessstudio - 50 CHF",
        "10.02.2025 - Ausflug Zürichsee - 25 CHF",
        "15.02.2025 - Buchhandlung - 22 CHF",
        "20.02.2025 - Café mit Freunden - 14 CHF",
        "25.02.2025 - Konzertticket - 60 CHF",
        "28.02.2025 - Eis essen - 6 CHF",
        "04.04.2025 - Theaterbesuch - 35 CHF",
        "08.04.2025 - Fahrradtour - 10 CHF",
        "12.04.2025 - Brettspielabend - 18 CHF",
        "16.04.2025 - Schwimmbad - 12 CHF",
        "20.04.2025 - Karaokeabend - 22 CHF",
        "02.05.2025 - Netflix Abo - 18 CHF",
        "06.05.2025 - Fitnessstudio - 50 CHF",
        "10.05.2025 - Ausflug Basel Altstadt - 28 CHF",
        "15.05.2025 - Café mit Freunden - 16 CHF",
        "19.05.2025 - Konzertticket - 65 CHF",
        "25.05.2025 - Eis essen - 7 CHF"
    ]
}

DATEN_DATEI = "budget_daten.json"


def _is_bcrypt_base64(s):
    """Prüft ob ein String ein bcrypt-gehashter Base64-String ist."""
    try:
        decoded = base64.b64decode(s.encode('utf-8'))
        return decoded.startswith(b'$2')
    except Exception:
        return False


def daten_laden():
    """
    Lädt gespeicherte Budgetdaten aus der JSON-Datei.
    Falls keine Datei existiert, werden Standardwerte verwendet.
    Migriert alte ungehashte Passwörter zu gehashten Passwörtern.

    Returns:
        tuple: (budget_kategorien, budget_limits, finanzziele,
                benutzer_passwort)
    """
    if os.path.exists(DATEN_DATEI):
        with open(DATEN_DATEI, "r", encoding="utf-8") as f:
            daten = json.load(f)
            budget_kategorien = daten.get("budget_kategorien", {})
            budget_limits = daten.get("budget_limits", {})
            finanzziele = daten.get("finanzziele", {})
            benutzer_passwort = daten.get(
                "benutzer_passwort", {"passwort": hash_passwort("Test1234!")})

            # Migration: Falls Passwort noch nicht gehashed ist
            stored_pass = benutzer_passwort.get("passwort")
            if stored_pass and not _is_bcrypt_base64(stored_pass):
                benutzer_passwort["passwort"] = hash_passwort(stored_pass)
                # Sofort speichern
                daten_speichern(budget_kategorien,
                                budget_limits,
                                finanzziele,
                                benutzer_passwort)
    else:
        budget_kategorien = STANDARD_KATEGORIEN.copy()
        budget_limits = {}
        finanzziele = {}
        benutzer_passwort = {"passwort": hash_passwort("Test1234!")}

    return budget_kategorien, budget_limits, finanzziele, benutzer_passwort


def daten_speichern(budget_kategorien,
                    budget_limits,
                    finanzziele,
                    benutzer_passwort):

    """
    Speichert alle aktuellen Budgetdaten in eine JSON-Datei.

    Args:
        budget_kategorien (dict): Budget-Kategorien mit Einträgen
        budget_limits (dict): Budget-Limits pro Kategorie
        finanzziele (dict): Finanzziele pro Kategorie
        benutzer_passwort (dict): Gehashtes Benutzer-Passwort
    """
    daten = {
        "budget_kategorien": budget_kategorien,
        "budget_limits": budget_limits,
        "finanzziele": finanzziele,
        "benutzer_passwort": benutzer_passwort
    }
    with open(DATEN_DATEI, "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)


