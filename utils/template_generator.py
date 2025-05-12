import pandas as pd
import os
from datetime import date, timedelta

def create_template_excel(output_path, template_type='base', num_records=8):
    """
    Crea un file Excel template con dati di esempio.
    
    Args:
        output_path (str): Percorso dove salvare il file Excel.
        template_type (str): Tipo di template da creare ('base', 'minimo', 'completo').
        num_records (int): Numero di record di esempio da creare.
        
    Returns:
        str: Percorso del file creato.
    """
    # Definisci i dati di esempio in base al tipo di template
    if template_type == 'minimo':
        # Template minimale con solo le colonne obbligatorie
        df = pd.DataFrame({
            'nome_cognome': ['Mario Rossi', 'Anna Verdi', 'Luca Bianchi'],
            'data': ['15/05/2025', '16/05/2025', '17/05/2025'],
            'ora_inizio': ['09:00', '14:00', '11:00'],
            'ora_fine': ['11:00', '16:00', '13:00'],
            'aula': ['A1', 'B2', 'C3'],
            'dipartimento': ['Scienze della Formazione', 'Scienze della Formazione', 'Scienze della Formazione'],
            'indirizzo': ['Via del Castro Pretorio 20, Roma', 'Via del Castro Pretorio 20, Roma', 'Via del Castro Pretorio 20, Roma'],
            'tipo_lezione': ['Didattica generale', 'Pedagogia', 'Psicologia dell\'educazione'],
            'tipo_percorso': ['PeF60 CFU', 'PeF30 CFU', 'PeF36 CFU'],
            'classe_concorso': ['A-01', 'A-12', 'A-25'],
            'email': ['mario.rossi@esempio.com', 'anna.verdi@esempio.com', 'luca.bianchi@esempio.com']
        })
    elif template_type == 'completo':
        # Importa la funzione per creare dati più completi e vari
        from utils.create_example_excel import create_example_excel
        return create_example_excel(output_path)
    else:
        # Template base (predefinito)
        # Percorsi formativi disponibili
        percorsi = [
            "PeF60 CFU",
            "PeF30 CFU",
            "PeF36 CFU",
            "PeF30 CFU (art. 13)"
        ]
        
        # Data odierna
        today = date.today()
        
        # Lista che conterrà i dati
        data = []
        
        for i in range(num_records):
            # Alterna i percorsi formativi
            percorso = percorsi[i % len(percorsi)]
            
            # Crea date distribuite nei giorni precedenti
            record_date = today - timedelta(days=i)
            record_date_str = record_date.strftime("%d/%m/%Y")
            
            # Alterna mattina/pomeriggio
            if i % 2 == 0:
                ora_inizio = "09:00"
                ora_fine = "11:00"
            else:
                ora_inizio = "14:30"
                ora_fine = "16:30"
            
            # Aggiungi il record
            data.append({
                'nome_cognome': f"Nome Cognome {i+1}",
                'data': record_date_str,
                'ora_inizio': ora_inizio,
                'ora_fine': ora_fine,
                'aula': f"Aula {i%5 + 1}",
                'dipartimento': "Scienze della Formazione",
                'indirizzo': "Via del Castro Pretorio 20, Roma",
                'tipo_lezione': ["Didattica generale", "Pedagogia", "Metodologie", "Psicologia"][i % 4],
                'tipo_percorso': percorso,
                'classe_concorso': f"A-{(i % 30) + 1:02d}",
                'email': f"utente{i+1}@esempio.com"
            })
        
        # Crea il DataFrame
        df = pd.DataFrame(data)
    
    # Assicurati che la directory esista
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Salva il DataFrame come file Excel
    df.to_excel(output_path, index=False)
    
    return output_path

def create_empty_template(output_path):
    """
    Crea un file Excel vuoto con solo le intestazioni delle colonne.
    
    Args:
        output_path (str): Percorso dove salvare il file Excel.
        
    Returns:
        str: Percorso del file creato.
    """
    # Crea un DataFrame vuoto con solo le intestazioni delle colonne richieste
    df = pd.DataFrame(columns=[
        'nome_cognome',
        'data',
        'ora_inizio',
        'ora_fine',
        'aula',
        'dipartimento',
        'indirizzo',
        'tipo_lezione',
        'tipo_percorso',
        'classe_concorso',
        'email'
    ])
    
    # Aggiungi una riga di esempio
    df.loc[0] = [
        'Nome Cognome',
        date.today().strftime("%d/%m/%Y"),
        '09:00',
        '11:00',
        'Aula',
        'Dipartimento',
        'Indirizzo',
        'Tipo di lezione',
        'PeF60 CFU',
        'A-01',
        'email@esempio.com'
    ]
    
    # Assicurati che la directory esista
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Salva il DataFrame come file Excel
    writer = pd.ExcelWriter(output_path, engine='openpyxl')
    df.to_excel(writer, index=False)
    
    # Ottenere il foglio attivo
    worksheet = writer.sheets['Sheet1']
    
    # Aggiungi note alle celle per spiegare il formato richiesto
    notes = {
        'A1': 'Inserire nome e cognome del partecipante',
        'B1': 'Formato data: GG/MM/AAAA (es. 15/05/2025)',
        'C1': 'Formato ora: HH:MM (es. 09:00)',
        'D1': 'Formato ora: HH:MM (es. 11:00)',
        'I1': 'Deve essere uno tra: "PeF60 CFU", "PeF30 CFU", "PeF36 CFU", "PeF30 CFU (art. 13)"',
        'K1': 'Indirizzo email valido'
    }
    
    # Salva il file
    writer.save()
    
    return output_path
