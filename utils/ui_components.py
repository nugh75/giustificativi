import streamlit as st
import pandas as pd
import os
import base64
from PIL import Image
import io

# Definizione colori e stile
PRIMARY_COLOR = "#0068c9"  # Blu (colore primario Streamlit)
SECONDARY_COLOR = "#ffd160"  # Giallo dorato
SUCCESS_COLOR = "#00c16e"  # Verde
WARNING_COLOR = "#ffbd45"  # Ambra
ERROR_COLOR = "#ff0e0e"  # Rosso

def custom_header(title, subtitle=None, icon=None):
    """
    Crea un'intestazione personalizzata con titolo, sottotitolo opzionale e icona
    
    Args:
        title (str): Titolo principale
        subtitle (str, optional): Sottotitolo. Default a None.
        icon (str, optional): Emoji o icona da mostrare. Default a None.
    """
    # Stile per il titolo
    title_style = f"color: {PRIMARY_COLOR}; font-weight: bold;"
    
    # Contenitore per l'intestazione
    header_container = st.container()
    
    with header_container:
        # Se è stata fornita un'icona, mostrala insieme al titolo
        if icon:
            st.markdown(f"<h1 style='{title_style}'>{icon} {title}</h1>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='{title_style}'>{title}</h1>", unsafe_allow_html=True)
        
        # Se è stato fornito un sottotitolo, mostralo
        if subtitle:
            st.markdown(f"<p style='font-size: 1.2em;'>{subtitle}</p>", unsafe_allow_html=True)
    
    return header_container

def show_info_box(message, color=None):
    """
    Mostra una casella informativa con uno sfondo colorato
    
    Args:
        message (str): Il messaggio da mostrare
        color (str, optional): Il colore dello sfondo. Default a None.
    """
    # Se non è stato specificato un colore, usa il colore primario
    if not color:
        color = PRIMARY_COLOR
        
    # Crea l'HTML per la casella informativa
    html = f"""
    <div style='background-color: {color}20; border-left: 5px solid {color}; 
              padding: 10px; border-radius: 5px;'>
        <p style='margin: 0;'>{message}</p>
    </div>
    """
    
    # Mostra l'HTML
    st.markdown(html, unsafe_allow_html=True)

def progress_bar_with_status(status_text, progress_value=0):
    """
    Crea una barra di progresso con testo esplicativo
    
    Args:
        status_text (str): Testo da mostrare sopra la barra di progresso
        progress_value (float): Valore della barra di progresso (da 0 a 1)
    """
    # Contaiiner per la barra di progresso e il testo
    container = st.container()
    
    with container:
        # Mostra il testo di stato
        status = st.empty()
        status.markdown(f"**{status_text}**")
        
        # Mostra la barra di progresso
        progress = st.progress(progress_value)
    
    # Restituisci gli oggetti per aggiornarli in seguito
    return container, status, progress

def show_help_section():
    """Mostra una sezione di aiuto e FAQ"""
    with st.expander("❓ Aiuto e FAQ", expanded=False):
        st.markdown("""
        ### Domande frequenti
        
        #### Come preparare il file Excel?
        Il file Excel deve contenere le seguenti colonne:
        - `nome_cognome`: Nome e cognome del partecipante
        - `data`: Data della lezione (formato: GG/MM/AAAA)
        - `ora_inizio` e `ora_fine`: Orari della lezione
        - `aula`: Aula della lezione
        - `dipartimento`: Nome del dipartimento
        - `indirizzo`: Indirizzo del dipartimento
        - `tipo_lezione`: Tipo di lezione seguita
        - `tipo_percorso`: Tipo di percorso (uno tra: "PeF60 CFU", "PeF30 CFU all.2", "PeF36 CFU", "PeF30 CFU (art. 13)")
        - `classe_concorso`: Classe di concorso
        - `email`: Indirizzo email del richiedente
        
        #### Quali provider email sono supportati?
        L'applicazione supporta i seguenti provider di posta elettronica:
        - Gmail
        - Outlook.com / Office 365
        - Libero
        
        #### Come ottenere una password per app (Gmail/Outlook)?
        **Per Gmail**:
        1. Attiva l'autenticazione a due fattori sul tuo account Google
        2. Vai su [Password per le app](https://myaccount.google.com/apppasswords)
        3. Crea una nuova password per app
        
        **Per Outlook**:
        1. Attiva l'autenticazione a due fattori sul tuo account Microsoft
        2. Vai su [Password per le app](https://account.microsoft.com/security)
        3. Crea una nuova password per app
        
        #### Cosa fare se l'invio email fallisce?
        1. Controlla che le credenziali SMTP siano corrette
        2. Verifica di avere una connessione internet stabile
        3. Se usi Gmail o Outlook, assicurati di utilizzare una password per app
        4. Verifica che il server SMTP non sia bloccato dalla rete o dal firewall
        5. Prova a inviare un'email di test nella sezione apposita
        """)

