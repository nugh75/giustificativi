import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import config
from PIL import Image as PILImage

# Registra i font se necessario
# pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

def generate_pdf(data, logo_path=None, firma_path=None, output_dir="output", modello="presenza"):
    """
    Genera un PDF di attestato di presenza basato sui dati forniti
    
    Args:
        data (dict): Dizionario contenente i dati per il PDF
        logo_path (str, optional): Percorso del logo. Default a None.
        firma_path (str, optional): Percorso dell'immagine della firma. Default a None.
        output_dir (str, optional): Directory di output. Default a "output".
        modello (str, optional): Tipo di modello da utilizzare ('presenza', 'telematico', 'personalizzato'). Default a "presenza".
        
    Returns:
        str: Percorso del file PDF generato o None in caso di errore
    """
    try:
        # Assicurati che la directory di output esista
        os.makedirs(output_dir, exist_ok=True)
        
        # Crea un nome file basato sul nome e cognome e la data
        file_name = f"attestato_{data['nome_cognome'].replace(' ', '_')}_{data['data'].replace('/', '-')}.pdf"
        file_path = os.path.join(output_dir, file_name)
        
        # Crea il documento PDF
        doc = SimpleDocTemplate(file_path, pagesize=A4, 
                                rightMargin=2*cm, leftMargin=2*cm, 
                                topMargin=2*cm, bottomMargin=2*cm)
        
        # Crea gli stili
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = styles['Normal']
        
        # Crea il contenuto del PDF
        content = []
        
        # Aggiungi il logo se disponibile
        if logo_path and os.path.exists(logo_path):
            # Ridimensiona il logo per adattarlo alla pagina
            # Usa PIL per ottenere le dimensioni corrette dell'immagine
            try:
                pil_img = PILImage.open(logo_path)
                img_width, img_height = pil_img.size
                aspect_ratio = img_width / img_height
                
                # Imposta un'altezza più piccola per il logo (da 2cm a 1.5cm)
                logo = Image(logo_path)
                logo.drawHeight = 1.5*cm
                logo.drawWidth = logo.drawHeight * aspect_ratio
                
                # Limita la larghezza massima a 7 cm
                if logo.drawWidth > 7*cm:
                    logo.drawWidth = 7*cm
                    logo.drawHeight = logo.drawWidth / aspect_ratio
                
                content.append(logo)
                # Aggiungi spazio dopo il logo
                content.append(Spacer(1, 0.5*cm))
            except Exception as e:
                print(f"Errore nel caricamento del logo: {str(e)}")
        
        # Seleziona il modello di testo appropriato
        if modello == "telematico":
            testo_modello = config.ATTESTATO_TELEMATICO
        elif modello == "personalizzato":
            testo_modello = config.ATTESTATO_PERSONALIZZATO
        else:  # default: presenza
            testo_modello = config.ATTESTATO_PRESENZA
            
        # Prepara il percorso completo
        percorsi_completi = {
            "PeF60 CFU": "PeF60 CFU (allegato 1 al DPCM 4 agosto 2023)",
            "PeF30 CFU all.2": "PeF30 CFU all.2 (allegato 2 al DPCM 4 agosto 2023)",
            "PeF36 CFU": "PeF36 CFU (allegato 5 al DPCM 4 agosto 2023)",
            "PeF30 CFU (art. 13)": "PeF30 CFU all.2 (art. 13 del DPCM 4 agosto 2023)",
            "PeF30 CFU all.2 art. 13": "PeF30 CFU all.2 (art. 13 del DPCM 4 agosto 2023)",
            "PeF36 CFU all.5": "PeF36 CFU (allegato 5 al DPCM 4 agosto 2023)",
            "PeF36 CFU (all.5)": "PeF36 CFU (allegato 5 al DPCM 4 agosto 2023)"
        }
        
        # Funzione per normalizzare i percorsi (simile a quella in excel_reader.py)
        def normalize_percorso(p):
            p = str(p).strip()
            p = p.replace("(", "").replace(")", "")  # Rimuovi parentesi
            p = p.replace("all.", "allegato")        # Standardizza abbreviazioni
            p = p.replace("art.", "articolo")        # Standardizza abbreviazioni
            return p
            
        # Trova il percorso completo che corrisponde al tipo_percorso selezionato
        percorso_selezionato = None
        percorso_normalizzato = normalize_percorso(data['tipo_percorso'])
        
        for key, percorso in percorsi_completi.items():
            # Confronta in modo diretto, come sottostringa o in formato normalizzato
            if (key == data['tipo_percorso'] or 
                key in data['tipo_percorso'] or 
                normalize_percorso(key) == percorso_normalizzato):
                percorso_selezionato = percorso
                break
        
        # Se non è stato trovato, usa il valore originale
        if not percorso_selezionato:
            percorso_selezionato = data['tipo_percorso']
            print(f"Avviso: Percorso formativo '{data['tipo_percorso']}' non mappato a una descrizione completa")
        
        # Formatta il testo del modello con i dati
        linee_testo = testo_modello.strip().split('\n')
        
        # Aggiungi il titolo (prime due linee) con stile speciale
        content.append(Paragraph(linee_testo[0], title_style))
        content.append(Paragraph(linee_testo[1], normal_style))
        content.append(Spacer(1, 0.5*cm))
        
        # Formatta il resto del testo con i dati del certificato
        # Aggiungi la data di rilascio (oggi) come data_rilascio
        data_rilascio = datetime.now().strftime("%d/%m/%Y")
        
        # Gestisci il caso in cui classe_concorso sia "--" o vuoto
        classe_concorso = data.get('classe_concorso', '')
        if classe_concorso == '--' or not classe_concorso.strip():
            classe_concorso = ""
        
        # Gestisci i campi opzionali aula, dipartimento e indirizzo
        aula = data.get('aula', '')
        dipartimento = data.get('dipartimento', '')
        indirizzo = data.get('indirizzo', '')
        
        if aula == '--' or not aula.strip():
            aula = ""
        if dipartimento == '--' or not dipartimento.strip():
            dipartimento = ""
        if indirizzo == '--' or not indirizzo.strip():
            indirizzo = ""
            
        # Modifica il template in base alla presenza o assenza di campi
        template_text = '\n'.join(linee_testo[2:])
        
        # Rimuovi classe_concorso se vuoto
        if not classe_concorso:
            template_text = template_text.replace(" – {classe_concorso}", "")
            
        # Modifica il testo per lezioni in presenza quando dipartimento è vuoto
        if modello == "presenza" and not dipartimento:
            # Sostituisci "l'aula {aula} del dipartimento di {dipartimento}" con "l'aula {aula}"
            template_text = template_text.replace("l'aula {aula} del dipartimento di {dipartimento}", "l'aula {aula}")
        
        testo_formattato = template_text.format(
            nome_cognome=data['nome_cognome'],
            data=data['data'],
            data_rilascio=data_rilascio,  # Data di rilascio (oggi)
            ora_inizio=data['ora_inizio'],
            ora_fine=data['ora_fine'],
            aula=aula,
            dipartimento=dipartimento,
            indirizzo=indirizzo,
            tipo_lezione=data['tipo_lezione'],
            tipo_percorso=percorso_selezionato,
            classe_concorso=classe_concorso,
            universita=config.UNIVERSITA,
            direttore_cafis=config.DIRETTORE_CAFIS
        )
        
        # Dividi il testo formattato in paragrafi e aggiungili al contenuto
        for paragrafo in testo_formattato.split('\n'):
            if paragrafo.strip():  # Ignora linee vuote
                content.append(Paragraph(paragrafo, normal_style))
            else:
                content.append(Spacer(1, 0.5*cm))
        
        # Aggiungi la firma se disponibile
        if firma_path and os.path.exists(firma_path):
            try:
                # Aggiungi spazio prima della firma
                content.append(Spacer(1, 1*cm))
                
                # Ridimensiona la firma per adattarla alla pagina
                pil_img = PILImage.open(firma_path)
                img_width, img_height = pil_img.size
                aspect_ratio = img_width / img_height
                
                # Imposta altezza firma a massimo 2 cm
                firma = Image(firma_path)
                firma.drawHeight = min(2*cm, firma.drawHeight)
                firma.drawWidth = firma.drawHeight * aspect_ratio
                
                # Limita la larghezza massima a 5 cm
                if firma.drawWidth > 5*cm:
                    firma.drawWidth = 5*cm
                    firma.drawHeight = firma.drawWidth / aspect_ratio
                    
                content.append(firma)
            except Exception as e:
                print(f"Errore nel caricamento della firma: {str(e)}")
        
        # Genera il PDF
        doc.build(content)
        
        return file_path
        
    except Exception as e:
        print(f"Errore nella generazione del PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
