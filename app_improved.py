# filepath: /Users/desi76/repo-git-nugh/giustificativi/app.py
import streamlit as st
import pandas as pd
import os
import tempfile
import time
from datetime import date
from utils.excel_reader import read_excel_file, validate_row, validate_excel_data
from utils.pdf_generator import generate_pdf
from utils.email_sender import send_email, check_smtp_connection
from utils.ui_components import (
    custom_header, show_info_box, progress_bar_with_status, 
    show_help_section, show_data_preview, show_footer
)
from utils.template_generator import create_template_excel, create_empty_template
import config

# Import error logger se disponibile
try:
    from utils.error_logger import error_logger
except ImportError:
    error_logger = None

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

# Assicura che la directory logs esista
logs_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(logs_dir, exist_ok=True)

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

# Funzione per generare PDF e inviare email
def process_attestato(row, logo_path, firma_path, send_mail=True):
    """
    Elabora un singolo attestato: genera il PDF e invia l'email se richiesto.
    
    Args:
        row (pd.Series): Una riga del DataFrame con i dati dell'attestato
        logo_path (str): Percorso del logo
        firma_path (str): Percorso della firma
        send_mail (bool): Se True, invia l'email con l'attestato
        
    Returns:
        bool, str: (True, pdf_path) se l'operazione ha successo, (False, error_message) altrimenti
    """
    try:
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
        
        # Genera il PDF con il modello selezionato
        output_dir = create_temp_dir()
        modello = st.session_state.get('attestato_modello', 'presenza')
        pdf_path = generate_pdf(pdf_data, logo_path, firma_path, output_dir, modello)
        
        if pdf_path is None:
            error_msg = "Errore nella generazione del PDF"
            if error_logger:
                error_logger.log_error(error_msg, error_code="PDF-001")
            return False, error_msg
        
        # Invia l'email se richiesto
        if send_mail:
            try:
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
                    if error_logger:
                        error_logger.log_error(f"Errore invio email: {message}", error_code="EMAIL-001")
                    return False, message
            except Exception as e:
                error_msg = f"Errore nella formattazione dell'email: {str(e)}"
                if error_logger:
                    error_logger.log_error(error_msg, exception=e, error_code="EMAIL-002")
                return False, error_msg
                
        return True, pdf_path
    
    except Exception as e:
        error_msg = f"Errore nell'elaborazione dell'attestato: {str(e)}"
        if error_logger:
            error_logger.log_error(error_msg, exception=e, error_code="PROC-001")
        return False, error_msg

# Intestazione dell'applicazione
custom_header(
    "Generatore Attestati di Presenza",
    "Università degli Studi Roma Tre - Centro CAFIS",
    icon="📝"
)

# Creazione dei tab
tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Generazione Attestati", 
    "✉️ Test Email", 
    "📥 Download Template",
    "❓ Aiuto"
])