def show_data_preview(df, max_rows=5):
    """
    Mostra un'anteprima dei dati con formattazione migliorata
    
    Args:
        df (pd.DataFrame): Il DataFrame da visualizzare
        max_rows (int, optional): Numero massimo di righe da mostrare. Default a 5.
    """
    if df is None or df.empty:
        st.warning("Nessun dato disponibile per l'anteprima")
        return
    
    # Limita il numero di righe visualizzate
    preview_df = df.head(max_rows)
    
    # Configura lo stile della tabella
    st.dataframe(
        preview_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Mostra le informazioni sul numero di righe
    total_rows = len(df)
    if total_rows > max_rows:
        st.caption(f"Mostrati {max_rows} di {total_rows} record totali")
    else:
        st.caption(f"Mostrati tutti i {total_rows} record")

def image_to_base64(img_path):
    """Converte un'immagine in stringa base64 per l'uso in HTML"""
    with open(img_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return encoded

def get_binary_file_downloader_html(bin_file, file_label='File', button_text='Download'):
    """
    Genera HTML per un pulsante di download personalizzato
    
    Args:
        bin_file (str): Percorso al file binario da scaricare
        file_label (str): Etichetta per il file
        button_text (str): Testo del pulsante
        
    Returns:
        str: HTML per un pulsante di download
    """
    with open(bin_file, 'rb') as f:
        data = f.read()
    
    b64 = base64.b64encode(data).decode()
    return f"""
    <a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(bin_file)}">
        <button style="
            background-color: {PRIMARY_COLOR};
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        ">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
            </svg>
            {button_text}
        </button>
    </a>
    """

def show_notification(message, type="info"):
    """
    Mostra una notifica all'utente
    
    Args:
        message (str): Il messaggio da mostrare
        type (str): Tipo di notifica ('info', 'success', 'warning', 'error')
    """
    if type == "info":
        st.info(message)
    elif type == "success":
        st.success(message)
    elif type == "warning":
        st.warning(message)
    elif type == "error":
        st.error(message)
    else:
        st.write(message)

def show_testimonial(quote, author, position=None, image_path=None):
    """
    Mostra una testimonianza con citazione, autore e immagine opzionale
    
    Args:
        quote (str): Testo della citazione
        author (str): Nome dell'autore
        position (str, optional): Posizione/ruolo dell'autore
        image_path (str, optional): Percorso all'immagine dell'autore
    """
    # Stile per la citazione
    quote_style = "font-style: italic; font-size: 1.1em; margin-bottom: 10px;"
    
    # Stile per l'autore
    author_style = "font-weight: bold; margin-bottom: 0px;"
    
    # Stile per la posizione
    position_style = "color: gray; font-size: 0.9em;"
    
    # HTML per la testimonianza
    html = f"""
    <div style="padding: 15px; border-radius: 10px; background-color: #f8f9fa; margin: 10px 0;">
        <p style="{quote_style}">"{quote}"</p>
        <p style="{author_style}">{author}</p>
    """
    
    # Aggiungi la posizione se fornita
    if position:
        html += f"""<p style="{position_style}">{position}</p>"""
    
    # Chiudi il div
    html += "</div>"
    
    # Mostra l'HTML
    st.markdown(html, unsafe_allow_html=True)

def show_footer():
    """Mostra un footer personalizzato"""
    st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
        <p>© 2025 Centro CAFIS - Università degli Studi Roma Tre</p>
        <p style="font-size: 0.8em; color: #666;">
            Sviluppato per la gestione degli attestati di presenza per i percorsi formativi DPCM
        </p>
    </div>
    """, unsafe_allow_html=True)
