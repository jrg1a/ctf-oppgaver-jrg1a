# Registerkart - Brønn under press

## Holding registers

| Register | Navn | Beskrivelse |
| --- | --- | --- |
| HR0 | BOP_STATUS | 0 = Lukket/Trygt, 1 = Åpen/Farlig |
| HR1 | TRYKK_BAR | Brønntrykk, normalt under 200 bar |
| HR2 | ESD_AKTIV | 0 = Av, 1 = På |
| HR3 | SIGNATUR | 0 = OK, 31337 = kompromittert |
| HR4 | VENTIL_POSISJON | 0-100 % |
| HR10-HR27 | FLAGG | Låst til systemet er gjenopprettet |

## Coils

| Coil | Navn | Beskrivelse |
| --- | --- | --- |
| C0 | ESD_BYPASS | False = Normal, True = Bypass aktiv |
| C1 | ALARM_UNDERTRYKK | False = Alarmer på, True = Dempet |
| C2 | FJERNTILGANG | True = Aktivert |
| C3 | TRYGG_TILSTAND | True = System gjenopprettet |

## Notater

- Bruk holding registers for tallverdiene og coils for bryterverdiene.
- Flaggregistrene er `0x0000` frem til BOP-systemet er tilbake i trygg tilstand.