# Sidebar per le configurazioni
with st.sidebar:
    st.header("Configurazioni")
    
    # Sezione per caricare il logo
    st.subheader("Logo")
    logo_file = st.file_uploader("Carica il logo dell'università", type=["png", "jpg", "jpeg"])
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
    firma_file = st.file_uploader("Carica l'immagine della firma", type=["png", "jpg", "jpeg"])
    if firma_file:
        # Salva la firma in una directory temporanea
        temp_dir = create_temp_dir()
        firma_path = os.path.join(temp_dir, "firma.png")
        with open(firma_path, "wb") as f:
            f.write(firma_file.getbuffer())
        st.session_state.firma = firma_path
        st.success("Firma caricata con successo!")
    
    # Sezione per personalizzare l'attestato
    st.subheader("Modello Attestato")
    
    # Inizializza la variabile di sessione per il modello se non esiste
    if 'attestato_modello' not in st.session_state:
        st.session_state.attestato_modello = "presenza"
    
    # Inizializza le variabili di sessione temporanee per tutti i modelli se non esistono
    if not hasattr(config, 'ATTESTATO_PRESENZA_TEMP'):
        config.ATTESTATO_PRESENZA_TEMP = config.ATTESTATO_PRESENZA
    
    if not hasattr(config, 'ATTESTATO_TELEMATICO_TEMP'):
        config.ATTESTATO_TELEMATICO_TEMP = config.ATTESTATO_TELEMATICO
        
    if not hasattr(config, 'ATTESTATO_PERSONALIZZATO_TEMP'):
        config.ATTESTATO_PERSONALIZZATO_TEMP = config.ATTESTATO_PERSONALIZZATO
        
    # Selettore per il tipo di modello
    attestato_tipo = st.radio(
        "Seleziona il tipo di attestato",
        ["Lezione in presenza", "Lezione telematica", "Personalizzato"],
        index=0 if st.session_state.attestato_modello == "presenza" else 
              1 if st.session_state.attestato_modello == "telematico" else 2
    )
    
    # Aggiorna la variabile di sessione in base alla selezione
    if attestato_tipo == "Lezione in presenza":
        st.session_state.attestato_modello = "presenza"
    elif attestato_tipo == "Lezione telematica":
        st.session_state.attestato_modello = "telematico"
    else:
        st.session_state.attestato_modello = "personalizzato"
    
    # Informazione sui segnaposti disponibili
    st.info("Puoi utilizzare i seguenti segnaposti nel testo dell'attestato: {nome_cognome}, {data} (data della lezione), {data_rilascio} (data odierna di rilascio), {ora_inizio}, {ora_fine}, {aula}, {dipartimento}, {indirizzo}, {tipo_lezione}, {tipo_percorso}, {classe_concorso}, {universita}, {direttore_cafis}")
    
    # Aggiungi nota sulla differenza tra data lezione e data rilascio
    st.caption("**Nota:** {data} rappresenta la data della lezione, mentre {data_rilascio} rappresenta la data odierna in cui viene emesso l'attestato.")
    
    # Gestione dei diversi modelli
    if attestato_tipo == "Lezione in presenza":
        with st.expander("Modifica modello per lezione in presenza", expanded=True):
            # Area di testo per la personalizzazione
            testo_presenza = st.text_area(
                "Testo dell'attestato per lezioni in presenza",
                value=config.ATTESTATO_PRESENZA_TEMP,
                height=400
            )
            
            # Aggiorna il valore quando cambia
            if testo_presenza != config.ATTESTATO_PRESENZA_TEMP:
                config.ATTESTATO_PRESENZA_TEMP = testo_presenza
            
            col1, col2 = st.columns(2)
            # Pulsante per salvare il modello
            if col1.button("Salva modello in presenza"):
                config.ATTESTATO_PRESENZA = config.ATTESTATO_PRESENZA_TEMP
                # Aggiorna anche il modello personalizzato se basato su questo
                if config.ATTESTATO_PERSONALIZZATO == config.ATTESTATO_PRESENZA:
                    config.ATTESTATO_PERSONALIZZATO = config.ATTESTATO_PRESENZA
                    config.ATTESTATO_PERSONALIZZATO_TEMP = config.ATTESTATO_PRESENZA
                st.success("Modello per lezioni in presenza salvato con successo!")
                
            # Pulsante per ripristinare il modello originale
            if col2.button("Ripristina modello originale (presenza)"):
                # Reimporta il modello originale dal file config_templates
                from config_templates import ATTESTATO_PRESENZA as MODELLO_ORIGINALE
                config.ATTESTATO_PRESENZA = MODELLO_ORIGINALE
                config.ATTESTATO_PRESENZA_TEMP = MODELLO_ORIGINALE
                st.success("Modello ripristinato alle impostazioni originali!")
    
    elif attestato_tipo == "Lezione telematica":
        with st.expander("Modifica modello per lezione telematica", expanded=True):
            # Area di testo per la personalizzazione
            testo_telematico = st.text_area(
                "Testo dell'attestato per lezioni telematiche",
                value=config.ATTESTATO_TELEMATICO_TEMP,
                height=400
            )
            
            # Aggiorna il valore quando cambia
            if testo_telematico != config.ATTESTATO_TELEMATICO_TEMP:
                config.ATTESTATO_TELEMATICO_TEMP = testo_telematico
            
            col1, col2 = st.columns(2)
            # Pulsante per salvare il modello
            if col1.button("Salva modello telematico"):
                config.ATTESTATO_TELEMATICO = config.ATTESTATO_TELEMATICO_TEMP
                # Aggiorna anche il modello personalizzato se basato su questo
                if config.ATTESTATO_PERSONALIZZATO == config.ATTESTATO_TELEMATICO:
                    config.ATTESTATO_PERSONALIZZATO = config.ATTESTATO_TELEMATICO
                    config.ATTESTATO_PERSONALIZZATO_TEMP = config.ATTESTATO_TELEMATICO
                st.success("Modello per lezioni telematiche salvato con successo!")
                
            # Pulsante per ripristinare il modello originale
            if col2.button("Ripristina modello originale (telematico)"):
                # Reimporta il modello originale dal file config_templates
                from config_templates import ATTESTATO_TELEMATICO as MODELLO_ORIGINALE
                config.ATTESTATO_TELEMATICO = MODELLO_ORIGINALE
                config.ATTESTATO_TELEMATICO_TEMP = MODELLO_ORIGINALE
                st.success("Modello ripristinato alle impostazioni originali!")
    
    else:  # Personalizzato
        with st.expander("Personalizza testo dell'attestato", expanded=True):
            # Area di testo per la personalizzazione
            testo_personalizzato = st.text_area(
                "Testo dell'attestato personalizzato",
                value=config.ATTESTATO_PERSONALIZZATO_TEMP,
                height=400
            )
            
            # Aggiorna il valore personalizzato quando cambia
            if testo_personalizzato != config.ATTESTATO_PERSONALIZZATO_TEMP:
                config.ATTESTATO_PERSONALIZZATO_TEMP = testo_personalizzato
            
            col1, col2, col3 = st.columns(3)
            # Pulsante per salvare il modello personalizzato
            if col1.button("Salva modello personalizzato"):
                config.ATTESTATO_PERSONALIZZATO = config.ATTESTATO_PERSONALIZZATO_TEMP
                st.success("Modello personalizzato salvato con successo!")
                
            # Pulsanti per ripristinare basati su modelli predefiniti
            if col2.button("Usa modello in presenza"):
                config.ATTESTATO_PERSONALIZZATO = config.ATTESTATO_PRESENZA
                config.ATTESTATO_PERSONALIZZATO_TEMP = config.ATTESTATO_PRESENZA
                st.success("Modello personalizzato impostato sul modello in presenza!")
                st.rerun()
                
            if col3.button("Usa modello telematico"):
                config.ATTESTATO_PERSONALIZZATO = config.ATTESTATO_TELEMATICO
                config.ATTESTATO_PERSONALIZZATO_TEMP = config.ATTESTATO_TELEMATICO
                st.success("Modello personalizzato impostato sul modello telematico!")
                st.rerun()
    
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
                index=1  # Default a Outlook
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
                provider_config["server"] if selected_provider != "custom" else ""
            )
            smtp_port = st.number_input(
                "Porta SMTP", 
                value=provider_config["port"]
            )
            
            # Opzione per TLS/SSL
            encryption_type = st.selectbox(
                "Crittografia", 
                ["STARTTLS", "SSL/TLS", "Nessuna"],
                index=0 if provider_config["encryption"] == "STARTTLS" else 
                      1 if provider_config["encryption"] == "SSL/TLS" else 2
            )
            smtp_use_tls = encryption_type == "STARTTLS"
            smtp_use_ssl = encryption_type == "SSL/TLS"
            
            # Se SSL/TLS è selezionato, aggiorna la porta a meno che non sia già stata modificata
            if smtp_use_ssl and smtp_port == 587:
                smtp_port = 465
            
            st.markdown("---")
            st.markdown("### Configurazione degli indirizzi email")
            
            st.info("**IMPORTANTE: Configurazione degli indirizzi email**\n\n"
                   "Questo sistema utilizza due indirizzi email distinti:\n"
                   "1. **Indirizzo tecnico** (@os.uniroma3.it): usato solo per l'autenticazione SMTP, mai visibile ai destinatari\n"
                   "2. **Indirizzo pubblico** (@uniroma3.it): indirizzo che i destinatari vedranno come mittente delle email")
            
            # Credenziali
            st.markdown("#### Configurazione Tecnica (Solo per Autenticazione)")
            smtp_username = st.text_input("Email tecnica per autenticazione", 
                                         placeholder="es. pef_presenze@os.uniroma3.it",
                                         help="Questo è l'indirizzo tecnico per l'autenticazione SMTP, non sarà mai visibile ai destinatari")
            smtp_password = st.text_input("Password dell'email tecnica", type="password")
            
            # Campo per indirizzo pubblico
            st.markdown("#### Configurazione Visibile (Mostrata ai Destinatari)")
            smtp_reply_to = st.text_input("Indirizzo email pubblico", 
                                         placeholder="es. pef.presenze@uniroma3.it",
                                         help="Questo è l'indirizzo che sarà visibile ai destinatari come mittente delle email e dove riceverai le risposte.")
            
            if smtp_username and not smtp_reply_to:
                st.caption("Se non specifichi un indirizzo di risposta, verrà utilizzato lo stesso indirizzo di autenticazione.")
            
            # Pulsante di test connessione
            st.markdown("---")
            test_connection = st.checkbox("Testa la connessione al server SMTP", value=False)
            
            submit_smtp = st.form_submit_button("Salva configurazione")
            
            if submit_smtp:
                if not smtp_username or not smtp_password:
                    st.error("Inserisci sia l'email mittente che la password")
                else:
                    # Se richiesto, testa la connessione
                    if test_connection:
                        with st.spinner("Verifica connessione al server SMTP..."):
                            connection_success, connection_message = check_smtp_connection(
                                smtp_server, smtp_port, smtp_use_tls
                            )
                            if not connection_success:
                                st.error(f"Errore nella connessione al server SMTP: {connection_message}")
                                st.stop()
                            else:
                                st.success("Connessione al server SMTP verificata con successo!")
                    
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
                   f"**Crittografia:** {'STARTTLS' if config.SMTP_USE_TLS else 'SSL/TLS' if hasattr(config, 'SMTP_USE_SSL') and config.SMTP_USE_SSL else 'Nessuna'}")
        
        with col2:
            visible_email = config.SMTP_REPLY_TO if hasattr(config, 'SMTP_REPLY_TO') and config.SMTP_REPLY_TO else config.SMTP_USERNAME
            st.info(f"**Configurazione indirizzi email**\n\n"
                   f"**Indirizzo tecnico:** {config.SMTP_USERNAME}\n"
                   f"**Indirizzo pubblico:** {visible_email}")
            
        if st.button("ℹ️ Come funzionano le email nel sistema", help="Clicca per saperne di più"):
            st.markdown("""
            ### Indirizzi email nel sistema
            
            Il sistema utilizza due indirizzi email distinti:
            
            1. **Indirizzo tecnico** (`{}`): 
               Questo indirizzo (@os.uniroma3.it) è configurato nel server Microsoft ed è utilizzato SOLO per l'autenticazione SMTP.
               **Non sarà mai visibile ai destinatari delle email**.
            
            2. **Indirizzo pubblico** (`{}`): 
               Questo è l'indirizzo (@uniroma3.it) che:
               - Appare come mittente dell'email ai destinatari
               - Riceve le risposte quando i destinatari risponderanno
            
            Questa configurazione permette di mantenere la separazione tra l'identità tecnica dell'account di autenticazione
            e l'identità pubblica visualizzata ai destinatari delle email.
            """.format(
                config.SMTP_USERNAME,
                visible_email
            ))
            
        if st.button("Modifica configurazione email"):
            st.session_state.smtp_configured = False
            st.rerun()
    
    st.subheader("Informazioni Centro CAFIS")
    direttore = st.text_input("Nome Direttore Centro CAFIS", config.DIRETTORE_CAFIS)
    if direttore != config.DIRETTORE_CAFIS:
        config.DIRETTORE_CAFIS = direttore
    
    # Sezione per visualizzare eventuali errori recenti
    if error_logger:
        with st.expander("Log errori recenti", expanded=False):
            errors = error_logger.get_latest_errors(5)
            if errors:
                for error in errors:
                    st.text(error)
            else:
                st.info("Nessun errore recente nel log.")

