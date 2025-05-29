import streamlit as st
import pandas as pd
import os
import tempfile
import time
from datetime import date
from utils.excel_reader import read_excel_file, validate_row, validate_excel_data
from utils.pdf_generator import generate_pdf
from utils.email_sender import send_email
import config

# Configurazione pagina Streamlit
st.set_page_config(
    page_title="Generatore Attestati di Presenza",
    page_icon="📝",
    layout="wide"
)

# Funzione per creare una directory temporanea per i PDF
def create_temp_dir():
    temp_dir = os.path.join(tempfile.gettempdir(), "attestati_temp")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

# Inizializzazione delle variabili di sessione
if 'df' not in st.session_state:
    st.session_state.df = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None
if 'logo' not in st.session_state:
    st.session_state.logo = None
if 'firma' not in st.session_state:
    st.session_state.firma = None
if 'smtp_configured' not in st.session_state:
    # Verifica se le credenziali SMTP sono state configurate
    st.session_state.smtp_configured = (
        config.SMTP_USERNAME != "" and 
        config.SMTP_PASSWORD != ""
    )
    
# Debug: print dei valori di configurazione all'avvio (visibili nei log)
print(f"SMTP Server: {config.SMTP_SERVER}")
print(f"SMTP Port: {config.SMTP_PORT}")
print(f"SMTP Username: {config.SMTP_USERNAME}")
print(f"SMTP Password set: {'Sì' if config.SMTP_PASSWORD else 'No'}")
print(f"SMTP Configured: {st.session_state.smtp_configured}")

# Funzione per generare PDF e inviare email
def process_attestato(row, logo_path, firma_path, send_mail=True):
    # Crea un dizionario con i dati per il PDF
    pdf_data = {
        'nome_cognome': row['nome_cognome'],
        'data': row['data'],
        'ora_inizio': row['ora_inizio'],
        'ora_fine': row['ora_fine'],
        'aula': row['aula'],
        'dipartimento': row['dipartimento'],
        'indirizzo': row['indirizzo'],
        'tipo_lezione': row['tipo_lezione'],
        'tipo_percorso': row['tipo_percorso'],
        'classe_concorso': row['classe_concorso']
    }
    
    # Genera il PDF
    output_dir = create_temp_dir()
    # Usa sempre il modello in presenza per la versione base dell'app
    pdf_path = generate_pdf(pdf_data, logo_path, firma_path, output_dir, "presenza")
    
    if pdf_path is None:
        return False, "Errore nella generazione del PDF"
    
    # Invia l'email se richiesto
    if send_mail:
        # Determina il firmatario dell'email
        if config.DOCENTE_CORSO:
            firmatario = f"Centro CAFIS\n{config.DIRETTORE_CAFIS}\nProf. {config.DOCENTE_CORSO}"
        else:
            firmatario = f"Centro CAFIS\n{config.DIRETTORE_CAFIS}"
        
        # Formatta il corpo dell'email con tutti i segnaposto disponibili
        email_body = config.EMAIL_BODY.format(
            nome_cognome=row['nome_cognome'],
            data=row['data'],
            firmatario=firmatario,
            universita=config.UNIVERSITA
        )
        
        # Invia l'email
        success, message = send_email(
            row['email'], 
            config.EMAIL_SUBJECT, 
            email_body, 
            pdf_path
        )
        
        if not success:
            return False, message
            
    return True, pdf_path

# Titolo dell'applicazione
st.title("📝 Generatore Attestati di Presenza")
st.markdown("### Università degli Studi Roma Tre - Centro CAFIS")
st.divider()

# Creazione dei tab
tab1, tab2, tab3 = st.tabs(["Generazione Attestati", "Test Email", "Download Template"])

