import pandas as pd
import os
import re
from datetime import datetime

# Importa error_logger se disponibile
try:
    from utils.error_logger import error_logger
except ImportError:
    error_logger = None

def read_excel_file(file_path):
    """
    Legge un file Excel e restituisce un DataFrame pandas
    
    Args:
        file_path (str): Percorso del file Excel
        
    Returns:
        pd.DataFrame: DataFrame contenente i dati del file Excel
    """
    try:
        df = pd.read_excel(file_path)
        
        # Verifica che le colonne necessarie siano presenti
        required_columns = [
            'nome_cognome', 'data', 'ora_inizio', 'ora_fine',
            'aula', 'dipartimento', 'indirizzo', 'tipo_lezione',
            'tipo_percorso', 'classe_concorso', 'email'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            error_msg = f"Colonne mancanti nel file Excel: {', '.join(missing_columns)}"
            if error_logger:
                error_logger.log_error(error_msg, error_code="EXCEL-001")
            return None, error_msg
            
        # Formatta la data (supporta formato italiano GG/MM/AAAA)
        if 'data' in df.columns:
            try:
                # Prova prima con il parametro dayfirst=True per il formato italiano
                df['data'] = pd.to_datetime(df['data'], dayfirst=True).dt.strftime('%d/%m/%Y')
            except Exception as e:
                # Se fallisce, prova ad usare il formato mixed che è più flessibile
                try:
                    df['data'] = pd.to_datetime(df['data'], format='mixed').dt.strftime('%d/%m/%Y')
                except Exception as e:
                    # Se anche questo fallisce, mantieni i dati originali come stringhe
                    error_msg = f"Attenzione: impossibile convertire le date. Verranno utilizzate come stringhe. Errore: {e}"
                    if error_logger:
                        error_logger.log_error(error_msg, exception=e, error_code="EXCEL-002")
                    print(error_msg)
                    # Assicurati che la colonna data sia di tipo stringa
                    df['data'] = df['data'].astype(str)
            
        # Verifica che i percorsi formativi siano validi
        valid_percorsi = ['PeF60 CFU', 'PeF30 CFU', 'PeF36 CFU', 'PeF30 CFU (art. 13)']
        invalid_percorsi = df[~df['tipo_percorso'].isin(valid_percorsi)]['tipo_percorso'].unique()
        
        if len(invalid_percorsi) > 0:
            error_msg = f"Percorsi formativi non validi: {', '.join(str(p) for p in invalid_percorsi)}"
            if error_logger:
                error_logger.log_error(error_msg, error_code="EXCEL-003")
            return None, error_msg
        
        # Esegui una validazione avanzata dei dati
        validation_errors = validate_excel_data(df)
        if validation_errors:
            if error_logger:
                error_logger.log_error(f"Errori di validazione nel file Excel: {len(validation_errors)} righe con problemi", error_code="EXCEL-004")
            return None, f"Il file contiene {len(validation_errors)} righe con errori di validazione. Controlla il formato dei dati."
            
        return df, None
        
    except Exception as e:
        error_msg = f"Errore nella lettura del file Excel: {str(e)}"
        if error_logger:
            error_logger.log_error(error_msg, exception=e, error_code="EXCEL-999")
        return None, error_msg
        
def validate_row(row):
    """
    Verifica che una riga del DataFrame contenga tutti i dati necessari
    
    Args:
        row (pd.Series): Una riga del DataFrame
        
    Returns:
        bool, str: (True, None) se la riga è valida, (False, error_message) altrimenti
    """
    # Verifica che i campi obbligatori siano presenti e non vuoti
    for field in ['nome_cognome', 'data', 'ora_inizio', 'ora_fine', 'aula', 'dipartimento', 
                 'indirizzo', 'tipo_lezione', 'tipo_percorso', 'classe_concorso', 'email']:
        if pd.isna(row[field]) or str(row[field]).strip() == '':
            return False, f"Campo '{field}' mancante o vuoto"
            
    # Verifica formato email
    if '@' not in str(row['email']):
        return False, f"Formato email non valido: {row['email']}"
    
    # Verifica formato ora
    ora_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$')
    if not ora_pattern.match(str(row['ora_inizio'])):
        return False, f"Formato ora inizio non valido: {row['ora_inizio']}, deve essere HH:MM"
    if not ora_pattern.match(str(row['ora_fine'])):
        return False, f"Formato ora fine non valido: {row['ora_fine']}, deve essere HH:MM"
        
    return True, None

def validate_excel_data(df):
    """
    Esegue una validazione avanzata dell'intero DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame da validare
    
    Returns:
        list: Lista di errori di validazione per riga
    """
    validation_errors = []
    
    # Espressione regolare per verificare il formato email
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Espressione regolare per verificare il formato ora (HH:MM)
    ora_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$')
    
    # Verifica percorsi formativi validi
    valid_percorsi = ['PeF60 CFU', 'PeF30 CFU', 'PeF36 CFU', 'PeF30 CFU (art. 13)']
    
    # Itera sulle righe del DataFrame
    for idx, row in df.iterrows():
        row_errors = []
        
        # Verifica formato email
        if 'email' in row and not email_pattern.match(str(row['email'])):
            row_errors.append(f"Email non valida: {row['email']}")
        
        # Verifica formato ore
        if 'ora_inizio' in row and not ora_pattern.match(str(row['ora_inizio'])):
            row_errors.append(f"Formato ora inizio non valido: {row['ora_inizio']}")
        if 'ora_fine' in row and not ora_pattern.match(str(row['ora_fine'])):
            row_errors.append(f"Formato ora fine non valido: {row['ora_fine']}")
        
        # Verifica tipo percorso
        if 'tipo_percorso' in row and str(row['tipo_percorso']) not in valid_percorsi:
            row_errors.append(f"Tipo percorso non valido: {row['tipo_percorso']}")
        
        # Verifica che l'ora di fine sia successiva all'ora di inizio
        try:
            if 'ora_inizio' in row and 'ora_fine' in row:
                ora_inizio = datetime.strptime(str(row['ora_inizio']), '%H:%M')
                ora_fine = datetime.strptime(str(row['ora_fine']), '%H:%M')
                if ora_fine <= ora_inizio:
                    row_errors.append(f"Ora fine ({row['ora_fine']}) deve essere successiva a ora inizio ({row['ora_inizio']})")
        except ValueError:
            # Errore già rilevato dai controlli precedenti
            pass
        
        # Aggiungi errori per questa riga se presenti
        if row_errors:
            validation_errors.append(f"Riga {idx+2}: {'; '.join(row_errors)}")
    
    return validation_errors
