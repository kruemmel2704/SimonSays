# Dokumentation: Raspberry Pi Simon Says (Cyber-Physical System)

## 1. Projektübersicht
Dieses Schulprojekt im Fachbereich Informatik/Technik realisiert das klassische "Simon Says" Gedächtnisspiel und demonstriert dabei die Prinzipien eines **Cyber-Physical Systems (CPS)**. Ein Raspberry Pi 4B steuert als zentrale Verarbeitungseinheit vier LEDs (Aktoren) und registriert Eingaben über Taster sowie einen SNES Controller (Sensoren). Ziel ist es, eine zufällig generierte und immer länger werdende Sequenz von Lichtsignalen fehlerfrei zu wiederholen. Ein aktiver Buzzer gibt akustisches Feedback zum Spielstatus. Durch die Integration einer Web-Oberfläche wird das lokale Hardware-System zu einem vollständig vernetzten IoT/CPS-Ökosystem erweitert.

## 2. Hardware-Komponenten (Physische Schnittstellen)

- **Zentraleinheit**: Raspberry Pi 4 Model B 
- **Eingabe (Sensoren)**: 
  - 4x Push-Button (Spiel-Taster: Rot, Grün, Blau, Gelb)
  - 3x Push-Button (Schwierigkeitsgrad: Easy, Medium, Hard)
  - 1x SNES Controller (Erweiterte Eingabeschnittstelle über Schieberegister-Protokoll)
- **Ausgabe (Aktoren)**: 
  - 4x LED (Optisch: Rot, Grün, Blau, Gelb)
  - 1x Aktiver Buzzer (Akustisches Feedback)
- **Elektronik**: 4x 220 $\Omega$ Vorwiderstände (für LEDs), Jumper-Kabel und Breadboard.

## 3. Anschlussplan (GPIO Belegung)

Die Software nutzt die BCM-Nummerierung. Die Taster sind gegen GND geschaltet (interner Pull-Up aktiviert).


| Farbe / Typ | Komponente | BCM Pin | Physischer Pin |
| --- | --- | --- | --- |
| Rot | LED | 17 | Pin 11 |
| Rot | Button | 18 | Pin 12 |
| Grün | LED | 27 | Pin 13 |
| Grün | Button | 22 | Pin 15 |
| Blau | LED | 23 | Pin 16 |
| Blau | Button | 24 | Pin 18 |
| Gelb | LED | 25 | Pin 22 |
| Gelb | Button | 5 | Pin 29 |
| Sound | Buzzer | 6 | Pin 31 |
| Masse | Common GND | - | "z.B. Pin 6, 9, 14" |

<div style="page-break-after: always;"></div>

### Schaltplan (Mermaid)

Der Signalfluss fließt konsequent von der Logikeinheit (links) zu den Aktoren/Sensoren und endet an der Masse (rechts).

