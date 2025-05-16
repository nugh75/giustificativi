# Modelli di testo per gli attestati

# Modello per lezioni in presenza
ATTESTATO_PRESENZA = """
ATTESTATO DI PRESENZA
Attività didattiche Percorso di formazione DPCM 4 agosto 2023 – A.A. 2024/2025

Si attesta che il/la sig./sig.ra {nome_cognome}
in data {data}, dalle ore {ora_inizio} alle ore {ora_fine} ha partecipato alla lezione di {tipo_lezione} svoltasi presso l'aula {aula} del dipartimento di {dipartimento} nell'ambito del percorso di formazione {tipo_percorso} – {classe_concorso} organizzato dall'{universita}.

Si rilascia su richiesta dell'interessato/a per tutti gli usi consentiti dalla legge.

Roma, lì {data_rilascio}

VISTO
Prof./Prof.ssa {direttore_cafis}
"""

# Modello per lezioni online (modalità telematica sincrona)
ATTESTATO_TELEMATICO = """
ATTESTATO DI PRESENZA
Attività didattiche Percorso di formazione DPCM 4 agosto 2023 – A.A. 2024/2025

Si attesta che il/la sig./sig.ra {nome_cognome}
in data {data}, dalle ore {ora_inizio} alle ore {ora_fine} ha partecipato alla lezione di {tipo_lezione} svoltasi in modalità telematica sincrona nell'ambito del percorso di formazione {tipo_percorso} – {classe_concorso} organizzato dall'{universita}.

Si rilascia su richiesta dell'interessato/a per tutti gli usi consentiti dalla legge.

Roma, lì {data_rilascio}

VISTO
Prof./Prof.ssa {direttore_cafis}
"""

# Modello personalizzabile (inizializzato con il modello per lezioni in presenza)
ATTESTATO_PERSONALIZZATO = ATTESTATO_PRESENZA
