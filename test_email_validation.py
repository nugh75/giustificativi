#!/usr/bin/env python3
import re

def test_email_pattern(email_text):
    # Pattern aggiornato per catturare correttamente l'intera email
    email_pattern = re.compile(r'.*?([a-zA-ZàèéìòóùÀÈÉÌÒÓÙ0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}).*')
    
    # Test di validità
    is_valid = '@' in email_text and email_pattern.match(email_text)
    
    # Estrazione email
    email_match = email_pattern.search(email_text)
    extracted_email = email_match.group(1) if email_match else "Nessuna email trovata"
    
    return {
        "testo_originale": email_text,
        "email_valida": is_valid,
        "email_estratta": extracted_email
    }

# Email di test problematiche
test_emails = [
    "normale@example.com",
    "email.con.punti@example.com",
    "giù.costanzo5@stud.uniroma3.it",
    "Giu.puggioni2@stud.uniroma3.it ",  # Con spazio alla fine
    "EMMANUEL LOSIO (Emm Losio emm.losio@stud.uniroma3.it)",
    "esempio@dominio.com.it",
    "mio-nome.cognome@sito-web.org",
    "nome_cognome+etichetta@provider.net",
    "Nome Cognome <email@example.com>",
]

# Esegui i test
print("======= TEST VALIDAZIONE EMAIL =======")
for email in test_emails:
    result = test_email_pattern(email)
    print(f"\nTesto originale: {result['testo_originale']}")
    print(f"Email valida: {'Sì' if result['email_valida'] else 'No'}")
    print(f"Email estratta: {result['email_estratta']}")
print("=====================================")
