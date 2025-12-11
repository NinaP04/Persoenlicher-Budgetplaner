# Packete um Eingaben zuspeichern vor beendung des programms
import json
import os
import threading
import sys
import re
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from datetime import datetime
from collections import defaultdict
import base64

try:
    import bcrypt
except ImportError:
    print(
        "\n\033[31mFehler: Das Paket 'bcrypt' ist erforderlich, aber nicht installiert.\033[0m")
    print("Installiere es mit: pip install bcrypt")
    sys.exit(1)

# JSON weil komplexe, strukturierte Daten einfach speichern und laden - Flexibilität
daten_datei = "budget_daten.json"

# Passwort-Hashing Funktionen


def hash_passwort(passwort):
    """
    Hasht ein Passwort mit bcrypt (oder SHA256 Fallback) für sichere Speicherung.

    Args:
        passwort (str): Das zu hashende Passwort

    Returns:
        str: Der gehashte Passwort-String (base64-kodiert für JSON-Kompatibilität)
    """
    # Verwende bcrypt für sicheres Hashing (bcrypt ist jetzt zwingend erforderlich)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(passwort.encode('utf-8'), salt)
    # Konvertiere zu Base64 für JSON-Speicherung
    return base64.b64encode(hashed).decode('utf-8')


def verifiziere_passwort(passwort, hashed_passwort):
    """
    Vergleicht ein eingegebenes Passwort mit einem gehashten Passwort.

    Args:
        passwort (str): Das zu verifizierende Passwort
        hashed_passwort (str): Der gehashte Passwort-String (base64-kodiert)

    Returns:
        bool: True wenn Passwort korrekt ist, False sonst
    """
    try:
        # Dekodiere Base64 zurück zu Bytes und prüfe mit bcrypt
        hashed_bytes = base64.b64decode(hashed_passwort.encode('utf-8'))
        return bcrypt.checkpw(passwort.encode('utf-8'), hashed_bytes)
    except Exception:
        return False


