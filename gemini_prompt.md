# Gemini Prompt: Projektdokumentation & Schaltplan

Kopiere den folgenden Text und füge ihn in Gemini ein, um eine vollständige und gut strukturierte Projektdokumentation inklusive Schaltplan generieren zu lassen.

***

**Prompt:**

Hallo Gemini, bitte schreibe eine ausführliche und akademisch strukturierte Projektdokumentation sowie einen detaillierten Schaltplan für mein Schulprojekt im Fachbereich Informatik/Technik. Das Projekt trägt den Titel "Simon Says" und behandelt das Thema **Cyber-Physical Systems (CPS)**. Die Dokumentation richtet sich an einen **Lehrer** und dient als Abgabe-/Prüfungsleistung.

Der Fokus soll darauf liegen, aufzuzeigen, warum und wie dieses Projekt ein Cyber-Physical System darstellt (Integration von physischen Sensoren/Aktoren mit digitaler Software-Logik und Netzwerkkomponenten). 

Bitte erstelle den Schaltplan entweder als **Mermaid.js Diagramm**, als strukturierte Tabelle oder als **ASCII-Art**, sodass die Verkabelung zwischen dem Raspberry Pi, den LEDs (inkl. 220 Ohm Vorwiderständen), den Tastern (gegen GND geschaltet, interne Pull-Ups) und dem aktiven Buzzer deutlich wird. 

Hier sind die Informationen zu meinem Projekt, die du als Grundlage für die Dokumentation und den Schaltplan verwenden sollst:

```text
Projekt: Raspberry Pi Simon Says als Cyber-Physical System
Hardware: Raspberry Pi 4 Model B

Komponenten (Physische Schnittstellen / Aktoren & Sensoren):
- 4x LEDs (Rot, Grün, Blau, Gelb) mit 220 Ohm Vorwiderständen (Aktoren)
- 4x Push-Buttons (Rot, Grün, Blau, Gelb) (Sensoren/Eingabe)
- 1x Aktiver Buzzer (Aktor für akustisches Feedback)
- 1x SNES Controller (Erweiterte Eingabeschnittstelle für Spielerinteraktion)
- Jumper-Kabel & Breadboard

Pin-Belegung (BCM):
- Rote LED: 17, Roter Button: 18
- Grüne LED: 27, Grüner Button: 22
- Blaue LED: 23, Blauer Button: 24
- Gelbe LED: 25, Gelber Button: 5
- Buzzer: 6
- Schwierigkeitsgrad-Buttons (Hard, Medium, Easy): 12, 13, 16
- SNES Controller (Schieberegister-Protokoll): Clock, Latch, Data (GPIO-Pins nach Wahl)
Alle Buttons sind gegen gemeinsame Masse (GND) geschaltet.

Software & Features (Digitale Verarbeitung & Vernetzung):
- Kernlogik in Python geschrieben (nutzt gpiozero und lgpio für GPIO).
- Bereitschafts-Modus: Wellen-Animation der LEDs.
- Spielablauf: Simon zeigt Sequenz (mit 1x Piepen) -> Spieler wiederholt (nach 2x Piepen) -> Game Over (Alle LEDs blinken, 3x langsames Piepen).
- Flask-Web-App (im `app/` Ordner) für ein Web-Interface (Netzwerk-Komponente des CPS):
  - Dashboard mit Top-10 Highscore-Liste (gespeichert in SQLite-Datenbank `simon.db`).
  - Remote Control: Spiel kann komplett synchron im Browser gesteuert und gespielt werden.
  - Schwierigkeitsstufen (Easy, Medium, Hard), die Blink-Dauer und Pausen anpassen.
- Deployment via Docker und Docker Compose (Debian 13 Basis).
```

**Anforderungen an deine Antwort (Struktur für die Lehrkraft):**
1. **Einleitung & Zielsetzung:** Kurze Zusammenfassung des Projekts und dessen pädagogischer/technischer Ziele.
2. **Klassifizierung als Cyber-Physical System (CPS):** Eine detaillierte Erklärung, wie die physischen Komponenten (Taster, LEDs) über den Raspberry Pi mit der digitalen Welt (Python-Logik) und dem Netzwerk (Flask Web-App) interagieren und so ein geschlossenes System bilden.
3. **Hardware-Architektur & Schaltplan:** Eine klare visuelle Repräsentation der Verkabelung (Mermaid.js oder ASCII) sowie eine tabellarische Übersicht der Komponenten und Pins (Widerstände für LEDs explizit erwähnen).
4. **Software-Architektur & Netzwerk:** Erklärung der Python-Steuerungslogik, der Einbindung der Flask Web-App (als IoT/CPS-Erweiterung) und der Datenhaltung per SQLite. **Wichtig: Füge hier ein konkretes Python-Codebeispiel hinzu, das demonstriert, wie die Abtastung (Auslesen) der gedrückten Knöpfe des SNES-Controllers über GPIO (Clock, Latch, Data) funktioniert.**
5. **Deployment:** Kurze Erklärung des professionellen Deployments mittels Docker.
6. **Sicherheitshinweise & Best Practices:** Relevante technische Hinweise (z.B. LEDs nicht ohne Widerstand betreiben), um technisches Verständnis zu demonstrieren.

Bitte verwende einen professionellen, sachlichen Ton (angemessen für eine Schulabgabe) und formatiere die Dokumentation sauber in Markdown.
