import os

# Tenta di caricare dotenv se disponibile
try:
    from dotenv import load_dotenv
    # Carica variabili d'ambiente da .env se presente
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_path)
    print(f"Caricato file di configurazione: {env_path}")
except ImportError:
    print("python-dotenv non è installato. Le variabili d'ambiente saranno caricate direttamente dal sistema.")
except Exception as e:
    print(f"Errore nel caricamento del file .env: {str(e)}")

# Configurazioni predefinite per provider di posta elettronica comuni
EMAIL_PROVIDERS = {
    "gmail": {
        "name": "Gmail",
        "server": "smtp.gmail.com",
        "port": 587,
        "encryption": "STARTTLS",
        "auth": "password",
        "note": "Per Gmail potrebbe essere necessario abilitare l'accesso alle app meno sicure o usare una password specifica per app"
    },
    "outlook": {
        "name": "Outlook.com / Office 365",
        "server": "smtp-mail.outlook.com",
        "port": 587,
        "encryption": "STARTTLS",
        "auth": "password", 
        "note": "Per Outlook potrebbe essere necessario generare una password per app"
    },
    "libero": {
        "name": "Libero",
        "server": "smtp.libero.it",
        "port": 465,
        "encryption": "SSL/TLS",
        "auth": "password",
        "note": "Per Libero potrebbe essere necessario abilitare l'accesso SMTP nelle impostazioni"
    },
    "custom": {
        "name": "Personalizzato",
        "server": "",
        "port": 587,
        "encryption": "STARTTLS",
        "auth": "password",
        "note": "Configura manualmente le impostazioni del tuo provider di posta"
    }
}

# Configurazioni SMTP per l'invio email
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp-mail.outlook.com")  # Default a Outlook
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = True

# Configurazioni del Centro CAFIS
DIRETTORE_CAFIS = os.getenv("DIRETTORE_CAFIS", "Prof. Mario Rossi")
DOCENTE_CORSO = os.getenv("DOCENTE_CORSO", "")
UNIVERSITA = "Università degli Studi Roma Tre"

# Percorsi default per assets
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
FIRMA_PATH = os.path.join(os.path.dirname(__file__), "assets", "firma.png")

# Configurazione email
EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT", "Attestato di Presenza - Percorso di formazione DPCM")
EMAIL_BODY_DEFAULT = """
Gentile {nome_cognome},

In allegato trova l'attestato di presenza relativo alla lezione del {data}.

Cordiali saluti,
{firmatario}
{universita}
"""

# Recupera il testo personalizzato dell'email o usa il default
EMAIL_BODY = os.getenv("EMAIL_BODY", EMAIL_BODY_DEFAULT)
