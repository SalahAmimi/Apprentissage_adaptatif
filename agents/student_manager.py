def analyze_performance(self, student_id):
    """Analyse les performances de l'étudiant"""
    try:
        with open(self.students_file, "r", encoding='utf-8') as f:
            students_data = json.load(f)

        # Trouver l'étudiant
        student = next((s for s in students_data["students"] if s["id"] == student_id), None)
        if not student:
            # Créer un nouveau profil étudiant
            return self._create_initial_performance_data()

        # Charger l'historique d'apprentissage
        learning_data = self._load_learning_data(student_id)
        if not learning_data or not learning_data["records"]:
            return self._create_initial_performance_data()

        # Créer un DataFrame pour l'analyse
        df = pd.DataFrame(learning_data["records"])
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Calculer les métriques de base
        performance = {
            "average_score": df["score"].mean() if "score" in df else 0.0,
            "completion_rate": df["completion_rate"].mean() if "completion_rate" in df else 0.0,
            "time_spent": df["time_spent"].sum() if "time_spent" in df else 0,
            
            # Analyser les tendances
            "trends": self._analyze_trends(df),
            
            # Identifier les points forts et faibles
            "strengths": self._identify_strengths(df),
            "weaknesses": self._identify_weaknesses(df),
            
            # Analyser les patterns d'apprentissage
            "learning_patterns": self._analyze_learning_patterns(df),
            
            # Évaluer la progression
            "progression": self._evaluate_progression(df),
            
            # Analyser l'engagement
            "engagement": self._analyze_engagement(df)
        }

        return performance

    except Exception as e:
        print(f"Erreur dans analyze_performance: {str(e)}")
        return self._create_initial_performance_data()

def _create_initial_performance_data(self):
    """Crée des données de performance initiales pour un nouvel étudiant"""
    return {
        "average_score": 0.0,
        "completion_rate": 0.0,
        "time_spent": 0,
        "trends": {
            "score_trend": "initial",
            "completion_trend": "initial",
            "engagement_trend": "initial"
        },
        "strengths": {
            "strong_subjects": [],
            "mastered_skills": [],
            "learning_style_match": None
        },
        "weaknesses": {
            "weak_subjects": [],
            "skills_to_improve": [],
            "recommended_focus": []
        },
        "learning_patterns": {
            "preferred_time_slots": [],
            "optimal_session_duration": {
                "min": 30,
                "max": 45
            },
            "best_performing_subjects": {}
        },
        "progression": {
            "current_level": "débutant",
            "next_milestone": "compléter le premier module",
            "progress_rate": "initial"
        },
        "engagement": {
            "session_frequency": "à déterminer",
            "average_session_duration": 0,
            "consistency_score": 0.0
        }
    }

def _analyze_trends(self, df):
    """Analyse les tendances des performances"""
    try:
        if len(df) < 2:
            return {
                "score_trend": "initial",
                "completion_trend": "initial",
                "engagement_trend": "initial"
            }

        recent_df = df.sort_values('timestamp').tail(5)
        
        # Calculer les tendances
        score_trend = self._calculate_trend(recent_df, 'score')
        completion_trend = self._calculate_trend(recent_df, 'completion_rate')
        engagement_trend = self._analyze_engagement_trend(recent_df)

        return {
            "score_trend": score_trend,
            "completion_trend": completion_trend,
            "engagement_trend": engagement_trend
        }

    except Exception:
        return {
            "score_trend": "initial",
            "completion_trend": "initial",
            "engagement_trend": "initial"
        }

def _calculate_trend(self, df, column):
    """Calcule la tendance d'une métrique"""
    if column not in df.columns or len(df) < 2:
        return "initial"

    values = df[column].values
    if len(values) < 2:
        return "initial"

    trend = values[-1] - values[0]
    if trend > 0.1:
        return "↗️ en hausse"
    elif trend < -0.1:
        return "↘️ en baisse"
    else:
        return "→ stable"

