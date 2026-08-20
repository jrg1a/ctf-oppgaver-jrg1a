# Basic på tråden

**Kategori:** Network
**Poeng:** 175
**Type:** Statisk fil (PCAP)
**Vanskelighetsgrad:** Lett / Medium

---

## Scenario

En kort nettverkssnutt fra standnettet viser flere innlogginger og kall mot
interne tjenester. Teamet sier at passordet til statuspanelet ikke kan sees
fordi trafikken "bare viser en header".

Se gjennom trafikken og finn hemmeligheten.

---

## Vedlegg

- [`basic_auth.pcap`](dist/basic_auth.pcap)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Følg HTTP-strømmene. Ikke alle innloggingene er relevante. |
| 35 poeng | `Authorization: Basic` er ikke kryptering. Se særlig på statuspanelet. |
| 70 poeng | Basic Auth dekodes til `brukernavn:hemmelighet`. Finn varianten som brukes mot statuspanelet. |

---

## Løsningsvei (kun for arrangør)

Finn HTTP-streamen til `status.nordverk.local` og `/admin/status`.
Det finnes flere `Authorization: Basic`-headere i PCAP-en, men bare denne
admin-status-innloggingen har flagget som passorddel.

```bash
python3 solver/solve.py
```

**Flagg:** `CTF{basic_auth_er_bare_base64}`
