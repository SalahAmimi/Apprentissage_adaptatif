import json
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

class TutorAgent:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.learning_data_file = self.data_dir / "learning_data.json"
        self.feedback_file = self.data_dir / "feedback.json"
        self.init_data_files()

    def init_data_files(self):
        """Initialise les fichiers de données s'ils n'existent pas"""
        self.data_dir.mkdir(exist_ok=True)
        
        if not self.feedback_file.exists():
            default_feedback = {
                "feedback_records": []
            }
            with open(self.feedback_file, "w", encoding='utf-8') as f:
                json.dump(default_feedback, f, indent=4, ensure_ascii=False)

        # Initialiser les données d'apprentissage avec des données de test
        if not self.learning_data_file.exists():
            test_data = {
                "learning_records": [
                    {
                        "student_id": "STUDENT001",
                        "timestamp": datetime.now().isoformat(),
                        "subject": "Mathématiques",
                        "content_type": "visual",
                        "content_id": "MATH001",
                        "score": 0.85,
                        "completion_rate": 95,
                        "time_spent": 45,
                        "difficulty_level": 3,
                        "success_rate": 0.82,
                        "sub_topic": "Algèbre",
                        "exercise_type": "Problèmes"
                    },
                    {
                        "student_id": "STUDENT001",
                        "timestamp": datetime.now().isoformat(),
                        "subject": "Physique",
                        "content_type": "practical",
                        "content_id": "PHY001",
                        "score": 0.65,
                        "completion_rate": 80,
                        "time_spent": 60,
                        "difficulty_level": 4,
                        "success_rate": 0.60,
                        "sub_topic": "Mécanique",
                        "exercise_type": "Expériences"
                    },
                    {
                        "student_id": "STUDENT001",
                        "timestamp": datetime.now().isoformat(),
                        "subject": "Informatique",
                        "content_type": "practical",
                        "content_id": "INFO001",
                        "score": 0.92,
                        "completion_rate": 100,
                        "time_spent": 30,
                        "difficulty_level": 2,
                        "success_rate": 0.95,
                        "sub_topic": "Programmation",
                        "exercise_type": "Coding"
                    }
                ]
            }
            with open(self.learning_data_file, "w", encoding='utf-8') as f:
                json.dump(test_data, f, indent=4, ensure_ascii=False)

    def provide_feedback(self, student_id, content_id=None):
        """Fournit un feedback personnalisé et adaptatif"""
        try:
            # Charger les données d'apprentissage
            with open(self.learning_data_file, "r", encoding='utf-8') as f:
                learning_data = json.load(f)

            # Initialiser les données pour un nouvel étudiant si nécessaire
            student_records = [r for r in learning_data["learning_records"] if r["student_id"] == student_id]
            if not student_records:
                # Créer des données initiales pour le nouvel étudiant
                initial_record = {
                    "student_id": student_id,
                    "timestamp": datetime.now().isoformat(),
                    "subject": "Général",
                    "content_type": "initial",
                    "score": 0.0,
                    "completion_rate": 0,
                    "time_spent": 0,
                    "success_rate": 0.0
                }
                learning_data["learning_records"].append(initial_record)
                with open(self.learning_data_file, "w", encoding='utf-8') as f:
                    json.dump(learning_data, f, indent=4, ensure_ascii=False)
                student_records = [initial_record]

            # Analyser les données
            df = pd.DataFrame(student_records)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Générer le feedback
            feedback = {
                "timestamp": datetime.now().isoformat(),
                "student_id": student_id,
                "content_id": content_id,
                "performance_summary": self._generate_performance_summary(df),
                "learning_plan": self._generate_learning_plan(df),
                "personalized_advice": self._generate_personalized_advice(df),
                "adaptive_recommendations": self._generate_adaptive_recommendations(df),
                "progress_tracking": self._track_detailed_progress(df),
                "skill_assessment": self._assess_skills(df),
                "engagement_metrics": self._analyze_engagement(df),
                "learning_path": self._suggest_learning_path(df),
                "mastery_tracking": self._track_mastery_levels(df)
            }

            return feedback

        except Exception as e:
            print(f"Erreur dans provide_feedback: {str(e)}")
            return {"status": "error", "message": "Erreur lors de la génération du feedback"}

    def _generate_performance_summary(self, df):
        """Génère un résumé détaillé des performances"""
        try:
            if df.empty:
                return self._get_default_performance_summary()

            recent_df = df.sort_values('timestamp').tail(5)
            return {
                "current_performance": {
                    "score": recent_df["score"].mean() if "score" in recent_df else 0.0,
                    "completion_rate": recent_df["completion_rate"].mean() if "completion_rate" in recent_df else 0,
                    "time_spent": recent_df["time_spent"].sum() if "time_spent" in recent_df else 0
                },
                "progress_rate": self._calculate_progress_rate(df),
                "learning_velocity": self._calculate_learning_velocity(df),
                "skill_gaps": self._identify_skill_gaps(df),
                "improvement_areas": self._identify_improvement_areas(df)
            }
        except Exception as e:
            print(f"Erreur dans _generate_performance_summary: {str(e)}")
            return self._get_default_performance_summary()

    def _get_default_performance_summary(self):
        """Retourne un résumé de performance par défaut pour les nouveaux étudiants"""
        return {
            "current_performance": {
                "score": 0.0,
                "completion_rate": 0,
                "time_spent": 0
            },
            "progress_rate": "initial",
            "learning_velocity": "à déterminer",
            "skill_gaps": [],
            "improvement_areas": ["Commencez par établir une base de connaissances"]
        }

    def _generate_learning_plan(self, df):
        """Génère un planning d'apprentissage personnalisé et adaptatif"""
        try:
            # Analyser les meilleures périodes d'apprentissage
            if not df.empty and 'timestamp' in df.columns:
                df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
                best_hours = df.groupby('hour')['score'].mean().nlargest(3).index.tolist()
            else:
                best_hours = [9, 14, 18]  # Heures par défaut

            return {
                "sessions_recommandées": {
                    "matin": [f"{h:02d}h00" for h in best_hours if h < 12],
                    "après-midi": [f"{h:02d}h00" for h in best_hours if 12 <= h < 18],
                    "soir": [f"{h:02d}h00" for h in best_hours if h >= 18]
                },
                "durée_optimale": self._calculate_optimal_duration(df),
                "fréquence_recommandée": self._calculate_optimal_frequency(df),
                "planning_hebdomadaire": self._create_weekly_schedule(df),
                "pauses_conseillées": self._calculate_optimal_breaks(df),
                "adaptations_dynamiques": self._generate_dynamic_adaptations(df)
            }
        except Exception as e:
            print(f"Erreur dans _generate_learning_plan: {str(e)}")
            return self._get_default_learning_plan()

    def _get_default_learning_plan(self):
        """Retourne un plan d'apprentissage par défaut pour les nouveaux étudiants"""
        return {
            "sessions_recommandées": {
                "matin": ["09h00", "11h00"],
                "après-midi": ["14h00", "16h00"],
                "soir": ["18h00", "20h00"]
            },
            "durée_optimale": "30 à 45 minutes",
            "fréquence_recommandée": "3 à 4 sessions par semaine",
            "planning_hebdomadaire": self._create_default_weekly_schedule(),
            "pauses_conseillées": {
                "courte_pause": "5-10 minutes toutes les 25 minutes",
                "longue_pause": "20-30 minutes toutes les 2 heures"
            }
        }

    def _create_default_weekly_schedule(self):
        """Crée un planning hebdomadaire par défaut pour les nouveaux étudiants"""
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        schedule = {}
        for i, day in enumerate(days):
            schedule[day] = {
                "priorité": "haute" if i < 2 else "moyenne",
                "sessions": ["09h00", "14h00"] if i < 3 else ["14h00", "18h00"],
                "focus": "Introduction et concepts de base" if i == 0 else "Pratique et révision"
            }
        return schedule

    def _calculate_progress_rate(self, df):
        """Calcule le taux de progression de l'étudiant"""
        try:
            if len(df) < 2:
                return "initial"
            
            recent_scores = df.sort_values('timestamp').tail(5)['score']
            progress_rate = (recent_scores.iloc[-1] - recent_scores.iloc[0]) / len(recent_scores)
            
            if progress_rate > 0.1:
                return "rapide"
            elif progress_rate > 0:
                return "régulier"
            else:
                return "nécessite attention"
        except Exception:
            return "à déterminer"

    def _calculate_learning_velocity(self, df):
        """Calcule la vitesse d'apprentissage"""
        try:
            if len(df) < 2:
                return "à déterminer"
            
            df = df.sort_values('timestamp')
            time_diff = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
            score_diff = df['score'].diff().mean()
            
            velocity = score_diff / time_diff if time_diff > 0 else 0
            
            if velocity > 0.05:
                return "rapide"
            elif velocity > 0:
                return "modérée"
            else:
                return "lente"
        except Exception:
            return "à déterminer"

    def _generate_dynamic_adaptations(self, df):
        """Génère des adaptations dynamiques basées sur les performances"""
        try:
            if df.empty:
                return self._get_default_adaptations()

            adaptations = {
                "ajustements_difficulté": self._calculate_difficulty_adjustments(df),
                "recommandations_format": self._suggest_format_adaptations(df),
                "support_supplémentaire": self._identify_support_needs(df)
            }
            return adaptations
        except Exception:
            return self._get_default_adaptations()

    def _get_default_adaptations(self):
        """Retourne des adaptations par défaut pour les nouveaux étudiants"""
        return {
            "ajustements_difficulté": "commencer par le niveau débutant",
            "recommandations_format": "utiliser une variété de formats",
            "support_supplémentaire": "guidance pas à pas disponible"
        }

    def _generate_personalized_advice(self, df):
        """Génère des conseils personnalisés basés sur l'analyse des données"""
        advice = {
            "conseils_généraux": self._generate_general_advice(df),
            "conseils_méthodologiques": self._generate_methodology_advice(df),
            "conseils_motivation": self._generate_motivation_advice(df),
            "techniques_apprentissage": self._suggest_learning_techniques(df),
            "gestion_temps": self._generate_time_management_advice(df)
        }
        return advice

    def _calculate_optimal_frequency(self, df):
        """Calcule la fréquence optimale des sessions d'apprentissage"""
        # Analyser l'intervalle entre les sessions réussies
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        successful_sessions = df[df['score'] > 0.7]
        
        if len(successful_sessions) < 2:
            return "3 à 4 sessions par semaine"
            
        intervals = successful_sessions['timestamp'].diff()
        optimal_interval = intervals.median()
        
        if optimal_interval.days < 1:
            return "Sessions quotidiennes"
        elif optimal_interval.days < 2:
            return "Sessions tous les deux jours"
        else:
            return f"{min(optimal_interval.days, 4)} sessions par semaine"

    def _create_weekly_schedule(self, df):
        """Crée un planning hebdomadaire personnalisé"""
        # Analyser les jours les plus productifs
        df['day'] = pd.to_datetime(df['timestamp']).dt.day_name()
        best_days = df.groupby('day')['score'].mean().nlargest(4)
        
        schedule = {}
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        for day in days:
            if day in best_days.index:
                schedule[day] = {
                    "sessions": [f"{hour}h00" for hour in df[df["day"] == day].groupby('hour')['score'].mean().nlargest(2).index.tolist()],
                    "priorité": "haute" if day in best_days.nlargest(2).index else "moyenne",
                    "focus": self._suggest_daily_focus(df, day)
                }
            else:
                schedule[day] = {
                    "sessions": [],
                    "priorité": "repos",
                    "focus": "révisions légères ou repos"
                }
                
        return schedule

    def _generate_general_advice(self, df):
        """Génère des conseils généraux basés sur l'analyse des données"""
        advice = []
        
        # Analyser le pattern de progression
        progress_pattern = df['score'].diff().mean()
        if progress_pattern < 0:
            advice.append("Prenez le temps de consolider vos acquis avant d'avancer")
        elif progress_pattern > 0.1:
            advice.append("Votre progression est excellente, maintenez ce rythme")
            
        # Analyser la régularité
        time_between_sessions = pd.to_datetime(df['timestamp']).diff().mean()
        if time_between_sessions.days > 3:
            advice.append("Une pratique plus régulière améliorerait votre apprentissage")
            
        return advice

    def _generate_methodology_advice(self, df):
        """Génère des conseils méthodologiques personnalisés"""
        methodology = []
        
        # Analyser l'efficacité selon le type de contenu
        content_effectiveness = df.groupby('content_type')['score'].mean()
        best_content_type = content_effectiveness.idxmax()
        
        methodology.append(f"Vous apprenez mieux avec le format {best_content_type}")
        
        # Suggestions basées sur la durée des sessions
        avg_duration = df['time_spent'].mean()
        if avg_duration > 90:
            methodology.append("Essayez de diviser vos sessions en périodes plus courtes")
        
        return methodology

    def _generate_motivation_advice(self, df):
        """Génère des conseils pour maintenir la motivation"""
        motivation = []
        
        # Analyser les progrès récents
        recent_progress = df.tail(5)['score'].mean() - df.head(5)['score'].mean()
        if recent_progress > 0:
            motivation.append("Vos progrès récents sont encourageants, continuez ainsi !")
        else:
            motivation.append("N'oubliez pas que les difficultés font partie du processus d'apprentissage")
            
        return motivation

    def _suggest_learning_techniques(self, df):
        """Suggère des techniques d'apprentissage adaptées"""
        techniques = []
        
        # Analyser le style d'apprentissage dominant
        if 'content_type' in df.columns:
            preferred_style = df.groupby('content_type')['score'].mean().idxmax()
            
            techniques_map = {
                "visual": [
                    "Utilisez des cartes mentales",
                    "Créez des schémas explicatifs",
                    "Regardez des vidéos éducatives"
                ],
                "audio": [
                    "Enregistrez vos cours",
                    "Participez à des discussions de groupe",
                    "Expliquez les concepts à voix haute"
                ],
                "practical": [
                    "Faites des exercices pratiques",
                    "Créez des projets personnels",
                    "Appliquez les concepts à des cas réels"
                ]
            }
            
            techniques.extend(techniques_map.get(preferred_style, []))
            
        return techniques

    def _generate_time_management_advice(self, df):
        """Génère des conseils pour la gestion du temps"""
        time_advice = []
        
        # Analyser les sessions les plus productives
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        best_hours = df.groupby('hour')['score'].mean().nlargest(3)
        
        time_advice.append(f"Vos meilleures heures d'apprentissage sont : {', '.join([f'{h}h' for h in best_hours.index])}")
        
        # Conseils sur la durée des sessions
        optimal_duration = df.groupby(pd.qcut(df['time_spent'], 4))['score'].mean().idxmax()
        time_advice.append(f"Durée optimale de session : {int(optimal_duration.left)} à {int(optimal_duration.right)} minutes")
        
        return time_advice

    def _suggest_daily_focus(self, df, day):
        """Suggère un focus d'apprentissage pour chaque jour"""
        # Analyser les performances par sujet pour ce jour
        day_df = df[pd.to_datetime(df['timestamp']).dt.day_name() == day]
        if len(day_df) > 0:
            best_subject = day_df.groupby('subject')['score'].mean().idxmax()
            return f"Focus sur {best_subject}"
        return "Révisions générales" 