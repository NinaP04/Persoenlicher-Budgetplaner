"""
Statistik-Modul für Budget-Tracker
Enthält Funktionen zur Datenaufbereitung und Visualisierung
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import to_rgba
from datetime import datetime
from collections import defaultdict


def monats_summen_pro_kategorie_mit_limits(budget_kategorien, budget_limits):
    """
    Berechnet pro Kategorie die Monatssummen und ordnet Farbcodes
    anhand gesetzter Budgetlimiten zu.

    Returns:
        dict: Dictionary mit Monats-Statistiken pro Kategorie
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
                farben.append("blue")
            elif betrag <= limit:
                farben.append("green")
            else:
                farben.append("red")

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

    Returns:
        dict: Dictionary mit Finanzziel-Statistiken
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


def plot_monats_summen_pro_kategorie(kategorien_daten, budget_limits=None):
    """Zeichnet monatliche Summen pro Kategorie."""
    kategorien = list(kategorien_daten.keys())

    if not kategorien:
        print("\n\033[33mKeine Kategorien-Daten zum Plotten.\033[0m")
        return

    prev_values = []
    curr_values = []
    farben = []

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

    x = np.arange(len(kategorien))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    bars_prev = ax.bar(x - width/2,
                       prev_values,
                       width,
                       label='Vormonat',
                       color='lightgray',
                       edgecolor='black',
                       alpha=0.6
                       )
    bars_curr = ax.bar(x + width/2,
                       curr_values, width,
                       color=farben,
                       edgecolor='black',
                       alpha=0.7
                       )

    if budget_limits:
        for i, kategorie in enumerate(kategorien):
            if kategorie in budget_limits:
                limit = budget_limits[kategorie]
                ax.plot(
                    [i - width - 0.1, i + width + 0.1],
                    [limit, limit],
                    color='#D2691E',
                    linestyle='--',
                    alpha=0.8,
                    linewidth=1.5
                )
                formatted_limit = f"{limit:,.2f}".replace(",", "'")
                ax.text(
                    i - 0.25,
                    limit,
                    formatted_limit,
                    fontsize=9,
                    color='#D2691E',
                    va='bottom',
                    ha='center',
                    fontweight='bold'
                )

    for i, bar in enumerate(bars_curr):
        h = bar.get_height()
        formatted_h = f"{h:,.2f}".replace(",", "'")
        ax.annotate(
            formatted_h,
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            fontsize=11
        )

        delta = curr_values[i] - prev_values[i]
        delta_text = f"{delta:+.2f}"
        delta_color = 'purple'
        ax.annotate(
            delta_text,
            xy=(bar.get_x() + bar.get_width() / 2, h + max(0.5, 0.02 * h)),
            xytext=(0, 18),
            textcoords="offset points",
            ha="center",
            fontsize=11,
            color=delta_color
        )

    for bar in bars_prev:
        h = bar.get_height()
        formatted_h = f"{h:,.2f}".replace(",", "'")
        ax.annotate(
            formatted_h, xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center", fontsize=10
        )

    ax.set_ylabel('Betrag (CHF)',
                  fontsize=13)
    ax.set_title('Monatliche Summen pro Kategorie: '
                 'Vormonat vs. Aktuell', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(
        kategorien,
        rotation=0,
        ha='center',
        fontsize=11
    )

    max_value = max(curr_values + prev_values)
    ax.set_ylim(0, max_value * 1.3)

    def format_thousands(x, p):
        return f"{int(x):,}".replace(",", "'")
    ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))

    legend_elements = [
        Line2D([0], [0],
               color='w',
               marker='s',
               markeredgecolor='black',
               markerfacecolor='lightgray',
               markersize=10,
               label='Vormonat',
               alpha=0.6),
        Line2D([0], [0],
               color='w',
               marker='s',
               markeredgecolor='black',
               markerfacecolor='green',
               markersize=10,
               label='Innerhalb Limit',
               alpha=0.7),
        Line2D([0], [0],
               color='w',
               marker='s',
               markeredgecolor='black',
               markerfacecolor='red',
               markersize=10,
               label='Limit überschritten',
               alpha=0.7),
        Line2D([0], [0],
               color='w',
               marker='s',
               markeredgecolor='black',
               markerfacecolor='blue',
               markersize=10,
               label='Kein Limit gesetzt',
               alpha=0.7),
    ]
    if budget_limits:
        legend_elements.append(
            Line2D([0], [0],
                   color='w',
                   marker='s',
                   markeredgecolor='black',
                   markerfacecolor='#D2691E',
                   markersize=10,
                   label='Budgetlimit',
                   alpha=0.8))

    ax.legend(
        handles=legend_elements,
        loc='upper center',
        bbox_to_anchor=(0.5, -0.15),
        ncol=20)

    plt.tight_layout()
    plt.savefig('monats_summen_diagramm.png',
                dpi=100,
                bbox_inches='tight')
    print("\n\033[32mDiagramm gespeichert als "
          "'monats_summen_diagramm.png'\033[0m")
    plt.close()


