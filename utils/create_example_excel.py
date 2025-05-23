import pandas as pd
import os
from datetime import date, timedelta

def create_example_excel(output_path):
    """
    Crea un file Excel di esempio con dati fittizi per testare l'applicazione.
    
    Args:
        output_path (str): Percorso dove salvare il file Excel.
    """
    # Definiamo i dipartimenti e le relative informazioni
    dipartimenti = [
        {
            "nome": "Scienze della Formazione",
            "indirizzo": "Via del Castro Pretorio 20, Roma",
            "aule": ["A1", "A2", "B1", "B2", "C1"]
        },
        {
            "nome": "Ingegneria",
            "indirizzo": "Via Vito Volterra 62, Roma",
            "aule": ["S1", "S2", "S3", "L1", "L2"]
        },
        {
            "nome": "Lettere e Filosofia",
            "indirizzo": "Via Ostiense 234, Roma",
            "aule": ["Aula 1", "Aula 2", "Aula Magna", "Aula 4", "Sala Conferenze"]
        }
    ]
    
    # Tipi di lezione
    lezioni = [
        "Didattica generale",
        "Pedagogia",
        "Psicologia dell'educazione",
        "Didattica inclusiva",
        "Metodologie e tecnologie didattiche",
        "Antropologia culturale",
        "Psicologia dello sviluppo",
        "Legislazione scolastica",
        "Pedagogia speciale",
        "Tecnologie per la didattica"
    ]
    
    # Classi di concorso
    classi_concorso = [
        "A-01 (Arte e immagine nella scuola secondaria)",
        "A-12 (Discipline letterarie)",
        "A-18 (Filosofia e scienze umane)",
        "A-25 (Lingua inglese)",
        "A-26 (Matematica)",
        "A-27 (Matematica e fisica)",
        "A-28 (Matematica e scienze)",
        "A-30 (Musica)",
        "A-48 (Scienze motorie)",
        "A-60 (Tecnologia)"
    ]
    
    # Tipi di percorso
    percorsi = [
        "PeF60 CFU",
        "PeF30 CFU all.2",
        "PeF36 CFU",
        "PeF30 CFU (art. 13)"
    ]
    
    # Crea una lista di dati
    data_list = []
    
    # Data di inizio (oggi)
    today = date.today()
    
    # Crea 20 record di esempio
    for i in range(20):
        # Calcola la data (distribuita nelle ultime due settimane)
        record_date = today - timedelta(days=i % 14)
        record_date_str = record_date.strftime("%d/%m/%Y")
        
        # Seleziona il dipartimento e l'aula
        dept_idx = i % len(dipartimenti)
        dipartimento = dipartimenti[dept_idx]
        aula = dipartimento["aule"][i % len(dipartimento["aule"])]
        
        # Seleziona il tipo di lezione e la classe di concorso
        tipo_lezione = lezioni[i % len(lezioni)]
        classe_concorso = classi_concorso[i % len(classi_concorso)]
        
        # Alterna i percorsi formativi
        tipo_percorso = percorsi[i % len(percorsi)]
        
        # Definisci gli orari (mattina o pomeriggio)
        if i % 2 == 0:
            ora_inizio = "09:00"
            ora_fine = "11:00"
        else:
            ora_inizio = "14:00"
            ora_fine = "16:00"
        
        # Crea un nome e cognome fittizio
        nomi = ["Mario", "Giulia", "Luca", "Anna", "Paolo", "Chiara", "Marco", "Francesca", "Andrea", "Laura"]
        cognomi = ["Rossi", "Bianchi", "Verdi", "Neri", "Ferrari", "Esposito", "Romano", "Russo", "Gallo", "Costa"]
        
        nome = nomi[i % len(nomi)]
        cognome = cognomi[(i + 3) % len(cognomi)]  # Offset per avere combinazioni diverse
        nome_cognome = f"{nome} {cognome}"
        
        # Crea un'email fittizia
        email = f"{nome.lower()}.{cognome.lower()}@esempio.com"
        
        # Aggiungi il record alla lista
        data_list.append({
            "nome_cognome": nome_cognome,
            "data": record_date_str,
            "ora_inizio": ora_inizio,
            "ora_fine": ora_fine,
            "aula": aula,
            "dipartimento": dipartimento["nome"],
            "indirizzo": dipartimento["indirizzo"],
            "tipo_lezione": tipo_lezione,
            "tipo_percorso": tipo_percorso,
            "classe_concorso": classe_concorso,
            "email": email
        })
    
    # Converti la lista in DataFrame
    df = pd.DataFrame(data_list)
    
    # Assicurati che la directory esista
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Salva il DataFrame come file Excel
    df.to_excel(output_path, index=False)
    print(f"File Excel di esempio creato: {output_path}")
    
    return output_path

if __name__ == "__main__":
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "esempi", "dati_esempio_completo.xlsx")
    create_example_excel(output_file)
