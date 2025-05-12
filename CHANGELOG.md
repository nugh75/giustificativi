# Changelog Attestati di Presenza

Tutte le modifiche rilevanti al progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-05-12

### Aggiunto
- Personalizzazione completa del testo delle email con supporto per segnaposto
- Possibilità di specificare il docente del corso come firmatario aggiuntivo
- Anteprima in tempo reale del testo dell'email personalizzato
- Validazione avanzata dei file Excel con controlli sui formati di data, ora ed email
- Configurazione personalizzabile dei blocchi di invio email e degli intervalli

### Modificato
- Migliorata la gestione degli errori con codici specifici per facilitare debugging
- Estesa l'integrazione con sistema di logging degli errori
- Interfaccia utente migliorata per la configurazione delle email

### Corretto
- Risolto errore di sintassi nel modulo di invio email
- Corretta gestione delle eccezioni durante la validazione dei file Excel

## [1.1.0] - 2025-04-15

### Aggiunto
- Sistema centralizzato di gestione errori con logging su file
- Gestione migliorata degli errori SMTP con ritentativi automatici
- Interfaccia utente migliorata con componenti personalizzati
- Generazione di diversi template Excel (base, minimo, completo, vuoto)
- Tab di aiuto con documentazione e FAQ dettagliate
- Verifica connessione SMTP prima del salvataggio delle credenziali
- Test di invio multiplo per verificare l'invio a blocchi

### Modificato
- Ridisegnato il generatore PDF per migliorare layout e leggibilità
- Ottimizzato l'invio email con gestione a blocchi e ritardi
- Migliorata la validazione dei dati Excel
- Aggiornate le informazioni sui provider di email supportati
- Ridimensionamento automatico di logo e firma per evitare problemi di layout

### Risolto
- Errore nella visualizzazione del percorso formativo selezionato
- Problema di perdita delle credenziali al riavvio dell'applicazione
- Errore nell'interpretazione delle date nel formato italiano
- Bug nella visualizzazione dell'anteprima dei dati
- Problemi di connessione con alcuni provider email

## [1.0.0] - 2025-04-15

### Aggiunto
- Funzionalità di base per caricare file Excel
- Generatore PDF per attestati di presenza
- Invio automatico di email con allegati PDF
- Interfaccia utente Streamlit con design responsive
- Supporto per provider email comuni (Gmail, Outlook, Libero)
- Memorizzazione credenziali SMTP in file .env
- Test di invio email singola
- Generazione PDF di test con dati fittizi

### Modificato
- Prima versione pubblica

### Risolto
- N/A
