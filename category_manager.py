"""
Kategorie-Verwaltungs-Modul für Budget-Tracker
Enthält alle Funktionen zur Verwaltung von Budget-Kategorien
"""

import re
from utils import validiere_datum, validiere_positiven_betrag


def anzeigen_kategorien(budget_kategorien, timed_input):
    """
    Zeigt alle verfügbaren Kategorien an und
    ermöglicht die Auswahl einer Kategorie
    zur detaillierten Kostenübersicht.

    Args:
        budget_kategorien (dict): Dictionary mit allen Kategorien
        timed_input (callable): Input-Funktion mit Timeout
    """
    while True:
        print("\n\033[1mAktuelle Budget-Kategorien: \033[0m")
        for i, kategorie in enumerate(budget_kategorien.keys(), start=1):
            print(f"{i}. {kategorie}")
        print("")

        try:
            auswahl = int(timed_input(
                "\033[34mGebe die Nummer der gewünschten Kategorie ein, "
                "um sie anzuzeigen (0 = Zurück): \033[0m"))
            if auswahl == 0:
                return
            auswahl -= 1
            kategorien_liste = list(budget_kategorien.keys())
            if 0 <= auswahl < len(kategorien_liste):
                gewählte_kategorie = kategorien_liste[auswahl]
                print(f"\n\033[1mKostenübersicht für "
                      f"\033[1m{gewählte_kategorie}\033[0m:")
                print(f"{'Datum':<15} {'Kostenart':<30} "
                      f"{'        Betrag (CHF)':>12}")
                print("-" * 67)

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
                                print(f"{datum:<15} {kostenart:<35} "
                                      f"{betrag:>15.2f}")
                            except ValueError:
                                print(f"{datum:<15} {kostenart:<35} "
                                      f"{'Ungültiger Betrag':>15}")
                        else:
                            print(f"{'':15} {zeile:<35} {'Formatfehler':>15}")
            else:
                print("\n\033[31mAchtung: Ungültige Nummer!\033[0m")
        except ValueError:
            print("\033[31mBitte eine gültige Zahl eingeben. \033[0m")


def neue_kategorie_hinzufügen(budget_kategorien, timed_input):
    """
    Fügt eine neue Budget-Kategorie hinzu.

    Args:
        budget_kategorien (dict): Dictionary mit
        allen Kategorien timed_input (callable):
        Input-Funktion mit Timeout

    Returns:
        dict: Aktualisiertes budget_kategorien Dictionary
    """
    while True:
        neue_kategorie = timed_input(
            "\n\033[34mGib den Namen der neuen Kategorie ein "
            "(nur Buchstaben, 0 = Zurück):\033[0m").strip()
        if neue_kategorie == "0":
            return budget_kategorien
        if not neue_kategorie:
            print("\n\033[31mAchtung: Bitte gib einen gültigen Namen ein."
                  "\033[0m")
            continue
        elif not re.match(r'^[A-Za-zÄÖÜäöüß]+$', neue_kategorie):
            print("\n\033[31mAchtung: "
                  "Ungültiger Name! Nur Buchstaben sind erlaubt.\033[0m")
            continue
        elif neue_kategorie in budget_kategorien:
            print(f"\n\033[31mAchtung: Die Kategorie "
                  f"'{neue_kategorie}' existiert bereits.\033[0m")
            continue
        else:
            budget_kategorien[neue_kategorie] = []
            print(f"\n\033[32mKategorie '{neue_kategorie}' "
                  f"wurde erfolgreich hinzugefügt.\033[0m")
            break
    return budget_kategorien