def _analyze_engagement_trend(self, df):
    """Analyse la tendance de l'engagement"""
    if 'time_spent' not in df.columns or len(df) < 2:
        return "initial"

    recent_engagement = df['time_spent'].mean()
    if recent_engagement > df['time_spent'].median() * 1.2:
        return "↗️ plus engagé"
    elif recent_engagement < df['time_spent'].median() * 0.8:
        return "↘️ moins engagé"
    else:
        return "→ engagement stable"

def _identify_strengths(self, df):
    """Identifie les points forts de l'étudiant"""
    if df.empty:
        return {
            "strong_subjects": [],
            "mastered_skills": [],
            "learning_style_match": None
        }

    try:
        # Identifier les matières fortes
        subject_performance = df.groupby("subject")["score"].mean()
        strong_subjects = subject_performance[subject_performance >= 0.7].index.tolist()

        # Identifier les compétences maîtrisées
        if "skills" in df.columns:
            skills_performance = df.groupby("skills")["score"].mean()
            mastered_skills = skills_performance[skills_performance >= 0.8].index.tolist()
        else:
            mastered_skills = []

        return {
            "strong_subjects": strong_subjects,
            "mastered_skills": mastered_skills,
            "learning_style_match": self._evaluate_learning_style_match(df)
        }

    except Exception:
        return {
            "strong_subjects": [],
            "mastered_skills": [],
            "learning_style_match": None
        }

def _identify_weaknesses(self, df):
    """Identifie les points faibles de l'étudiant"""
    if df.empty:
        return {
            "weak_subjects": [],
            "skills_to_improve": [],
            "recommended_focus": []
        }

    try:
        # Identifier les matières faibles
        subject_performance = df.groupby("subject")["score"].mean()
        weak_subjects = subject_performance[subject_performance < 0.6].index.tolist()

        # Identifier les compétences à améliorer
        if "skills" in df.columns:
            skills_performance = df.groupby("skills")["score"].mean()
            skills_to_improve = skills_performance[skills_performance < 0.6].index.tolist()
        else:
            skills_to_improve = []

        return {
            "weak_subjects": weak_subjects,
            "skills_to_improve": skills_to_improve,
            "recommended_focus": self._generate_focus_recommendations(df)
        }

    except Exception:
        return {
            "weak_subjects": [],
            "skills_to_improve": [],
            "recommended_focus": []
        }

def _analyze_learning_patterns(self, df):
    """Analyse les patterns d'apprentissage"""
    if df.empty:
        return {
            "preferred_time_slots": [],
            "optimal_session_duration": {"min": 30, "max": 45},
            "best_performing_subjects": {}
        }

    try:
        # Identifier les meilleures périodes d'apprentissage
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        performance_by_hour = df.groupby('hour')['score'].mean()
        preferred_hours = performance_by_hour.nlargest(3).index.tolist()

        # Calculer la durée optimale des sessions
        optimal_duration = self._calculate_optimal_session_duration(df)

        # Identifier les meilleures performances par matière
        best_subjects = df.groupby("subject")["score"].mean().nlargest(3).to_dict()

        return {
            "preferred_time_slots": preferred_hours,
            "optimal_session_duration": optimal_duration,
            "best_performing_subjects": best_subjects
        }

    except Exception:
        return {
            "preferred_time_slots": [],
            "optimal_session_duration": {"min": 30, "max": 45},
            "best_performing_subjects": {}
        }

def _calculate_optimal_session_duration(self, df):
    """Calcule la durée optimale des sessions d'apprentissage"""
    try:
        if 'time_spent' not in df.columns or len(df) < 4:
            return {"min": 30, "max": 45}

        # Créer des bins de durée
        df['duration_bin'] = pd.qcut(df['time_spent'], 
                                   q=min(4, len(df)), 
                                   duplicates='drop')
        
        # Calculer la performance moyenne par bin
        performance_by_duration = df.groupby('duration_bin')['score'].mean()
        
        # Trouver le bin optimal
        optimal_bin = performance_by_duration.idxmax()
        
        return {
            "min": int(optimal_bin.left),
            "max": int(optimal_bin.right)
        }

    except Exception:
        return {"min": 30, "max": 45}

