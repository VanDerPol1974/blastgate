import serial
import time
import threading

# ============================
# KONFIGURATION
# ============================
SERIAL_PORT = "/dev/ttyACM0"   # später ggf. anpassen
BAUDRATE = 115200
READ_TIMEOUT = 1.0

HEARTBEAT_TIMEOUT = 3.0  # Sekunden


# ============================
# STATE OBJEKT
# ============================
class ArduinoState:
    def __init__(self):
        self.online = False
        self.last_heartbeat = 0

        self.state = "UNKNOWN"   # RUN / SERVICE / ERROR
        self.motor1 = False
        self.motor2 = False

        self.gates = [False] * 6  # True = OPEN
        self.error = None


# ============================
# SERIAL BRIDGE
# ============================
class SerialBridge:
    def __init__(self):
        self.state = ArduinoState()
        self.ser = None
        self.running = True
        self.lock = threading.Lock()

        self.reader_thread = threading.Thread(
            target=self._read_loop,
            daemon=True
        )
        self.watchdog_thread = threading.Thread(
            target=self._watchdog_loop,
            daemon=True
        )

        self.reader_thread.start()
        self.watchdog_thread.start()

    # ------------------------
    # Verbindung aufbauen
    # ------------------------
    def _connect(self):
        while self.running:
            try:
                self.ser = serial.Serial(
                    SERIAL_PORT,
                    BAUDRATE,
                    timeout=READ_TIMEOUT
                )
                print("[SERIAL] verbunden")
                return
            except Exception:
                print("[SERIAL] warte auf Arduino...")
                time.sleep(2)

    # ------------------------
    # Lesen vom Arduino
    # ------------------------
    def _read_loop(self):
        while self.running:
            if not self.ser or not self.ser.is_open:
                self._connect()

            try:
                line = self.ser.readline().decode("utf-8").strip()
                if line:
                    self._handle_line(line)
            except Exception as e:
                print("[SERIAL] Fehler:", e)
                try:
                    self.ser.close()
                except Exception:
                    pass
                time.sleep(1)

    # ------------------------
    # Parser
    # ------------------------
    def _handle_line(self, line: str):
        print("[ARDUINO]", line)

        # Heartbeat
        if line.startswith("HB:"):
            self.state.last_heartbeat = time.time()
            self.state.online = True

            parts = line.split(":")
            if len(parts) >= 4:
                self.state.state = parts[1]
                self.state.motor1 = parts[2].endswith("1")
                self.state.motor2 = parts[3].endswith("1")
            return

        # State
        if line.startswith("STATE:"):
            self.state.state = line.split(":")[1]
            return

        # Gate Status
        if line.startswith("GATE:"):
            # GATE:<N>:OPEN / CLOSE
            try:
                _, idx, status = line.split(":")
                idx = int(idx)
                self.state.gates[idx] = (status == "OPEN")
            except Exception:
                pass
            return

        # Motor Status
        if line == "MOTOR1:ON":
            self.state.motor1 = True
            return

        if line == "MOTOR2:ON":
            self.state.motor2 = True
            return

        if line == "MOTORS:OFF":
            self.state.motor1 = False
            self.state.motor2 = False
            return

        # Fehler
        if line.startswith("ERROR:"):
            self.state.error = line.split(":")[1]
            self.state.state = "ERROR"
            return

    # ------------------------
    # Heartbeat Überwachung
    # ------------------------
    def _watchdog_loop(self):
        while self.running:
            if time.time() - self.state.last_heartbeat > HEARTBEAT_TIMEOUT:
                self.state.online = False
            time.sleep(1)

    # ------------------------
    # Senden zum Arduino
    # ------------------------
    def send(self, cmd: str):
        with self.lock:
            if self.ser and self.ser.is_open:
                msg = cmd.strip() + "\n"
                self.ser.write(msg.encode("utf-8"))
                print("[SEND]", msg.strip())
