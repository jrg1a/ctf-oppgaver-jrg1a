"""
CTF Challenge: "Brønn under press"
Modbus TCP-server som simulerer et sabotert BOP-kontrollsystem.

Registerkart:
  Holding Registers (HR):
    HR0  - BOP_STATUS       : 0=Lukket/Trygt, 1=Åpen/Farlig   (sabotert: 1)
    HR1  - TRYKK_BAR        : Brønntrykk i bar                 (sabotert: 847)
    HR2  - ESD_AKTIV        : 0=Normal, 1=ESD aktivert         (sabotert: 0, bypass)
    HR3  - SIGNATUR         : 0=OK, 31337=hacket               (sabotert: 31337)
    HR4  - VENTIL_POSISJON  : 0-100 (%)                        (sabotert: 100=fullt åpen)
    HR10-HR27 - FLAGG       : Låst (0x0000) til systemet er gjenopprettet

  Coils (C):
    C0 - ESD_BYPASS         : False=Normal, True=Bypass aktiv  (sabotert: True)
    C1 - ALARM_UNDERTRYKK   : False=Alarmer på, True=Dempet    (sabotert: True)
    C2 - FJERNTILGANG       : True=Aktivert                    (uendret)
    C3 - TRYGG_TILSTAND     : False (settes True ved suksess)

Riktig gjenopprettingssekvens:
  1. Slå av ESD bypass   (C0 = False)
  2. Lukk BOP            (HR0 = 0)
  3. Aktiver ESD         (HR2 = 1)
  4. Rett ventilposisjon (HR4 = 0)
  5. Skru på alarmer     (C1 = False)
  → Systemet setter C3=True og skriver flagget til HR10-HR27
"""

import asyncio
import contextvars
import itertools
import logging
import os
from copy import deepcopy
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server.async_io import ModbusServerRequestHandler, ModbusTcpServer

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

FLAG = "CTF{bop_r3st0r3d_bl0w0ut_pr3v3nt3d}"
PORT = int(os.environ.get("PORT", "502"))
CURRENT_SESSION = contextvars.ContextVar("CURRENT_SESSION", default=None)


def flag_to_registers(flag_str):
    padded = flag_str if len(flag_str) % 2 == 0 else flag_str + "\x00"
    regs = []
    for i in range(0, len(padded), 2):
        regs.append((ord(padded[i]) << 8) | ord(padded[i + 1]))
    return regs


FLAG_REGS = flag_to_registers(FLAG)
LOCKED_REGS = [0x0000] * len(FLAG_REGS)

# --- Sabotert starttilstand ---
# Pymodbus 3.x: klient-adresse N → intern data-blokk-indeks N+1
# Derfor putter vi alle verdier på indeks+1 i arrayet.
INIT_HR = [0] * 110
INIT_HR[1] = 1        # HR0: BOP åpen (farlig)
INIT_HR[2] = 847      # HR1: Trykk 847 bar
INIT_HR[3] = 0        # HR2: ESD deaktivert
INIT_HR[4] = 31337    # HR3: Hacket signatur
INIT_HR[5] = 100      # HR4: Ventil 100% åpen
# HR10-HR27: flagget låst (klient-adresse 10 → intern indeks 11)
for i, v in enumerate(LOCKED_REGS):
    INIT_HR[11 + i] = v

INIT_COILS = [False] * 20
# Coils har samme +1 offset som HR: klient-adresse N → intern indeks N+1
INIT_COILS[1] = True   # C0: ESD bypass ON
INIT_COILS[2] = True   # C1: Alarmer dempet
INIT_COILS[3] = True   # C2: Fjerntilgang ON
INIT_COILS[4] = False  # C3: Trygg tilstand: ikke nådd