```mermaid
flowchart LR
    %% Globale Styling-Klassen für ein ansprechendes Design
    classDef pi fill:#2D3139,stroke:#8B9BB4,stroke-width:2px,color:#fff;
    classDef ledR fill:#FF4B4B,stroke:#990000,stroke-width:2px,color:#fff;
    classDef ledG fill:#4CAF50,stroke:#006600,stroke-width:2px,color:#fff;
    classDef ledB fill:#2196F3,stroke:#000099,stroke-width:2px,color:#fff;
    classDef ledY fill:#FFC107,stroke:#996600,stroke-width:2px,color:#333;
    classDef btn fill:#E0E0E0,stroke:#666,stroke-width:2px,color:#333;
    classDef snes fill:#B0BEC5,stroke:#455A64,stroke-width:2px,color:#000;
    classDef gnd fill:#1A1A1A,stroke:#666,stroke-width:2px,color:#fff;
    classDef pwr fill:#D32F2F,stroke:#fff,stroke-width:2px,color:#fff;
    classDef res fill:#8D6E63,stroke:#3E2723,stroke-width:2px,color:#fff;

    %% Raspberry Pi (Zentrale links)
    subgraph RP["Raspberry Pi 4 (GPIOs)"]
        direction TB
        VCC[3.3V Power]:::pwr
        P17[GPIO 17]:::pi
        P18[GPIO 18]:::pi
        P27[GPIO 27]:::pi
        P22[GPIO 22]:::pi
        P23[GPIO 23]:::pi
        P24[GPIO 24]:::pi
        P25[GPIO 25]:::pi
        P5[GPIO 5]:::pi
        P6[GPIO 6 - Buzzer]:::pi
        P12[GPIO 12]:::pi
        P13[GPIO 13]:::pi
        P16[GPIO 16]:::pi
        PCLK[GPIO Clock]:::pi
        PLAT[GPIO Latch]:::pi
        PDAT[GPIO Data]:::pi
    end

    %% Gemeinsame Masse-Punkte
    GND_R[GND]:::gnd
    GND_G[GND]:::gnd
    GND_B[GND]:::gnd
    GND_Y[GND]:::gnd
    GND_BUZ[GND]:::gnd
    GND_DIFF[GND]:::gnd
    GND_SNES[GND]:::gnd

    %% Verkabelung
    P17 -- Signal --> R1[220Ω]:::res --> LEDR((LED Rot)):::ledR --> GND_R
    P18 -. Pull-Up .-> BTNR([Taster Rot]):::btn --> GND_R

    P27 -- Signal --> R2[220Ω]:::res --> LEDG((LED Grün)):::ledG --> GND_G
    P22 -. Pull-Up .-> BTNG([Taster Grün]):::btn --> GND_G

    P23 -- Signal --> R3[220Ω]:::res --> LEDB((LED Blau)):::ledB --> GND_B
    P24 -. Pull-Up .-> BTNB([Taster Blau]):::btn --> GND_B

    P25 -- Signal --> R4[220Ω]:::res --> LEDY((LED Gelb)):::ledY --> GND_Y
    P5 -. Pull-Up .-> BTNY([Taster Gelb]):::btn --> GND_Y
    
    P6 -- Signal --> BUZ(((Aktiver Buzzer))):::btn --> GND_BUZ

    P12 -. Pull-Up .-> BTNH([Taster Hard]):::btn --> GND_DIFF
    P13 -. Pull-Up .-> BTNM([Taster Medium]):::btn --> GND_DIFF
    P16 -. Pull-Up .-> BTNE([Taster Easy]):::btn --> GND_DIFF

    subgraph SN["SNES Controller"]
        direction TB
        S_VCC[VCC]:::snes
        S_CLK[Clock]:::snes
        S_LAT[Latch]:::snes
        S_DAT[Data]:::snes
        S_GND[GND]:::snes
    end

    VCC -- 3.3V --> S_VCC
    PCLK -- Takt --> S_CLK
    PLAT -- Latch --> S_LAT
    S_DAT -- Daten --> PDAT
    S_GND --> GND_SNES
```


## 4. Software-Architektur
### Dateistruktur

`Config.py`: Enthält die Pin-Konfiguration und Hardware-Zuweisung.

`SimonSay.py`: Beinhaltet die gesamte Spiellogik, Klassenstruktur und Hardware-Interaktion via gpiozero.

`Dockerfile` / `docker-compose.yml`: Ermöglicht den Betrieb in einer isolierten Container-Umgebung auf Debian-Basis.

### Spiel-Ablauf & Signale
****Bereitschaft (Idle)****: Eine "Wellen-Animation" läuft dauerhaft über die LEDs, bis ein beliebiger Knopf gedrückt wird.

****Simon-Phase****: Simon fügt der Sequenz eine neue Farbe hinzu und spielt diese ab. Der Buzzer piept 1x zur Einleitung.

****Spieler-Phase****: Der Buzzer piept 2x schnell. Der Spieler muss die Sequenz wiederholen.

****Game Over****: Bei falscher Eingabe blinken alle LEDs und der Buzzer piept 3x langsam. Danach kehrt das Programm zur Bereitschafts-Welle zurück.


<div style="page-break-after: always;"></div>

## 5. Deployment via Docker

