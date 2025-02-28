import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path
import time
import json
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from agents.crew_agents import AdaptiveLearningCrewAgents

# Configuration de la page
st.set_page_config(
    page_title="Adaptive Learning Dashboard",
    page_icon="📚",
    layout="wide"
)

# Initialisation des agents
crew_agents = AdaptiveLearningCrewAgents()

# Titre
st.title("📚 Système d'Apprentissage Adaptatif")

# Sidebar - Partie 1 : ID Étudiant
with st.sidebar:
    st.header("Configuration")
    student_id = st.text_input("ID Étudiant", "STUDENT001")

# Gestion de l'état de la session
if "current_student_id" not in st.session_state or st.session_state.current_student_id != student_id:
    st.session_state.current_student_id = student_id
    # Réinitialiser l'état pour le nouvel étudiant
    st.session_state.show_questionnaire = True
    if "learning_style" in st.session_state:
        del st.session_state.learning_style

# Vérification du style d'apprentissage
if "learning_style" not in st.session_state:
    learning_style = crew_agents.student_manager.get_learning_style(student_id)
    if learning_style:
        st.session_state.learning_style = learning_style
        st.session_state.show_questionnaire = False

# Sidebar - Partie 2 : Autres configurations
with st.sidebar:
    # Récupérer les préférences actuelles
    current_preferences = crew_agents.student_manager.get_current_preferences(student_id)
    
    # Sélection de la matière et du module
    st.subheader("Sélection du Cours")
    selected_subject = st.selectbox(
        "Matière",
        ["Mathématiques", "Physique", "Chimie", "Informatique", "Langues"],
        key="subject_select"
    )
    
    # Modules spécifiques selon la matière
    modules = {
        "Mathématiques": ["Algèbre", "Analyse", "Géométrie", "Probabilités", "Statistiques"],
        "Physique": ["Mécanique", "Électricité", "Optique", "Thermodynamique", "Quantique"],
        "Chimie": ["Chimie organique", "Chimie inorganique", "Biochimie", "Chimie analytique"],
        "Informatique": ["Programmation", "Algorithmes", "Bases de données", "Réseaux", "IA"],
        "Langues": ["Grammaire", "Vocabulaire", "Expression orale", "Compréhension"]
    }
    
    selected_module = st.selectbox(
        "Module spécifique",
        modules.get(selected_subject, ["Général"]),
        key="module_select"
    )
    
    # Préférences d'apprentissage
    st.subheader("Préférences d'Apprentissage")
    
    # Niveau de difficulté souhaité
    desired_difficulty = st.slider(
        "Niveau de difficulté souhaité",
        min_value=1,
        max_value=5,
        value=current_preferences.get("difficulty", 3) if current_preferences else 3,
        help="1 = Débutant, 5 = Expert",
        key="difficulty_slider"
    )
    
    # Durée de session préférée
    preferred_duration = st.select_slider(
        "Durée de session préférée (minutes)",
        options=[15, 30, 45, 60, 90, 120],
        value=current_preferences.get("duration", 30) if current_preferences else 30,
        key="duration_slider"
    )
    
    # Type de contenu préféré
    default_content_types = current_preferences.get("content_types", ["Vidéos", "Exercices interactifs"]) if current_preferences else ["Vidéos", "Exercices interactifs"]
    preferred_content_types = st.multiselect(
        "Types de contenu préférés",
        ["Vidéos", "Documents PDF", "Exercices interactifs", "Audio", "Quiz"],
        default=default_content_types,
        key="content_types_select"
    )
    
    # Objectifs d'apprentissage
    st.subheader("Objectifs")
    learning_goal = st.text_area(
        "Décrivez vos objectifs d'apprentissage",
        value=current_preferences.get("learning_goal", "") if current_preferences else "",
        placeholder="Ex: Je souhaite comprendre les concepts de base de l'algèbre linéaire...",
        key="learning_goal_input"
    )

    # Bouton pour mettre à jour les préférences
    if st.button("Mettre à jour mes préférences", type="primary"):
        new_preferences = {
            "subject": selected_subject,
            "module": selected_module,
            "difficulty": desired_difficulty,
            "duration": preferred_duration,
            "content_types": preferred_content_types,
            "learning_goal": learning_goal
        }
        
        if crew_agents.student_manager.update_learning_preferences(student_id, new_preferences):
            st.success("✅ Préférences mises à jour avec succès !")
            st.info("Le style d'apprentissage a été recalculé en fonction de vos nouvelles préférences.")
            # Forcer le rechargement de la page pour afficher les nouvelles préférences
            st.rerun()
        else:
            st.error("❌ Erreur lors de la mise à jour des préférences.")

