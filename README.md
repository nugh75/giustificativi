# Generatore Attestati di Presenza

Applicazione Streamlit per generare attestati di presenza per attività didattiche del Percorso di formazione DPCM e inviarli automaticamente via email.

## Funzionalità

- Caricamento e validazione avanzata di file Excel con i dati dei partecipanti
- Generazione automatica di attestati di presenza in formato PDF
- Invio automatico degli attestati via email ai richiedenti
- Personalizzazione completa del testo delle email con supporto per segnaposto
- Possibilità di specificare diversi firmatari (Direttore CAFIS e/o Docente)
- Gestione intelligente degli invii email con blocchi personalizzabili
- Sistema di registrazione errori per semplificare la risoluzione dei problemi
- Interfaccia user-friendly per la configurazione e l'utilizzo
- Supporto per la configurazione di indirizzi email di risposta personalizzati

## Requisiti

- Python 3.8 o superiore
- Librerie Python (vedi `requirements.txt`)

## Installazione

### Installazione di Python

Se non hai già Python installato sul tuo sistema, segui queste istruzioni:

#### Windows
1. Scarica Python dalla [pagina ufficiale](https://www.python.org/downloads/windows/)
2. Esegui l'installer scaricato
3. **Importante:** Seleziona l'opzione "Add Python to PATH" durante l'installazione
4. Completa l'installazione seguendo le istruzioni a schermo

#### macOS
1. Metodo consigliato utilizzando Homebrew:
   ```bash
   # Installa Homebrew se non è già presente
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   # Installa Python
   brew install python
   ```
2. Oppure scarica Python dalla [pagina ufficiale](https://www.python.org/downloads/macos/)

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Installazione dell'applicazione

1. Clona il repository:
   ```bash
   git clone <URL_del_repository>
   cd giustificativi
   ```

2. Crea un ambiente virtuale e attivalo:
   ```bash
   python -m venv venv
   source venv/bin/activate  # su Windows: venv\Scripts\activate
   ```

3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

## Configurazione

### Configurazione email

Per l'invio automatico delle email, è necessario configurare le credenziali SMTP. È possibile farlo direttamente nell'interfaccia dell'applicazione o creando un file `.env` nella directory principale con le seguenti variabili:

```
SMTP_SERVER=smtp.esempio.com
SMTP_PORT=587
SMTP_USERNAME=tua_email@esempio.com
SMTP_PASSWORD=tua_password
SMTP_REPLY_TO=email_risposta@esempio.com
DIRETTORE_CAFIS=Nome del Direttore
```

#### Configurazione di indirizzo Reply-To

Se l'indirizzo email utilizzato per l'autenticazione SMTP (`SMTP_USERNAME`) è diverso dall'indirizzo al quale si desidera ricevere le risposte, è possibile configurare un indirizzo di risposta personalizzato utilizzando la variabile `SMTP_REPLY_TO`. Questo è particolarmente utile quando:

- Si utilizza un indirizzo email di servizio configurato sul server Microsoft (es. `pef_presenze@os.uniroma3.it`)
- Si desidera che le risposte vengano inviate a un indirizzo email più semplice da ricordare o più diffuso (es. `pef.presenze@uniroma3.it`)

L'applicazione imposterà automaticamente l'header "Reply-To" nelle email inviate, in modo che quando i destinatari rispondono, la risposta venga inviata all'indirizzo corretto.

### Risorse grafiche

Preparare le seguenti immagini:
- Logo dell'Università (formato PNG o JPG)
- Firma del Direttore del Centro CAFIS (formato PNG o JPG)

Queste immagini possono essere caricate direttamente tramite l'interfaccia dell'applicazione.

## Utilizzo

1. Avvia l'applicazione:
   ```bash
   streamlit run app.py
   ```

2. Accedi all'applicazione dal browser (di solito http://localhost:8501)

3. Carica il file Excel con i dati dei partecipanti

4. Carica il logo e la firma (opzionale)

5. Configura le credenziali SMTP (se non fatto in precedenza)

6. Configura il direttore del Centro CAFIS e il docente del corso (opzionale)

7. Personalizza il testo delle email (oggetto, corpo e firmatari)

8. Configura le opzioni avanzate per l'invio delle email (blocchi e intervalli)

9. Genera gli attestati e invia le email

## Formato del file Excel

Il file Excel deve contenere le seguenti colonne:

| Colonna | Descrizione |
|---------|-------------|
| nome_cognome | Nome e cognome del partecipante |
| data | Data della lezione (formato: GG/MM/AAAA) |
| ora_inizio | Ora di inizio lezione |
| ora_fine | Ora di fine lezione |
| aula | Aula della lezione |
| dipartimento | Nome del dipartimento |
| indirizzo | Indirizzo del dipartimento |
| tipo_lezione | Tipo di lezione seguita |
| tipo_percorso | Tipo di percorso (uno tra: "PeF60 CFU", "PeF30 CFU", "PeF36 CFU", "PeF30 CFU (art. 13)") |
| classe_concorso | Classe di concorso |
| email | Indirizzo email del richiedente |

## Note

- Assicurarsi che le credenziali SMTP siano corrette per evitare problemi di invio email
- In caso di errori nell'invio email, verificare che il provider email permetta l'accesso da app meno sicure o generare una password specifica per l'applicazione
- Per Gmail, potrebbe essere necessario attivare l'autenticazione a due fattori e generare una password per l'app

## Risoluzione Problemi

### Errori di Connessione SMTP
- Verificare che le credenziali siano corrette
- Assicurarsi che l'autenticazione a due fattori sia attiva (per Gmail/Outlook) e che si stia utilizzando una password per app
- Controllare che il server SMTP non sia bloccato dal firewall della rete
- Verificare che il provider email supporti l'accesso SMTP

### Errori di Generazione PDF
- Verificare che i file di logo e firma siano in un formato supportato (PNG, JPG)
- Controllare che tutte le colonne obbligatorie nel file Excel siano presenti e compilate
- Assicurarsi che la directory temporanea sia scrivibile dall'applicazione

### Errori nell'Invio Email
- Verificare la connessione Internet
- Controllare che il server SMTP sia configurato correttamente
- Verificare che l'indirizzo email di destinazione sia valido
- Provare a inviare un'email di test dalla sezione apposita
- Verificare i log di errore nella directory logs (se disponibile)

### Gestione errori comuni provider email
- **Gmail**: Abilitare "App meno sicure" o usare una password per app
- **Outlook/Office 365**: Usare una password per app specifica
- **Libero**: Verificare che il proprio account abbia l'accesso SMTP abilitato

## Aggiornamento alla versione migliorata

L'applicazione include ora una versione migliorata con nuove funzionalità e interfaccia utente ottimizzata.

Per testare la nuova versione:
```bash
streamlit run app_improved.py
```

Le nuove funzionalità includono:
- Gestione avanzata degli errori con logging
- Interfaccia utente migliorata
- Generatore di template Excel avanzato
- Tab di aiuto con documentazione dettagliata
- Test di connessione SMTP

Una volta verificato che la nuova versione funziona correttamente, è possibile sostituire la vecchia versione:
```bash
mv app_improved.py app.py
```

## Licenza

© 2025 Centro CAFIS - Università degli Studi Roma Tre