# Contenuto principale
with tab1:
    st.header("Carica il file Excel con i dati")
    
    # Aggiungi informazioni rapide sulla struttura del file
    show_info_box("""
    Il file Excel deve contenere colonne come: nome_cognome, data, tipo_percorso, email, ecc.
    Scarica un template dalla sezione "Download Template" per vedere la struttura richiesta.
    """)
    
    uploaded_file = st.file_uploader("Seleziona un file Excel", type=["xlsx", "xls"])

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
                        # Mostra gli errori di validazione
                        error_message = f"Errori di validazione nel file Excel ({len(validation_errors)} errori totali)"
                        if error_logger:
                            error_logger.log_error(error_message, error_code="APP-EXCEL-001")
                            
                        st.error(error_message)
                        with st.expander("Dettagli degli errori (primi 5)", expanded=True):
                            for i, error in enumerate(validation_errors[:5]):
                                st.error(error)
                            if len(validation_errors) > 5:
                                st.warning(f"... e altri {len(validation_errors) - 5} errori. Correggi il file e ricaricalo.")
                else:
                    if error_logger:
                        error_logger.log_error(f"Errore nel caricamento del file Excel: {error_message}", error_code="APP-EXCEL-002")
                    st.error(f"Errore nel caricamento del file: {error_message}")

    # Visualizza i dati se disponibili
    if st.session_state.df is not None:
        st.header("Dati caricati")
        
        df = st.session_state.df
        show_data_preview(df)
        
        # Sezione per generare i PDF e inviare le email
        st.header("Generazione Attestati e Invio Email")
        
        # Opzioni di generazione
        col1, col2 = st.columns(2)
        with col1:
            generate_all = st.checkbox("Genera tutti gli attestati", value=True)
            if not generate_all:
                num_records = st.slider("Numero di attestati da generare", 1, min(10, len(df)), 1)
        with col2:
            send_email_option = st.checkbox("Invia email", value=True)
            if send_email_option and not st.session_state.smtp_configured:
                st.warning("Per inviare email, configura prima le credenziali SMTP nella sidebar")
                
        # Configurazione avanzata per l'invio delle email
        if send_email_option:
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
                        help="Quante email inviare prima di fare una pausa"
                    )
                with col_email2:
                    PAUSE_SECONDS = st.number_input(
                        "Intervallo tra i blocchi (secondi)", 
                        min_value=1, 
                        max_value=60, 
                        value=5,
                        help="Quanti secondi attendere tra un blocco di email e il successivo"
                    )
                
                st.info(f"Le email verranno inviate a gruppi di {BLOCK_SIZE} con una pausa di {PAUSE_SECONDS} secondi tra un gruppo e l'altro. Questa configurazione aiuta a evitare blocchi da parte dei provider email.")
        
        # Bottone di generazione
        if st.button("Genera attestati", use_container_width=True, type="primary"):
            if not st.session_state.smtp_configured and send_email_option:
                st.error("Per inviare email, configura prima le credenziali SMTP nella sidebar")
            elif not config.SMTP_USERNAME or not config.SMTP_PASSWORD:
                st.error("Le credenziali SMTP non sono configurate correttamente. Ricontrolla la configurazione nella sidebar.")
            else:
                # Verifica se il logo e la firma sono stati caricati
                logo_path = st.session_state.logo if st.session_state.logo else None
                firma_path = st.session_state.firma if st.session_state.firma else None
                
                # Seleziona le righe da processare
                if generate_all:
                    rows_to_process = df
                else:
                    rows_to_process = df.iloc[:num_records]
                
                # Crea una barra di progresso
                progress_container, status_text, progress_bar = progress_bar_with_status(
                    "Generazione attestati in corso. Attendere...",
                    0
                )
                
                # Contatori per i risultati
                success_count = 0
                error_count = 0
                success_messages = []
                error_messages = []
                
                # Dimensione del blocco e pausa tra i blocchi sono già definiti sopra
                # BLOCK_SIZE e PAUSE_SECONDS sono già definiti nella configurazione avanzata
                
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
                    with st.expander("Dettagli operazioni riuscite", expanded=False):
                        for msg in success_messages:
                            st.write(f"✅ {msg}")
                
                if error_count > 0:
                    st.error(f"{error_count} errori durante la generazione")
                    with st.expander("Dettagli errori", expanded=True):
                        for msg in error_messages:
                            st.write(f"❌ {msg}")
        
        # Aggiungi una nota informativa sul formato del file Excel
        st.divider()
        with st.expander("Formato del file Excel", expanded=False):
            st.markdown("""
            Il file Excel deve contenere le seguenti colonne:
            
            | Colonna | Descrizione | Formato/Esempio |
            | ------- | ----------- | --------------- |
            | nome_cognome | Nome e cognome del partecipante | Mario Rossi |
            | data | Data della lezione | GG/MM/AAAA (es. 15/05/2025) |
            | ora_inizio | Ora di inizio lezione | HH:MM (es. 09:00) |
            | ora_fine | Ora di fine lezione | HH:MM (es. 11:00) |
            | aula | Aula della lezione | A1 |
            | dipartimento | Nome del dipartimento | Scienze della Formazione |
            | indirizzo | Indirizzo del dipartimento | Via del Castro Pretorio 20 |
            | tipo_lezione | Tipo di lezione seguita | Didattica generale |
            | tipo_percorso | Tipo di percorso | Uno tra: "PeF60 CFU", "PeF30 CFU all.2", "PeF36 CFU", "PeF30 CFU (art. 13)" |
            | classe_concorso | Classe di concorso | A-01 |
            | email | Indirizzo email del richiedente | mario.rossi@esempio.com |
            """)