def _evaluate_progression(self, df):
    """Évalue la progression de l'étudiant"""
    if df.empty:
        return {
            "current_level": "débutant",
            "next_milestone": "compléter le premier module",
            "progress_rate": "initial"
        }

    try:
        # Calculer le niveau actuel
        avg_score = df['score'].mean()
        if avg_score >= 0.8:
            current_level = "avancé"
            next_milestone = "maîtriser les concepts avancés"
        elif avg_score >= 0.6:
            current_level = "intermédiaire"
            next_milestone = "atteindre le niveau avancé"
        else:
            current_level = "débutant"
            next_milestone = "atteindre le niveau intermédiaire"

        # Calculer le taux de progression
        progress_rate = self._calculate_progress_rate(df)

        return {
            "current_level": current_level,
            "next_milestone": next_milestone,
            "progress_rate": progress_rate
        }

    except Exception:
        return {
            "current_level": "débutant",
            "next_milestone": "compléter le premier module",
            "progress_rate": "initial"
        }

def _analyze_engagement(self, df):
    """Analyse l'engagement de l'étudiant"""
    if df.empty:
        return {
            "session_frequency": "à déterminer",
            "average_session_duration": 0,
            "consistency_score": 0.0
        }

    try:
        # Calculer la fréquence des sessions
        session_frequency = self._calculate_session_frequency(df)

        # Calculer la durée moyenne des sessions
        avg_duration = df['time_spent'].mean() if 'time_spent' in df.columns else 0

        # Calculer le score de consistance
        consistency = self._calculate_consistency_score(df)

        return {
            "session_frequency": session_frequency,
            "average_session_duration": int(avg_duration),
            "consistency_score": consistency
        }

    except Exception:
        return {
            "session_frequency": "à déterminer",
            "average_session_duration": 0,
            "consistency_score": 0.0
        }

def _calculate_session_frequency(self, df):
    """Calcule la fréquence des sessions d'apprentissage"""
    try:
        if len(df) < 2:
            return "à déterminer"

        # Calculer l'intervalle moyen entre les sessions
        df = df.sort_values('timestamp')
        intervals = df['timestamp'].diff().dropna()
        avg_interval = intervals.mean().total_seconds() / (24 * 3600)  # en jours

        if avg_interval <= 1:
            return "quotidienne"
        elif avg_interval <= 2:
            return "tous les deux jours"
        elif avg_interval <= 7:
            return "hebdomadaire"
        else:
            return "irrégulière"

    except Exception:
        return "à déterminer"

def _calculate_consistency_score(self, df):
    """Calcule un score de consistance dans l'apprentissage"""
    try:
        if len(df) < 2:
            return 0.0

        # Calculer la régularité des intervalles
        intervals = df['timestamp'].diff().dropna().dt.total_seconds()
        consistency = 1 - (intervals.std() / intervals.mean())
        return max(0.0, min(1.0, consistency))

    except Exception:
        return 0.0

def _evaluate_learning_style_match(self, df):
    """Évalue l'adéquation avec le style d'apprentissage"""
    try:
        if 'learning_style' not in df.columns or df.empty:
            return None

        style_performance = df.groupby('learning_style')['score'].mean()
        if not style_performance.empty:
            best_style = style_performance.idxmax()
            return {
                "style": best_style,
                "efficacité": float(style_performance.max())
            }
        return None

    except Exception:
        return None

def _generate_focus_recommendations(self, df):
    """Génère des recommandations de focus basées sur les performances"""
    try:
        if df.empty:
            return []

        recommendations = []
        
        # Analyser les performances par type de contenu
        if 'content_type' in df.columns:
            type_performance = df.groupby('content_type')['score'].mean()
            weak_types = type_performance[type_performance < 0.6]
            for content_type in weak_types.index:
                recommendations.append(f"Pratiquer davantage avec {content_type}")

        # Analyser les performances par compétence
        if 'skills' in df.columns:
            skills_performance = df.groupby('skills')['score'].mean()
            weak_skills = skills_performance[skills_performance < 0.6]
            for skill in weak_skills.index:
                recommendations.append(f"Renforcer la compétence: {skill}")

        return recommendations[:3]  # Limiter à 3 recommandations

    except Exception:
        return []