# Affichage du questionnaire ou du contenu principal
if st.session_state.show_questionnaire:
    st.header("🎯 Détermination du Style d'Apprentissage")
    st.write("Pour personnaliser votre expérience d'apprentissage, veuillez répondre à ce court questionnaire.")
    
    questionnaire = crew_agents.student_manager.get_learning_style_questionnaire()
    answers = []
    
    for question in questionnaire["questions"]:
        choice = st.radio(
            question["text"],
            options=[choice["text"] for choice in question["choices"]],
            key=f"q_{question['id']}"
        )
        selected_choice = next(c for c in question["choices"] if c["text"] == choice)
        answers.append(selected_choice["id"])
    
    if st.button("Soumettre le Questionnaire"):
        learning_style = crew_agents.student_manager.get_learning_style(student_id, answers)
        crew_agents.student_manager.save_learning_style(student_id, learning_style)
        st.success("Style d'apprentissage déterminé avec succès !")
        st.info(f"Votre style d'apprentissage dominant est : {learning_style}")
        
        # Mettre à jour l'état de la session
        st.session_state.show_questionnaire = False
        st.session_state.learning_style = learning_style
        
        # Forcer le rechargement de la page
        st.rerun()

else:
    # Récupérer le style d'apprentissage de la session
    learning_style = st.session_state.learning_style

# Layout principal avec les nouvelles informations
col1, col2 = st.columns(2)

# Profil d'apprentissage
with col1:
    st.subheader("Profil d'Apprentissage")
    
    # Style d'apprentissage
    with st.expander("🎯 Style d'Apprentissage", expanded=True):
        st.info(f"Style d'apprentissage dominant : {learning_style}")
        
        # Récupérer les détails du style d'apprentissage
        with open(crew_agents.student_manager.students_file, "r", encoding='utf-8') as f:
            students_data = json.load(f)
            student = next((s for s in students_data["students"] if s["id"] == student_id), None)
            if student and "learning_style_details" in student:
                details = student["learning_style_details"]
                
                # Afficher les pourcentages pour chaque style
                st.write("**Répartition des styles d'apprentissage :**")
                for style, percentage in details["style_percentages"].items():
                    st.progress(percentage / 100)
                    st.write(f"{style.capitalize()}: {percentage:.1f}%")
                
                # Afficher les styles secondaires
                st.write("**Styles secondaires :**")
                for style, pct in details["secondary_styles"]:
                    st.write(f"- {style.capitalize()}: {pct:.1f}%")
                
                # Date de la dernière mise à jour
                st.write(f"*Dernière mise à jour : {datetime.fromisoformat(student['learning_style_updated']).strftime('%d/%m/%Y')}*")
                
                # Bouton pour refaire le questionnaire
                if st.button("Refaire le questionnaire"):
                    st.session_state.redo_questionnaire = True
                    st.rerun()
    
    # Afficher les préférences sélectionnées
    st.subheader("Préférences Actuelles")
    st.write(f"**Module:** {selected_module} ({selected_subject})")
    st.write(f"**Niveau souhaité:** {desired_difficulty}/5")
    st.write(f"**Durée de session:** {preferred_duration} minutes")
    st.write("**Types de contenu préférés:**")
    for content_type in preferred_content_types:
        st.write(f"- {content_type}")
    
    if learning_goal:
        st.write("**Objectifs:**")
        st.write(learning_goal)

# Contenu Recommandé
st.header("📚 Contenu Recommandé")

# Préparer les préférences utilisateur
user_preferences = {
    "module": selected_module,
    "difficulty": desired_difficulty,
    "duration": preferred_duration,
    "content_types": preferred_content_types,
    "learning_goal": learning_goal
}

# Obtenir les recommandations
recommendations = crew_agents.content_manager.recommend_content(
    student_id, 
    subject=selected_subject,
    preferences=user_preferences
)

