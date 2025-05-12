import os
import logging
from datetime import datetime
import streamlit as st

class ErrorLogger:
    """
    Classe per la gestione centralizzata degli errori dell'applicazione.
    Implementa logging su file e mostra messaggi utente in Streamlit.
    """
    
    def __init__(self, log_dir="logs"):
        """
        Inizializza il logger degli errori.
        
        Args:
            log_dir (str): Directory dove salvare i file di log
        """
        # Crea la directory per i log se non esiste
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Configura il logger
        self.log_file = os.path.join(self.log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
    def log_error(self, error_message, exception=None, show_ui=True, error_code=None):
        """
        Registra un errore nel file di log e mostra un messaggio all'utente.
        
        Args:
            error_message (str): Messaggio di errore da mostrare all'utente
            exception (Exception, optional): L'eccezione catturata. Default a None.
            show_ui (bool): Se True, mostra l'errore nell'interfaccia Streamlit
            error_code (str): Codice opzionale per identificare il tipo di errore
        """
        # Crea un messaggio dettagliato per il log
        log_message = f"{error_message}"
        if error_code:
            log_message = f"[{error_code}] {log_message}"
        
        if exception:
            log_message += f" - Exception: {str(exception)}"
            
        # Registra l'errore nel file di log
        logging.error(log_message)
        
        # Mostra l'errore nell'interfaccia utente se richiesto
        if show_ui:
            st.error(error_message)
            
    def log_info(self, message):
        """
        Registra un messaggio informativo nel log.
        
        Args:
            message (str): Il messaggio da registrare
        """
        logging.info(message)
    
    def get_latest_errors(self, count=10):
        """
        Recupera gli ultimi errori dal file di log.
        
        Args:
            count (int): Numero massimo di errori da recuperare
            
        Returns:
            list: Lista degli ultimi errori
        """
        errors = []
        
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    
                # Filtra solo le linee con ERROR
                error_lines = [line.strip() for line in lines if "ERROR" in line]
                
                # Prendi gli ultimi 'count' errori
                errors = error_lines[-count:]
        except Exception as e:
            print(f"Errore nel recupero dei log: {str(e)}")
            
        return errors

# Crea un'istanza globale del logger
error_logger = ErrorLogger()
