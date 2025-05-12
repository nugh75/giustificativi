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

def generate_pdf(data, logo_path=None, firma_path=None, output_dir="output"):
    """
    Genera un PDF di attestato di presenza basato sui dati forniti
    
    Args:
        data (dict): Dizionario contenente i dati per il PDF
        logo_path (str, optional): Percorso del logo. Default a None.
        firma_path (str, optional): Percorso dell'immagine della firma. Default a None.
        output_dir (str, optional): Directory di output. Default a "output".
        
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
        
        # Aggiungi il titolo
        content.append(Paragraph("ATTESTATO DI PRESENZA", title_style))
        content.append(Paragraph("Attività didattiche Percorso di formazione DPCM 4 agosto 2023", normal_style))
        content.append(Spacer(1, 0.5*cm))
        
        # Aggiungi i dati principali
        content.append(Paragraph(f"Si attesta che il/la sig./sig.ra <b>{data['nome_cognome']}</b>", normal_style))
        content.append(Paragraph(f"in data odierna, dalle ore <b>{data['ora_inizio']}</b> alle ore <b>{data['ora_fine']}</b> presso l'aula", normal_style))
        content.append(Paragraph(f"<b>{data['aula']}</b> del Dipartimento di <b>{data['dipartimento']}</b>,", normal_style))
        content.append(Paragraph(f"in via <b>{data['indirizzo']}</b> ha seguito la lezione di", normal_style))
        content.append(Paragraph(f"<b>{data['tipo_lezione']}</b> nell'ambito del", normal_style))
        
        content.append(Spacer(1, 0.5*cm))
        
        # Crea il contenuto per il tipo di percorso formativo - Mostra solo il percorso selezionato
        percorsi_completi = {
            "PeF60 CFU": "PeF60 CFU (allegato 1 al DPCM 4 agosto 2023)",
            "PeF30 CFU": "PeF30 CFU (allegato 2 al DPCM 4 agosto 2023)",
            "PeF36 CFU": "PeF36 CFU (allegato 5 al DPCM 4 agosto 2023)",
            "PeF30 CFU (art. 13)": "PeF30 CFU (art. 13 del DPCM 4 agosto 2023)"
        }
        
        # Trova il percorso completo che corrisponde al tipo_percorso selezionato
        percorso_selezionato = None
        for key, percorso in percorsi_completi.items():
            if key in data['tipo_percorso']:
                percorso_selezionato = percorso
                break
        
        # Se non è stato trovato, usa il valore originale
        if not percorso_selezionato:
            percorso_selezionato = data['tipo_percorso']
            
        # Crea uno stile con testo più grande e grassetto
        percorso_style = ParagraphStyle(
            'PercorsoStyle',
            parent=normal_style,
            fontSize=12,
            leading=14,
            spaceAfter=6
        )
        
        # Aggiungi solo il percorso selezionato
        content.append(Paragraph(f"<b>{percorso_selezionato}</b>", percorso_style))
                
        content.append(Spacer(1, 0.5*cm))
        
        content.append(Paragraph(f"per la classe di concorso <b>{data['classe_concorso']}</b> organizzato", normal_style))
        content.append(Paragraph(f"dall'{config.UNIVERSITA}.", normal_style))
        content.append(Spacer(1, 0.5*cm))
        content.append(Paragraph("Si rilascia su richiesta dell'interessato/a per tutti gli usi consentiti dalla legge.", normal_style))
        
        # Aggiungi la data
        content.append(Spacer(1, 1*cm))
        content.append(Paragraph(f"Roma, lì {data['data']}", normal_style))
        
        # Aggiungi il VISTO e il nome del direttore - Riduci lo spazio
        content.append(Spacer(1, 0.7*cm))
        content.append(Paragraph("VISTO", normal_style))
        content.append(Paragraph(f"Prof./Prof.ssa {config.DIRETTORE_CAFIS}", normal_style))
        
        # Aggiungi la firma se disponibile
        if firma_path and os.path.exists(firma_path):
            try:
                # Usa PIL per ottenere l'aspect ratio corretto
                pil_img = PILImage.open(firma_path)
                img_width, img_height = pil_img.size
                aspect_ratio = img_width / img_height
                
                firma = Image(firma_path)
                # Riduci l'altezza della firma per evitare che vada nella seconda pagina
                firma.drawHeight = 1.2*cm
                firma.drawWidth = firma.drawHeight * aspect_ratio
                
                # Limita la larghezza massima
                if firma.drawWidth > 5*cm:
                    firma.drawWidth = 5*cm
                    firma.drawHeight = firma.drawWidth / aspect_ratio
                
                content.append(firma)
            except Exception as e:
                print(f"Errore nel caricamento della firma: {str(e)}")
        
        # Costruisci il documento
        doc.build(content)
        
        return file_path
        
    except Exception as e:
        print(f"Errore nella generazione del PDF: {str(e)}")
        return None
