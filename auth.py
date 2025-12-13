"""
Authentifizierungs-Modul für Budget-Tracker
Enthält alle Funktionen für Passwort-Hashing, Login und Passwortänderung
"""

import base64
import os
import sys

try:
    import bcrypt
except ImportError:
    print("\n\033[31mFehler: Das Paket 'bcrypt' ist erforderlich, "
          "aber nicht installiert.\033[0m")
    print("\n\033[32mInstalliere es mit: pip install bcrypt\033[0m")
    sys.exit(1)


def hash_passwort(passwort):
    """
    Hasht ein Passwort mit bcrypt für sichere Speicherung.

    Args:
        passwort (str): Das zu hashende Passwort

    Returns:
        str: Der gehashte Passwort-String
        (base64-kodiert für JSON-Kompatibilität)
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(passwort.encode('utf-8'), salt)
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
        hashed_bytes = base64.b64decode(hashed_passwort.encode('utf-8'))
        return bcrypt.checkpw(passwort.encode('utf-8'), hashed_bytes)
    except Exception:
        return False


def passwort_login(benutzer_passwort, daten_speichern_func):
    """
    Führt den Login-Prozess durch.
    Nach 3 fehlgeschlagenen Versuchen wird das Programm beendet.

    Args:
        benutzer_passwort (dict): Dictionary mit gehashtem
        Passwort daten_speichern_func (callable):
        Funktion zum Speichern der Daten
    """
    hashed_passwort = benutzer_passwort.get("passwort",
                                            hash_passwort("Test1234!"))
    anmeldeversuche = 0
    passwort_input = input("\n\033[34mBitte gebe dein Passwort ein:\033[0m")

    while not verifiziere_passwort(passwort_input, hashed_passwort):
        anmeldeversuche += 1
        if anmeldeversuche == 3:
            print("\n\033[31mZu viele fehlerhafte Anmeldungen!\033[0m")
            os._exit(1)
        else:
            passwort_input = input(
                "\n\033[31mFehlerhaftes Passwort! "
                "Versuche es bitte nochmals:\033[0m")

    print("\n\033[32mErfolgreich eingeloggt!\033[0m\n")


def passwort_ändern(benutzer_passwort, timed_input, daten_speichern_func):
    """
    Ermöglicht das Ändern des Passworts.
    Validiert das neue Passwort nach festgelegten Sicherheitskriterien.

    Args:
        benutzer_passwort (dict): Dictionary mit gehashtem Passwort
        timed_input (callable): Input-Funktion mit Timeout
        daten_speichern_func (callable): Funktion zum Speichern der Daten

    Returns:
        dict: Aktualisiertes benutzer_passwort Dictionary
    """
    hashed_passwort = benutzer_passwort.get("passwort",
                                            hash_passwort("Test1234!"))

    änderung_input = timed_input(
        "\n\033[34mBitte geben Sie Ihr aktuelles Passwort ein:\033[0m")
    while not verifiziere_passwort(änderung_input, hashed_passwort):
        print("\n\033[31mUngültiges Passwort!\033[0m")
        änderung_input = timed_input("Versuche es bitte erneut: ")

    print("\n\033[1mPasswort neu festlegen\033[0m")
    print("Das Passwort muss enthalten: ")
    print("\033[3m- Mindestens 8 Zeichen\033[0m")
    print("\033[3m- Gross- und Kleinschreibung\033[0m")
    print("\033[3m- Mindestens eine Zahl\033[0m")
    print("\033[3m- Mindestens ein Sonderzeichen: "
          "$, @, #, %, !, ?, &, *\033[0m")

    SpecialSym = ['$', '@', '#', '%', '!', '?', '&', '*']

    while True:
        val = True
        passwort_neu1 = timed_input(
            "\n\033[34mGeben Sie Ihr neues Passwort ein:\033[0m")

        if len(passwort_neu1) < 8:
            print('\n\033[31m -Passwort muss mindestens 8 Zeichen lang sein'
                  '\033[0m')
            val = False
        if len(passwort_neu1) > 20:
            print('\033[31m -Passwort darf maximal 20 Zeichen lang sein'
                  '\033[0m')
            val = False
        if not any(char.isdigit() for char in passwort_neu1):
            print('\033[31m -Passwort muss mindestens eine Zahl enthalten'
                  '\033[0m')
            val = False
        if not any(char.isupper() for char in passwort_neu1):
            print('\033[31m -Passwort muss mindestens einen Grossbuchstaben '
                  'enthalten\033[0m')
            val = False
        if not any(char.islower() for char in passwort_neu1):
            print('\033[31m -Passwort muss mindestens einen Kleinbuchstaben '
                  'enthalten\033[0m')
            val = False
        if not any(char in SpecialSym for char in passwort_neu1):
            print('\033[31m -Passwort muss mindestens ein Sonderzeichen '
                  'enthalten ($,@,#,%,!,?,&,*)\033[0m')
            val = False
            continue

        if val:
            passwort_neu2 = timed_input(
                "\033[34mGeben Sie Ihr neues Passwort erneut ein:\033[0m")
            if passwort_neu1 == passwort_neu2:
                benutzer_passwort["passwort"] = hash_passwort(passwort_neu1)
                daten_speichern_func()
                print("\n\033[32mPasswort erfolgreich geändert!\033[0m")
                break
            else:
                print(
                    "\n\033[31mDie Passwörter stimmen nicht überein!\033[0m\n")
        else:
            print("\n\033[31mBitte versuchen Sie es erneut.\033[0m\n")

    return benutzer_passwort
