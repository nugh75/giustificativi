import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import config
import ssl
from datetime import datetime
import logging
import socket
import time

# Prova ad importare il logger degli errori se disponibile
try:
    from utils.error_logger import error_logger
except ImportError:
    error_logger = None

def check_smtp_connection(server, port, use_tls=True, timeout=5):
    """
    Verifica se è possibile stabilire una connessione con il server SMTP
    
    Args:
        server (str): Server SMTP
        port (int): Porta SMTP
        use_tls (bool, optional): Usa TLS per la connessione. Default a True.
        timeout (int, optional): Timeout della connessione in secondi. Default a 5.
        
    Returns:
        bool, str: (True, None) se la connessione ha successo, (False, error_message) altrimenti
    """
    try:
        # Tenta la connessione al server
        with socket.create_connection((server, port), timeout=timeout) as sock:
            # Se la connessione ha successo, prova ad utilizzare SMTP
            if use_tls:
                with smtplib.SMTP(server, port, timeout=timeout) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()
                    return True, None
            else:
                # Se non si usa TLS, verifica solo che la socket funzioni
                return True, None
    except (socket.timeout, ConnectionRefusedError) as e:
        return False, f"Impossibile connettersi al server SMTP {server}:{port}. Errore: {str(e)}"
    except Exception as e:
        return False, f"Errore nella verifica della connessione SMTP: {str(e)}"

def send_email(recipient_email, subject, body, attachment_path=None, retry_count=2, retry_delay=3):
    """
    Invia un'email con un allegato opzionale
    
    Args:
        recipient_email (str): Indirizzo email del destinatario
        subject (str): Oggetto dell'email
        body (str): Corpo dell'email
        attachment_path (str, optional): Percorso del file da allegare. Default a None.
        retry_count (int, optional): Numero di tentativi in caso di errore. Default a 2.
        retry_delay (int, optional): Secondi di attesa tra i tentativi. Default a 3.
        
    Returns:
        bool, str: (True, None) se l'email è stata inviata con successo, (False, error_message) altrimenti
    """
    # Verifica che le credenziali SMTP siano configurate
    if not config.SMTP_USERNAME or not config.SMTP_PASSWORD:
        error_msg = "Credenziali SMTP non configurate"
        if error_logger:
            error_logger.log_error(error_msg, error_code="SMTP-001")
        return False, error_msg
    
    try:
        # Crea il messaggio email
        message = MIMEMultipart()
        message["From"] = config.SMTP_USERNAME
        message["To"] = recipient_email
        message["Subject"] = subject
        message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
        
        # Aggiungi il Reply-To header se configurato
        if hasattr(config, 'SMTP_REPLY_TO') and config.SMTP_REPLY_TO:
            message["Reply-To"] = config.SMTP_REPLY_TO
        
        # Aggiungi il corpo del messaggio
        message.attach(MIMEText(body, "plain"))
        
        # Aggiungi l'allegato se presente
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEApplication(attachment.read(), Name=os.path.basename(attachment_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                message.attach(part)
        
        # Seleziona il metodo di connessione in base alla porta
        if config.SMTP_PORT == 465:
            # Per SSL/TLS diretto (come Libero)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, context=context) as server:
                try:
                    server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                    server.send_message(message)
                except smtplib.SMTPAuthenticationError as e:
                    print(f"Errore di autenticazione: {e}")
                    return False, f"Errore di autenticazione: {e}. Verifica che le credenziali siano corrette. Per Microsoft Outlook, utilizza una password per app."
        else:
            # Per STARTTLS (come Gmail e Outlook)
            with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                try:
                    server.ehlo()
                    if config.SMTP_USE_TLS:
                        server.starttls()
                        server.ehlo()
                    server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                    server.send_message(message)
                except smtplib.SMTPAuthenticationError as e:
                    print(f"Errore di autenticazione: {e}")
                    return False, f"Errore di autenticazione: {e}. Verifica che le credenziali siano corrette. Per Microsoft Outlook, utilizza una password per app."
            
        if error_logger:
            error_logger.log_info(f"Email inviata con successo a {recipient_email}")
        return True, None
        
    except smtplib.SMTPConnectError as e:
        error_msg = f"Errore di connessione al server SMTP: {str(e)}"
        if error_logger:
            error_logger.log_error(error_msg, exception=e, error_code="SMTP-002")
        
        # Prova a riconnettersi
        if retry_count > 0:
            if error_logger:
                error_logger.log_info(f"Tentativo di riconnessione tra {retry_delay} secondi...")
            time.sleep(retry_delay)
            return send_email(recipient_email, subject, body, attachment_path, retry_count-1, retry_delay+2)
        return False, error_msg
        
    except smtplib.SMTPServerDisconnected as e:
        error_msg = f"Disconnesso dal server SMTP: {str(e)}"
        if error_logger:
            error_logger.log_error(error_msg, exception=e, error_code="SMTP-003")
        return False, error_msg
        
    except smtplib.SMTPException as e:
        error_msg = f"Errore SMTP: {str(e)}"
        if error_logger:
            error_logger.log_error(error_msg, exception=e, error_code="SMTP-004")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Errore nell'invio dell'email: {str(e)}"
        if error_logger:
            error_logger.log_error(error_msg, exception=e, error_code="SMTP-999")
        return False, error_msg
