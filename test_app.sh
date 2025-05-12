#!/bin/bash

# Generatore Attestati di Presenza - Script di Test Completo
# Questo script esegue un test completo dell'applicazione migliorata

# Mostra intestazione
echo "==============================================================="
echo "    TEST COMPLETO GENERATORE ATTESTATI DI PRESENZA v1.1.0"
echo "==============================================================="
echo

# Verifica ambiente Python
echo "Verifica ambiente Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python non trovato. Installare Python 3.7 o superiore."
    exit 1
fi

echo "✅ Python trovato: $($PYTHON_CMD --version)"

# Verifica pacchetti installati
echo
echo "Verifica pacchetti installati..."

$PYTHON_CMD -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Streamlit non trovato. Installare le dipendenze con: pip install -r requirements.txt"
    exit 1
fi

$PYTHON_CMD -c "import pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Pandas non trovato. Installare le dipendenze con: pip install -r requirements.txt"
    exit 1
fi

$PYTHON_CMD -c "import reportlab" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ ReportLab non trovato. Installare le dipendenze con: pip install -r requirements.txt"
    exit 1
fi

echo "✅ Tutti i pacchetti richiesti sono installati"

# Verifica directory e file
echo
echo "Verifica directory e file..."

# Verifica che le directory richieste esistano
dirs=("assets" "esempi" "utils" "logs")
for dir in "${dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "➕ Creata directory mancante: $dir"
    fi
done

# Verifica file app migliorata
if [ ! -f "app_improved.py" ]; then
    echo "❌ app_improved.py non trovato. Verificare il repository."
    exit 1
fi

echo "✅ Struttura directory e file verificata"

# Genera dati di esempio se necessario
echo
echo "Generazione dati di esempio..."
if [ ! -f "esempi/template_attestati.xlsx" ]; then
    echo "Creazione file template Excel di esempio..."
    $PYTHON_CMD -c "from utils.template_generator import create_template_excel; create_template_excel('esempi/template_attestati.xlsx')" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "❓ Non è stato possibile generare automaticamente i template. I file verranno creati all'avvio dell'applicazione."
    else
        echo "✅ Template Excel creato in: esempi/template_attestati.xlsx"
    fi
fi

# Mostra istruzioni finali
echo
echo "==============================================================="
echo "                  ISTRUZIONI PER L'AVVIO"
echo "==============================================================="
echo
echo "Per avviare la versione migliorata dell'applicazione, eseguire:"
echo "streamlit run app_improved.py"
echo
echo "Per rendere la versione migliorata permanente, eseguire:"
echo "mv app_improved.py app.py"
echo
echo "==============================================================="
echo "                       BUON LAVORO!"
echo "==============================================================="