class SessionStateManager:
    """Holder BOP-tilstand isolert per TCP-tilkobling."""

    def __init__(self):
        self.sessions = {}

    @staticmethod
    def _initial_state():
        return {
            "hr": deepcopy(INIT_HR),
            "co": deepcopy(INIT_COILS),
        }

    def ensure(self, session_id):
        if session_id is None:
            session_id = "fallback"
        if session_id not in self.sessions:
            self.sessions[session_id] = self._initial_state()
        return self.sessions[session_id]

    def close(self, session_id):
        self.sessions.pop(session_id, None)

    def get_values(self, area, address, count=1):
        state = self.ensure(CURRENT_SESSION.get())
        values = state[area]
        return values[address : address + count]

    def set_values(self, area, address, values):
        if not isinstance(values, list):
            values = [values]
        session_id = CURRENT_SESSION.get()
        state = self.ensure(session_id)
        state[area][address : address + len(values)] = values
        self._check_state(session_id, state)

    def _check_state(self, session_id, state):
        # Pymodbus 3.x: klient-adresse N → intern data-blokk-indeks N+1.
        hr = state["hr"]
        co = state["co"]

        esd_bypass   = co[1]   # C0
        alarm_demped = co[2]   # C1
        bop_status   = hr[1]   # HR0
        esd_aktiv    = hr[3]   # HR2
        ventil       = hr[5]   # HR4

        restored = (
            not esd_bypass   and   # C0 = False
            not alarm_demped and   # C1 = False
            bop_status == 0  and   # HR0 = 0
            esd_aktiv  == 1  and   # HR2 = 1
            ventil     == 0        # HR4 = 0
        )

        current_flag = hr[11 : 11 + len(FLAG_REGS)]   # HR10 → indeks 11
        already_unlocked = current_flag == FLAG_REGS

        if restored and not already_unlocked:
            log.info(
                "[session %s] Riktig sekvens utført — skriver flagg til HR10-HR27",
                session_id,
            )
            hr[11 : 11 + len(FLAG_REGS)] = FLAG_REGS
            co[4] = True   # C3
        elif not restored and already_unlocked:
            log.warning("[session %s] Tilstand endret tilbake — låser flagget igjen", session_id)
            hr[11 : 11 + len(FLAG_REGS)] = LOCKED_REGS
            co[4] = False


class SessionDataBlock(ModbusSequentialDataBlock):
    """Datablock som leser/skriver mot session-manageren."""

    def __init__(self, manager, area, initial_values):
        super().__init__(0, initial_values)
        self.manager = manager
        self.area = area

    def getValues(self, address, count=1):
        return self.manager.get_values(self.area, address, count)

    def setValues(self, address, values):
        self.manager.set_values(self.area, address, values)


class SessionRequestHandler(ModbusServerRequestHandler):
    def __init__(self, owner):
        super().__init__(owner)
        self.session_id = owner.next_session_id()

    def callback_connected(self):
        self.server.state_manager.ensure(self.session_id)
        log.info("[session %s] Ny Modbus TCP-tilkobling", self.session_id)
        super().callback_connected()

    def callback_disconnected(self, call_exc):
        self.server.state_manager.close(self.session_id)
        log.info("[session %s] Tilkobling lukket, tilstand fjernet", self.session_id)
        super().callback_disconnected(call_exc)

    def execute(self, request, *addr):
        token = CURRENT_SESSION.set(self.session_id)
        try:
            return super().execute(request, *addr)
        finally:
            CURRENT_SESSION.reset(token)


class SessionModbusTcpServer(ModbusTcpServer):
    def __init__(self, *args, state_manager, **kwargs):
        self.state_manager = state_manager
        self._session_ids = itertools.count(1)
        super().__init__(*args, **kwargs)

    def next_session_id(self):
        return next(self._session_ids)

    def callback_new_connection(self):
        return SessionRequestHandler(self)


def build_context(state_manager):
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [False] * 20),   # Discrete Inputs
        co=SessionDataBlock(state_manager, "co", INIT_COILS),
        hr=SessionDataBlock(state_manager, "hr", INIT_HR),
        ir=ModbusSequentialDataBlock(0, [0] * 20),        # Input Registers
    )
    return ModbusServerContext(slaves=store, single=True)


async def main():
    state_manager = SessionStateManager()
    context = build_context(state_manager)
    log.info("Starter Modbus TCP-server på port %s...", PORT)
    log.info("Tilstand isoleres per TCP-tilkobling.")
    log.info("Flagg: %s", FLAG)
    log.info(
        "Flagg-registre (HR10-HR%s): %s",
        10 + len(FLAG_REGS) - 1,
        [hex(r) for r in FLAG_REGS],
    )
    server = SessionModbusTcpServer(
        context=context,
        address=("0.0.0.0", PORT),
        state_manager=state_manager,
    )
    await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
