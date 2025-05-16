"""
Modulo per la visualizzazione dell'anteprima delle email inviate dall'applicazione.
Mostra come appariranno le email ai destinatari, compresi gli indirizzi email utilizzati.
"""
import streamlit as st
import config
from datetime import datetime

def show_email_preview():
    """
    Mostra un'anteprima dell'email come apparirà ai destinatari.
    Include informazioni sull'intestazione dell'email e sul campo Reply-To.
    """
    st.header("Anteprima Email")
    st.markdown("""
    Questa sezione mostra come appariranno le email inviate dall'applicazione ai destinatari,
    con particolare attenzione agli indirizzi email utilizzati.
    """)
    
    # Verifica che le credenziali siano configurate
    if not hasattr(config, "SMTP_USERNAME") or not config.SMTP_USERNAME:
        st.warning("Per visualizzare l'anteprima email, configura prima le credenziali SMTP nella barra laterale.")
        return
    
    # Determina l'indirizzo Reply-To effettivo
    reply_to = config.SMTP_REPLY_TO if hasattr(config, "SMTP_REPLY_TO") and config.SMTP_REPLY_TO else config.SMTP_USERNAME
    
    # Visualizza la struttura dell'email in due colonne
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Come appare l'email nel client di posta")
        
        # Crea un contenitore per l'anteprima dell'email
        email_container = st.container()
        with email_container:
            st.markdown("""
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 20px;">
                <div style="border-bottom: 1px solid #eee; margin-bottom: 15px; padding-bottom: 10px;">
                    <div><strong>Da:</strong> {from_email}</div>
                    <div><strong>A:</strong> destinatario@esempio.com</div>
                    <div><strong>Oggetto:</strong> {subject}</div>
                    <div><strong>Data:</strong> {date}</div>
                </div>
                
                <div style="font-family: Arial, sans-serif; padding: 10px;">
                    {body_content}
                </div>
                
                <div style="margin-top: 20px; padding-top: 10px; border-top: 1px dashed #eee; font-size: 0.9em; color: #666;">
                    <em>Questo messaggio è stato inviato da {institution} - Centro CAFIS.</em>
                </div>
            </div>
            """.format(
                from_email=config.SMTP_USERNAME,
                subject=config.EMAIL_SUBJECT,
                date=datetime.now().strftime("%a, %d %b %Y %H:%M:%S"),
                body_content=config.EMAIL_BODY.format(
                    nome_cognome="Mario Rossi",
                    data="16/05/2025",
                    firmatario=f"Centro CAFIS\n{config.DIRETTORE_CAFIS}",
                    universita=config.UNIVERSITA
                ).replace("\n", "<br>"),
                institution=config.UNIVERSITA
            ), unsafe_allow_html=True)
            
            st.caption("👆 Questa è una rappresentazione visuale di come l'email sarà ricevuta dal destinatario")
    
    with col2:
        st.subheader("Intestazioni tecniche")
        st.info(f"""
        **From:** {config.SMTP_USERNAME}
        
        **Reply-To:** {reply_to}
        
        **Subject:** {config.EMAIL_SUBJECT}
        
        **Date:** {datetime.now().strftime("%a, %d %b %Y %H:%M:%S")}
        
        **MIME-Version:** 1.0
        
        **Content-Type:** multipart/mixed
        """)
        
        if config.SMTP_USERNAME != reply_to:
            st.success("✅ L'indirizzo di risposta (Reply-To) è stato personalizzato")
        
    # Sezione di spiegazione
    st.divider()
    st.subheader("Come funzionano gli indirizzi email nel sistema")
    
    explain_col1, explain_col2 = st.columns(2)
    
    with explain_col1:
        st.markdown("#### Quando un destinatario riceve l'email")
        st.markdown(f"""
        1. **Da:** {config.SMTP_USERNAME}
          - Questo è l'indirizzo che appare come mittente dell'email
        
        2. **Rispondi-a:** {reply_to}
          - Quando il destinatario clicca "Rispondi", la risposta sarà indirizzata a questo indirizzo
        
        3. **Comportamento client di posta**
          - La maggior parte dei client di posta mostra solo il campo "Da" nell'interfaccia utente
          - L'intestazione "Reply-To" è normalmente nascosta, ma viene utilizzata automaticamente
        """)
        
    with explain_col2:
        st.markdown("#### Come funziona il sistema di email")
        st.markdown(f"""
        1. **Autenticazione sul server** tramite {config.SMTP_USERNAME}
          - Il server SMTP accetta la connessione perché viene fornito un account valido
          
        2. **Invio dell'email** mostrandosi come {config.SMTP_USERNAME}
          - L'email viene inviata con l'intestazione "Da" impostata a questo indirizzo
          
        3. **Configurazione Reply-To** impostata su {reply_to}
          - L'intestazione speciale "Reply-To" indica ai client di posta di inviare le risposte a questo indirizzo invece che a quello mostrato nel campo "Da"
        """)
    
    st.divider()
    
    # Test di invio email
    st.subheader("Test invio email")
    
    email_test = st.text_input("Inserisci la tua email per ricevere un'email di test")
    send_test = st.button("Invia email di test")
    
    if send_test:
        if not email_test:
            st.error("Inserisci un indirizzo email valido per il test")
        else:
            with st.spinner("Invio email di test in corso..."):
                from utils.email_sender import send_email
                
                # Crea corpo email
                test_body = f"""
Gentile utente,

Questa è un'email di test inviata dall'applicazione "Generatore Attestati di Presenza".

L'email è stata inviata con le seguenti configurazioni:
- Server SMTP: {config.SMTP_SERVER}
- Porta: {config.SMTP_PORT}
- Indirizzo mittente: {config.SMTP_USERNAME}
- Indirizzo per risposte: {reply_to}

Quando rispondi a questa email, la risposta verrà inviata all'indirizzo {reply_to}.

Cordiali saluti,
Centro CAFIS
{config.UNIVERSITA}
                """
                
                success, message = send_email(
                    email_test,
                    "Test configurazione email - Generatore Attestati di Presenza",
                    test_body
                )
                
                if success:
                    st.success(f"Email di test inviata con successo a {email_test}")
                    st.markdown("""
                    ✅ **Email inviata correttamente!**
                    
                    Controlla la tua casella di posta e verifica che:
                    1. L'email appaia come proveniente dall'indirizzo corretto
                    2. Quando rispondi, la risposta venga indirizzata all'indirizzo Reply-To configurato
                    """)
                else:
                    st.error(f"Errore nell'invio dell'email: {message}")