if recommendations:
    for i, content in enumerate(recommendations):
        with st.expander(f"📖 {content['title']} ({content['module']})", expanded=False):
            col_content1, col_content2 = st.columns([2, 1])
            
            with col_content1:
                st.write(f"**Type:** {content['type']}")
                st.write(f"**Niveau:** {content['difficulty']}/5")
                st.write(f"**Description:** {content['description']}")
                
                # Afficher les objectifs
                if 'objectives' in content and content['objectives']:
                    st.write("**Objectifs:**")
                    for obj in content['objectives']:
                        st.write(f"• {obj}")
                
                # Afficher les prérequis
                if 'prerequisites' in content and content['prerequisites']:
                    st.write("**Prérequis:**")
                    for prereq in content['prerequisites']:
                        st.write(f"• {prereq}")
            
            with col_content2:
                st.write(f"**Durée:** {content['duration']} minutes")
                
                # Afficher la ressource principale selon le type
                st.write("**Ressource Principale:**")
                if content.get('resource_type') == 'video':
                    try:
                        st.video(content['resource_url'])
                    except:
                        st.write(f"[Voir la vidéo]({content['resource_url']})")
                else:
                    st.write(f"[Accéder à la ressource]({content['resource_url']})")
                
                # Afficher les ressources complémentaires
                if 'additional_resources' in content and content['additional_resources']:
                    st.write("**Ressources Complémentaires:**")
                    for resource in content['additional_resources']:
                        st.write(f"• [{resource['type'].title()}]({resource['url']})")
            
            # Afficher les prochaines étapes
            if 'next_steps' in content and content['next_steps']:
                st.write("**Prochaines étapes suggérées:**")
                for step in content['next_steps']:
                    st.write(f"• {step}")
            
            # Bouton pour commencer avec une clé unique
            if st.button("Commencer", key=f"btn_{content['id']}_{i}"):
                st.session_state.selected_content = content['id']
                st.success("Contenu sélectionné ! Le tuteur virtuel suivra votre progression.")
                st.rerun()
else:
    st.info("Aucune recommandation disponible pour le moment. Veuillez ajuster vos préférences.")

# Section Planning du Tuteur
if recommendations:
    st.header("📅 Planning d'Apprentissage Recommandé")
    
    # Obtenir le feedback du tuteur
    tutor_feedback = crew_agents.tutor_manager.provide_feedback(student_id)
    
    # Afficher le planning hebdomadaire
    st.subheader("Programme de la Semaine")
    
    # Créer des colonnes pour les jours de la semaine
    cols = st.columns(3)
    
    # Répartir les recommandations sur la semaine
    for i, content in enumerate(recommendations):
        jour = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"][i % 5]
        with cols[i % 3]:
            st.markdown(f"**{jour}**")
            st.markdown(f"""
            🎯 **{content['title']}**
            - Durée: {content['duration']} minutes
            - Type: {content['type']}
            - Niveau: {content['difficulty']}/5
            """)
            
            # Ajouter des conseils spécifiques
            if content.get('resource_type') == 'video':
                st.markdown("""
                💡 **Conseils:**
                - Prenez des notes pendant le visionnage
                - Faites des pauses toutes les 20 minutes
                - Révisez vos notes après la vidéo
                """)
    
    # Conseils généraux du tuteur
    st.subheader("💡 Conseils pour Optimiser votre Apprentissage")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Organisation du Temps**
        - Commencez par les contenus les plus complexes quand vous êtes le plus concentré
        - Prévoyez des pauses de 10-15 minutes entre chaque session
        - Révisez brièvement le contenu de la veille avant de commencer
        """)
        
        st.markdown("""
        **Méthode d'Apprentissage**
        - Prenez des notes actives pendant les sessions
        - Faites des résumés après chaque session
        - Testez vos connaissances régulièrement
        """)
    
    with col2:
        st.markdown("""
        **Progression Recommandée**
        1. Commencez par les concepts fondamentaux
        2. Pratiquez avec les exercices après chaque vidéo
        3. Faites une auto-évaluation à la fin de la semaine
        """)
        
        st.markdown("""
        **Points d'Attention**
        - Assurez-vous de bien comprendre chaque concept avant de passer au suivant
        - N'hésitez pas à revoir les vidéos si nécessaire
        - Gardez un rythme régulier dans votre apprentissage
        """)
    
    # Rappel des objectifs
    st.info(f"""
    🎯 **Objectif de la semaine:** 
    Maîtriser les concepts de {selected_module} en {selected_subject} 
    à travers {len(recommendations)} sessions d'apprentissage structurées.
    """)
    
    # Barre de progression
    st.subheader("📊 Suivi de la Progression")
    progress_placeholder = st.empty()
    if 'progress' not in st.session_state:
        st.session_state.progress = 0
    
    progress_bar = progress_placeholder.progress(st.session_state.progress)
    st.caption("Progression de votre plan d'apprentissage cette semaine")