standard_kategorien = {
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

# Erstellen von Listen die, die neu erstellen Kategorien abspeichern
budget_kategorien = {}
budget_limits = {}
finanzziele = {}
benutzer_passwort = {}

# Globale Variable für timed_input - wird in allen Funktionen verwendet
timed_input = None

# Maximale Budgetlimite für Studenten (konstante daher alles gross)
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


def inaktivität_wrapper(timeout=60):
    """
    Erstellt eine Wrapper-Funktion für input() mit automatischem Logout bei Inaktivität.

    Args:
        timeout (int): Zeit in Sekunden bis zum automatischen Logout

    Returns:
        function: Wrapper-Funktion die input() mit Timer kombiniert
    """

    def logout():
        print("\n\n\033[31mDu wurdest wegen Inaktivität ausgeloggt! \033[0m")
        daten_speichern()
        os._exit(0)

    def timed_input_func(prompt):
        timer = threading.Timer(timeout, logout)
        timer.start()
        try:
            eingabe = input(prompt)
            timer.cancel()
            return eingabe
        except BaseException as e:
            # Fängt alle Fehler und Abbrüche (Strg+C, EOF, Programmfehler) ab
            timer.cancel()
            print(
                f"\n\n\033[31mEingabe abgebrochen oder Fehler aufgetreten: {e}\033[0m")
            daten_speichern()
            os._exit(0)

    return timed_input_func


def daten_laden():
    """
    Lädt gespeicherte Budgetdaten aus der JSON-Datei.
    Falls keine Datei existiert, werden Standardwerte verwendet.
    Migriert alte ungeh ashte Passwörter zu gehashten Passwörtern.

    Modifiziert globale Variablen:
        budget_kategorien, budget_limits, finanzziele, benutzer_passwort
    """
    global budget_kategorien, budget_limits, finanzziele, benutzer_passwort
    if os.path.exists(daten_datei):
        with open(daten_datei, "r", encoding="utf-8") as f:
            daten = json.load(f)
            budget_kategorien = daten.get("budget_kategorien", {})
            budget_limits = daten.get("budget_limits", {})
            finanzziele = daten.get("finanzziele", {})
            benutzer_passwort = daten.get(
                "benutzer_passwort", {"passwort": hash_passwort("Test1234")})

            # Migration: Falls Passwort noch nicht gehashed ist (alte Version), hashe es jetzt
            stored_pass = benutzer_passwort.get("passwort")

            def _is_bcrypt_base64(s):
                try:
                    decoded = base64.b64decode(s.encode('utf-8'))
                    # bcrypt-Hashes beginnen mit b'$2a', b'$2b', b'$2y' ...
                    return decoded.startswith(b'$2')
                except Exception:
                    return False

            if stored_pass and not _is_bcrypt_base64(stored_pass):
                # Wahrscheinlich ein Klartext-Passwort oder altes Format -> jetzt mit bcrypt hashen
                benutzer_passwort["passwort"] = hash_passwort(stored_pass)
                daten_speichern()  # Speichere das gehashte Passwort sofort
    else:
        budget_kategorien = standard_kategorien.copy()
        budget_limits = {}
        finanzziele = {}
        # Hashe das Standard-Passwort beim ersten Start
        benutzer_passwort = {"passwort": hash_passwort("Test1234")}


def daten_speichern():
    """
    Speichert alle aktuellen Budgetdaten in eine JSON-Datei.
    Überschreibt die bestehende Datei mit den aktuellen Werten.
    """
    daten = {
        "budget_kategorien": budget_kategorien,
        "budget_limits": budget_limits,
        "finanzziele": finanzziele,
        "benutzer_passwort": benutzer_passwort
    }
    with open(daten_datei, "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)


def validiere_positiven_betrag(betrag, max_wert=None):
    """
    Validiert ob ein Betrag positiv (>=0) und optional unter einem Maximum liegt.

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
            f"\n\033[31mFehler: Der Betrag darf maximal {max_wert:.2f} CHF betragen!\033[0m")
        return False
    return True


def anzeigen_kategorien():
    """
    Zeigt alle verfügbaren Kategorien an und ermöglicht die Auswahl einer Kategorie
    zur detaillierten Kostenübersicht.
    """
    while True:
        print("\n\033[1mAktuelle Budget-Kategorien: \033[0m")
        for i, kategorie in enumerate(budget_kategorien.keys(), start=1):
            print(f"{i}. {kategorie}")
        print("")

        try:
            auswahl = int(timed_input(
                "\033[38;5;208mGebe die Nummer der gewünschten Kategorie ein, um sie anzuzeigen (0 = Zurück): \033[0m"))
            if auswahl == 0:
                return
            auswahl -= 1
            kategorien_liste = list(budget_kategorien.keys())
            if 0 <= auswahl < len(kategorien_liste):
                gewählte_kategorie = kategorien_liste[auswahl]
                print(
                    f"\n\033[1mKostenübersicht für \033[1m{gewählte_kategorie}\033[0m:")
                print(f"{'Datum':<15} {'Kostenart':<30} {'Betrag (CHF)':>12}")
                print("-" * 65)

                if not budget_kategorien[gewählte_kategorie]:
                    print("Keine Einträge vorhanden.")
                else:
                    for zeile in budget_kategorien[gewählte_kategorie]:
                        teile = zeile.split(" - ")
                        if len(teile) == 3:
                            datum = teile[0].strip()
                            kostenart = teile[1].strip()
                            betrag_str = teile[2].replace("CHF", "").strip()
                            try:
                                betrag = float(betrag_str)
                                print(
                                    f"{datum:<15} {kostenart:<35} {betrag:>15.2f}")
                            except ValueError:
                                print(
                                    f"{datum:<15} {kostenart:<35} {'Ungültiger Betrag':>15}")
                        else:
                            print(f"{'':15} {zeile:<35} {'Formatfehler':>15}")
            else:
                print("\n\033[31mAchtung: Ungültige Nummer!\033[0m")
        except ValueError:
            print("\033[31mBitte eine gültige Zahl eingeben. \033[0m")


def neue_kategorie_hinzufügen():
    """
    Fügt eine neue Budget-Kategorie hinzu.
    Prüft ob der Name gültig und noch nicht vorhanden ist, nur Buchstaben.
    """
    while True:
        neue_kategorie = timed_input(
            "\n\033[38;5;208mGib den Namen der neuen Kategorie ein (nur Buchstaben, 0 = Zurück): \033[0m").strip()
        if neue_kategorie == "0":
            return
        if not neue_kategorie:
            print(
                "\n\033[38;5;196mAchtung: Bitte gib einen gültigen Namen ein.\033[0m")
            continue
        elif not re.match(r'^[A-Za-zÄÖÜäöüß]+$', neue_kategorie):
            print(
                "\n\033[38;5;196mAchtung: Ungültiger Name! Nur Buchstaben sind erlaubt.\033[0m")
            continue
        elif neue_kategorie in budget_kategorien:
            print(
                f"\n\033[38;5;196mAchtung: Die Kategorie '{neue_kategorie}' existiert bereits.\033[0m")
            continue
        else:
            budget_kategorien[neue_kategorie] = []
            print(
                f"\n\033[38;5;46mKategorie '{neue_kategorie}' wurde erfolgreich hinzugefügt.\033[0m")
            break


def kategorie_bearbeiten():
    """
    Ermöglicht das Bearbeiten einer bestehenden Kategorie.
    Optionen: Namen ändern, Eintrag hinzufügen/löschen, Kategorie löschen
    """
    while True:
        kategorien_liste = list(budget_kategorien.keys())
        print("\n\033[1mAktuelle Budget-Kategorien: \033[0m")
        for i, kategorie in enumerate(kategorien_liste, start=1):
            print(f"{i}. {kategorie}")
        print("")

        try:
            index = int(
                timed_input("\033[38;5;208mWähle eine Kategorie, die du bearbeiten möchtest (0 = Zurück): \033[0m"))
            if index == 0:
                return
            index -= 1
        except ValueError:
            print("\n\033[31mAchtung: Bitte eine gültige Zahl eingeben.\033[0m")
            continue

        if not (0 <= index < len(kategorien_liste)):
            print("\n\033[31mAchtung: Ungültige Nummer.\033[0m")
            continue

        gewählte_kategorie = kategorien_liste[index]

        while True:
            print(
                f"\n\033[1mWas soll in der Kategorie '{gewählte_kategorie}' bearbeiten werden?\033[0m")
            print("1. Namen ändern")
            print("2. Eintrag hinzufügen")
            print("3. Eintrag löschen")
            print("")

            try:
                aktion = int(
                    timed_input("\033[38;5;208mGib die Nummer der gewünschten Aktion ein (0 = Zurück): \033[0m"))
                if aktion == 0:
                    break
            except ValueError:
                print("\n\033[31mBitte eine gültige Zahl eingeben.\033[0m")
                continue

            if aktion == 1:
                neuer_name = timed_input(
                    "Neuer Name für die Kategorie: ").strip()
                if not neuer_name:
                    print(
                        "\n\033[31mDer neue Name darf nicht leer sein.\033[0m")
                    continue
                elif not re.match(r'^[A-Za-zÄÖÜäöüß]+$', neuer_name):
                    print(
                        "\n\033[31mUngültiger Name! Nur Buchstaben sind erlaubt.\033[0m")
                    continue
                elif neuer_name in budget_kategorien:
                    print(
                        f"\n\033[31mDie Kategorie '{neuer_name}' existiert bereits.\033[0m")
                    continue
                else:
                    budget_kategorien[neuer_name] = budget_kategorien.pop(
                        gewählte_kategorie)
                    print(
                        f"\n\033[32mKategorie wurde erfolgreich von '{gewählte_kategorie}' zu '{neuer_name}' umbenannt.\033[0m")
                    break

            elif aktion == 2:
                while True:
                    datum = timed_input(
                        "\nDatum der Kosten (DD.MM.YYYY, z.B. 01.02.2025, 0 = Zurück): ").strip()

                    if datum == "0":
                        break

                    if not validiere_datum(datum):
                        print(
                            "\n\033[31mUngültiges Datum! Bitte verwende das Format DD.MM.YYYY (z.B. 01.02.2025)\033[0m")
                        continue

                    while True:
                        art = timed_input(
                            "\nArt der Kosten (nur Buchstaben, 0 = Zurück): ").strip()

                        if art == "0":
                            break

                        if not art:
                            print(
                                "\n\033[31mDie Kostenart darf nicht leer sein.\033[0m")
                            continue
                        elif not re.match(r'^[A-Za-zÄÖÜäöüß]+$', art):
                            print(
                                "\n\033[31mUngültige Kostenart! Nur Buchstaben sind erlaubt.\033[0m")
                            continue

                        try:
                            betrag = float(timed_input("Betrag in CHF: "))
                            if not validiere_positiven_betrag(betrag):
                                continue

                            aktuelle_summe = 0
                            for eintrag in budget_kategorien[gewählte_kategorie]:
                                teile = eintrag.split(" - ")
                                if len(teile) == 3:
                                    try:
                                        aktuelle_summe += float(
                                            teile[2].replace("CHF", "").strip())
                                    except ValueError:
                                        continue

                            neue_summe = aktuelle_summe + betrag
                            limit = budget_limits.get(gewählte_kategorie)

                            print(
                                f"\n\033[32mEintrag '{datum} - {art} - {betrag} CHF' wurde erfolgreich hinzugefügt.\033[0m")
                            if limit is not None and neue_summe > limit:
                                print(
                                    f"\033[31mAchtung: Budgetlimit von {limit:.2f} CHF für '{gewählte_kategorie}' überschritten!\033[0m")

                            budget_kategorien[gewählte_kategorie].append(
                                f"{datum} - {art} - {betrag} CHF")
                            break
                        except ValueError:
                            print(
                                "\n\033[31mAchtung: Ungültiger Betrag.\033[0m")

                    break

            elif aktion == 3:
                einträge = budget_kategorien[gewählte_kategorie]
                if not einträge:
                    print("\n\033[33mKeine Einträge vorhanden!\033[0m")
                    continue
                print("\n\033[1mAktuelle Einträge: \033[0m")
                for i, eintrag in enumerate(einträge, start=1):
                    print(f"{i}. {eintrag}")
                try:
                    zu_löschen = int(
                        timed_input("\n\033[38;5;208mNummer des Eintrags zum Löschen (0 = Zurück): \033[0m"))
                    if zu_löschen == 0:
                        continue
                    zu_löschen -= 1
                    gelöscht = einträge.pop(zu_löschen)
                    print(
                        f"\n\033[32mEintrag '{gelöscht}' wurde erfolgreich gelöscht.\033[0m")
                except (ValueError, IndexError):
                    print("\n\033[31mUngültige Auswahl.\033[0m")


def kategorie_löschen():
    """
    Löscht eine ausgewählte Kategorie komplett aus dem System.
    """
    while True:
        kategorien_liste = list(budget_kategorien.keys())
        print("\n\033[1mAktuelle Budget-Kategorien: \033[0m")
        for i, kategorie in enumerate(kategorien_liste, start=1):
            print(f"{i}. {kategorie}")
        print("")
        try:
            index = int(timed_input(
                "\n\033[38;5;208mWelche Kategorie möchtest du löschen? (0 = Zurück): \033[0m"))
            if index == 0:
                return
            index -= 1
            if 0 <= index < len(kategorien_liste):
                entfernte = kategorien_liste[index]
                budget_kategorien.pop(entfernte)
                print(
                    f"\n\033[32mKategorie '{entfernte}' wurde erfolgreich gelöscht. \033[0m")
            else:
                print("\n\033[31mAchtung: Ungültige Nummer. \033[0m")
        except ValueError:
            print("\n\033[31mAchtung:Bitte eine gültige Zahl eingeben. \033[0m")


def finanzkontrolle():
    """
    Verwaltet Budgetlimits und Finanzziele für einzelne Kategorien.
    Ermöglicht Anzeigen, Setzen, Ändern und Entfernen von Limits und Zielen.
    """
    global budget_limits, finanzziele
    kategorien_liste = list(budget_kategorien.keys())
    print("\n\033[1mFinanzkontrolle pro Kategorie\033[0m")
    for i, kategorie in enumerate(kategorien_liste, start=1):
        print(f"{i}. {kategorie}")
    print("")

    try:
        index = int(timed_input(
            "\033[38;5;208mWähle eine Kategorie für die Finanzkontrolle (0 = Hauptmenü): \033[0m"))
        if index == 0:
            return
        index -= 1
        if not (0 <= index < len(kategorien_liste)):
            print("\n\033[31mUngültige Auswahl.\033[0m")
            return
    except ValueError:
        print("\n\033[31mBitte eine gültige Zahl eingeben.\033[0m")
        return

    gewählte_kategorie = kategorien_liste[index]

    while True:
        print(
            f"\n\033[1mWas möchtest du für '{gewählte_kategorie}' bearbeiten?\033[0m")
        print("1. Budgetlimite")
        print("2. Finanzziel")

        hauptwahl = timed_input(
            "\n\033[38;5;208mWähle eine Option (0 = Hauptmenü, 1–2): \033[0m")

        if hauptwahl == "0":
            return

        if hauptwahl == "1":
            while True:
                print(
                    f"\n\033[1mBudgetlimite für '{gewählte_kategorie}'\033[0m")
                print("1. Anzeigen")
                print("2. Setzen")
                print("3. Ändern")
                print("4. Entfernen")
                auswahl = timed_input(
                    "\n\033[38;5;208mWähle eine Option (0 = Zurück, 1–4): \033[0m")

                if auswahl == "0":
                    break

                if auswahl == "1":
                    limit = budget_limits.get(gewählte_kategorie)
                    if limit is not None:
                        print(
                            f"\n\033[1mAktuelles Budgetlimit:\033[0m {limit:.2f} CHF")
                    else:
                        print("\n\033[33mKein Budgetlimit gesetzt.\033[0m")

                elif auswahl == "2":
                    try:
                        limit = float(timed_input(
                            f"Neues Budgetlimit in CHF (max. {MAX_BUDGET_LIMIT:.2f} CHF): "))
                        if validiere_positiven_betrag(limit, MAX_BUDGET_LIMIT):
                            budget_limits[gewählte_kategorie] = limit
                            daten_speichern()
                            print(
                                f"\n\033[32mBudgetlimite gesetzt: {limit:.2f} CHF\033[0m")
                    except ValueError:
                        print("\n\033[31mUngültiger Betrag.\033[0m")

                elif auswahl == "3":
                    if gewählte_kategorie not in budget_limits:
                        print("\n\033[33mKein Limit vorhanden.\033[0m")
                    else:
                        try:
                            neues_limit = float(
                                timed_input(f"Neues Limit in CHF (max. {MAX_BUDGET_LIMIT:.2f} CHF): "))
                            if validiere_positiven_betrag(neues_limit, MAX_BUDGET_LIMIT):
                                budget_limits[gewählte_kategorie] = neues_limit
                                daten_speichern()
                                print(
                                    f"\n\033[32mLimit geändert auf {neues_limit:.2f} CHF\033[0m")
                        except ValueError:
                            print("\n\033[31mUngültiger Betrag.\033[0m")
                elif auswahl == "4":
                    if gewählte_kategorie in budget_limits:
                        del budget_limits[gewählte_kategorie]
                        daten_speichern()
                        print(f"\n\033[32mLimit entfernt.\033[0m")
                    else:
                        print("\n\033[33mKein Limit vorhanden.\033[0m")

        elif hauptwahl == "2":
            while True:
                print(f"\n\033[1mFinanzziel für '{gewählte_kategorie}'\033[0m")
                print("1. Anzeigen")
                print("2. Setzen")
                print("3. Ändern")
                print("4. Entfernen")
                auswahl = timed_input(
                    "\n\033[38;5;208mWähle eine Option (0 = Zurück, 1–4): \033[0m")

                if auswahl == "0":
                    break

                if auswahl == "1":
                    ziel_info = finanzziele.get(gewählte_kategorie)
                    if ziel_info:
                        print(f"\n\033[1mZiel:\033[0m {ziel_info['ziel']} CHF")
                        print(f"Meldung: {ziel_info['meldung']}")
                    else:
                        print("\n\033[33mKein Ziel gesetzt.\033[0m")

                elif auswahl == "2":
                    try:
                        ziel = float(timed_input("Zielbetrag in CHF: "))
                        if validiere_positiven_betrag(ziel):
                            meldung = timed_input(
                                "Meldung bei Zielerreichung: ").strip()
                            finanzziele[gewählte_kategorie] = {
                                "ziel": ziel, "meldung": meldung}
                            daten_speichern()
                            print(
                                f"\n\033[32mZiel {ziel} CHF gespeichert.\033[0m")
                    except ValueError:
                        print("\n\033[31mUngültiger Betrag.\033[0m")

                elif auswahl == "3":
                    if gewählte_kategorie not in finanzziele:
                        print("\n\033[33mKein Ziel vorhanden.\033[0m")
                    else:
                        try:
                            neues_ziel = float(
                                timed_input("Neues Ziel in CHF: "))
                            if validiere_positiven_betrag(neues_ziel):
                                neue_meldung = timed_input(
                                    "Neue Meldung: ").strip()
                                finanzziele[gewählte_kategorie] = {
                                    "ziel": neues_ziel, "meldung": neue_meldung}
                                daten_speichern()
                                print(f"\n\033[32mZiel aktualisiert.\033[0m")
                        except ValueError:
                            print("\n\033[31mUngültiger Betrag.\033[0m")

                elif auswahl == "4":
                    if gewählte_kategorie in finanzziele:
                        del finanzziele[gewählte_kategorie]
                        daten_speichern()
                        print(f"\n\033[32mZiel entfernt.\033[0m")
                    else:
                        print("\n\033[33mKein Ziel vorhanden.\033[0m")


def passwort_login():
    """
    Führt den Login-Prozess durch.
    Nach 3 fehlgeschlagenen Versuchen wird das Programm beendet.
    """
    hashed_passwort = benutzer_passwort.get(
        "passwort", hash_passwort("Test1234"))
    anmeldeversuche = 0
    passwort_input = input(
        "\n\033[38;5;208mBitte gebe dein Passwort ein: \033[0m")

    while not verifiziere_passwort(passwort_input, hashed_passwort):
        anmeldeversuche += 1
        if anmeldeversuche == 3:
            print("\n\033[31mZu viele fehlerhafte Anmeldungen!\033[0m")
            os._exit(1)
        else:
            passwort_input = input(
                "\n\033[31mFehlerhaftes Passwort! Versuche es bitte nochmals: \033[0m")

    print("\n\033[92mErfolgreich eingeloggt!\033[0m\n")


def passwort_ändern():
    """
    Ermöglicht das Ändern des Passworts.
    Validiert das neue Passwort nach festgelegten Sicherheitskriterien.
    """
    global benutzer_passwort
    hashed_passwort = benutzer_passwort.get(
        "passwort", hash_passwort("Test1234"))

    änderung_input = timed_input(
        "\n\033[38;5;208mBitte geben Sie Ihr aktuelles Passwort ein: \033[0m")
    while not verifiziere_passwort(änderung_input, hashed_passwort):
        print("\n\033[31mUngültiges Passwort!\033[0m")
        änderung_input = timed_input("Versuche es bitte erneut: ")

    print("\n\033[1mPasswort neu festlegen\033[0m")
    print("Das Passwort muss enthalten: ")
    print("\033[3m- Mindestens 8 Zeichen \033[0m")
    print("\033[3m- Gross- und Kleinschreibung \033[0m")
    print("\033[3m- Mindestens eine Zahl \033[0m")
    print("\033[3m- Mindestens ein Sonderzeichen: $, @, #, %, !, ?, &, * \033[0m")

    SpecialSym = ['$', '@', '#', '%', '!', '?', '&', '*']

    while True:
        val = True
        passwort_neu1 = timed_input(
            "\n\033[38;5;208mGeben Sie Ihr neues Passwort ein: \033[0m")

        if len(passwort_neu1) < 8:
            print(
                '\n\033[31m -Passwort muss mindestens 8 Zeichen lang sein\033[0m')
            val = False
        if len(passwort_neu1) > 20:
            print('\033[31m -Passwort darf maximal 20 Zeichen lang sein\033[0m')
            val = False
        if not any(char.isdigit() for char in passwort_neu1):
            print('\033[31m -Passwort muss mindestens eine Zahl enthalten\033[0m')
            val = False
        if not any(char.isupper() for char in passwort_neu1):
            print(
                '\033[31m -Passwort muss mindestens einen Grossbuchstaben enthalten\033[0m')
            val = False
        if not any(char.islower() for char in passwort_neu1):
            print(
                '\033[31m -Passwort muss mindestens einen Kleinbuchstaben enthalten\033[0m')
            val = False
        if not any(char in SpecialSym for char in passwort_neu1):
            print(
                '\033[31m -Passwort muss mindestens ein Sonderzeichen enthalten ($,@,#,%,!,?,&,*)\033[0m')
            val = False
            continue

        if val:
            passwort_neu2 = timed_input(
                "\033[38;5;208mGeben Sie Ihr neues Passwort erneut ein: \033[0m")
            if passwort_neu1 == passwort_neu2:
                # Hashe das neue Passwort vor dem Speichern
                benutzer_passwort["passwort"] = hash_passwort(passwort_neu1)
                daten_speichern()
                print("\n\033[32mPasswort erfolgreich geändert!\033[0m")
                break
            else:
                print(
                    "\n\033[31mDie Passwörter stimmen nicht überein!\033[0m\n")
        else:
            print("\n\033[31mBitte versuchen Sie es erneut.\033[0m\n")


# -----------------------------------------------------------
#  STATISTIK – Datenaufbereitung für spätere Matplotlib-Darstellung
# -----------------------------------------------------------

def monats_summen_pro_kategorie_mit_limits(budget_kategorien, budget_limits):
    """
    Berechnet pro Kategorie die Monatssummen und ordnet Farbcodes
    anhand gesetzter Budgetlimiten zu.

    Rückgabeformat (Dict):

        {
           "Lebensmittel": {
               "monate": [...],   # Liste von Strings "YYYY-MM"
               "werte":  [...],   # Liste von floats
               "farben": [...],   # "blue" / "green" / "red"
               "limit":  limit_oder_None
           },
           ...
        }
    """
    ergebnis = {}

    for kategorie, eintraege in budget_kategorien.items():
        monats_summen = defaultdict(float)

        for e in eintraege:
            teile = e.split(" - ")
            if len(teile) != 3:
                continue

            datum_str = teile[0].strip()
            betrag_str = teile[2].replace("CHF", "").strip()

            try:
                datum = datetime.strptime(datum_str, "%d.%m.%Y")
                monat = datum.strftime("%Y-%m")
                betrag = float(betrag_str)
                monats_summen[monat] += betrag
            except Exception:
                continue

        monate = sorted(monats_summen.keys())
        werte = [monats_summen[m] for m in monate]

        limit = budget_limits.get(kategorie)
        farben = []

        for betrag in werte:
            if limit is None:
                farben.append("blue")      # kein Limit gesetzt
            elif betrag <= limit:
                farben.append("green")     # innerhalb Limit
            else:
                farben.append("red")       # über Limit

        ergebnis[kategorie] = {
            "monate": monate,
            "werte": werte,
            "farben": farben,
            "limit": limit
        }

    return ergebnis


def finanzziel_statistik_daten(budget_kategorien, finanzziele):
    """
    Bereitet Statistik-Daten für Finanzziele pro Kategorie vor.

    Es werden nur Kategorien berücksichtigt, für die ein Finanzziel gesetzt wurde
    UND die noch in budget_kategorien existieren.

    Rückgabeformat (Dict):

        {
            "Lebensmittel": {
                "ziel": zielbetrag_float,
                "ausgaben_gesamt": gesamtausgaben_float,
                "differenz": ziel_minus_ausgaben,
                "erreicht": True/False,
                "farbe": "green" oder "red"
            },
            ...
        }
    """
    ergebnis = {}

    for kategorie, ziel_info in finanzziele.items():
        if kategorie not in budget_kategorien:
            continue

        ziel = ziel_info.get("ziel")
        if ziel is None:
            continue

        gesamt_ausgaben = 0.0
        for eintrag in budget_kategorien[kategorie]:
            teile = eintrag.split(" - ")
            if len(teile) != 3:
                continue

            betrag_str = teile[2].replace("CHF", "").strip()
            try:
                betrag = float(betrag_str)
                gesamt_ausgaben += betrag
            except ValueError:
                continue

        differenz = ziel - gesamt_ausgaben
        erreicht = gesamt_ausgaben >= ziel
        farbe = "green" if erreicht else "red"

        ergebnis[kategorie] = {
            "ziel": ziel,
            "ausgaben_gesamt": gesamt_ausgaben,
            "differenz": differenz,
            "erreicht": erreicht,
            "farbe": farbe
        }

    return ergebnis


def plot_budget_status_counts(kategorien_daten):
    """
    Zeichnet ein gruppiertes Balkendiagramm mit der Anzahl Kategorien in drei Status:
      - Innerhalb Limit
      - Limit überschritten
      - Kein Limit gesetzt

    Die Bestimmung erfolgt pro Kategorie anhand des letzten vorhandenen Monatswertes
    (falls vorhanden). Ziel ist eine kompakte Übersicht, wie viele Kategorien aktuell
    ihr Limit überschreiten bzw. innerhalb sind.
    """
    # Vergleicht Status (Innerhalb/Überschritten/Kein Limit) für Vormonat und aktuellen Monat
    within_prev = over_prev = no_limit_prev = 0
    within_curr = over_curr = no_limit_curr = 0

    for kategorie, daten in kategorien_daten.items():
        werte = daten.get("werte", [])
        limit = daten.get("limit")

        # Werte für aktuellen Monat und Vormonat (falls vorhanden)
        letzter_wert = werte[-1] if len(werte) >= 1 else 0.0
        vorheriger_wert = werte[-2] if len(werte) >= 2 else 0.0

        def _status(val, lim):
            if lim is None:
                return 'no_limit'
            elif val > lim:
                return 'over'
            else:
                return 'within'

        s_prev = _status(vorheriger_wert, limit)
        s_curr = _status(letzter_wert, limit)

        if s_prev == 'within':
            within_prev += 1
        elif s_prev == 'over':
            over_prev += 1
        else:
            no_limit_prev += 1

        if s_curr == 'within':
            within_curr += 1
        elif s_curr == 'over':
            over_curr += 1
        else:
            no_limit_curr += 1

    labels = ["Innerhalb Limit", "Limit überschritten", "Kein Limit gesetzt"]
    prev_counts = [within_prev, over_prev, no_limit_prev]
    curr_counts = [within_curr, over_curr, no_limit_curr]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5))
    bars_prev = ax.bar(x - width/2, prev_counts, width, label='Vormonat',
                       color=['lightgreen', 'lightcoral', 'lightblue'], edgecolor='black', alpha=0.7)
    bars_curr = ax.bar(x + width/2, curr_counts, width,
                       color=['lightgreen', 'lightcoral', 'lightblue'], edgecolor='black', alpha=0.4)

    ax.set_ylabel("Anzahl Kategorien", fontsize=13)
    ax.set_title(
        "Budget-Status pro Kategorie: Vergleich Vormonat vs. aktuell", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    # Formatiere Y-Achse mit Tausender-Trennzeichen
    from matplotlib.ticker import FuncFormatter

    def format_thousands(x, p):
        return f"{int(x):,}".replace(",", "'")
    ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))
    legend_elements = [
        Line2D([0], [0], color='w', marker='s', markerfacecolor='lightgreen',
               markersize=10, label='Innerhalb Limit (Vormonat)', alpha=0.7),
        Line2D([0], [0], color='w', marker='s', markerfacecolor='lightgreen',
               markersize=10, label='Innerhalb Limit (Aktuell)', alpha=0.4),
        Line2D([0], [0], color='w', marker='s', markerfacecolor='lightcoral',
               markersize=10, label='Limit überschritten (Vormonat)', alpha=0.7),
        Line2D([0], [0], color='w', marker='s', markerfacecolor='lightcoral',
               markersize=10, label='Limit überschritten (Aktuell)', alpha=0.4),
        Line2D([0], [0], color='w', marker='s', markerfacecolor='lightblue',
               markersize=10, label='Kein Limit (Vormonat)', alpha=0.7),
        Line2D([0], [0], color='w', marker='s', markerfacecolor='lightblue',
               markersize=10, label='Kein Limit (Aktuell)', alpha=0.4),
        Line2D([0], [0], color='w', marker='s',
               markerfacecolor='lightgray', markersize=8, label='Vormonat'),
        # 'Aktuell' legend entry removed per user request
    ]
    ax.legend(handles=legend_elements, loc='upper center',
              bbox_to_anchor=(0.5, -0.15), ncol=20)

    # Werte über den Balken annotieren
    for bar in list(bars_prev) + list(bars_curr):
        h = bar.get_height()
        formatted_h = f"{int(h):,}".replace(",", "'")
        ax.annotate(formatted_h, xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=11)

    plt.tight_layout()
    plt.savefig('budget_status_diagramm.png', dpi=100, bbox_inches='tight')
    print(
        "\n\033[32mDiagramm gespeichert als 'budget_status_diagramm.png'\033[0m")
    plt.close()


def plot_monats_summen_pro_kategorie(kategorien_daten, budget_limits=None):
    """
    Zeichnet monatliche Summen pro Kategorie mit Farbcodierung nach Budget-Status.

    Farbcodes:
      - Grün: Ausgaben innerhalb des Limits
      - Rot: Limit überschritten
      - Blau: Kein Limit gesetzt

    Args:
        kategorien_daten (dict): Daten aus monats_summen_pro_kategorie_mit_limits()
        budget_limits (dict): Optional - Budget-Limits pro Kategorie
    """
    kategorien = list(kategorien_daten.keys())

    if not kategorien:
        print("Keine Kategorien-Daten zum Plotten.")
        return

    # Für jede Kategorie jeweils Vormonats- und aktuellen Monatswert extrahieren
    prev_values = []
    curr_values = []
    farben = []  # Farbe für aktuellen Monat je Kategorie

    for kategorie in kategorien:
        daten = kategorien_daten[kategorie]
        werte = daten.get("werte", [])

        curr = werte[-1] if len(werte) >= 1 else 0.0
        prev = werte[-2] if len(werte) >= 2 else 0.0

        prev_values.append(prev)
        curr_values.append(curr)

        limit = daten.get("limit")
        if limit is None:
            farben.append("blue")
        elif curr > limit:
            farben.append("red")
        else:
            farben.append("green")

    # Erstelle gruppiertes Balkendiagramm: Vormonat vs. Aktuell
    x = np.arange(len(kategorien))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    bars_prev = ax.bar(x - width/2, prev_values, width,
                       label='Vormonat', color='lightgray', edgecolor='black', alpha=0.6)
    bars_curr = ax.bar(x + width/2, curr_values, width,
                       color=farben, edgecolor='black', alpha=0.7)

    # Budgetlimits als horizontale Linien nur für relevante Kategorien einzeichnen
    if budget_limits:
        for i, kategorie in enumerate(kategorien):
            if kategorie in budget_limits:
                limit = budget_limits[kategorie]
                # Zeichne die Linie nur in dem Bereich dieser Kategorie
                ax.plot([i - width - 0.1, i + width + 0.1], [limit, limit],
                        color='#D2691E', linestyle='--', alpha=0.8, linewidth=1.5)
                # Füge die Beschriftung des Budgetlimits oberhalb der Linie hinzu
                formatted_limit = f"{limit:,.2f}".replace(",", "'")
                ax.text(i - 0.25, limit, formatted_limit, fontsize=9,
                        color='#D2691E', va='bottom', ha='center', fontweight='bold')

    # Werte über den Balken annotieren und Delta (Aktuell - Vormonat)
    for i, bar in enumerate(bars_curr):
        h = bar.get_height()
        formatted_h = f"{h:,.2f}".replace(",", "'")
        ax.annotate(formatted_h, xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=11)

        delta = curr_values[i] - prev_values[i]
        delta_text = f"{delta:+.2f}"
        # weniger Ausgabe = positiv (grün)
        delta_color = 'green' if delta <= 0 else 'red'
        ax.annotate(delta_text, xy=(bar.get_x() + bar.get_width() / 2, h + max(0.5, 0.02 * h)),
                    xytext=(0, 18), textcoords="offset points", ha="center", fontsize=11, color=delta_color)

    for bar in bars_prev:
        h = bar.get_height()
        formatted_h = f"{h:,.2f}".replace(",", "'")
        ax.annotate(formatted_h, xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=10)

    ax.set_ylabel('Betrag (CHF)', fontsize=13)
    ax.set_title(
        'Monatliche Summen pro Kategorie: Vormonat vs. Aktuell', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(kategorien, rotation=0, ha='center', fontsize=11)

    # Erhöhe die y-Achsen-Grenze, damit Delta-Beschriftungen nicht abgeschnitten werden
    max_value = max(curr_values + prev_values)
    ax.set_ylim(0, max_value * 1.3)
    # Formatiere Y-Achse mit Tausender-Trennzeichen
    from matplotlib.ticker import FuncFormatter

    def format_thousands(x, p):
        return f"{int(x):,}".replace(",", "'")
    ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))
    legend_elements = [
        Line2D([0], [0], color='w', marker='s',
               markerfacecolor='lightgray', markersize=10, label='Vormonat', alpha=0.6),
        # 'Aktuell' legend entry removed per user request
        Patch(facecolor='green', edgecolor='black',
              label='Innerhalb Limit', alpha=0.7),
        Patch(facecolor='red', edgecolor='black',
              label='Limit überschritten', alpha=0.7),
        Patch(facecolor='blue', edgecolor='black',
              label='Kein Limit gesetzt', alpha=0.7),
    ]
    # Falls Budgetlimits eingezeichnet werden, ergänze das in der Legende
    if budget_limits:
        legend_elements.append(
            Line2D([0], [0], color='orange', linestyle='--', label='Budgetlimit'))

    ax.legend(handles=legend_elements, loc='upper center',
              bbox_to_anchor=(0.5, -0.15), ncol=20)

    plt.tight_layout()
    plt.savefig('monats_summen_diagramm.png', dpi=100, bbox_inches='tight')
    print(
        "\n\033[32mDiagramm gespeichert als 'monats_summen_diagramm.png'\033[0m")
    plt.close()


def plot_finanzziele(finanzziel_daten):
    """
    Zeichnet ein Balkendiagramm für Finanzziele mit Vergleich zwischen Ziel und aktuellen Ausgaben.

    Farbcodes:
      - Grün: Ziel erreicht (Ausgaben >= Ziel)
      - Rot: Ziel nicht erreicht (Ausgaben < Ziel)

    Args:
        finanzziel_daten (dict): Daten aus finanzziel_statistik_daten()
    """
    kategorien = list(finanzziel_daten.keys())

    if not kategorien:
        print("Keine Finanzziel-Daten zum Plotten.")
        return

    # Extrahiere Daten für Ziele und aktuelle Ausgaben
    ziele = []
    ausgaben = []
    farben = []

    for kategorie in kategorien:
        daten = finanzziel_daten[kategorie]
        ziele.append(daten.get("ziel", 0.0))
        ausgaben.append(daten.get("ausgaben_gesamt", 0.0))

        # Farbcode: Grün wenn Ziel erreicht, Rot wenn nicht
        erreicht = daten.get("erreicht", False)
        farben.append("green" if erreicht else "red")

    # X-Positionen für die Balken
    x = np.arange(len(kategorien))
    width = 0.35

    # Erstelle das Balkendiagramm
    fig, ax = plt.subplots(figsize=(12, 6))

    # Zwei Balkengruppen: Ziel und aktuelle Ausgaben
    bars1 = ax.bar(x - width/2, ziele, width, label='Finanzziel',
                   color='lightblue', edgecolor='black', linewidth=1, alpha=0.6)
    bars2 = ax.bar(x + width/2, ausgaben, width, label='Aktuelle Ausgaben',
                   color=farben, edgecolor='black', linewidth=1, alpha=0.7)

    # Werte über den Balken annotieren
    for bar in bars1:
        h = bar.get_height()
        formatted_h = f"{int(h):,}".replace(",", "'")
        ax.annotate(formatted_h, xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=11)

    for bar in bars2:
        h = bar.get_height()
        formatted_h = f"{int(h):,}".replace(",", "'")
        ax.annotate(formatted_h, xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=11)

    ax.set_ylabel('Betrag (CHF)', fontsize=13)
    ax.set_title('Finanzziele vs. Aktuelle Ausgaben', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(kategorien, rotation=0, ha='center', fontsize=11)

    # Erhöhe die y-Achsen-Grenze für bessere Sichtbarkeit
    max_ziele_ausgaben = max(ziele + ausgaben)
    ax.set_ylim(0, max_ziele_ausgaben * 1.3)
    # Formatiere Y-Achse mit Tausender-Trennzeichen
    from matplotlib.ticker import FuncFormatter

    def format_thousands(x, p):
        return f"{int(x):,}".replace(",", "'")
    ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))

    # Legende
    legend_elements = [
        plt.Line2D([0], [0], color='w', marker='s',
                   markerfacecolor='lightblue', markersize=10, label='Finanzziel'),
        Patch(facecolor='green', edgecolor='black', label='Ziel erreicht'),
        Patch(facecolor='red', edgecolor='black', label='Ziel nicht erreicht'),
    ]
    ax.legend(handles=legend_elements, loc='upper center',
              bbox_to_anchor=(0.5, -0.15), ncol=20)

    ax.set_ylabel('Betrag (CHF)', fontsize=13)
    ax.set_title('Finanzziele vs. Aktuelle Ausgaben', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(kategorien, rotation=0, ha='center', fontsize=11)

    plt.tight_layout()
    plt.savefig('finanzziele_diagramm.png', dpi=100, bbox_inches='tight')
    print("\n\033[32mDiagramm gespeichert als 'finanzziele_diagramm.png'\033[0m")
    plt.close()


def statistik_menü():
    """
    Zeigt ein Untermenü für Statistik-Funktionen an.

    Option 1: Statistik nach Kategorie (Budgetlimiten)
    Option 2: Statistik Finanzziele

    Beide Optionen bereiten nur die Daten vor und lassen einen
    Platzhalter für die spätere Matplotlib-Darstellung.
    """
    while True:
        print("\n\033[1mStatistik-Menü\033[0m")
        print("1. Statistik nach Kategorie (Budgetlimiten)")
        print("2. Statistik Finanzziele")

        auswahl = timed_input(
            "\n\033[38;5;208mGib die Nummer der gewünschten Statistik-Funktion ein (0 = Zurück): \033[0m"
        )

        if auswahl == "0":
            return

        elif auswahl == "1":
            kategorien_daten = monats_summen_pro_kategorie_mit_limits(
                budget_kategorien, budget_limits)

            kategorien = list(kategorien_daten.keys())
            if not kategorien:
                print("\n\033[33mKeine Kategorien-Daten vorhanden.\033[0m")
                _ = timed_input(
                    "\n\033[38;5;208mDrücke Enter, um zurückzukehren.\033[0m")
                continue

            # Aufruf der Plot-Funktion
            plot_monats_summen_pro_kategorie(kategorien_daten, budget_limits)

            _ = timed_input(
                "\n\033[38;5;208mStatistik-Daten für Budgetlimiten wurden vorbereitet. Drücke Enter, um zurückzukehren.\033[0m"
            )

        elif auswahl == "2":
            finanzziel_daten = finanzziel_statistik_daten(
                budget_kategorien, finanzziele)

            if not finanzziel_daten:
                print("\n\033[33mKeine Finanzziele gesetzt.\033[0m")
                _ = timed_input(
                    "\n\033[38;5;208mDrücke Enter, um zurückzukehren.\033[0m")
                continue

            # Aufruf der Plot-Funktion für Finanzziele
            plot_finanzziele(finanzziel_daten)

            _ = timed_input(
                "\n\033[38;5;208mStatistik-Daten für Finanzziele wurden vorbereitet. Drücke Enter, um zurückzukehren.\033[0m"
            )

        else:
            print("\n\033[31mAchtung: Ungültige Nummer!\033[0m")


def hauptmenü():
    """
    Zeigt das Hauptmenü an und verarbeitet Benutzerauswahlen.
    Bietet Zugang zu allen Hauptfunktionen des Budget-Trackers.
    """
    global timed_input
    timed_input = inaktivität_wrapper(120)

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

        auswahl = timed_input(
            "\n\033[38;5;208mWähle eine Option (1-8): \033[0m")

        if auswahl == "1":
            anzeigen_kategorien()
        elif auswahl == "2":
            neue_kategorie_hinzufügen()
        elif auswahl == "3":
            kategorie_bearbeiten()
        elif auswahl == "4":
            kategorie_löschen()
        elif auswahl == "5":
            finanzkontrolle()
        elif auswahl == "6":
            passwort_ändern()
        elif auswahl == "7":
            statistik_menü()
        elif auswahl == "8":
            print("\n\033[32mProgramm beendet.\033[0m")
            break
        else:
            print(
                "\n\033[31mUngültige Eingabe: Bitte wähle eine Zahl zwischen 1 und 8.\033[0m")


def main():
    """
    Hauptfunktion des Programms.
    Lädt Daten, führt Login durch, startet Hauptmenü und speichert beim Beenden.
    """
    daten_laden()
    passwort_login()
    hauptmenü()
    daten_speichern()


if __name__ == "__main__":
    main()
