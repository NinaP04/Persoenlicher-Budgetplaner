"""
Finanzkontroll-Modul für Budget-Tracker
Enthält Funktionen zur Verwaltung von Budgetlimits und Finanzzielen
"""

from utils import validiere_positiven_betrag, MAX_BUDGET_LIMIT


def finanzkontrolle(budget_kategorien,
                    budget_limits,
                    finanzziele,
                    timed_input,
                    daten_speichern_func):
    """
    Verwaltet Budgetlimits und Finanzziele für einzelne Kategorien.

    Args:
        budget_kategorien (dict): Dictionary mit allen Kategorien
        budget_limits (dict): Dictionary mit Budget-Limits
        finanzziele (dict): Dictionary mit Finanzzielen
        timed_input (callable): Input-Funktion mit Timeout
        daten_speichern_func (callable): Funktion zum Speichern der Daten

    Returns:
        tuple: (budget_limits, finanzziele)
    """
    kategorien_liste = list(budget_kategorien.keys())
    print("\n\033[1mFinanzkontrolle pro Kategorie\033[0m")
    for i, kategorie in enumerate(kategorien_liste, start=1):
        print(f"{i}. {kategorie}")
    print("")

    try:
        index = int(timed_input(
            "\033[34mWähle eine Kategorie für die Finanzkontrolle "
            "(0 = Hauptmenü):\033[0m")
        )
        if index == 0:
            return budget_limits, finanzziele
        index -= 1
        if not (0 <= index < len(kategorien_liste)):
            print("\n\033[31mUngültige Auswahl.\033[0m")
            return budget_limits, finanzziele
    except ValueError:
        print("\n\033[31mBitte eine gültige Zahl eingeben.\033[0m")
        return budget_limits, finanzziele

    gewählte_kategorie = kategorien_liste[index]

    while True:
        print(f"\n\033[1mWas möchtest du für '{gewählte_kategorie}' "
              f"bearbeiten?\033[0m")
        print("1. Budgetlimite")
        print("2. Finanzziel")

        hauptwahl = timed_input(
            "\n\033[34mWähle eine Option (0 = Hauptmenü, 1–2):\033[0m")

        if hauptwahl == "0":
            return budget_limits,finanzziele

        if hauptwahl == "1":
            budget_limits = _budgetlimite_verwalten(
                gewählte_kategorie,
                budget_limits,
                timed_input,
                daten_speichern_func)

        elif hauptwahl == "2":
            finanzziele = _finanzziel_verwalten(
                gewählte_kategorie,
                finanzziele,
                timed_input,
                daten_speichern_func)

    return budget_limits, finanzziele


def _budgetlimite_verwalten(kategorie,
                            budget_limits,
                            timed_input,
                            daten_speichern_func):
    """Verwaltung der Budgetlimite für eine Kategorie."""
    while True:
        print(f"\n\033[1mBudgetlimite für '{kategorie}'\033[0m")
        print("1. Anzeigen")
        print("2. Setzen")
        print("3. Ändern")
        print("4. Entfernen")
        auswahl = timed_input(
            "\n\033[34mWähle eine Option (0 = Zurück, 1–4): \033[0m")

        if auswahl == "0":
            break

        if auswahl == "1":
            limit = budget_limits.get(kategorie)
            if limit is not None:
                print(
                    f"\n\033[1mAktuelles Budgetlimit: {limit:.2f} CHF\033[0m")
            else:
                print("\n\033[33mKein Budgetlimit gesetzt.\033[0m")

        elif auswahl == "2":
            try:
                limit = float(timed_input(
                    f"\n\033[34mNeues Budgetlimit in CHF (max.{MAX_BUDGET_LIMIT:.2f}"
                    f"CHF):\033[0m")
                )
                if validiere_positiven_betrag(limit, MAX_BUDGET_LIMIT):
                    budget_limits[kategorie] = limit
                    daten_speichern_func()
                    print(f"\n\033[32mBudgetlimite gesetzt: {limit:.2f} "
                          f"CHF\033[0m")
            except ValueError:
                print("\n\033[31mUngültiger Betrag.\033[0m")

        elif auswahl == "3":
            if kategorie not in budget_limits:
                print("\n\033[33mKein Limit vorhanden.\033[0m")
            else:
                try:
                    neues_limit = float(
                        timed_input(f"\n\033[34mNeues Limit in CHF "
                                    f"(max. {MAX_BUDGET_LIMIT:.2f} CHF):\033[0m"))
                    if validiere_positiven_betrag(neues_limit,
                                                  MAX_BUDGET_LIMIT):
                        budget_limits[kategorie] = neues_limit
                        daten_speichern_func()
                        print(
                            f"\n\033[32mLimit geändert auf {neues_limit:.2f} "
                            f"CHF\033[0m")
                except ValueError:
                    print("\n\033[31mUngültiger Betrag.\033[0m")

        elif auswahl == "4":
            if kategorie in budget_limits:
                del budget_limits[kategorie]
                daten_speichern_func()
                print(f"\n\033[32mLimit entfernt.\033[0m")
            else:
                print("\n\033[33mKein Limit vorhanden.\033[0m")

    return budget_limits


def _finanzziel_verwalten(kategorie,
                          finanzziele,
                          timed_input,
                          daten_speichern_func):
    """Verwaltung des Finanzziels für eine Kategorie."""
    while True:
        print(f"\n\033[1mFinanzziel für '{kategorie}'\033[0m")
        print("1. Anzeigen")
        print("2. Setzen")
        print("3. Ändern")
        print("4. Entfernen")
        auswahl = timed_input(
            "\n\033[34mWähle eine Option (0 = Zurück, 1–4):\033[0m")

        if auswahl == "0":
            break

        if auswahl == "1":
            ziel_info = finanzziele.get(kategorie)
            if ziel_info:
                print(f"\n\033[1mZiel:\033[0m {ziel_info['ziel']} CHF")
                print(f"\033[1mMeldung:\033[0m {ziel_info['meldung']}")
            else:
                print("\n\033[33mKein Ziel gesetzt.\033[0m")

        elif auswahl == "2":
            try:
                ziel = float(timed_input("\n\033[34mZielbetrag in CHF:\033[0m"))
                if validiere_positiven_betrag(ziel):
                    meldung = (
                        timed_input("\033[34mMeldung bei Zielerreichung:\033[0m").strip())
                    finanzziele[kategorie] = {"ziel": ziel, "meldung": meldung}
                    daten_speichern_func()
                    print(f"\n\033[32mZiel {ziel} CHF gespeichert.\033[0m")
            except ValueError:
                print("\n\033[31mUngültiger Betrag.\033[0m")

        elif auswahl == "3":
            if kategorie not in finanzziele:
                print("\n\033[33mKein Ziel vorhanden.\033[0m")
            else:
                try:
                    neues_ziel = float(timed_input("\n\033[34mNeues Ziel in CHF:\033[0m"))
                    if validiere_positiven_betrag(neues_ziel):
                        neue_meldung = timed_input("\033[34mNeue Meldung:\033[0m").strip()
                        finanzziele[kategorie] = {"ziel": neues_ziel,
                                                  "meldung": neue_meldung}
                        daten_speichern_func()
                        print(f"\n\033[32mZiel aktualisiert.\033[0m")
                except ValueError:
                    print("\n\033[31mUngültiger Betrag.\033[0m")

        elif auswahl == "4":
            if kategorie in finanzziele:
                del finanzziele[kategorie]
                daten_speichern_func()
                print(f"\n\033[32mZiel entfernt.\033[0m")
            else:
                print("\n\033[33mKein Ziel vorhanden.\033[0m")

    return finanzziele
