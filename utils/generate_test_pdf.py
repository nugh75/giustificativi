#!/usr/bin/env python3
"""
Script per generare un PDF di test con dati fittizi
"""
import os
import sys
from datetime import date

# Aggiungi la directory principale al path per permettere l'importazione dei moduli
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_generator import generate_pdf

def main():
    # Dati fittizi per il test
    test_data = {
        'nome_cognome': 'Mario Rossi',
        'data': date.today().strftime("%d/%m/%Y"),
        'ora_inizio': '09:00',
        'ora_fine': '11:00',
        'aula': 'A1',
        'dipartimento': 'Scienze della Formazione',
        'indirizzo': 'Via del Castro Pretorio 20',
        'tipo_lezione': 'Didattica generale',
        'tipo_percorso': 'PeF60 CFU',
        'classe_concorso': 'A-01'
    }
    
    # Percorsi logo e firma
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Verifica se esistono file di logo e firma nella directory assets
    assets_dir = os.path.join(base_dir, 'assets')
    logo_path = None
    firma_path = None
    
    # Cerca file di logo
    for file in os.listdir(assets_dir):
        if file.lower().startswith('logo') or 'logo' in file.lower():
            logo_path = os.path.join(assets_dir, file)
            break
    
    # Cerca file di firma
    for file in os.listdir(assets_dir):
        if file.lower().startswith('firma') or 'firma' in file.lower():
            firma_path = os.path.join(assets_dir, file)
            break
    
    # Se non troviamo il logo o la firma, informiamo l'utente
    if not logo_path:
        print("ATTENZIONE: Nessun file di logo trovato nella directory assets.")
        print("Per un test completo, aggiungi un'immagine chiamata logo.png o logo.jpg nella directory assets.")
    
    if not firma_path:
        print("ATTENZIONE: Nessun file di firma trovato nella directory assets.")
        print("Per un test completo, aggiungi un'immagine chiamata firma.png o firma.jpg nella directory assets.")
    
    # Directory di output
    output_dir = os.path.join(base_dir, 'test_output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Genera il PDF
    pdf_path = generate_pdf(test_data, logo_path, firma_path, output_dir)
    
    if pdf_path:
        print(f"PDF generato con successo: {pdf_path}")
    else:
        print("Errore nella generazione del PDF")

if __name__ == "__main__":
    main()
