from crewai import Agent
import google.generativeai as genai
from .student_agent import StudentAgent
from .content_agent import ContentAgent
from .tutor_agent import TutorAgent
import os
from dotenv import load_dotenv

class AdaptiveLearningCrewAgents:
    def __init__(self):
        # Charger les variables d'environnement
        load_dotenv()
        
        # Configuration de Gemini
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Initialiser le modèle Gemini
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialiser les agents spécialisés
        self.student_manager = StudentAgent()
        self.content_manager = ContentAgent()
        self.tutor_manager = TutorAgent()

    def _create_llm_with_gemini(self):
        """Crée une fonction qui utilise Gemini pour générer des réponses"""
        def llm_function(prompt):
            response = self.model.generate_content(prompt)
            return response.text
        return llm_function

    def create_student_agent(self):
        """Crée l'agent responsable de l'analyse des étudiants"""
        return Agent(
            role='Student Analysis Specialist',
            goal='Analyze and track student learning patterns and progress',
            backstory='Expert in educational psychology and learning analytics',
            tools=[
                {
                    'name': 'analyze_performance',
                    'description': 'Analyze student performance and learning patterns',
                    'func': self.student_manager.analyze_performance
                },
                {
                    'name': 'get_learning_style',
                    'description': 'Determine student learning style',
                    'func': self.student_manager.get_learning_style
                },
                {
                    'name': 'track_progress',
                    'description': 'Track student progress over time',
                    'func': self.student_manager.track_progress
                }
            ],
            verbose=True,
            llm=self._create_llm_with_gemini()
        )

    def create_content_agent(self):
        """Crée l'agent responsable du contenu pédagogique"""
        return Agent(
            role='Content Recommendation Specialist',
            goal='Recommend and adapt learning content based on student needs',
            backstory='Expert in educational content curation and personalization',
            tools=[
                {
                    'name': 'recommend_content',
                    'description': 'Recommend personalized learning content',
                    'func': self.content_manager.recommend_content
                },
                {
                    'name': 'adapt_difficulty',
                    'description': 'Adapt content difficulty level',
                    'func': self.content_manager.adapt_difficulty
                },
                {
                    'name': 'get_content_stats',
                    'description': 'Get statistics about content effectiveness',
                    'func': self.content_manager.get_content_stats
                }
            ],
            verbose=True,
            llm=self._create_llm_with_gemini()
        )

    def create_tutor_agent(self):
        """Crée l'agent responsable du tutorat virtuel"""
        return Agent(
            role='Virtual Tutor Specialist',
            goal='Provide personalized tutoring and support',
            backstory='Expert in adaptive tutoring and student support',
            tools=[
                {
                    'name': 'provide_feedback',
                    'description': 'Provide personalized feedback',
                    'func': self.tutor_manager.provide_feedback
                },
                {
                    'name': 'identify_struggles',
                    'description': 'Identify areas where student is struggling',
                    'func': self.tutor_manager.identify_struggles
                },
                {
                    'name': 'suggest_exercises',
                    'description': 'Suggest targeted practice exercises',
                    'func': self.tutor_manager.suggest_exercises
                }
            ],
            verbose=True,
            llm=self._create_llm_with_gemini()
        )
