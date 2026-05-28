# TCS Benzinpreis Schweiz

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Home Assistant Integration für Schweizer Tankstellenpreise, basierend auf dem TCS Benzinpreis-Radar.

Die Integration erstellt für jede konfigurierte Tankstelle ein **Gerät** mit mehreren **Sensoren** – einen pro angebotener Benzinsorte.

## Wozu es da ist

Zeigt die aktuellen Benzinpreise von Schweizer Tankstellen direkt in Home Assistant an. Ideal für Dashboards, Automatisierungen (z.B. Benachrichtigung bei Preisänderung) und Energie-Monitoring.

Die Preisdaten stammen aus dem [TCS Benzinpreis-Radar](https://benzin.tcs.ch/) – einer Public-Cloud-Funktion der TCS-Website, die ohne Authentifizierung genutzt werden kann.

## Installation

### HACS (empfohlen)

1. HACS → Integrationen → Drei Punkte → Benutzerdefinierte Repositorys
2. URL: `https://github.com/Zeronova/HA_tcs_benzin`
3. Kategorie: Integration
4. HACS → Integrationen → TCS Benzinpreis Schweiz → Herunterladen

### Manuell

1. `custom_components/tcs_benzin/` in dein Home Assistant `custom_components/`-Verzeichnis kopieren
2. Home Assistant neu starten

## Konfiguration

Einstellungen → Geräte und Dienste → Integration hinzufügen → **TCS Benzinpreis Schweiz**

### Tankstellen-ID finden

Gehe auf [benzin.tcs.ch](https://benzin.tcs.ch/), suche eine Tankstelle, kopiere die ID aus der URL:

```
https://benzin.tcs.ch/de/station/zpIcUjj4Ct2id9PXp2Wp/SP95
                                     └──────────────┘
                                           ID
```

Du kannst auch den ganzen Link einfügen – die Integration extrahiert die ID automatisch.

## Sensoren

| Sensor | Inhalt |
|--------|--------|
| Bleifrei 95 (SP95) | Preis pro Liter |
| Bleifrei 98+ (SP98) | Preis pro Liter |
| Diesel | Preis pro Liter |
| Premium-Diesel | Preis pro Liter |
| LPG (Autogas) | Preis pro Liter |
| Ethanol 85 (E85) | Preis pro Liter |
| Adblue | Preis pro Liter |
| HVO100 | Preis pro Liter |
| Wasserstoff (H2) | Preis pro Liter |
| Erdgas (CNG) | Preis pro Liter |

Nicht alle Tankstellen bieten alle Sorten an – es werden nur die tatsächlich verfügbaren Sensoren erstellt.

### Attribute

Jeder Sensor enthält zusätzlich:
- `fuel_type_display` – Anzeigename der Sorte
- `brand` – Marke der Tankstelle (z.B. AVIA, BP, SHELL)
- `address` – Adresse der Tankstelle
- `fiability_level` – Datenqualität (CONFIDENT, MODERATE, LOW, OLD_LAST_UPDATE)
- `fiability_label` – Beschriftung auf Deutsch
- `last_price_update` – Zeitstempel der letzten Preisaktualisierung
- `num_recent_price_updates` – Anzahl kürzlicher Updates

## Datenquelle

Die Integration nutzt die öffentlich zugängliche Cloud-Funktion `benzinGetStationById` der TCS-Website. Es wird kein API-Key benötigt.

## Unterstützte Home Assistant Version

- **HA 2026.4+** (OptionsFlow.config_entry ist read-only)