# Sidebar per le configurazioni
with st.sidebar:
    st.header("Configurazioni")
    
    # Sezione per caricare il logo
    st.subheader("Logo")
    logo_file = st.file_uploader("Carica il logo dell'università", type=["png", "jpg", "jpeg"], key="logo_uploader")
    if logo_file:
        # Salva il logo in una directory temporanea
        temp_dir = create_temp_dir()
        logo_path = os.path.join(temp_dir, "logo.png")
        with open(logo_path, "wb") as f:
            f.write(logo_file.getbuffer())
        st.session_state.logo = logo_path
        st.success("Logo caricato con successo!")
    
    # Sezione per caricare la firma
    st.subheader("Firma")
    firma_file = st.file_uploader("Carica l'immagine della firma", type=["png", "jpg", "jpeg"], key="firma_uploader")
    if firma_file:
        # Salva la firma in una directory temporanea
        temp_dir = create_temp_dir()
        firma_path = os.path.join(temp_dir, "firma.png")
        with open(firma_path, "wb") as f:
            f.write(firma_file.getbuffer())
        st.session_state.firma = firma_path
        st.success("Firma caricata con successo!")
    
    # Sezione per configurare le credenziali SMTP
    st.subheader("Configurazione Email")
    if not st.session_state.smtp_configured:
        with st.form("smtp_form"):
            # Aggiungi un selettore per provider di posta comuni
            provider_options = list(config.EMAIL_PROVIDERS.keys())
            provider_names = [config.EMAIL_PROVIDERS[p]["name"] for p in provider_options]
            
            selected_provider_name = st.selectbox(
                "Provider di posta elettronica",
                provider_names,
                index=1,  # Default a Outlook
                key="provider_email"
            )
            
            # Trova la chiave del provider selezionato
            selected_provider = provider_options[provider_names.index(selected_provider_name)]
            provider_config = config.EMAIL_PROVIDERS[selected_provider]
            
            # Mostra informazioni sul provider selezionato
            st.info(provider_config["note"])
            
            # Informazioni aggiuntive per Outlook
            if selected_provider == "outlook":
                st.warning("""
                **Importante per Outlook.com / Office 365:**
                
                Per utilizzare Outlook.com o Office 365, è necessario:
                1. Attivare l'autenticazione a due fattori
                2. Creare una "Password per app" specifica
                
                Per creare una password per app:
                1. Accedi a [account.microsoft.com/security](https://account.microsoft.com/security)
                2. Vai a "Opzioni di sicurezza avanzate"
                3. Sotto "Password per app", crea una nuova password
                4. Copia e incolla questa password qui sotto (non la password del tuo account Microsoft)
                """)
            
            # Campi di configurazione
            smtp_server = st.text_input(
                "Server SMTP", 
                provider_config["server"] if selected_provider != "custom" else "",
                key="smtp_server"
            )
            smtp_port = st.number_input(
                "Porta SMTP", 
                value=provider_config["port"],
                key="smtp_port"
            )
            
            # Opzione per TLS/SSL
            encryption_type = st.selectbox(
                "Crittografia", 
                ["STARTTLS", "SSL/TLS", "Nessuna"],
                index=0 if provider_config["encryption"] == "STARTTLS" else 
                      1 if provider_config["encryption"] == "SSL/TLS" else 2,
                key="encryption_type"
            )
            smtp_use_tls = encryption_type == "STARTTLS"
            smtp_use_ssl = encryption_type == "SSL/TLS"
            
            # Se SSL/TLS è selezionato, aggiorna la porta a meno che non sia già stata modificata
            if smtp_use_ssl and smtp_port == 587:
                smtp_port = 465
            
            st.markdown("---")
            st.markdown("### Configurazione degli indirizzi email")
            
            st.info("**Informazione sugli indirizzi email**\n\n"
                   "Questo sistema permette di utilizzare due indirizzi email distinti:\n"
                   "1. Un indirizzo per l'autenticazione sul server Microsoft\n"
                   "2. Un indirizzo che i destinatari vedranno come 'Rispondi a'")
            
            # Credenziali
            smtp_username = st.text_input("Email per autenticazione sul server", 
                                         placeholder="es. pef_presenze@os.uniroma3.it",
                                         help="Questo è l'indirizzo email configurato sul server Microsoft e usato per l'autenticazione",
                                         key="smtp_username")
            smtp_password = st.text_input("Password", type="password", key="smtp_password")
            
            # Campo Reply-To con spiegazione migliorata
            smtp_reply_to = st.text_input("Indirizzo email visibile ai destinatari (Reply-To)", 
                                         placeholder="es. pef.presenze@uniroma3.it",
                                         help="Questo è l'indirizzo email che i destinatari vedranno come indirizzo di risposta. Quando risponderanno alle email, le risposte arriveranno a questo indirizzo.",
                                         key="smtp_reply_to")
            
            if smtp_username and not smtp_reply_to:
                st.caption("Se non specifichi un indirizzo di risposta, verrà utilizzato lo stesso indirizzo di autenticazione.")
            
            submit_smtp = st.form_submit_button("Salva configurazione")
            
            if submit_smtp:
                if not smtp_username or not smtp_password:
                    st.error("Inserisci sia l'email mittente che la password")
                else:
                    # Importa il modulo per salvare le credenziali
                    from utils.credentials_manager import save_smtp_credentials
                    
                    # Aggiorna le configurazioni SMTP
                    config.SMTP_SERVER = smtp_server
                    config.SMTP_PORT = smtp_port
                    config.SMTP_USERNAME = smtp_username
                    config.SMTP_PASSWORD = smtp_password
                    config.SMTP_USE_TLS = smtp_use_tls
                    
                    # Gestisci l'indirizzo Reply-To
                    if smtp_reply_to and smtp_reply_to.strip():
                        config.SMTP_REPLY_TO = smtp_reply_to.strip()
                    else:
                        # Se non specificato, usa l'email mittente come Reply-To
                        config.SMTP_REPLY_TO = smtp_username
                    
                    # Salva le credenziali nel file .env
                    saved = save_smtp_credentials(
                        smtp_server, 
                        smtp_port, 
                        smtp_username, 
                        smtp_password, 
                        smtp_use_tls,
                        smtp_reply_to.strip() if smtp_reply_to and smtp_reply_to.strip() else None
                    )
                    
                    if saved:
                        st.session_state.smtp_configured = True
                        st.success("Configurazione SMTP salvata con successo!")
                    else:
                        st.warning("Configurazione SMTP salvata solo per questa sessione. Potrebbe non persistere al riavvio dell'applicazione.")
                    
                    st.rerun()
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Configurazione del server email**\n\n"
                   f"**Server SMTP:** {config.SMTP_SERVER}\n"
                   f"**Porta:** {config.SMTP_PORT}\n"
                   f"**Username:** {config.SMTP_USERNAME}")
        
        with col2:
            visible_email = config.SMTP_REPLY_TO if hasattr(config, 'SMTP_REPLY_TO') and config.SMTP_REPLY_TO else config.SMTP_USERNAME
            st.info(f"**Come appare agli utenti**\n\n"
                   f"**Da:** {config.SMTP_USERNAME}\n"
                   f"**Risposte inviate a:** {visible_email}")
            
        if st.button("ℹ️ Come funzionano le email nel sistema", help="Clicca per saperne di più"):
            st.markdown("""
            ### Indirizzi email nel sistema
            
            Il sistema utilizza due indirizzi email:
            
            1. **Indirizzo per autenticazione server** (`{}`): 
               Questo indirizzo è configurato nel server Microsoft ed è utilizzato per l'autenticazione SMTP.
            
            2. **Indirizzo visibile per le risposte** (`{}`): 
               Questo è l'indirizzo che riceverà le risposte quando i destinatari risponderanno alle email.
            
            Questa configurazione ti permette di utilizzare un indirizzo istituzionale per l'invio, ma ricevere le risposte
            su un indirizzo più semplice da ricordare o più comunemente utilizzato.
            """.format(
                config.SMTP_USERNAME,
                visible_email
            ))
            
        if st.button("Modifica configurazione email"):
            st.session_state.smtp_configured = False
            st.rerun()
        if st.button("Modifica configurazione email", key="modifica_config_email_button"):
            st.session_state.smtp_configured = False
            st.rerun()
    
    st.subheader("Informazioni Centro CAFIS e Firmatari")
    
    col_dir1, col_dir2 = st.columns(2)
    with col_dir1:
        direttore = st.text_input("Nome Direttore Centro CAFIS", config.DIRETTORE_CAFIS, key="direttore_cafis")
        if direttore != config.DIRETTORE_CAFIS:
            config.DIRETTORE_CAFIS = direttore
    
    with col_dir2:
        docente = st.text_input("Nome Docente del Corso (opzionale)", config.DOCENTE_CORSO, key="docente_corso")
        if docente != config.DOCENTE_CORSO:
            config.DOCENTE_CORSO = docente
    
    # Personalizzazione email
    st.subheader("Personalizza Email")
    with st.expander("Configura testo dell'email", expanded=False):
        st.markdown("Personalizza l'oggetto e il testo dell'email che verrà inviata con gli attestati.")
        
        email_subject = st.text_input("Oggetto dell'email", config.EMAIL_SUBJECT, key="config_email_subject")
        if email_subject != config.EMAIL_SUBJECT:
            config.EMAIL_SUBJECT = email_subject
        
        st.markdown("Nel testo puoi utilizzare i seguenti segnaposto:")
        st.markdown("- `{nome_cognome}`: Nome e cognome del destinatario")
        st.markdown("- `{data}`: Data della lezione")
        st.markdown("- `{firmatario}`: Il firmatario (Direttore CAFIS o Docente)")
        st.markdown("- `{universita}`: Nome dell'università")
        
        email_body = st.text_area("Testo dell'email", config.EMAIL_BODY, height=200, key="config_email_body")
        if email_body != config.EMAIL_BODY:
            config.EMAIL_BODY = email_body
            
        # Seleziona il firmatario dell'email
        firmatario_options = ["Direttore CAFIS", "Docente del Corso", "Entrambi"]
        firmatario_selezione = st.radio(
            "Firmatario dell'email",
            firmatario_options,
            horizontal=True,
            key="firmatario_selezione"
        )
        
        # Mostra anteprima
        st.markdown("### Anteprima dell'email")
        
        # Determina il firmatario in base alla selezione
        if firmatario_selezione == "Direttore CAFIS":
            firmatario = f"Centro CAFIS\n{config.DIRETTORE_CAFIS}"
        elif firmatario_selezione == "Docente del Corso" and config.DOCENTE_CORSO:
            firmatario = f"Prof. {config.DOCENTE_CORSO}"
        else:  # "Entrambi" o docente non specificato
            firmatario_text = f"Centro CAFIS\n{config.DIRETTORE_CAFIS}"
            if config.DOCENTE_CORSO:
                firmatario_text += f"\nProf. {config.DOCENTE_CORSO}"
            firmatario = firmatario_text
        
        # Mostra anteprima
        preview = config.EMAIL_BODY.format(
            nome_cognome="Mario Rossi",
            data="01/01/2025",
            firmatario=firmatario,
            universita=config.UNIVERSITA
        )
        st.code(preview, language="text")

