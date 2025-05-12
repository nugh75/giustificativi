import pandas as pd
import os
import datetime

def create_requirements_file(output_path="requirements.txt"):
    """
    Genera un file requirements.txt con le dipendenze necessarie per il progetto.
    """
    # Lista delle dipendenze
    dependencies = [
        "streamlit>=1.21.0",
        "pandas>=1.5.0",
        "openpyxl>=3.0.10",
        "reportlab>=3.6.12",
        "pillow>=9.0.0",
        "python-dotenv>=0.20.0",
        "watchdog>=2.1.9",  # Per la ricarica automatica durante lo sviluppo
    ]
    
    # Aggiungi la data come commento
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    header = f"# Generatore Attestati - Dipendenze\n# Generato: {current_date}\n\n"
    
    # Scrivi il file
    with open(output_path, "w") as f:
        f.write(header)
        for dep in dependencies:
            f.write(f"{dep}\n")
    
    return output_path
