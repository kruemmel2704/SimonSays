# Simon Says - Schaltplan (Mermaid)

Hier ist der aufgeräumte, gut strukturierte Schaltplan, der das "cursed" Kabelgewirr vermeidet. Der Trick besteht darin, die Signalflüsse konsequent von links (Raspberry Pi) nach rechts (Komponenten & Masse) fließen zu lassen und individuelle Masse-Symbole (GND) zu verwenden, um lange, kreuzende Linien zu verhindern.

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

    %% Gemeinsame Masse-Punkte (Rechts platziert für sauberes Layout ohne Kreuzungen)
    GND_R[GND]:::gnd
    GND_G[GND]:::gnd
    GND_B[GND]:::gnd
    GND_Y[GND]:::gnd
    GND_BUZ[GND]:::gnd
    GND_DIFF[GND]:::gnd
    GND_SNES[GND]:::gnd

    %% --- VERKABELUNG ---

    %% Rote Gruppe
    P17 -- Signal --> R1[220Ω]:::res --> LEDR((LED Rot)):::ledR --> GND_R
    P18 -. Pull-Up .-> BTNR([Taster Rot]):::btn --> GND_R

    %% Grüne Gruppe
    P27 -- Signal --> R2[220Ω]:::res --> LEDG((LED Grün)):::ledG --> GND_G
    P22 -. Pull-Up .-> BTNG([Taster Grün]):::btn --> GND_G

    %% Blaue Gruppe
    P23 -- Signal --> R3[220Ω]:::res --> LEDB((LED Blau)):::ledB --> GND_B
    P24 -. Pull-Up .-> BTNB([Taster Blau]):::btn --> GND_B

    %% Gelbe Gruppe
    P25 -- Signal --> R4[220Ω]:::res --> LEDY((LED Gelb)):::ledY --> GND_Y
    P5 -. Pull-Up .-> BTNY([Taster Gelb]):::btn --> GND_Y
    
    %% Buzzer Verbindung
    P6 -- Signal --> BUZ(((Aktiver Buzzer))):::btn --> GND_BUZ

    %% Schwierigkeitsgrad Taster
    P12 -. Pull-Up .-> BTNH([Taster Hard]):::btn --> GND_DIFF
    P13 -. Pull-Up .-> BTNM([Taster Medium]):::btn --> GND_DIFF
    P16 -. Pull-Up .-> BTNE([Taster Easy]):::btn --> GND_DIFF

    %% SNES Controller Verbindungen
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