Das Projekt ist für den Betrieb unter ****Debian 13 (Trixie)**** mit ****Kernel 6.12**** optimiert.

#### Voraussetzungen

- Docker & Docker Compose installiert.

- lgpio Bibliothek im Container für modernen Kernel-Zugriff.

```bash
# Bauen und Starten im Hintergrund
docker compose up -d --build

# Logs einsehen (um Spielanweisungen zu lesen)
docker compose logs -f
```

## 6. Sicherheitshinweise

- ****Widerstände****: Betreibe LEDs niemals ohne Vorwiderstand am Pi 4B, um die GPIO-Ports zu schützen.

- ****GND****: Achte darauf, dass alle Buttons und LED-Kathoden eine saubere Verbindung zur gemeinsamen Masse (GND) haben.

- ****Case Sensitivity****: Unter Linux muss die Konfigurationsdatei strikt kleingeschrieben als config.py vorliegen, damit der Import im Docker-Container funktioniert.


<<<<<<< HEAD
****Projekt von****: ***Sebastian Scholtysek, Robin Zindler, Lars Krümmel***
## 7. Die Web-Oberfläche (Netzwerk-Komponente des CPS)

Um das Projekt zu einem vollwertigen Cyber-Physical System zu erweitern, wurde das lokale Hardware-Setup um eine vernetzte Komponente ergänzt. Eine in Python (Flask) geschriebene Web-Applikation (`app/`) dient als digitale Schnittstelle und verknüpft die physischen Sensoren und Aktoren des Raspberry Pi mit einem netzwerkbasierten Dashboard.

### Funktionen der Web-App

1. **Dashboard & Datenpersistenz (Highscores)**:
    Die gesammelten Spieldaten werden in einer lokalen SQLite-Datenbank (`simon.db`) persistent gespeichert. Sobald ein "Game Over" auf der Hardware registriert wird, kann der Nutzer seinen Namen im Web-Interface eintragen. Das Dashboard ruft diese Daten ab und präsentiert eine interaktive Top-10-Bestenliste. Dies demonstriert die Integration von physischen Ereignissen mit klassischer Software-Datenhaltung.
    
    ![Dashboard](screenshots/dashboard.png)

2. **Remote Control & Bidirektionale Echtzeit-Synchronisation**:
    Das Herzstück der Netzwerkintegration ist die Remote-Control-Ansicht, die über WebSockets eine latenzarme, bidirektionale Kommunikation ermöglicht:
    - **Beobachten (Digitaler Zwilling)**: Die Zustände der physischen Hardware werden in Echtzeit in den Browser gespiegelt. Leuchtet eine LED am Steckbrett auf, wird dies simultan auf der Weboberfläche visualisiert.
    - **Steuern (Fernzugriff)**: Das System kann vollständig über den Browser bedient werden. Ein Klick auf die virtuellen farbigen Taster löst exakt denselben Logik-Trigger aus wie ein physischer Knopfdruck am Breadboard.
    - **Schwierigkeitswahl**: Über Buttons (Easy, Medium, Hard) lässt sich die Spielgeschwindigkeit dynamisch zur Laufzeit anpassen, was direkte Auswirkungen auf die Blink- und Pausendauern der physischen LEDs hat.

    ![Remote Control](screenshots/remote.png)

### Schwierigkeitsstufen

Das Spiel bietet drei Schwierigkeitsgrade, die Geschwindigkeit und Pausen beeinflussen:

| Stufe | Blink-Dauer | Pause zwischen Signalen | Beschreibung |
| :--- | :--- | :--- | :--- |
| **Easy** | 0.8s | 0.5s | Langsam und entspannt. Gut zum Einstieg. |
| **Medium** | 0.5s | 0.3s | Standard-Geschwindigkeit. Ausgewogen. |
| **Hard** | 0.2s | 0.1s | Sehr schnell. Nur für Experten! |

Die Schwierigkeit kann über die **Web-Oberfläche (Remote)** oder über dedizierte **Hardware-Buttons** (GPIO 12, 13, 16) eingestellt werden.

 