# Contenuto principale
with tab1:
    st.header("Carica il file Excel con i dati")
    uploaded_file = st.file_uploader("Seleziona un file Excel", type=["xlsx", "xls"], key="excel_uploader")

    if uploaded_file:
        # Salva il nome del file
        st.session_state.file_name = uploaded_file.name            # Leggi il file Excel
        with st.spinner("Caricamento e validazione del file in corso..."):
                # Salva temporaneamente il file
                temp_dir = create_temp_dir()
                temp_file = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_file, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Leggi il file Excel
                df, error_message = read_excel_file(temp_file)
                
                if df is not None:
                    # Esegui la validazione avanzata
                    validation_errors = validate_excel_data(df)
                    
                    if not validation_errors:
                        st.session_state.df = df
                        st.success(f"File caricato con successo! {len(df)} record trovati.")
                    else:
                        # Mostra i primi 5 errori di validazione
                        st.error(f"Errori di validazione nel file Excel ({len(validation_errors)} errori totali):")
                        with st.expander("Dettagli degli errori (primi 5)", expanded=True):
                            for i, error in enumerate(validation_errors[:5]):
                                st.error(error)
                            if len(validation_errors) > 5:
                                st.warning(f"... e altri {len(validation_errors) - 5} errori. Correggi il file e ricaricalo.")
                else:
                    st.error(f"Errore nel caricamento del file: {error_message}")

    # Visualizza i dati se disponibili
    if st.session_state.df is not None:
        st.header("Dati caricati")
        
        df = st.session_state.df
        st.dataframe(df)
        
        # Sezione per generare i PDF e inviare le email
        st.header("Generazione Attestati e Invio Email")
        
        # Opzioni di generazione
        col1, col2 = st.columns(2)
        with col1:
            generate_all = st.checkbox("Genera tutti gli attestati", value=False, key="generate_all_attestati")
        with col2:
            send_email_option = st.checkbox("Invia email", value=True, key="send_email_option")
            
        # Configurazione avanzata per l'invio delle email
        with st.expander("Configurazione avanzata invio email", expanded=False):
            # Dimensione del blocco (quante email mandare alla volta)
            st.subheader("Configurazione blocchi e intervalli")
            col_email1, col_email2 = st.columns(2)
            with col_email1:
                BLOCK_SIZE = st.number_input(
                    "Numero di email per blocco", 
                    min_value=1, 
                    max_value=50, 
                    value=10,
                    help="Quante email inviare prima di fare una pausa",
                    key="main_block_size"
                )
            with col_email2:
                PAUSE_SECONDS = st.number_input(
                    "Intervallo tra i blocchi (secondi)", 
                    min_value=1, 
                    max_value=60, 
                    value=5,
                    help="Quanti secondi attendere tra un blocco di email e il successivo",
                    key="main_pause_seconds"
                )
            
            st.info(f"Le email verranno inviate a gruppi di {BLOCK_SIZE} con una pausa di {PAUSE_SECONDS} secondi tra un gruppo e l'altro. Questa configurazione aiuta a evitare blocchi da parte dei provider email.")
        
        # Bottone di generazione
        if st.button("Genera attestati", key="genera_attestati_button"):
            # Debug: mostra stato attuale delle credenziali SMTP
            smtp_debug = st.expander("Debug informazioni SMTP", expanded=False)
            with smtp_debug:
                st.write(f"SMTP Server: {config.SMTP_SERVER}")
                st.write(f"SMTP Port: {config.SMTP_PORT}")
                st.write(f"SMTP Username: {config.SMTP_USERNAME}")
                st.write(f"SMTP Password: {'*' * len(config.SMTP_PASSWORD) if config.SMTP_PASSWORD else 'Non impostata'}")
                st.write(f"SMTP Configured (session): {st.session_state.smtp_configured}")
            
            if not st.session_state.smtp_configured and send_email_option:
                st.error("Per inviare email, configura prima le credenziali SMTP nella sidebar")
            elif not config.SMTP_USERNAME or not config.SMTP_PASSWORD:
                st.error("Le credenziali SMTP non sono configurate correttamente. Ricontrolla la configurazione nella sidebar.")
            else:
                # Verifica se il logo e la firma sono stati caricati
                logo_path = st.session_state.logo if st.session_state.logo else None
                firma_path = st.session_state.firma if st.session_state.firma else None
                
                # Seleziona le righe da processare
                rows_to_process = df if generate_all else df.iloc[0:1]
                
                # Crea una barra di progresso
                progress_text = "Generazione attestati in corso. Attendere..."
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Contatori per i risultati
                success_count = 0
                error_count = 0
                success_messages = []
                error_messages = []
                
                # Dimensione del blocco e pausa tra i blocchi (in secondi) 
                # Usa i valori definiti nella configurazione avanzata
                # BLOCK_SIZE e PAUSE_SECONDS sono già definiti sopra
                
                # Processa ogni riga a blocchi
                total_rows = len(rows_to_process)
                for block_start in range(0, total_rows, BLOCK_SIZE):
                    # Determina fine del blocco corrente
                    block_end = min(block_start + BLOCK_SIZE, total_rows)
                    
                    # Visualizza informazioni sul blocco corrente
                    status_text.info(f"Elaborazione blocco {block_start // BLOCK_SIZE + 1} ({block_start+1}-{block_end} di {total_rows})")
                    
                    # Elabora ogni riga nel blocco corrente
                    for i in range(block_start, block_end):
                        row_index = i
                        row = rows_to_process.iloc[row_index]
                        
                        # Aggiorna la barra di progresso
                        progress = (i + 1) / total_rows
                        progress_bar.progress(progress)
                        
                        # Verifica che la riga sia valida
                        is_valid, error = validate_row(row)
                        if not is_valid:
                            error_count += 1
                            error_messages.append(f"Errore riga {i+1}: {error}")
                            continue
                        
                        # Genera il PDF e invia l'email
                        success, result = process_attestato(row, logo_path, firma_path, send_email_option)
                        
                        if success:
                            success_count += 1
                            success_messages.append(f"Attestato per {row['nome_cognome']} generato con successo")
                            if send_email_option:
                                success_messages[-1] += f" e inviato a {row['email']}"
                        else:
                            error_count += 1
                            error_messages.append(f"Errore per {row['nome_cognome']}: {result}")
                    
                    # Pausa tra i blocchi (solo se ci sono altri blocchi da elaborare)
                    if block_end < total_rows and send_email_option:
                        with st.spinner(f"Pausa di {PAUSE_SECONDS} secondi tra i blocchi di email..."):
                            time.sleep(PAUSE_SECONDS)
                
                # Resetta la barra di progresso
                progress_bar.empty()
                
                # Mostra i risultati
                if success_count > 0:
                    st.success(f"{success_count} attestati generati con successo")
                    for msg in success_messages:
                        st.write(f"✅ {msg}")
                
                if error_count > 0:
                    st.error(f"{error_count} errori durante la generazione")
                    for msg in error_messages:
                        st.write(f"❌ {msg}")
        
        # Aggiungi una nota informativa sul formato del file Excel
        st.divider()
        st.markdown("### Formato del file Excel")
        st.markdown("""
        Il file Excel deve contenere le seguenti colonne:
        - `nome_cognome`: Nome e cognome del partecipante
        - `data`: Data della lezione (formato: GG/MM/AAAA)
        - `ora_inizio`: Ora di inizio lezione
        - `ora_fine`: Ora di fine lezione
        - `aula`: Aula della lezione
        - `dipartimento`: Nome del dipartimento
        - `indirizzo`: Indirizzo del dipartimento
        - `tipo_lezione`: Tipo di lezione seguita
        - `tipo_percorso`: Tipo di percorso (uno tra: "PeF 60", "PeF 30 all.2", "PeF 36", "PeF 30 art. 13")
        - `classe_concorso`: Classe di concorso
        - `email`: Indirizzo email del richiedente
        """)

