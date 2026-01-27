📡 BlastGate Serial Protocol

Arduino ↔ Raspberry Pi

Version

Protocol: v1.0

Baudrate: 115200

Encoding: ASCII, Zeilenende \n

1. Grundprinzip

Arduino ist Master für Hardware

Raspberry Pi ist Master für UI

Kommunikation ist textbasiert, zustandsorientiert

Keine Binärdaten, kein JSON → bewusst einfach & robust

2. Systemzustände

Der Arduino befindet sich immer in genau einem Zustand:

Zustand	Bedeutung
RUN	Normalbetrieb
SERVICE	Wartung / manuelles Fahren
ERROR	Fehlerzustand (Sperre aktiv)
Zustandsmeldung
STATE:RUN
STATE:SERVICE
STATE:ERROR

3. Heartbeat (Lebenszeichen)

Wird jede Sekunde vom Arduino gesendet.

Format
HB:<STATE>:M1=<0|1>:M2=<0|1>

Beispiel
HB:RUN:M1=1:M2=1
HB:RUN:M1=1:M2=0
HB:SERVICE:M1=0:M2=0

Bedeutung

M1 → Motor 1 Relais

M2 → Motor 2 Relais

➡️ Bleibt der Heartbeat >2s aus → Fehler annehmen

4. Gate-Statusmeldungen

Wenn ein Gate manuell (Taster) oder per Befehl geändert wird:

GATE:<N>:OPEN
GATE:<N>:CLOSE

Beispiel
GATE:0:OPEN
GATE:3:CLOSE

5. Motor-Statusmeldungen
MOTOR1:ON
MOTOR2:ON
MOTORS:OFF


Besonderheit:

Motor 2 wird zeitverzögert nach Motor 1 eingeschaltet

6. Befehle vom Raspberry Pi → Arduino
6.1 Gate schalten
CMD:GATE:<N>:OPEN
CMD:GATE:<N>:CLOSE
CMD:GATE:<N>:TOGGLE

Beispiel
CMD:GATE:2:OPEN

6.2 Systemzustand setzen
CMD:STATE:RUN
CMD:STATE:SERVICE
CMD:STATE:ERROR


Bedeutung:

RUN → Normalbetrieb

SERVICE → UI erlaubt manuelles Fahren

ERROR → alles gesperrt, Motoren AUS

6.3 Motoren steuern (Service / Error)
CMD:MOTORS:ON
CMD:MOTORS:OFF


⚠️ Nur erlaubt in SERVICE oder ERROR

6.4 Watchdog / Alive

Optionaler Keep-Alive vom Pi:

CMD:PING


Antwort Arduino:

PONG

7. Fehlerprotokoll
Fehler melden
ERROR:<CODE>

Standard-Fehlercodes
Code	Bedeutung
WD	Watchdog Reset
SERIAL	Ungültiger Befehl
STATE	Befehl im falschen Zustand
MOTOR	Motor-Fehler
Beispiel
ERROR:MOTOR
STATE:ERROR

8. Timing & Robustheit

Arduino akzeptiert nur vollständige Zeilen

Unbekannte Befehle → ERROR:SERIAL

Nach ERROR:

Motoren AUS

Gates bleiben in Position

Nur CMD:STATE:SERVICE oder RUN erlaubt

9. Design-Entscheidungen (bewusst)

❌ kein JSON → zu fragil auf Serial

❌ keine Konfiguration → UI-Sache

✅ menschenlesbar

✅ debugbar mit Arduino Serial Monitor

✅ einfach in Flask / Python parsebar

10. Minimalbeispiel (Live)
STATE:RUN
HB:RUN:M1=0:M2=0
GATE:1:OPEN
MOTOR1:ON
MOTOR2:ON
HB:RUN:M1=1:M2=1
GATE:1:CLOSE
MOTORS:OFF
HB:RUN:M1=0:M2=0

✅ Abnahme

Wenn:

Arduino sendet STATE + HB

Gates melden korrekt

Motoren melden korrekt

➡️ Protokoll funktioniert