with tab2:
    st.header("Test Email e Generazione PDF")
    st.markdown("""
    Questa sezione ti permette di inviare un'email di prova per verificare che la configurazione SMTP sia corretta.
    Compila i campi sottostanti e opzionalmente genera un attestato di esempio.
    """)
    
    # Crea due colonne
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configurazione Email")
        email_to_test = st.text_input("Email del destinatario")
        test_email_subject = st.text_input("Oggetto dell'email", value="Test - Attestato di Presenza")
        test_email_body = st.text_area("Corpo dell'email", value="""
Gentile utente,

In allegato trova l'attestato di presenza di prova.

Cordiali saluti,
Centro CAFIS
Università degli Studi Roma Tre
        """, height=200)
    
    with col2:
        st.subheader("Dati Attestato di Prova")
        nome_cognome_test = st.text_input("Nome e Cognome", value="Utente di Prova")
        data_test = st.date_input("Data", value=date.today())
        ora_inizio_test = st.text_input("Ora Inizio", value="09:00")
        ora_fine_test = st.text_input("Ora Fine", value="11:00")
        aula_test = st.text_input("Aula", value="A1")
        dipartimento_test = st.text_input("Dipartimento", value="Scienze della Formazione")
        indirizzo_test = st.text_input("Indirizzo", value="Via del Castro Pretorio 20")
        tipo_lezione_test = st.text_input("Tipo Lezione", value="Didattica generale")
        
        tipo_percorso_options = [
            "PeF60 CFU",
            "PeF30 CFU all.2",
            "PeF36 CFU", 
            "PeF30 CFU (art. 13)"
        ]
        tipo_percorso_test = st.selectbox("Tipo Percorso", tipo_percorso_options)
        classe_concorso_test = st.text_input("Classe di Concorso", value="A-01")
    
    # Opzioni
    col1_opt, col2_opt = st.columns(2)
    with col1_opt:
        genera_pdf_test = st.checkbox("Genera attestato di esempio", value=True)
    with col2_opt:
        test_multiple = st.checkbox("Test invio multiplo", value=False, 
                                    help="Simula l'invio di più email allo stesso indirizzo per testare l'invio a blocchi")
    
    if test_multiple:
        # Opzioni per il test multiplo
        col_multi1, col_multi2 = st.columns(2)
        with col_multi1:
            num_emails = st.slider("Numero di email da inviare", 1, 30, 15)
        
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
                    help="Quante email inviare prima di fare una pausa"
                )
            with col_conf2:
                test_pause_seconds = st.number_input(
                    "Intervallo tra i blocchi (secondi)", 
                    min_value=1, 
                    max_value=30, 
                    value=5,
                    help="Quanti secondi attendere tra un blocco di email e il successivo"
                )
        
        st.info(f"Verranno inviate {num_emails} email allo stesso indirizzo a blocchi di {test_block_size}, con una pausa di {test_pause_seconds} secondi tra i blocchi.")
    
    # Bottone per inviare l'email di test
    if st.button("Invia email di test", use_container_width=True):
        if not st.session_state.smtp_configured:
            st.error("Per inviare email, configura prima le credenziali SMTP nella sidebar")
        elif not email_to_test:
            st.error("Inserisci l'email del destinatario")
        else:
            # Determina quante email inviare
            num_to_send = num_emails if test_multiple else 1
            
            # Crea elementi per feedback in tempo reale
            progress_container, status_text, progress_bar = progress_bar_with_status(
                "Invio email di test in corso...",
                0
            )
            
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
                            
                            # Genera il PDF con il modello selezionato
                            output_dir = create_temp_dir()
                            modello = st.session_state.get('attestato_modello', 'presenza')
                            pdf_path = generate_pdf(pdf_data, logo_path, firma_path, output_dir, modello)
                            
                            if pdf_path is None:
                                st.error("Errore nella generazione del PDF")
                                st.stop()
                    
                    # Aggiorna la barra di progresso
                    progress = (i + 1) / num_to_send
                    progress_bar.progress(progress)
                    
                    # Invia l'email
                    status_text.info(f"Invio email {i+1} di {num_to_send}...")
                    subject = f"{test_email_subject} {i+1}" if test_multiple else test_email_subject
                    success, message = send_email(
                        email_to_test, 
                        subject, 
                        test_email_body, 
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
                with open(pdf_path, "rb") as file:
                    st.download_button(
                        label="Scarica il PDF generato",
                        data=file,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )
            elif not genera_pdf_test:
                st.info("Nessun PDF generato come richiesto.")
                    
    # Informazioni aggiuntive
    st.divider()
    with st.expander("Informazioni sulla configurazione email", expanded=False):
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
    Scarica un modello Excel da utilizzare per preparare i dati per la generazione di attestati multipli.
    Seleziona il tipo di modello più adatto alle tue esigenze.
    """)
    
    # Opzioni per i template
    template_type = st.radio(
        "Seleziona il tipo di template da scaricare:",
        ["Base", "Minimo", "Completo", "Vuoto"],
        horizontal=True,
        help="Base: 8 record di esempio con tutti i percorsi formativi. Minimo: 3 record essenziali. Completo: 20 record con vari dati. Vuoto: Solo intestazioni colonne."
    )
    
    # Genera il file template temporaneo in base alla selezione
    try:
        temp_dir = create_temp_dir()
        if template_type == "Base":
            template_path = os.path.join(temp_dir, "template_attestati_base.xlsx")
            create_template_excel(template_path, template_type='base', num_records=8)
            template_description = "Template con 8 record di esempio che coprono tutti i tipi di percorso formativo."
        elif template_type == "Minimo":
            template_path = os.path.join(temp_dir, "template_attestati_minimo.xlsx")
            create_template_excel(template_path, template_type='minimo', num_records=3)
            template_description = "Template minimale con 3 record di esempio."
        elif template_type == "Completo":
            template_path = os.path.join(temp_dir, "template_attestati_completo.xlsx")
            create_template_excel(template_path, template_type='completo', num_records=20)
            template_description = "Template completo con 20 record di esempio e date variabili."
        elif template_type == "Vuoto":
            template_path = os.path.join(temp_dir, "template_attestati_vuoto.xlsx")
            create_empty_template(template_path)
            template_description = "Template con solo le intestazioni delle colonne e una riga di esempio da compilare."
        
        # Leggi il file template in un dataframe per l'anteprima
        template_df = pd.read_excel(template_path)
        
        # Mostra l'anteprima del template
        st.subheader("Anteprima del template")
        st.info(template_description)
        show_data_preview(template_df, max_rows=5)
        
        # Crea un pulsante per il download
        with open(template_path, "rb") as f:
            template_data = f.read()
            
        st.download_button(
            label=f"Scarica Template Excel ({template_type})",
            data=template_data,
            file_name=os.path.basename(template_path),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Errore nella generazione del template: {str(e)}")
        if error_logger:
            error_logger.log_error(f"Errore nella generazione del template: {str(e)}", exception=e, error_code="TMPL-001")

# Contenuto per il tab "Aiuto"
with tab4:
    st.header("Aiuto e Documentazione")
    
    # Aggiungi la sezione FAQ
    show_help_section()
    
    # Aggiungi informazioni su come contattare il supporto
    st.subheader("Contattare il supporto")
    st.write("""
    Se hai problemi o domande sull'utilizzo dell'applicazione, puoi contattarci ai seguenti recapiti:
    
    - **Email**: supporto.cafis@uniroma3.it
    - **Telefono**: 06.1234567
    """)
    
    # Aggiungi informazioni sugli errori comuni
    st.subheader("Errori comuni")
    
    # Crea tab per le diverse categorie di errori
    error_tab1, error_tab2, error_tab3 = st.tabs(["Errori Excel", "Errori Email", "Errori PDF"])
    
    with error_tab1:
        st.markdown("""
        ### Errori relativi al file Excel
        
        1. **Colonne mancanti**: Assicurati che il file Excel contenga tutte le colonne richieste.
        2. **Formato data errato**: Le date devono essere nel formato GG/MM/AAAA (es. 15/05/2025).
        3. **Percorso formativo non valido**: Il tipo di percorso deve essere uno tra: "PeF60 CFU", "PeF30 CFU all.2", "PeF36 CFU", "PeF30 CFU (art. 13)".
        4. **Email non valida**: L'indirizzo email deve essere nel formato corretto.
        
        **Soluzione**: Scarica uno dei template dalla sezione "Download Template" e usalo come base per i tuoi dati.
        """)
    
    with error_tab2:
        st.markdown("""
        ### Errori relativi all'invio email
        
        1. **Autenticazione fallita**: Controlla le credenziali email inserite.
        2. **Connessione rifiutata**: Verifica che il server SMTP sia corretto e accessibile.
        3. **Timeout di connessione**: Verifica la tua connessione internet.
        4. **Sicurezza Gmail/Outlook**: Per questi provider è necessario utilizzare una password per app specifica.
        
        **Soluzione**: Usa la funzione "Test Email" per verificare la configurazione e diagnosticare eventuali problemi.
        """)
    
    with error_tab3:
        st.markdown("""
        ### Errori relativi alla generazione PDF
        
        1. **Logo o firma non trovati**: Assicurati di aver caricato correttamente il logo e la firma.
        2. **Formato immagine non supportato**: Usa immagini nei formati PNG o JPG.
        3. **Errore nella creazione del PDF**: Verifica che tutti i dati necessari siano presenti.
        
        **Soluzione**: Prova a generare un PDF di test nella sezione "Test Email" per verificare che tutto funzioni correttamente.
        """)
    
    # Aggiungi una sezione con collegamenti utili
    st.subheader("Collegamenti utili")
    st.markdown("""
    - [Documentazione Streamlit](https://docs.streamlit.io/)
    - [Riferimento al DPCM 4 agosto 2023](https://www.gazzettaufficiale.it/eli/id/2023/09/25/23A05428/sg)
    - [Centro CAFIS - Università Roma Tre](https://www.cafis.uniroma3.it/)
    """)

# Nota a piè di pagina
st.divider()
show_footer()