with tab2:
    st.header("Test Email")
    st.markdown("""
    Questa sezione ti permette di inviare un'email di prova per verificare che la configurazione SMTP sia corretta.
    Compila i campi sottostanti e opzionalmente genera un attestato di esempio.
    """)
    
    # Crea due colonne
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configurazione Email")
        email_to_test = st.text_input("Email del destinatario", key="email_destinatario_test")
        test_email_subject = st.text_input("Oggetto dell'email", value=config.EMAIL_SUBJECT, key="test_email_subject")
        
        # Determina il firmatario per l'email di test
        if config.DOCENTE_CORSO:
            firmatario_test = f"Centro CAFIS\n{config.DIRETTORE_CAFIS}\nProf. {config.DOCENTE_CORSO}"
        else:
            firmatario_test = f"Centro CAFIS\n{config.DIRETTORE_CAFIS}"
        
        # Preferisci utilizzare il template dell'applicazione
        template_test = config.EMAIL_BODY.format(
            nome_cognome="Utente di Prova",
            data="01/01/2025",
            firmatario=firmatario_test,
            universita=config.UNIVERSITA
        )
        
        test_email_body = st.text_area("Corpo dell'email", value=template_test, height=200, key="test_email_body")
    
    with col2:
        st.subheader("Dati Attestato di Prova")
        nome_cognome_test = st.text_input("Nome e Cognome", value="Utente di Prova", key="test_nome_cognome")
        data_test = st.date_input("Data", value=date.today(), key="test_data")
        ora_inizio_test = st.text_input("Ora Inizio", value="09:00", key="test_ora_inizio")
        ora_fine_test = st.text_input("Ora Fine", value="11:00", key="test_ora_fine")
        aula_test = st.text_input("Aula", value="A1", key="test_aula")
        dipartimento_test = st.text_input("Dipartimento", value="Scienze della Formazione", key="test_dipartimento")
        indirizzo_test = st.text_input("Indirizzo", value="Via del Castro Pretorio 20", key="test_indirizzo")
        tipo_lezione_test = st.text_input("Tipo Lezione", value="Didattica generale", key="test_tipo_lezione")
        
        tipo_percorso_options = [
            "PeF 60",
            "PeF 30 all.2",
            "PeF 36",
            "PeF 30 art. 13"
        ]
        tipo_percorso_test = st.selectbox("Tipo Percorso", tipo_percorso_options, key="test_tipo_percorso")
        classe_concorso_test = st.text_input("Classe di Concorso", value="A-01", key="test_classe_concorso")
    
    # Opzioni
    col1_opt, col2_opt = st.columns(2)
    with col1_opt:
        genera_pdf_test = st.checkbox("Genera attestato di esempio", value=True, key="genera_pdf_test")
    with col2_opt:
        test_multiple = st.checkbox("Test invio multiplo", value=False, 
                                    help="Simula l'invio di più email allo stesso indirizzo per testare l'invio a blocchi",
                                    key="test_multiple")
    
    if test_multiple:
        # Opzioni per il test multiplo
        col_multi1, col_multi2 = st.columns(2)
        with col_multi1:
            num_emails = st.slider("Numero di email da inviare", 1, 30, 15, key="num_emails_slider")
        
        # Configurazione avanzata per l'invio delle email di test
        with st.expander("Configurazione avanzata", expanded=False):
            # Dimensione del blocco (quante email mandare alla volta)
            col_conf1, col_conf2 = st.columns(2)
            with col_conf1:
                test_block_size = st.number_input(
                    "Numero di email per blocco", 
                    min_value=1, 
                    max_value=20, 
                    value=10,
                    help="Quante email inviare prima di fare una pausa",
                    key="test_block_size"
                )
            with col_conf2:
                test_pause_seconds = st.number_input(
                    "Intervallo tra i blocchi (secondi)", 
                    min_value=1, 
                    max_value=30, 
                    value=5,
                    help="Quanti secondi attendere tra un blocco di email e il successivo",
                    key="test_pause_seconds"
                )
        
        st.info(f"Verranno inviate {num_emails} email allo stesso indirizzo a blocchi di {test_block_size}, con una pausa di {test_pause_seconds} secondi tra i blocchi.")
    
    # Bottone per inviare l'email di test
    if st.button("Invia email di test", key="invia_test_button"):
        if not st.session_state.smtp_configured:
            st.error("Per inviare email, configura prima le credenziali SMTP nella sidebar")
        elif not email_to_test:
            st.error("Inserisci l'email del destinatario")
        else:
            # Determina quante email inviare
            num_to_send = num_emails if test_multiple else 1
            
            # Crea elementi per feedback in tempo reale
            progress_bar = st.progress(0)
            status_text = st.empty()
            results_area = st.empty()
            
            # Dimensione del blocco e pausa tra i blocchi (in secondi)
            # Usa i valori personalizzati se definiti nel test multiplo, altrimenti valori predefiniti
            BLOCK_SIZE = test_block_size if test_multiple else 10
            PAUSE_SECONDS = test_pause_seconds if test_multiple else 5
            
            success_count = 0
            error_count = 0
            pdf_path = None
            
            # Processa ogni email a blocchi
            for block_start in range(0, num_to_send, BLOCK_SIZE):
                # Determina fine del blocco corrente
                block_end = min(block_start + BLOCK_SIZE, num_to_send)
                
                # Visualizza informazioni sul blocco corrente
                status_text.info(f"Elaborazione blocco {block_start // BLOCK_SIZE + 1} ({block_start+1}-{block_end} di {num_to_send})")
                
                # Elabora ogni email nel blocco corrente
                for i in range(block_start, block_end):
                    # Genera il PDF solo la prima volta o se è richiesto per ogni email
                    if i == 0 or (test_multiple and genera_pdf_test):
                        with st.spinner("Generazione PDF in corso..."):
                            # Crea un dizionario con i dati per il PDF
                            pdf_data = {
                                'nome_cognome': f"{nome_cognome_test} {i+1}" if test_multiple else nome_cognome_test,
                                'data': data_test.strftime("%d/%m/%Y"),
                                'ora_inizio': ora_inizio_test,
                                'ora_fine': ora_fine_test,
                                'aula': aula_test,
                                'dipartimento': dipartimento_test,
                                'indirizzo': indirizzo_test,
                                'tipo_lezione': tipo_lezione_test,
                                'tipo_percorso': tipo_percorso_test,
                                'classe_concorso': classe_concorso_test
                            }
                            
                            # Verifica se il logo e la firma sono stati caricati
                            logo_path = st.session_state.logo if st.session_state.logo else None
                            firma_path = st.session_state.firma if st.session_state.firma else None
                            
                            # Genera il PDF
                            output_dir = create_temp_dir()
                            # Usa sempre il modello in presenza per la versione base dell'app
                            pdf_path = generate_pdf(pdf_data, logo_path, firma_path, output_dir, "presenza")
                            
                            if pdf_path is None:
                                st.error("Errore nella generazione del PDF")
                                st.stop()
                    
                    # Aggiorna la barra di progresso
                    progress = (i + 1) / num_to_send
                    progress_bar.progress(progress)
                    
                    # Invia l'email
                    status_text.info(f"Invio email {i+1} di {num_to_send}...")
                    subject = f"{test_email_subject} {i+1}" if test_multiple else test_email_subject
                    
                    # Determina il firmatario per l'email di test
                    if config.DOCENTE_CORSO:
                        firmatario_test = f"Centro CAFIS\n{config.DIRETTORE_CAFIS}\nProf. {config.DOCENTE_CORSO}"
                    else:
                        firmatario_test = f"Centro CAFIS\n{config.DIRETTORE_CAFIS}"
                    
                    # Sostituisci i segnaposto nel testo dell'email
                    email_body_formatted = test_email_body
                    try:
                        email_body_formatted = test_email_body.format(
                            nome_cognome=nome_cognome_test,
                            data=data_test.strftime("%d/%m/%Y"),
                            firmatario=firmatario_test,
                            universita=config.UNIVERSITA
                        )
                    except Exception:
                        # Se la formattazione fallisce, usa il testo così com'è
                        email_body_formatted = test_email_body
                    
                    success, message = send_email(
                        email_to_test, 
                        subject, 
                        email_body_formatted, 
                        pdf_path if genera_pdf_test else None
                    )
                    
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        results_area.error(f"Errore nell'invio dell'email {i+1}: {message}")
                
                # Mostra il resoconto parziale
                results_area.info(f"Inviate {success_count} email su {i+1}, {error_count} errori")
                
                # Pausa tra i blocchi (solo se ci sono altri blocchi da elaborare)
                if block_end < num_to_send:
                    with st.spinner(f"Pausa di {PAUSE_SECONDS} secondi tra i blocchi di email..."):
                        time.sleep(PAUSE_SECONDS)
            
            # Resoconto finale
            if success_count == num_to_send:
                results_area.success(f"Tutte le {num_to_send} email sono state inviate con successo a {email_to_test}")
            else:
                results_area.warning(f"Inviate {success_count} email su {num_to_send} ({error_count} errori)")
                
            # Permetti il download del PDF se generato
            if pdf_path and genera_pdf_test:
                    if pdf_path:
                        # Crea un link per il download del PDF generato
                        with open(pdf_path, "rb") as file:
                            st.download_button(
                                label="Scarica il PDF generato",
                                data=file,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf"
                            )
            else:
                    st.error(f"Errore nell'invio dell'email: {message}")
                    
    # Informazioni aggiuntive
    st.divider()
    st.markdown("""
    **Nota**: Prima di inviare l'email di test, assicurati di aver configurato correttamente le credenziali SMTP nella barra laterale.
    
    Se utilizzi Gmail:
    1. Attiva l'autenticazione a due fattori
    2. Genera una "Password per le app" specifica per questa applicazione
    
    Se utilizzi Outlook.com / Office 365:
    1. Usa `smtp-mail.outlook.com` come server SMTP
    2. Usa la porta `587` con STARTTLS
    3. Attiva l'autenticazione a due fattori sul tuo account Microsoft
    4. Usa una "Password per app" invece della tua password normale
    5. Assicurati di utilizzare l'indirizzo email completo come nome utente
    """)

