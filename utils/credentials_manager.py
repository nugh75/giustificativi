import os
import streamlit as st

def save_smtp_credentials(smtp_server, smtp_port, smtp_username, smtp_password, smtp_use_tls=True, smtp_reply_to=None):
    """
    Salva le credenziali SMTP in un file .env nella directory del progetto
    
    Args:
        smtp_server (str): Server SMTP
        smtp_port (int): Porta SMTP
        smtp_username (str): Nome utente SMTP
        smtp_password (str): Password SMTP
        smtp_use_tls (bool): Usa TLS per la connessione SMTP
        smtp_reply_to (str, optional): Indirizzo email di risposta (Reply-To). Default a None.
    
    Returns:
        bool: True se le credenziali sono state salvate con successo, False altrimenti
    """
    try:
        # Percorso del file .env
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        
        # Legge le credenziali esistenti se presenti
        env_vars = {}
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if line.strip() and "=" in line:
                        key, value = line.strip().split("=", 1)
                        env_vars[key] = value
        
        # Aggiorna le credenziali SMTP
        env_vars["SMTP_SERVER"] = smtp_server
        env_vars["SMTP_PORT"] = str(smtp_port)
        env_vars["SMTP_USERNAME"] = smtp_username
        env_vars["SMTP_PASSWORD"] = smtp_password
        env_vars["SMTP_USE_TLS"] = "1" if smtp_use_tls else "0"
        
        # Aggiorna l'indirizzo Reply-To se specificato
        if smtp_reply_to:
            env_vars["SMTP_REPLY_TO"] = smtp_reply_to
        elif "SMTP_REPLY_TO" in env_vars and not smtp_reply_to:
            # Se era presente un valore ma ora è vuoto, lo rimuoviamo
            env_vars.pop("SMTP_REPLY_TO")
        
        # Scrive le credenziali nel file .env
        with open(env_path, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        return True
    except Exception as e:
        st.error(f"Errore nel salvataggio delle credenziali: {str(e)}")
        return False