def kategorie_bearbeiten(budget_kategorien, budget_limits, timed_input):
    """
    Ermöglicht das Bearbeiten einer bestehenden Kategorie.

    Args:
        budget_kategorien (dict): Dictionary mit allen Kategorien
        budget_limits (dict): Dictionary mit Budget-Limits
        timed_input (callable): Input-Funktion mit Timeout

    Returns:
        dict: Aktualisiertes budget_kategorien Dictionary
    """
    while True:
        kategorien_liste = list(budget_kategorien.keys())
        print("\n\033[1mAktuelle Budget-Kategorien:\033[0m")
        for i, kategorie in enumerate(kategorien_liste, start=1):
            print(f"{i}. {kategorie}")
        print("")

        try:
            index = int(timed_input(
                "\033[34mWähle eine Kategorie, die du bearbeiten möchtest "
                "(0 = Zurück):\033[0m"))
            if index == 0:
                return budget_kategorien
            index -= 1
        except ValueError:
            print("\n\033[31mAchtung: Bitte eine gültige Zahl eingeben."
                  "\033[0m")
            continue

        if not (0 <= index < len(kategorien_liste)):
            print("\n\033[31mAchtung: Ungültige Nummer.\033[0m")
            continue

        gewählte_kategorie = kategorien_liste[index]

        while True:
            print(f"\n\033[1mWas soll in der Kategorie '{gewählte_kategorie}' "
                  f"bearbeiten werden?\033[0m")
            print("1. Namen ändern")
            print("2. Eintrag hinzufügen")
            print("3. Eintrag löschen")
            print("")

            try:
                aktion = int(timed_input(
                    "\033[34mGib die Nummer der gewünschten Aktion ein "
                    "(0 = Zurück):\033[0m"))
                if aktion == 0:
                    break
            except ValueError:
                print("\n\033[31mBitte eine gültige Zahl eingeben.\033[0m")
                continue
            # Neuer Name
            if aktion == 1:
                neuer_name = timed_input(
                    "Neuer Name für die Kategorie: ").strip()
                if not neuer_name:
                    print("\n\033[31mDer neue Name darf nicht leer sein."
                          "\033[0m")
                    continue
                elif not re.match(r'^[A-Za-zÄÖÜäöüß]+$', neuer_name):
                    print("\n\033[31mUngültiger Name! "
                          "Nur Buchstaben sind erlaubt.\033[0m")
                    continue
                elif neuer_name in budget_kategorien:
                    print(f"\n\033[31mDie Kategorie '{neuer_name}' "
                          f"existiert bereits.\033[0m")
                    continue
                else:
                    budget_kategorien[neuer_name] = budget_kategorien.pop(
                        gewählte_kategorie)
                    print(f"\n\033[32mKategorie wurde erfolgreich von "
                          f"'{gewählte_kategorie}' zu "
                          f"'{neuer_name}' umbenannt.\033[0m")
                    break
            # Neuer Eintrag
            elif aktion == 2:
                while True:
                    datum = timed_input(
                        "\n\033[34mDatum der Kosten "
                        "(DD.MM.YYYY, z.B. 01.02.2025, 0 = Zurück):"
                        "\033[0m").strip()
                    if datum == "0":
                        break
                    if not validiere_datum(datum):
                        print("\n\033[31mUngültiges Datum! "
                              "Bitte verwende das Format "
                              "DD.MM.YYYY (z.B. 01.02.2025)\033[0m")
                        continue

                    while True:
                        art = timed_input(
                            "\033[34mArt der Kosten (nur Buchstaben, "
                            "0 = Zurück):\033[0m").strip()
                        if art == "0":
                            break
                        if not art:
                            print(
                                "\n\033[31mDie Kostenart darf nicht leer sein."
                                "\033[0m")
                            continue
                        elif not re.match(r'^[A-Za-zÄÖÜäöüß]+$', art):
                            print("\n\033[31mUngültige Kostenart! "
                                  "Nur Buchstaben sind erlaubt.\033[0m")
                            continue

                        try:
                            betrag = float(timed_input("\033[34mBetrag in CHF:\033[0m"))
                            if not validiere_positiven_betrag(betrag):
                                continue

                            aktuelle_summe = 0
                            for eintrag in budget_kategorien[gewählte_kategorie]:
                                teile = eintrag.split(" - ")
                                if len(teile) == 3:
                                    try:
                                        aktuelle_summe += float(
                                            teile[2].replace(
                                                "CHF", "").strip())
                                    except ValueError:
                                        continue

                            neue_summe = aktuelle_summe + betrag
                            limit = budget_limits.get(gewählte_kategorie)

                            print(f"\n\033[32mEintrag "
                                  f"'{datum} - {art} - {betrag} CHF' "
                                  f"wurde erfolgreich hinzugefügt.\033[0m")
                            if limit is not None and neue_summe > limit:
                                print(f"\033[31mAchtung: "
                                      f"Budgetlimit von {limit:.2f} CHF für "
                                      f"'{gewählte_kategorie}' "
                                      f"überschritten!\033[0m")

                            budget_kategorien[gewählte_kategorie].append(
                                f"{datum} - {art} - {betrag} CHF")
                            break
                        except ValueError:
                            print("\n\033[31mAchtung: Ungültiger Betrag."
                                  "\033[0m")
                    break
            # Eintrag löschen
            elif aktion == 3:
                einträge = budget_kategorien[gewählte_kategorie]
                if not einträge:
                    print("\n\033[33mKeine Einträge vorhanden!\033[0m")
                    continue
                print("\n\033[1mAktuelle Einträge:\033[0m")
                for i, eintrag in enumerate(einträge, start=1):
                    print(f"{i}. {eintrag}")
                try:
                    zu_löschen = int(timed_input(
                        "\n\033[34mNummer des Eintrags zum Löschen "
                        "(0 = Zurück):\033[0m"))
                    if zu_löschen == 0:
                        continue
                    zu_löschen -= 1
                    gelöscht = einträge.pop(zu_löschen)
                    print(f"\n\033[32mEintrag '{gelöscht}' wurde "
                          f"erfolgreich gelöscht.\033[0m")
                except (ValueError, IndexError):
                    print("\n\033[31mUngültige Auswahl.\033[0m")

    return budget_kategorien


def kategorie_löschen(budget_kategorien, timed_input):
    """
    Löscht eine ausgewählte Kategorie komplett aus dem System.

    Args:
        budget_kategorien (dict): Dictionary mit allen Kategorien
        timed_input (callable): Input-Funktion mit Timeout

    Returns:
        dict: Aktualisiertes budget_kategorien Dictionary
    """
    while True:
        kategorien_liste = list(budget_kategorien.keys())
        print("\n\033[1mAktuelle Budget-Kategorien: \033[0m")
        for i, kategorie in enumerate(kategorien_liste, start=1):
            print(f"{i}. {kategorie}")
        print("")
        try:
            index = int(timed_input(
                "\n\033[34mWelche Kategorie möchtest du löschen? (0 = Zurück):"
                "\033[0m"))
            if index == 0:
                return budget_kategorien
            index -= 1
            if 0 <= index < len(kategorien_liste):
                entfernte = kategorien_liste[index]
                budget_kategorien.pop(entfernte)
                print(
                    f"\n\033[32mKategorie '{entfernte}' wurde "
                    f"erfolgreich gelöscht.\033[0m")
            else:
                print("\n\033[31mAchtung: Ungültige Nummer. \033[0m")
        except ValueError:
            print("\n\033[31mAchtung:Bitte eine gültige Zahl eingeben.\033[0m")

    return budget_kategorien
