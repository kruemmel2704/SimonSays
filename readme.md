# Dokumentation: Raspberry Pi Simon Says

## 1. Projektübersicht
Dieses Projekt realisiert das klassische "Simon Says" Gedächtnisspiel. Ein Raspberry Pi 4B steuert vier LEDs und registriert Eingaben über vier Taster. Ziel ist es, eine zufällig generierte und immer länger werdende Sequenz von Lichtsignalen fehlerfrei zu wiederholen. Ein aktiver Buzzer gibt akustisches Feedback zum Spielstatus.

## 2. Hardware-Komponenten

- Zentraleinheit: Raspberry Pi 4 Model B 
- Eingabe: 4x Push-Button (Taster).
- Ausgabe (Optisch): 4x LED (Rot, Grün, Blau, Gelb).
- Ausgabe (Akustisch): 1x Aktiver Buzzer (Pieper).
- Widerstände: 4x 220 $\Omega$ (für LEDs).
- Verkabelung: Jumper-Kabel und Breadboard.

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

```plaintext
          (SD-Karten-Slot Seite)
         3,3V  [01] [02]  <- Spk (5V) 🔊
  (I2C) GPIO2  [03] [04]  5V
  (I2C) GPIO3  [05] [06]  GND ⚫
        GPIO4  [07] [08]  GPIO14
          GND  [09] [10]  GPIO15
🔴 LED (17) -> [11] [12] <- Btn (18) 🔴
🟢 LED (27) -> [13] [14]  GND ⚫
🟢 Btn (22) -> [15] [16] <- LED (23) 🔵
         3,3V  [17] [18] <- Btn (24) 🔵
       GPIO10  [19] [20]  GND ⚫
        GPIO9  [21] [22] <- LED (25) 🟡
       GPIO11  [23] [24]  GPIO8
          GND  [25] [26]  GPIO7
        GPIO0  [27] [28]  GPIO1
🟡 Btn (05) -> [29] [30]  GND ⚫
🔊 Spk (06) -> [31] [32]  GPIO12
       GPIO13  [33] [34]  GND ⚫
       GPIO19  [35] [36]  GPIO16
       GPIO26  [37] [38]  GPIO20
          GND  [39] [40]  GPIO21
          (USB/Ethernet Seite)
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
## 7.Erweiterung
