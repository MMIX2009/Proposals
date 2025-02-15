import streamlit as st
import webbrowser
import urllib.parse
import datetime
import tempfile
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

image_path = os.path.join(os.path.dirname(__file__), "resources", "DBRDC_logo2.png")

st.set_page_config(
    page_title="Assistant de Projet RDC",
    page_icon=image_path
)

st.markdown("""
    <style>
        .stButton > button {
            background-color: #38b2ce;
            color: white;
        }
        .stButton > button:hover {
            background-color: #281341;
        }
    </style>
""", unsafe_allow_html=True)

def generate_pdf(form_data):
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')

    doc = SimpleDocTemplate(
        temp_pdf.name,
        pagesize=A4,
        title=f"Projet: {form_data.get('Nom du Projet', 'Nouveau Projet')}"
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        textColor=colors.HexColor('#0074a2'),
        spaceAfter=30,
        alignment=1
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        textColor=colors.HexColor('#0074a2'),
        spaceAfter=12
    )

    elements = []

    elements.append(Paragraph('Digital Bridge RDC', title_style))
    elements.append(Paragraph(f"Projet: {form_data.get('Nom du Projet', 'Nouveau Projet')}", heading_style))
    elements.append(Spacer(1, 20))

    sections = {
        "Informations de Base": ["Nom du Projet", "Lieu du Projet", "Statut du Projet",
                                 "Date de Début", "Date de Fin", "Description"],
        "Objectifs": ["Objectifs à Court Terme", "Objectifs à Long Terme", "Phases du Projet"],
        "Équipe et Budget": ["Personne(s) Responsable(s)", "Membres de l'Équipe",
                             "Budget Estimé", "Sources de Financement"],
        "Analyse": ["Risques", "Récompenses"],
        "Analyse SWOT": ["Forces", "Faiblesses", "Opportunités", "Menaces"],
        "Suivi": ["Parties Prenantes", "Mesures d'Impact", "Fréquence des Rapports",
                   "Lien vers la Documentation", "Remarques"]
    }

    for section, fields in sections.items():
        elements.append(Paragraph(section, heading_style))
        for field in fields:
            if field in form_data:
                data = [[field, str(form_data[field])]]
                t = Table(data, colWidths=[150, 350])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f0f2f6')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 12),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                ]))
                elements.append(t)
                elements.append(Spacer(1, 10))
        elements.append(Spacer(1, 20))

    doc.build(elements)
    return temp_pdf.name

def init_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 0
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}

def next_page():
    st.session_state.page += 1
    st.query_params['page'] = st.session_state.page

def prev_page():
    st.session_state.page -= 1
    st.query_params['page'] = st.session_state.page

def format_email_body():
    body = "Détails du Projet:\n\n"
    for key, value in st.session_state.form_data.items():
        if isinstance(value, list):
            value = ", ".join(value)
        elif isinstance(value, datetime.date):
            value = value.strftime('%Y-%m-%d')
        body += f"{key}: {value}\n"
    return body

def header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
            <h1 style='font-size: 3.5em; margin: 0; padding-left: 1rem;'>
                <span style='color: #281341; font-weight: normal;'>Digital Bridge</span> <span style='color: #38b2ce; font-weight: bold;'>RDC</span>
            </h1>
            """, unsafe_allow_html=True)
    with col2:
        try:
            st.image(image_path, width=300)
        except:
            st.error("Logo DBRDC_logo2.png non trouvé")
    st.divider()

def footer():
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em; margin-top: 2rem;'>
        <strong>AVIS DE CONFIDENTIALITÉ</strong><br>
        Ce document est la propriété du Digital Bridge RDC, SPRL. Les informations contenues dans ce document sont 
        strictement confidentielles et ne peuvent être partagées sans autorisation écrite préalable.
        © 2025 Digital Bridge RDC, SPRL. Tous droits réservés.
    </div>
    """, unsafe_allow_html=True)

def goto_page(page_num):
    st.session_state.page = page_num
    st.query_params['page'] = page_num