# Contenuto per il tab "Download Template"
with tab3:
    st.header("Download Template Excel")
    st.markdown("""
    Scarica un file Excel di esempio precompilato con dati fittizi. 
    Questo template può essere utilizzato come modello per preparare i dati per la generazione di attestati multipli.
    """)
    
    # Leggi il file template come bytes
    try:
        with open("esempi/template_attestati.xlsx", "rb") as f:
            template_data = f.read()
            
        # Crea un pulsante per il download
        st.download_button(
            label="Scarica Template Excel",
            data=template_data,
            file_name="template_attestati.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Clicca per scaricare un file Excel precompilato con dati di esempio"
        )
        
        st.success("Il file template contiene 8 record di esempio con diversi tipi di percorsi formativi.")
        
        st.markdown("""
        ### Struttura del template
        
        Il file Excel deve contenere le seguenti colonne:
        
        | Colonna | Descrizione | Formato/Esempio |
        | ------- | ----------- | --------------- |
        | nome_cognome | Nome e cognome del partecipante | Mario Rossi |
        | data | Data della lezione | GG/MM/AAAA (es. 15/05/2025) |
        | ora_inizio | Ora di inizio lezione | HH:MM (es. 09:00) |
        | ora_fine | Ora di fine lezione | HH:MM (es. 11:00) |
        | aula | Aula della lezione | A1 |
        | dipartimento | Nome del dipartimento | Scienze della Formazione |
        | indirizzo | Indirizzo del dipartimento | Via del Castro Pretorio 20, Roma |
        | tipo_lezione | Tipo di lezione seguita | Didattica generale |
        | tipo_percorso | Tipo di percorso formativo | PeF 60, PeF 30 all.2, PeF 36 o PeF 30 art. 13 |
        | classe_concorso | Classe di concorso | A-01 |
        | email | Indirizzo email del richiedente | mario.rossi@esempio.com |
        """)
        
    except Exception as e:
        st.error(f"Impossibile caricare il file template: {e}")
        st.info("Puoi comunque preparare un file Excel con le colonne indicate sotto.")
        
        st.markdown("""
        ### Crea il tuo file Excel
        
        Il file Excel deve contenere le seguenti colonne:
        
        - `nome_cognome`
        - `data` (formato GG/MM/AAAA)
        - `ora_inizio`
        - `ora_fine`
        - `aula`
        - `dipartimento`
        - `indirizzo`
        - `tipo_lezione`
        - `tipo_percorso` (uno tra: "PeF 60", "PeF 30 all.2", "PeF 36", "PeF 30 art. 13")
        - `classe_concorso`
        - `email`
        """)

# Nota a piè di pagina
st.divider()
st.markdown("""
<div style="text-align: center">
    <p>© 2025 Centro CAFIS - Università degli Studi Roma Tre</p>
</div>
""", unsafe_allow_html=True)