def plot_finanzziele(finanzziel_daten):
    """Zeichnet ein Balkendiagramm für Finanzziele."""
    kategorien = list(finanzziel_daten.keys())

    if not kategorien:
        print("Keine Finanzziel-Daten zum Plotten.")
        return

    ziele = []
    ausgaben = []
    farben = []

    for kategorie in kategorien:
        daten = finanzziel_daten[kategorie]
        ziele.append(daten.get("ziel", 0.0))
        ausgaben.append(daten.get("ausgaben_gesamt", 0.0))
        erreicht = daten.get("erreicht", False)
        farben.append("green" if erreicht else "red")

    x = np.arange(len(kategorien))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))

    bars1 = ax.bar(x - width/2,
                   ziele, width,
                   label='Finanzziel',
                   color='lightblue',
                   edgecolor='black',
                   linewidth=1,
                   alpha=0.6
                   )
    bars2 = ax.bar(x + width/2,
                   ausgaben, width,
                   label='Aktuelle Ausgaben',
                   color=farben,
                   edgecolor='black',
                   linewidth=1,
                   alpha=0.7
                   )

    for bar in bars1:
        h = bar.get_height()
        formatted_h = f"{int(h):,}".replace(",", "'")
        ax.annotate(formatted_h,
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    fontsize=11
                    )

    for bar in bars2:
        h = bar.get_height()
        formatted_h = f"{int(h):,}".replace(",", "'")
        ax.annotate(formatted_h,
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    fontsize=11
                    )

    ax.set_ylabel('Betrag (CHF)', fontsize=13)
    ax.set_title('Finanzziele vs. Aktuelle Ausgaben', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(kategorien, rotation=0, ha='center', fontsize=11)

    max_ziele_ausgaben = max(ziele + ausgaben)
    ax.set_ylim(0, max_ziele_ausgaben * 1.3)

    def format_thousands(x, p):
        return f"{int(x):,}".replace(",", "'")
    ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))

    legend_elements = [
        plt.Line2D([0], [0],
                   color='w',
                   marker='s',
                   markeredgecolor='black',
                   markerfacecolor=to_rgba('lightblue', 0.6),
                   markersize=10,
                   label='Finanzziel'),
        plt.Line2D([0], [0],
                   color='w',
                   marker='s',
                   markeredgecolor='black',
                   markerfacecolor=to_rgba('green', 0.7),
                   markersize=10,
                   label='Ziel erreicht'),
        plt.Line2D([0], [0],
                   color='w',
                   marker='s',
                   markeredgecolor='black',
                   markerfacecolor=to_rgba('red', 0.7),
                   markersize=10,
                   label='Ziel nicht erreicht'),
    ]
    ax.legend(handles=legend_elements,
              loc='upper center',
              bbox_to_anchor=(0.5, -0.15),
              ncol=20)

    plt.tight_layout()
    plt.savefig('finanzziele_diagramm.png',
                dpi=100, bbox_inches='tight')
    print(
        "\n\033[32mDiagramm gespeichert als 'finanzziele_diagramm.png'\033[0m")
    plt.close()


def statistik_menü(budget_kategorien, budget_limits, finanzziele, timed_input):
    """Zeigt ein Untermenü für Statistik-Funktionen an."""
    while True:
        print("\n\033[1mStatistik-Menü\033[0m")
        print("1. Statistik nach Kategorie (Budgetlimiten)")
        print("2. Statistik Finanzziele")

        auswahl = timed_input(
            "\n\033[34mGib die Nummer der gewünschten Statistik-Funktion ein "
            "(0 = Zurück): \033[0m"
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
                    "\n\033[33mDrücke Enter, um zurückzukehren.\033[0m")
                continue

            plot_monats_summen_pro_kategorie(kategorien_daten, budget_limits)
            _ = timed_input(
                "\n\033[34mStatistik-Daten für Budgetlimiten "
                "wurden vorbereitet. Drücke Enter, um zurückzukehren.\033[0m"
            )

        elif auswahl == "2":
            finanzziel_daten = finanzziel_statistik_daten(budget_kategorien,
                                                          finanzziele)

            if not finanzziel_daten:
                print("\n\033[34mKeine Finanzziele gesetzt.\033[0m")
                _ = timed_input(
                    "\n\033[34mDrücke Enter, um zurückzukehren.\033[0m")
                continue

            plot_finanzziele(finanzziel_daten)
            _ = timed_input(
                "\n\033[34mStatistik-Daten für Finanzziele wurden vorbereitet. "
                "Drücke Enter, um zurückzukehren.\033[0m"
            )

        else:
            print("\n\033[31mAchtung: Ungültige Nummer!\033[0m")

