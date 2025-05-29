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
            
        # Pre-elaborazione: gestione dei valori speciali come '--'
        # Sostituisci '--' con valori appropriati per i campi opzionali
        def preprocess_value(val, campo):
            if pd.isna(val) or str(val).strip() == '--':
                if campo in ['aula', 'dipartimento', 'indirizzo']:
                    return ""  # Campi opzionali possono essere vuoti
                return val     # Per altri campi, mantieni il valore originale
                
            # Normalizzazione email
            if campo == 'email':
                val_str = str(val).strip()
                
                # Pattern specifico per email degli studenti di Roma Tre (mmm.mmmmmmm@stud.uniroma3.it)
                student_email_match = re.search(r'([a-zA-ZàèéìòóùÀÈÉÌÒÓÙ]{2,3}\.[a-zA-ZàèéìòóùÀÈÉÌÒÓÙ0-9_\-]+@stud\.uniroma3\.it)', val_str)
                if student_email_match:
                    return student_email_match.group(1).strip()
                
                # Pattern standard per altre email
                email_match = re.search(r'([a-zA-ZàèéìòóùÀÈÉÌÒÓÙ0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', val_str)
                if email_match:
                    return email_match.group(1).strip()  # Restituisce solo l'indirizzo email e rimuove eventuali spazi
            
            # Normalizzazione formato ora
            if campo in ['ora_inizio', 'ora_fine']:
                val_str = str(val).strip()
                
                # Rimuovi i secondi dal formato HH:MM:SS
                if re.match(r'^([01]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$', val_str):
                    # Print log message for conversion
                    if error_logger:
                        error_logger.log_info(f"Formato ora con secondi convertito: da {val_str} a {val_str[:5]}")
                    return val_str[:5]  # Prendi solo HH:MM
                
                # Converti formato HH.MM in HH:MM
                if re.match(r'^([01]?[0-9]|2[0-3])\.([0-5][0-9])$', val_str):
                    return val_str.replace('.', ':')
                
                # Converti formato HHMM in HH:MM
                if re.match(r'^([01]?[0-9]|2[0-3])([0-5][0-9])$', val_str) and len(val_str) >= 3:
                    if len(val_str) == 3:  # Formato HMM (es: 945)
                        return f"0{val_str[0]}:{val_str[1:]}"
                    else:  # Formato HHMM (es: 0945)
                        return f"{val_str[:2]}:{val_str[2:]}"
            
            return val
            
        # Applica il pre-processamento a tutte le celle del DataFrame
        for col in df.columns:
            df[col] = df[col].apply(lambda x: preprocess_value(x, col))
            
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
        valid_percorsi = [
            'PeF60 CFU',
            'PeF30 CFU',
            'PeF30 CFU all.2', 
            'PeF36 CFU', 
            'PeF30 CFU (art. 13)', 
            'PeF30 CFU all.2 art. 13',  # Variante senza parentesi
            'PeF36 CFU all.5',    # Variante con allegato 5 in formato abbreviato
            'PeF36 CFU (all.5)',   # Variante con parentesi
            # Varianti senza "CFU" che vengono utilizzate nell'app
            'PeF 60',
            'PeF 30 all.2',
            'PeF 36',
            'PeF 30 art. 13'
        ]
        
        # Normalizza i percorsi per gestire le varianti di scrittura
        def normalize_percorso(p):
            p = str(p).strip()
            p = p.replace("(", "").replace(")", "")  # Rimuovi parentesi
            p = p.replace("all.", "allegato")        # Standardizza abbreviazioni
            p = p.replace("art.", "articolo")        # Standardizza abbreviazioni
            return p
            
        # Crea una versione normalizzata dei percorsi validi
        normalized_valid = [normalize_percorso(p) for p in valid_percorsi]
        
        # Trova i percorsi non validi confrontando versioni normalizzate
        invalid_percorsi = []
        for percorso in df['tipo_percorso'].unique():
            if normalize_percorso(percorso) not in normalized_valid and percorso not in valid_percorsi:
                invalid_percorsi.append(percorso)
        
        if len(invalid_percorsi) > 0:
            error_msg = f"Percorsi formativi non validi: {', '.join(str(p) for p in invalid_percorsi)}"
            if error_logger:
                error_logger.log_error(error_msg, error_code="EXCEL-003")
            return None, error_msg
        
        # Esegui una validazione avanzata dei dati
        validation_errors = validate_excel_data(df)
        if validation_errors:
            # Limita il numero di errori mostrati nel messaggio
            max_errors_to_show = 5
            error_examples = "\n- " + "\n- ".join(validation_errors[:max_errors_to_show])
            
            if len(validation_errors) > max_errors_to_show:
                error_examples += f"\n... e altri {len(validation_errors) - max_errors_to_show} errori."
            
            error_msg = f"Il file contiene {len(validation_errors)} righe con errori di validazione. Esempi:{error_examples}"
            
            # Aggiungi suggerimenti per i valori '--' e formati ora
            error_msg += "\n\nSuggerimenti:" 
            error_msg += "\n- Per i campi opzionali (aula, dipartimento, indirizzo) puoi usare '--' per indicare un valore vuoto."
            error_msg += "\n- I formati ora supportati sono: HH:MM, HH:MM:SS (i secondi vengono rimossi), HH.MM e HHMM."
            
            if error_logger:
                error_logger.log_error(f"Errori di validazione nel file Excel: {len(validation_errors)} righe con problemi", error_code="EXCEL-004")
            
            return None, error_msg
            
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
    # Definisci quali campi sono essenziali e quali possono essere sostituiti con valori predefiniti
    campi_essenziali = ['nome_cognome', 'data', 'ora_inizio', 'ora_fine', 'tipo_lezione',
                        'tipo_percorso', 'email']
    
    campi_opzionali = ['aula', 'dipartimento', 'indirizzo', 'classe_concorso']
    
    # Verifica che i campi essenziali siano presenti e non vuoti
    for field in campi_essenziali:
        value = str(row[field]).strip() if not pd.isna(row[field]) else ''
        if value == '' or value == '--':
            return False, f"Campo essenziale '{field}' mancante o vuoto"
            
    # Per i campi opzionali, i valori '--' e vuoti sono accettati e verranno gestiti in seguito
    # Non è necessario fare controlli sui campi opzionali poiché possono essere vuoti o contenere "--"
            
    # Verifica formato email con supporto per formati complessi
    email_text = str(row['email']).strip()
    # Espressione regolare migliorata che supporta caratteri accentati, spazi e formati 'Nome <email@example.com>'
    # Migliorata per supportare specificamente le email @stud.uniroma3.it
    email_pattern = re.compile(r'.*?([a-zA-ZàèéìòóùÀÈÉÌÒÓÙ0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}).*')
    
    # Pattern specifico per email degli studenti di Roma Tre (mmm.mmmmmmm@stud.uniroma3.it)
    student_email_pattern = re.compile(r'([a-zA-ZàèéìòóùÀÈÉÌÒÓÙ]{2,3}\.[a-zA-ZàèéìòóùÀÈÉÌÒÓÙ0-9_\-]+@stud\.uniroma3\.it)')
    
    # Cerca nel testo usando entrambi i pattern
    is_valid_standard = '@' in email_text and email_pattern.search(email_text)
    is_valid_student = student_email_pattern.search(email_text)
    
    if not (is_valid_standard or is_valid_student):
        return False, f"Formato email non valido: {email_text}"
    
    # Verifica formato ora con gestione flessibile
    def validate_ora(ora_str):
        # Rimuovi eventuali spazi
        ora_str = str(ora_str).strip()
        
        # Pattern standard HH:MM
        ora_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$')
        
        # Pattern con secondi HH:MM:SS
        ora_pattern_sec = re.compile(r'^([01]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$') 
        
        # Pattern alternativi che potrebbero essere importati da Excel
        ora_pattern_alt1 = re.compile(r'^([01]?[0-9]|2[0-3])\.([0-5][0-9])$')  # HH.MM
        ora_pattern_alt2 = re.compile(r'^([01]?[0-9]|2[0-3])([0-5][0-9])$')    # HHMM
        
        if ora_pattern.match(ora_str):
            return True
        elif ora_pattern_sec.match(ora_str):  # HH:MM:SS
            return True
        elif ora_pattern_alt1.match(ora_str):
            return True
        elif ora_pattern_alt2.match(ora_str) and len(ora_str) >= 3:  # Almeno 3 cifre per evitare confusione
            return True
        return False
    
    if not validate_ora(row['ora_inizio']):
        return False, f"Formato ora inizio non valido: {row['ora_inizio']}, deve essere HH:MM"
    if not validate_ora(row['ora_fine']):
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
    
    # Espressione regolare migliorata per verificare il formato email
    # Supporta caratteri accentati, spazi e formati complessi
    # Pattern aggiornato per catturare correttamente l'intero indirizzo email
    email_pattern = re.compile(r'.*?([a-zA-ZàèéìòóùÀÈÉÌÒÓÙ0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}).*')
    
    # Pattern specifico per studenti di Roma Tre (mmm.mmmmmmm@stud.uniroma3.it)
    student_email_pattern = re.compile(r'([a-zA-ZàèéìòóùÀÈÉÌÒÓÙ]{2,3}\.[a-zA-ZàèéìòóùÀÈÉÌÒÓÙ0-9_\-]+@stud\.uniroma3\.it)')
    
    # Espressione regolare per verificare il formato ora (HH:MM)
    ora_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$')
    
    # Verifica percorsi formativi validi con normalizzazione
    valid_percorsi = [
        'PeF60 CFU', 
        'PeF30 CFU all.2', 
        'PeF36 CFU', 
        'PeF30 CFU (art. 13)', 
        'PeF30 CFU all.2 art. 13', 
        'PeF36 CFU all.5', 
        'PeF36 CFU (all.5)',
        # Varianti senza "CFU" che vengono utilizzate nell'app
        'PeF 60',
        'PeF 30 all.2',
        'PeF 36',
        'PeF 30 art. 13'
    ]
    
    # Funzione per normalizzare i percorsi
    def normalize_percorso(p):
        p = str(p).strip()
        p = p.replace("(", "").replace(")", "")
        p = p.replace("all.", "allegato")
        p = p.replace("art.", "articolo")
        return p
        
    normalized_valid = [normalize_percorso(p) for p in valid_percorsi]
    
    # Itera sulle righe del DataFrame
    for idx, row in df.iterrows():
        row_errors = []
        
        # Verifica formato email con supporto avanzato
        if 'email' in row:
            email_text = str(row['email']).strip()
            # Cerca nel testo usando entrambi i pattern
            is_valid_standard = '@' in email_text and email_pattern.search(email_text)
            is_valid_student = student_email_pattern.search(email_text)
            
            if not (is_valid_standard or is_valid_student):
                row_errors.append(f"Email non valida: {email_text}. Esempio formato: nome.cognome@uniroma3.it o xxx.yyyyyyy@stud.uniroma3.it")
        
        # Verifica formato ore con validazione flessibile
        def is_valid_ora_format(ora_str):
            ora_str = str(ora_str).strip()
            
            # Pattern standard HH:MM
            if ora_pattern.match(ora_str):
                return True
                
            # Pattern con secondi HH:MM:SS
            if re.match(r'^([01]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$', ora_str):
                return True
                
            # Pattern alternativi che potrebbero essere importati da Excel
            if re.match(r'^([01]?[0-9]|2[0-3])\.([0-5][0-9])$', ora_str):  # HH.MM
                return True
                
            if re.match(r'^([01]?[0-9]|2[0-3])([0-5][0-9])$', ora_str) and len(ora_str) >= 3:  # HHMM o HMM
                return True
                
            return False
        
        if 'ora_inizio' in row and not is_valid_ora_format(row['ora_inizio']):
            row_errors.append(f"Formato ora inizio non valido: {row['ora_inizio']} (deve essere HH:MM)")
        if 'ora_fine' in row and not is_valid_ora_format(row['ora_fine']):
            row_errors.append(f"Formato ora fine non valido: {row['ora_fine']} (deve essere HH:MM)")
        
        # Verifica tipo percorso con normalizzazione
        if 'tipo_percorso' in row:
            percorso = str(row['tipo_percorso'])
            if percorso not in valid_percorsi and normalize_percorso(percorso) not in normalized_valid:
                row_errors.append(f"Tipo percorso non valido: {row['tipo_percorso']}")
        
        # Verifica che l'ora di fine sia successiva all'ora di inizio
        try:
            if 'ora_inizio' in row and 'ora_fine' in row:
                # Normalizza le ore rimuovendo i secondi se presenti
                ora_inizio_str = str(row['ora_inizio']).strip()
                ora_fine_str = str(row['ora_fine']).strip()
                
                # Se l'ora è nel formato HH:MM:SS, estrai solo HH:MM
                if re.match(r'^([01]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$', ora_inizio_str):
                    ora_inizio_str = ora_inizio_str[:5]
                if re.match(r'^([01]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$', ora_fine_str):
                    ora_fine_str = ora_fine_str[:5]
                
                # Converti altri formati a HH:MM prima di confrontare
                if re.match(r'^([01]?[0-9]|2[0-3])\.([0-5][0-9])$', ora_inizio_str):  # HH.MM
                    ora_inizio_str = ora_inizio_str.replace('.', ':')
                if re.match(r'^([01]?[0-9]|2[0-3])\.([0-5][0-9])$', ora_fine_str):  # HH.MM
                    ora_fine_str = ora_fine_str.replace('.', ':')
                    
                # Solo se le ore sono già nel formato standard, confrontale
                if re.match(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$', ora_inizio_str) and re.match(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$', ora_fine_str):
                    ora_inizio = datetime.strptime(ora_inizio_str, '%H:%M')
                    ora_fine = datetime.strptime(ora_fine_str, '%H:%M')
                    if ora_fine <= ora_inizio:
                        row_errors.append(f"Ora fine ({ora_fine_str}) deve essere successiva a ora inizio ({ora_inizio_str})")
        except ValueError:
            # Errore già rilevato dai controlli precedenti
            pass
        
        # Aggiungi errori per questa riga se presenti
        if row_errors:
            # Includi alcuni dati della riga per facilitare l'identificazione
            row_info = f"{row['nome_cognome'] if 'nome_cognome' in row else 'Sconosciuto'} ({row['email'] if 'email' in row and not pd.isna(row['email']) else 'email mancante'})"
            validation_errors.append(f"Riga {idx+2} [{row_info}]: {'; '.join(row_errors)}")
    
    return validation_errors
