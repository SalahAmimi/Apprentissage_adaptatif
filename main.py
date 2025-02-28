from crewai import Crew, Task
from agents.crew_agents import AdaptiveLearningCrewAgents
import streamlit as st
import time
import threading

def run_adaptive_learning_crew(student_id=None, subject=None):
    # Créer une instance de AdaptiveLearningCrewAgents
    crew_agents = AdaptiveLearningCrewAgents()
    
    # Obtenir les agents
    student_agent = crew_agents.create_student_agent()
    content_agent = crew_agents.create_content_agent()
    tutor_agent = crew_agents.create_tutor_agent()
    
    # Définir les tâches
    tasks = [
        Task(
            description=f"Analyze learning patterns and progress for student {student_id}",
            agent=student_agent,
            expected_output="Detailed student learning profile and performance analysis"
        ),
        Task(
            description=f"Generate personalized content recommendations for student {student_id} in {subject if subject else 'all subjects'}",
            agent=content_agent,
            expected_output="List of recommended learning materials and activities"
        ),
        Task(
            description=f"Provide tutoring support and identify areas needing attention for student {student_id}",
            agent=tutor_agent,
            expected_output="Personalized tutoring recommendations and intervention strategies"
        )
    ]
    
    # Créer l'équipage
    crew = Crew(
        agents=[student_agent, content_agent, tutor_agent],
        tasks=tasks,
        verbose=True
    )
    
    try:
        # Lancer l'exécution
        result = crew.kickoff()
        return result
    except KeyboardInterrupt:
        print("\nArrêt du système d'apprentissage...")
    except Exception as e:
        print(f"Une erreur est survenue : {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Adaptive Learning System",
        page_icon="📚",
        layout="wide"
    )

    st.title("🎓 Système d'Apprentissage Adaptatif")
    
    # Sidebar pour les contrôles
    with st.sidebar:
        st.header("Configuration")
        student_id = st.text_input("ID Étudiant", "STUDENT001")
        subject = st.selectbox(
            "Matière",
            ["Tous les sujets", "Mathématiques", "Physique", "Chimie", "Informatique", "Langues"]
        )
        
        if st.button("Démarrer l'Analyse", type="primary"):
            with st.spinner("Analyse en cours..."):
                result = run_adaptive_learning_crew(
                    student_id=student_id,
                    subject=subject if subject != "Tous les sujets" else None
                )
                if result:
                    st.success("Analyse terminée !")
                    st.session_state.analysis_result = result

    # Affichage des résultats
    if "analysis_result" in st.session_state:
        result = st.session_state.analysis_result
        
        # Afficher les résultats de l'analyse
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Profil d'Apprentissage")
            st.json(result.get("student_profile", {}))
            
            st.subheader("Points Forts")
            strengths = result.get("strengths", [])
            for strength in strengths:
                st.success(f"✓ {strength}")
        
        with col2:
            st.subheader("Recommandations")
            recommendations = result.get("recommendations", [])
            for rec in recommendations:
                st.info(rec)
            
            st.subheader("Points à Améliorer")
            areas_to_improve = result.get("areas_to_improve", [])
            for area in areas_to_improve:
                st.warning(f"⚠ {area}")

        # Afficher les suggestions de contenu
        st.subheader("Contenu Recommandé")
        content_recommendations = result.get("content_recommendations", [])
        for content in content_recommendations:
            with st.expander(f"📚 {content['title']}"):
                st.write(f"**Type:** {content['type']}")
                st.write(f"**Niveau:** {content['difficulty']}/5")
                st.write(f"**Description:** {content['description']}")
                if st.button("Commencer", key=content['id']):
                    st.session_state.selected_content = content['id']

        # Afficher le support du tuteur
        st.subheader("Support du Tuteur Virtuel")
        tutor_support = result.get("tutor_support", {})
        if tutor_support:
            col3, col4 = st.columns(2)
            
            with col3:
                st.subheader("Difficultés Identifiées")
                for difficulty in tutor_support.get("difficulties", []):
                    st.error(difficulty)
            
            with col4:
                st.subheader("Suggestions d'Exercices")
                for exercise in tutor_support.get("exercises", []):
                    with st.expander(f"📝 {exercise['title']}"):
                        st.write(f"**Durée:** {exercise['duration']} minutes")
                        st.write(f"**Objectif:** {exercise['objective']}")
                        st.write("**Points à travailler:**")
                        for point in exercise['focus_points']:
                            st.write(f"- {point}")

if __name__ == "__main__":
    main()
