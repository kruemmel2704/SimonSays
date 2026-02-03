# BBS 1 Mainz BSFI24D Projekt

## Simon Says Raspi Edition
Wir haben uns dazu entschieden ein Spiel zu programmieren was Simon Says nachempfunden ist. Das Programm ist simpel mit Python programmiert. Die Knöpfe und die LED's werden in der `config.py` Konfiguriert.

### Installation

```bash
git clone https://github.com/kruemmel2704/SimonSays1.git
cd SimonSays
```

#### Programm automatisiert starten
Damit das Programm im Hintergrund läuft muss `screen` installiert sein.

```bash
sudo apt update && sudo apt install screen -y
```

danach mit `cronjob` bei neustart das Programm ausführen lassen

```bash
@reboot -dmS SimonSays python /dein/pfad/SimonSays.py
```

dann einmal mit `sudo reboot` neustarten

### Aufbau

Die von Ihnen gewählten Pins in der `config.py` werden mit 3,3V versorgt. Die anderen Pins der LED's und der Knöpfe müssen dann an einer der Massen angeschlossen werden.

```plaintext
          (SD-Karten-Slot Seite)
         3,3V  [01] [02]  5V
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
        GPIO6  [31] [32]  GPIO12
       GPIO13  [33] [34]  GND ⚫
       GPIO19  [35] [36]  GPIO16
       GPIO26  [37] [38]  GPIO20
          GND  [39] [40]  GPIO21
          (USB/Ethernet Seite)
```

### Konfiguration

Die Konfiguration wird in der `config.py` vorgenommen

```ini, toml
HARDWARE_SETUP = {
    "red": {"led": PIN_ROTE_LED, "btn": PIN_KNOPF_ROTE_LED},
    "green": {"led": PIN_GRÜNE_LED, "btn": PIN_KNOPF_GRÜNE_LED},
    "blue": {"led": PIN_BLAUE_LED, "btn": PIN_KNOPF_BLAUE_LED},
    "yellow": {"led": PIN_GELBE_LED, "btn": PIN_KNOPF_GELBE_LED}
}
```

Bitte passen Sie die Pins der Jeweiligen LED's und Knöpfe an

### Das Programm

Wenn das Programm ausgeführt wird, leuchten alle LED's in einer Wellenform auf. Drücken Sie hier einen Knopf um das Spiel zu beginnen. Der Computer gibt Ihnen eine Reihenfolge vor, diese müssen Sie sich merken und dann über die Knöpfe wiedergeben. Falls Sie einen Fehler machen haben Sie verloren. Alle LED's blinken gleichzeitig und Sie gelangen wieder zum Start.

![Spielablauf](/video/game.webm)