def update_learning_preferences(self, student_id, new_preferences):
    """Met à jour les préférences d'apprentissage de l'étudiant"""
    try:
        with open(self.students_file, "r", encoding='utf-8') as f:
            students_data = json.load(f)

        # Trouver l'étudiant
        student = next((s for s in students_data["students"] if s["id"] == student_id), None)
        if not student:
            return False

        # Récupérer l'historique des préférences
        current_preferences = student.get("learning_preferences_history", [])
        
        # Ajouter les nouvelles préférences avec timestamp
        new_preference_entry = {
            "timestamp": datetime.now().isoformat(),
            "preferences": new_preferences
        }
        current_preferences.append(new_preference_entry)

        # Mettre à jour le style d'apprentissage basé sur les nouvelles préférences
        updated_style = self._calculate_updated_learning_style(student, new_preferences)
        
        # Mettre à jour les données de l'étudiant
        student.update({
            "learning_preferences_history": current_preferences,
            "current_preferences": new_preferences,
            "preferred_learning_style": updated_style["primary_style"],
            "learning_style_details": {
                "style_percentages": updated_style["style_percentages"],
                "secondary_styles": updated_style["secondary_styles"]
            },
            "learning_style_updated": datetime.now().isoformat()
        })

        # Sauvegarder les modifications
        with open(self.students_file, "w", encoding='utf-8') as f:
            json.dump(students_data, f, indent=4, ensure_ascii=False)

        return True

    except Exception as e:
        print(f"Erreur lors de la mise à jour des préférences: {str(e)}")
        return False

def _calculate_updated_learning_style(self, student, new_preferences):
    """Calcule le style d'apprentissage mis à jour basé sur l'historique et les nouvelles préférences"""
    try:
        # Récupérer l'historique des préférences
        preferences_history = student.get("learning_preferences_history", [])
        
        # Calculer les poids pour chaque style d'apprentissage
        style_weights = {
            "visual": 0.0,
            "audio": 0.0,
            "text": 0.0,
            "practical": 0.0
        }

        # Analyser les types de contenu préférés actuels
        content_type_mapping = {
            "Vidéos": "visual",
            "Audio": "audio",
            "Documents PDF": "text",
            "Exercices interactifs": "practical",
            "Quiz": "practical"
        }

        # Donner plus de poids aux préférences récentes
        for content_type in new_preferences.get("content_types", []):
            if content_type in content_type_mapping:
                style_weights[content_type_mapping[content_type]] += 2.0

        # Prendre en compte l'historique avec des poids décroissants
        for i, hist_entry in enumerate(reversed(preferences_history)):
            weight_factor = 1.0 / (i + 2)  # Poids décroissant pour les anciennes préférences
            for content_type in hist_entry["preferences"].get("content_types", []):
                if content_type in content_type_mapping:
                    style_weights[content_type_mapping[content_type]] += weight_factor

        # Normaliser les poids
        total_weight = sum(style_weights.values()) or 1.0
        style_percentages = {
            style: (weight / total_weight) * 100 
            for style, weight in style_weights.items()
        }

        # Déterminer le style principal et les styles secondaires
        sorted_styles = sorted(
            style_percentages.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            "primary_style": sorted_styles[0][0],
            "style_percentages": style_percentages,
            "secondary_styles": sorted_styles[1:]
        }

    except Exception as e:
        print(f"Erreur lors du calcul du style d'apprentissage: {str(e)}")
        return {
            "primary_style": "visual",
            "style_percentages": {"visual": 25, "audio": 25, "text": 25, "practical": 25},
            "secondary_styles": []
        }

def get_current_preferences(self, student_id):
    """Récupère les préférences actuelles de l'étudiant"""
    try:
        with open(self.students_file, "r", encoding='utf-8') as f:
            students_data = json.load(f)

        student = next((s for s in students_data["students"] if s["id"] == student_id), None)
        if student and "current_preferences" in student:
            return student["current_preferences"]
        return None

    except Exception as e:
        print(f"Erreur lors de la récupération des préférences: {str(e)}")
        return None 