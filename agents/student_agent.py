import json
from pathlib import Path
import pandas as pd
from datetime import datetime

class StudentAgent:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.students_file = self.data_dir / "students.json"
        self.learning_data_file = self.data_dir / "learning_data.json"
        self.feedback_file = self.data_dir / "feedback.json"
        self.init_data_files()

    def init_data_files(self):
        """Initialise les fichiers de données s'ils n'existent pas"""
        self.data_dir.mkdir(exist_ok=True)
        
        if not self.students_file.exists():
            default_students = {
                "students": [
                    {
                        "id": "STUDENT001",
                        "name": "Jean Dupont",
                        "level": "Licence 1",
                        "preferred_learning_style": "visual",
                        "current_preferences": {
                            "subject": "Mathématiques",
                            "module": "Algèbre",
                            "difficulty": 3,
                            "duration": 30,
                            "content_types": ["Vidéos", "Exercices interactifs"],
                            "learning_goal": "Comprendre les bases de l'algèbre"
                        },
                        "learning_preferences_history": [],
                        "enrolled_subjects": [
                            "Mathématiques",
                            "Physique",
                            "Informatique",
                            "Chimie"
                        ]
                    }
                ]
            }
            with open(self.students_file, "w", encoding='utf-8') as f:
                json.dump(default_students, f, indent=4, ensure_ascii=False)
        
        if not self.learning_data_file.exists():
            default_learning_data = {
                "learning_records": [
                    {
                        "student_id": "STUDENT001",
                        "timestamp": datetime.now().isoformat(),
                        "subject": "Mathématiques",
                        "content_type": "visual",
                        "score": 0.85,
                        "completion_rate": 95,
                        "time_spent": 45,
                        "success_rate": 0.82
                    },
                    {
                        "student_id": "STUDENT001",
                        "timestamp": datetime.now().isoformat(),
                        "subject": "Physique",
                        "content_type": "practical",
                        "score": 0.65,
                        "completion_rate": 80,
                        "time_spent": 60,
                        "success_rate": 0.60
                    },
                    {
                        "student_id": "STUDENT001",
                        "timestamp": datetime.now().isoformat(),
                        "subject": "Informatique",
                        "content_type": "practical",
                        "score": 0.92,
                        "completion_rate": 100,
                        "time_spent": 30,
                        "success_rate": 0.95
                    }
                ]
            }
            with open(self.learning_data_file, "w", encoding='utf-8') as f:
                json.dump(default_learning_data, f, indent=4, ensure_ascii=False)

    def analyze_performance(self, student_id):
        """Analyse les performances d'un étudiant de manière dynamique"""
        with open(self.learning_data_file, "r", encoding='utf-8') as f:
            data = json.load(f)
        
        student_records = [r for r in data["learning_records"] if r["student_id"] == student_id]
        if not student_records:
            return {
                "status": "error",
                "message": "Aucune donnée trouvée pour cet étudiant"
            }
        
        # Analyse des performances avec tendances temporelles
        df = pd.DataFrame(student_records)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Analyser les tendances récentes
        recent_df = df.tail(10)  # 10 dernières activités
        
        # Calculer les métriques globales
        average_score = recent_df["score"].mean()
        completion_rate = recent_df["completion_rate"].mean()
        time_spent = recent_df["time_spent"].sum()
        
        analysis = {
            # Métriques principales pour le dashboard
            "average_score": average_score,
            "completion_rate": completion_rate,
            "time_spent": time_spent,
            
            # Analyse détaillée
            "current_performance": {
                "average_score": average_score,
                "completion_rate": completion_rate,
                "time_spent": time_spent,
            },
            "trends": {
                "score_trend": self._calculate_trend(recent_df["score"]),
                "completion_trend": self._calculate_trend(recent_df["completion_rate"]),
                "engagement_trend": self._calculate_trend(recent_df["time_spent"])
            },
            "learning_patterns": self._analyze_learning_patterns(df),
            "strengths": self._identify_strengths(df),
            "weaknesses": self._identify_weaknesses(df),
            "recommended_focus_areas": self._identify_focus_areas(df)
        }
        
        return analysis

    def _calculate_trend(self, series):
        """Calcule la tendance d'une série de données"""
        if len(series) < 2:
            return "stable"
        
        slope = (series.iloc[-1] - series.iloc[0]) / len(series)
        if slope > 0.05:
            return "amélioration"
        elif slope < -0.05:
            return "détérioration"
        return "stable"

    def _analyze_learning_patterns(self, df):
        """Analyse les patterns d'apprentissage de l'étudiant"""
        patterns = {
            "preferred_time_slots": self._get_preferred_time_slots(df),
            "optimal_session_duration": self._get_optimal_session_duration(df),
            "best_performing_subjects": self._get_best_performing_subjects(df),
            "learning_style_effectiveness": self._analyze_learning_style_effectiveness(df)
        }
        return patterns

    def _get_preferred_time_slots(self, df):
        """Identifie les créneaux horaires préférés de l'étudiant"""
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        performance_by_hour = df.groupby('hour')['score'].mean()
        return performance_by_hour.nlargest(3).index.tolist()

    def _get_optimal_session_duration(self, df):
        """Détermine la durée optimale des sessions d'apprentissage"""
        try:
            if len(df) < 4:  # Si pas assez de données
                return {
                    "min": 30,
                    "max": 45
                }
            
            # Créer des bins de durée plus robustes
            bins = [0, 30, 60, 90, float('inf')]
            labels = ['0-30', '31-60', '61-90', '90+']
            df['duration_bin'] = pd.cut(df['time_spent'], bins=bins, labels=labels)
            
            performance_by_duration = df.groupby('duration_bin')['score'].mean()
            best_duration = performance_by_duration.idxmax()
            
            # Extraire les limites du meilleur intervalle
            if best_duration == '0-30':
                return {"min": 0, "max": 30}
            elif best_duration == '31-60':
                return {"min": 31, "max": 60}
            elif best_duration == '61-90':
                return {"min": 61, "max": 90}
            else:
                return {"min": 90, "max": 120}
            
        except Exception as e:
            print(f"Erreur dans _get_optimal_session_duration: {str(e)}")
            return {"min": 30, "max": 45}  # Valeurs par défaut

    def _get_best_performing_subjects(self, df):
        """Identifie les matières où l'étudiant performe le mieux"""
        return df.groupby('subject')['score'].mean().nlargest(3).to_dict()

    def _analyze_learning_style_effectiveness(self, df):
        """Analyse l'efficacité de chaque style d'apprentissage"""
        style_effectiveness = df.groupby('content_type').agg({
            'score': 'mean',
            'completion_rate': 'mean',
            'time_spent': 'mean'
        }).to_dict('index')
        
        return {style: {
            'efficacité': (stats['score'] * 0.4 + 
                         stats['completion_rate'] * 0.4 + 
                         (1 / (stats['time_spent'] + 1)) * 0.2)
        } for style, stats in style_effectiveness.items()}

    def get_learning_style(self, student_id, answers=None):
        """Détermine le style d'apprentissage d'un étudiant"""
        if answers:
            # Si des réponses sont fournies, analyser le questionnaire
            learning_style = self._analyze_questionnaire_responses(answers)
            self.save_learning_style(student_id, learning_style)
            return learning_style
            
        # Sinon, vérifier si le style est déjà enregistré
        with open(self.students_file, "r", encoding='utf-8') as f:
            students_data = json.load(f)
            
        student = next((s for s in students_data["students"] if s["id"] == student_id), None)
        if student and "learning_style_determined" in student and student["learning_style_determined"]:
            # Vérifier si une mise à jour est nécessaire (par exemple, tous les 30 jours)
            if "learning_style_updated" in student:
                last_update = datetime.fromisoformat(student["learning_style_updated"])
                if (datetime.now() - last_update).days > 30:
                    return None  # Demander une nouvelle évaluation
            return student["preferred_learning_style"]
            
        return None

    def get_learning_style_questionnaire(self):
        """Retourne le questionnaire de style d'apprentissage"""
        return {
            "questions": [
                {
                    "id": 1,
                    "text": "Comment préférez-vous apprendre un nouveau concept ?",
                    "choices": [
                        {"id": "visual", "text": "En regardant des diagrammes et des vidéos"},
                        {"id": "audio", "text": "En écoutant des explications"},
                        {"id": "text", "text": "En lisant des documents"},
                        {"id": "practical", "text": "En pratiquant directement"}
                    ]
                },
                {
                    "id": 2,
                    "text": "Quelle méthode vous aide le mieux à mémoriser ?",
                    "choices": [
                        {"id": "visual", "text": "Les schémas et les images"},
                        {"id": "audio", "text": "La répétition à voix haute"},
                        {"id": "text", "text": "La prise de notes"},
                        {"id": "practical", "text": "La mise en pratique"}
                    ]
                },
                {
                    "id": 3,
                    "text": "Comment préférez-vous réviser ?",
                    "choices": [
                        {"id": "visual", "text": "En créant des cartes mentales"},
                        {"id": "audio", "text": "En discutant avec d'autres"},
                        {"id": "text", "text": "En relisant vos notes"},
                        {"id": "practical", "text": "En faisant des exercices"}
                    ]
                },
                {
                    "id": 4,
                    "text": "Quelle activité vous aide le plus à comprendre ?",
                    "choices": [
                        {"id": "visual", "text": "Regarder une démonstration"},
                        {"id": "audio", "text": "Écouter une explication"},
                        {"id": "text", "text": "Lire une documentation"},
                        {"id": "practical", "text": "Essayer par vous-même"}
                    ]
                },
                {
                    "id": 5,
                    "text": "Comment préférez-vous recevoir des instructions ?",
                    "choices": [
                        {"id": "visual", "text": "Avec des illustrations"},
                        {"id": "audio", "text": "Oralement"},
                        {"id": "text", "text": "Par écrit"},
                        {"id": "practical", "text": "Par l'exemple"}
                    ]
                }
            ]
        }

    def _analyze_questionnaire_responses(self, answers):
        """Analyse les réponses au questionnaire pour déterminer le style d'apprentissage"""
        style_counts = {
            "visual": 0,
            "audio": 0,
            "text": 0,
            "practical": 0
        }
        
        # Poids des questions (plus le poids est élevé, plus la question est importante)
        question_weights = {
            1: 1.5,  # Question sur la préférence générale d'apprentissage
            2: 1.2,  # Question sur la mémorisation
            3: 1.0,  # Question sur la révision
            4: 1.3,  # Question sur la compréhension
            5: 1.0   # Question sur les instructions
        }
        
        # Analyser chaque réponse avec son poids
        for i, answer in enumerate(answers, 1):
            weight = question_weights[i]
            style_counts[answer] += weight
        
        # Calculer les pourcentages pour chaque style
        total_points = sum(style_counts.values())
        style_percentages = {
            style: (count / total_points) * 100 
            for style, count in style_counts.items()
        }
        
        # Déterminer le style dominant et les styles secondaires
        dominant_style = max(style_counts.items(), key=lambda x: x[1])[0]
        
        # Sauvegarder les détails de l'analyse
        self._save_learning_style_details(style_percentages)
        
        return dominant_style

    def _save_learning_style_details(self, style_percentages):
        """Sauvegarde les détails de l'analyse du style d'apprentissage"""
        try:
            learning_style_details = {
                "timestamp": datetime.now().isoformat(),
                "style_percentages": style_percentages,
                "primary_style": max(style_percentages.items(), key=lambda x: x[1])[0],
                "secondary_styles": sorted(
                    [(style, pct) for style, pct in style_percentages.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[1:]
            }
            
            # Créer le fichier s'il n'existe pas
            learning_styles_file = self.data_dir / "learning_styles.json"
            if not learning_styles_file.exists():
                with open(learning_styles_file, "w", encoding='utf-8') as f:
                    json.dump({"learning_style_analyses": []}, f, indent=4, ensure_ascii=False)
            
            # Ajouter la nouvelle analyse
            with open(learning_styles_file, "r+", encoding='utf-8') as f:
                data = json.load(f)
                data["learning_style_analyses"].append(learning_style_details)
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.truncate()
            return True
            
        except Exception as e:
            print(f"Erreur dans _save_learning_style_details: {str(e)}")
            return False

    def save_learning_style(self, student_id, learning_style):
        """Enregistre le style d'apprentissage déterminé"""
        try:
            # Vérifier si le fichier existe
            if not self.students_file.exists():
                default_data = {"students": []}
                with open(self.students_file, "w", encoding='utf-8') as f:
                    json.dump(default_data, f, indent=4, ensure_ascii=False)

            # Lire les données existantes
            with open(self.students_file, "r", encoding='utf-8') as f:
                data = json.load(f)

            # Trouver ou créer l'étudiant
            student_found = False
            for student in data["students"]:
                if student["id"] == student_id:
                    student["preferred_learning_style"] = learning_style
                    student["learning_style_determined"] = True
                    student["learning_style_updated"] = datetime.now().isoformat()
                    
                    # Charger les détails du style d'apprentissage
                    learning_styles_file = self.data_dir / "learning_styles.json"
                    if learning_styles_file.exists():
                        try:
                            with open(learning_styles_file, "r", encoding='utf-8') as lsf:
                                style_data = json.load(lsf)
                                if "learning_style_analyses" in style_data and style_data["learning_style_analyses"]:
                                    latest_analysis = style_data["learning_style_analyses"][-1]
                                    student["learning_style_details"] = latest_analysis
                        except Exception as e:
                            print(f"Erreur lors du chargement des détails du style: {str(e)}")
                    student_found = True
                    break

            # Si l'étudiant n'existe pas, le créer
            if not student_found:
                new_student = {
                    "id": student_id,
                    "preferred_learning_style": learning_style,
                    "learning_style_determined": True,
                    "learning_style_updated": datetime.now().isoformat(),
                    "enrolled_subjects": []
                }
                data["students"].append(new_student)

            # Sauvegarder les modifications
            with open(self.students_file, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"Erreur lors de la sauvegarde du style d'apprentissage: {str(e)}")
            return False

        return True

    def track_progress(self, student_id, time_period="week"):
        """Suit les progrès d'un étudiant sur une période donnée"""
        with open(self.learning_data_file, "r", encoding='utf-8') as f:
            data = json.load(f)
        
        student_records = [r for r in data["learning_records"] if r["student_id"] == student_id]
        if not student_records:
            return []
        
        df = pd.DataFrame(student_records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Grouper par période
        if time_period == "week":
            grouped = df.groupby(df["timestamp"].dt.isocalendar().week)
        elif time_period == "month":
            grouped = df.groupby(df["timestamp"].dt.month)
        else:
            grouped = df.groupby(df["timestamp"].dt.date)
        
        progress = grouped.agg({
            "score": "mean",
            "completion_rate": "mean",
            "time_spent": "sum"
        }).reset_index()
        
        return progress.to_dict("records")

    def _identify_strengths(self, df):
        """Identifie les points forts de l'étudiant"""
        strengths = []
        
        # Analyser les performances par sujet
        subject_performance = df.groupby("subject")["score"].mean()
        good_subjects = subject_performance[subject_performance >= 0.75].index.tolist()
        
        # Analyser les types de contenu préférés
        content_performance = df.groupby("content_type")["success_rate"].mean()
        preferred_content = content_performance[content_performance >= 0.75].index.tolist()
        
        return {
            "strong_subjects": good_subjects,
            "preferred_content_types": preferred_content
        }

    def _identify_weaknesses(self, df):
        """Identifie les points faibles de l'étudiant"""
        weaknesses = []
        
        # Analyser les performances par sujet
        subject_performance = df.groupby("subject")["score"].mean()
        weak_subjects = subject_performance[subject_performance < 0.6].index.tolist()
        
        # Analyser les types de contenu problématiques
        content_performance = df.groupby("content_type")["success_rate"].mean()
        difficult_content = content_performance[content_performance < 0.6].index.tolist()
        
        return {
            "weak_subjects": weak_subjects,
            "difficult_content_types": difficult_content
        }

    def _identify_focus_areas(self, df):
        """Identifie les domaines nécessitant une attention particulière"""
        focus_areas = []
        
        # Analyse par sujet
        subject_performance = df.groupby("subject")["score"].mean()
        weak_subjects = subject_performance[subject_performance < 0.7].index.tolist()
        
        # Analyse par type de contenu
        content_type_performance = df.groupby("content_type")["success_rate"].mean()
        weak_content_types = content_type_performance[content_type_performance < 0.7].index.tolist()
        
        # Analyse des sous-thèmes si disponibles
        if "sub_topic" in df.columns:
            subtopic_performance = df.groupby("sub_topic")["score"].mean()
            weak_subtopics = subtopic_performance[subtopic_performance < 0.7].index.tolist()
        else:
            weak_subtopics = []
            
        # Analyse des types d'exercices si disponibles
        if "exercise_type" in df.columns:
            exercise_performance = df.groupby("exercise_type")["score"].mean()
            weak_exercises = exercise_performance[exercise_performance < 0.7].index.tolist()
        else:
            weak_exercises = []
            
        return {
            "subjects": weak_subjects,
            "content_types": weak_content_types,
            "subtopics": weak_subtopics,
            "exercise_types": weak_exercises,
            "priority_level": self._calculate_priority_level(df)
        }

    def _calculate_priority_level(self, df):
        """Calcule le niveau de priorité pour chaque domaine identifié"""
        recent_performance = df.sort_values('timestamp').tail(5)["score"].mean()
        if recent_performance < 0.6:
            return "haute"
        elif recent_performance < 0.75:
            return "moyenne"
        else:
            return "basse"

    def get_current_preferences(self, student_id):
        """Récupère les préférences actuelles de l'étudiant"""
        try:
            with open(self.students_file, "r", encoding='utf-8') as f:
                students_data = json.load(f)

            student = next((s for s in students_data["students"] if s["id"] == student_id), None)
            if student:
                # Si l'étudiant existe mais n'a pas encore de préférences, créer des préférences par défaut
                if "current_preferences" not in student:
                    default_preferences = {
                        "subject": "Mathématiques",
                        "module": "Algèbre",
                        "difficulty": 3,
                        "duration": 30,
                        "content_types": ["Vidéos", "Exercices interactifs"],
                        "learning_goal": ""
                    }
                    student["current_preferences"] = default_preferences
                    # Sauvegarder les préférences par défaut
                    with open(self.students_file, "w", encoding='utf-8') as f:
                        json.dump(students_data, f, indent=4, ensure_ascii=False)
                return student["current_preferences"]
            return None

        except Exception as e:
            print(f"Erreur lors de la récupération des préférences: {str(e)}")
            return None

    def update_learning_preferences(self, student_id, new_preferences):
        """Met à jour les préférences d'apprentissage de l'étudiant"""
        try:
            with open(self.students_file, "r", encoding='utf-8') as f:
                students_data = json.load(f)

            # Trouver l'étudiant
            student = next((s for s in students_data["students"] if s["id"] == student_id), None)
            if not student:
                # Créer un nouvel étudiant si non existant
                student = {
                    "id": student_id,
                    "preferred_learning_style": "visual",  # Style par défaut
                    "learning_style_determined": False,
                    "learning_preferences_history": [],
                    "enrolled_subjects": []
                }
                students_data["students"].append(student)

            # Sauvegarder l'historique des préférences
            if "learning_preferences_history" not in student:
                student["learning_preferences_history"] = []
            
            # Ajouter les nouvelles préférences avec timestamp
            preference_entry = {
                "timestamp": datetime.now().isoformat(),
                "preferences": new_preferences
            }
            student["learning_preferences_history"].append(preference_entry)

            # Mettre à jour les préférences actuelles
            student["current_preferences"] = new_preferences

            # Mettre à jour le style d'apprentissage basé sur les types de contenu préférés
            content_type_mapping = {
                "Vidéos": "visual",
                "Documents PDF": "text",
                "Audio": "audio",
                "Exercices interactifs": "practical",
                "Quiz": "practical"
            }

            # Calculer les poids pour chaque style
            style_weights = {
                "visual": 0,
                "text": 0,
                "audio": 0,
                "practical": 0
            }

            # Donner plus de poids aux préférences récentes
            for content_type in new_preferences.get("content_types", []):
                if content_type in content_type_mapping:
                    style_weights[content_type_mapping[content_type]] += 2

            # Normaliser les poids
            total_weight = sum(style_weights.values()) or 1
            style_percentages = {
                style: (weight / total_weight) * 100 
                for style, weight in style_weights.items()
            }

            # Déterminer le style dominant et les styles secondaires
            sorted_styles = sorted(
                style_percentages.items(),
                key=lambda x: x[1],
                reverse=True
            )

            # Mettre à jour les détails du style d'apprentissage
            student["learning_style_details"] = {
                "timestamp": datetime.now().isoformat(),
                "style_percentages": style_percentages,
                "primary_style": sorted_styles[0][0],
                "secondary_styles": sorted_styles[1:]
            }
            student["preferred_learning_style"] = sorted_styles[0][0]
            student["learning_style_updated"] = datetime.now().isoformat()

            # Sauvegarder les modifications
            with open(self.students_file, "w", encoding='utf-8') as f:
                json.dump(students_data, f, indent=4, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Erreur lors de la mise à jour des préférences: {str(e)}")
            return False 