def main():
    init_session_state()

    # Sidebar for navigation
    pages = [
        "Informations de Base",
        "Objectifs",
        "Équipe et Budget",
        "Analyse",
        "Analyse SWOT",
        "Suivi"
    ]
    
    with st.sidebar:
        st.markdown("## Navigation")
        for i, page_name in enumerate(pages):
            if st.button(page_name, key=f"nav_btn_{i}"):
                goto_page(i)

    # Load query parameters using st.query_params
    params = st.query_params
    if 'page' in params:
        st.session_state.page = int(params['page'])

    header()

    field_descriptions = {
        "Nom du Projet": "Entrez un nom unique et descriptif pour votre projet (ex: 'Formation-Tech-Kinshasa-2024')",
        "Lieu du Projet": "Précisez la ville et la province où le projet sera mis en œuvre",
        "Statut du Projet": "Sélectionnez l'état actuel du projet",
        "Date de Début": "Date prévue ou effective du début du projet",
        "Date de Fin": "Date prévue de fin du projet",
        "Description": "Résumez en 1-2 phrases l'objectif principal et les activités clés du projet",
        "Objectifs à Court Terme": "Listez 3-5 objectifs spécifiques à atteindre dans les 3-6 mois",
        "Objectifs à Long Terme": "Décrivez les impacts durables attendus dans 1-3 ans",
        "Phases du Projet": "Énumérez les étapes principales avec leurs délais approximatifs",
        "Personne(s) Responsable(s)": "Nommez le chef de projet et les responsables principaux avec leurs contacts",
        "Membres de l'Équipe": "Listez les membres clés et leurs rôles spécifiques",
        "Budget Estimé": "Détaillez les coûts par catégorie (personnel, équipement, déplacements)",
        "Sources de Financement": "Indiquez les sources confirmées et potentielles de financement",
        "Risques": "Identifiez les principaux risques et leurs stratégies de mitigation",
        "Récompenses": "Décrivez les bénéfices attendus (sociaux, économiques, environnementaux)",
        "Forces": "Listez les avantages internes et capacités distinctives du projet",
        "Faiblesses": "Identifiez les limitations et défis internes à surmonter",
        "Opportunités": "Décrivez les facteurs externes favorables au projet",
        "Menaces": "Énumérez les obstacles externes potentiels",
        "Parties Prenantes": "Identifiez tous les acteurs impliqués (communautés, autorités, partenaires)",
        "Mesures d'Impact": "Définissez les indicateurs clés de performance",
        "Fréquence des Rapports": "Choisissez la périodicité du suivi",
        "Lien vers la Documentation": "Ajoutez les liens vers les documents détaillés du projet",
        "Remarques": "Ajoutez toute information supplémentaire pertinente"
    }

    pages_content = [
        {"name": "Informations de Base", "fields": [
            ("Nom du Projet", "text"),
            ("Lieu du Projet", ["Mbuji Mayi",
                                "Kanaga",
                                "Kinshasa",
                                "Kikwit",
                                "Autre..."]),
            ("Statut du Projet", ["Proposé", "Actif", "En Cours", "Terminé"]),
            ("Date de Début", "date"),
            ("Date de Fin", "date"),
            ("Description", "text_area")
        ]},
        {"name": "Objectifs", "fields": [
            ("Objectifs à Court Terme", "text_area"),
            ("Objectifs à Long Terme", "text_area"),
            ("Phases du Projet", "text_area")
        ]},
        {"name": "Équipe et Budget", "fields": [
            ("Personne(s) Responsable(s)", "text"),
            ("Membres de l'Équipe", "text_area"),
            ("Budget Estimé", "text"),
            ("Sources de Financement", "text_area")
        ]},
        {"name": "Analyse", "fields": [
            ("Risques", "text_area"),
            ("Récompenses", "text_area")
        ]},
        {"name": "Analyse SWOT", "fields": [
            ("Forces", "text_area"),
            ("Faiblesses", "text_area"),
            ("Opportunités", "text_area"),
            ("Menaces", "text_area")
        ]},
        {"name": "Suivi", "fields": [
            ("Parties Prenantes", "text_area"),
            ("Mesures d'Impact", "text_area"),
            ("Fréquence des Rapports", ["Hebdomadaire", "Mensuel", "Trimestriel"]),
            ("Lien vers la Documentation", "text"),
            ("Remarques", "text_area")
        ]}
    ]

    current_page_content = pages_content[st.session_state.page]
    st.header(current_page_content["name"])

    for field_name, field_type in current_page_content["fields"]:
        st.subheader(field_name)
        st.caption(field_descriptions[field_name])

        if isinstance(field_type, list):
            selected_value = st.selectbox(
                field_name,
                field_type,
                index=field_type.index(st.session_state.form_data.get(field_name)) if st.session_state.form_data.get(field_name) in field_type else 0,
                key=f"select_{field_name}"
            )
            if field_name == "Lieu du Projet" and selected_value == "Autre...":
                st.session_state.form_data[field_name] = st.text_input(
                    "Spécifiez le lieu",
                    st.session_state.form_data.get(field_name, ""),
                    key=f"input_{field_name}"
                )
            else:
                st.session_state.form_data[field_name] = selected_value
        elif field_type == "text":
            st.session_state.form_data[field_name] = st.text_input(
                field_name,
                st.session_state.form_data.get(field_name, ""),
                key=f"input_{field_name}"
            )
        elif field_type == "text_area":
            st.session_state.form_data[field_name] = st.text_area(
                field_name,
                st.session_state.form_data.get(field_name, ""),
                key=f"textarea_{field_name}"
            )
        elif field_type == "date":
            st.session_state.form_data[field_name] = st.date_input(
                field_name,
                st.session_state.form_data.get(field_name, datetime.date.today()),
                key=f"date_{field_name}"
            )

        st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.page > 0:
            st.button("Précédent", on_click=prev_page, key="btn_prev")

    with col2:
        if st.session_state.page < len(pages_content) - 1:
            st.button("Suivant", on_click=next_page, key="btn_next")
        else:
            # Use columns for better layout on the last page
            col_email, col_pdf = st.columns(2)
            with col_email:
              recipient_email = st.text_input("Email du destinataire", key="email_input")
              if st.button("Envoyer par Gmail", key="btn_send"):
                  if recipient_email:
                      subject = f"Projet: {st.session_state.form_data.get('Nom du Projet', 'Nouveau Projet')}"
                      body = format_email_body()

                      pdf_path = generate_pdf(st.session_state.form_data)

                      gmail_url = (f"https://mail.google.com/mail/?view=cm&fs=1&to={recipient_email}"
                                  f"&su={urllib.parse.quote(subject)}&body={urllib.parse.quote(body + chr(10) + chr(10) + 'Note: Please find the attached PDF document with project details.')}")
                      webbrowser.open(gmail_url)
                      os.remove(pdf_path)
                  else:
                      st.error("Veuillez entrer une addresse email.")

            with col_pdf:
              pdf_path = generate_pdf(st.session_state.form_data)
              with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                  label="Télécharger le PDF",
                  data=pdf_file,
                  file_name=f"projet_{st.session_state.form_data.get('Nom du Projet', 'nouveau')}.pdf",
                  mime="application/pdf",
                  key="pdf_download"
                )
              os.remove(pdf_path)

    footer()

if __name__ == "__main__":
    main()