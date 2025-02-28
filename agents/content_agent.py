import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

class ContentAgent:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.content_file = self.data_dir / "content.json"
        self.learning_data_file = self.data_dir / "learning_data.json"
        
        # Configuration de Gemini
        load_dotenv()
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
        
        self.init_data_files()

    def init_data_files(self):
        """Initialise les fichiers de données s'ils n'existent pas"""
        self.data_dir.mkdir(exist_ok=True)
        
        if not self.content_file.exists():
            default_content = {
                "content_items": [
                    {
                        "id": "MATH001",
                        "title": "Introduction à l'Algèbre",
                        "subject": "Mathématiques",
                        "type": "visual",
                        "difficulty": 3,
                        "description": "Cours interactif sur les bases de l'algèbre"
                    },
                    {
                        "id": "PHY001",
                        "title": "Principes de la Mécanique",
                        "subject": "Physique",
                        "type": "practical",
                        "difficulty": 4,
                        "description": "Expériences pratiques en mécanique classique"
                    },
                    {
                        "id": "INFO001",
                        "title": "Bases de la Programmation",
                        "subject": "Informatique",
                        "type": "practical",
                        "difficulty": 2,
                        "description": "Introduction aux concepts de programmation"
                    },
                    {
                        "id": "MATH002",
                        "title": "Géométrie Avancée",
                        "subject": "Mathématiques",
                        "type": "visual",
                        "difficulty": 4,
                        "description": "Étude approfondie des concepts géométriques"
                    },
                    {
                        "id": "CHIM001",
                        "title": "Chimie Organique",
                        "subject": "Chimie",
                        "type": "practical",
                        "difficulty": 3,
                        "description": "Introduction à la chimie organique"
                    }
                ]
            }
            with open(self.content_file, "w", encoding='utf-8') as f:
                json.dump(default_content, f, indent=4, ensure_ascii=False)

    def recommend_content(self, student_id, subject=None, preferences=None, count=5):
        """Recommande du contenu personnalisé pour un étudiant en utilisant Gemini"""
        # Charger les données
        with open(self.learning_data_file, "r", encoding='utf-8') as f:
            learning_data = json.load(f)
        
        student_history = [r for r in learning_data["learning_records"] if r["student_id"] == student_id]
        df_history = pd.DataFrame(student_history) if student_history else None
        
        # Analyser le profil de l'étudiant
        profile = self._analyze_student_profile(df_history) if df_history is not None else {
            "performance": {"average_score": 0.5, "completion_rate": 0.5, "success_rate": 0.5},
            "learning_style": "visual",
            "subject_performance": {},
            "difficulty_level": "débutant"
        }
        
        # Intégrer les préférences utilisateur
        if preferences:
            profile.update({
                "module": preferences.get("module", ""),
                "desired_difficulty": preferences.get("difficulty", 3),
                "preferred_duration": preferences.get("duration", 30),
                "preferred_content_types": preferences.get("content_types", []),
                "learning_goal": preferences.get("learning_goal", "")
            })
        
        # Générer des recommandations avec Gemini
        recommendations = self._generate_recommendations_with_gemini(
            self._create_recommendation_prompt(profile, subject)
        )
        
        # Filtrer et trier les recommandations selon les préférences
        filtered_recommendations = []
        for rec in recommendations:
            score = self._calculate_recommendation_relevance(rec, profile, preferences)
            if score > 0.5:  # Seulement garder les recommandations pertinentes
                rec['relevance_score'] = score
                filtered_recommendations.append(rec)
        
        # Trier par pertinence
        filtered_recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return filtered_recommendations[:count]

    def _calculate_recommendation_relevance(self, recommendation, profile, preferences):
        """Calcule la pertinence d'une recommandation selon le profil et les préférences"""
        score = 0.0
        weights = {
            'learning_style': 0.3,
            'difficulty': 0.2,
            'duration': 0.15,
            'content_type': 0.2,
            'subject_relevance': 0.15
        }
        
        # Vérifier la correspondance du style d'apprentissage
        if recommendation['type'] == profile['learning_style']:
            score += weights['learning_style']
        
        # Vérifier la difficulté
        if preferences and 'difficulty' in preferences:
            diff_match = 1 - abs(recommendation['difficulty'] - preferences['difficulty']) / 4
            score += weights['difficulty'] * diff_match
        
        # Vérifier la durée
        if preferences and 'duration' in preferences:
            duration_match = 1 - abs(recommendation['duration'] - preferences['duration']) / preferences['duration']
            score += weights['duration'] * max(0, duration_match)
        
        # Vérifier les types de contenu préférés
        if preferences and 'content_types' in preferences:
            content_type_match = any(ct.lower() in recommendation['type'].lower() 
                                   for ct in preferences['content_types'])
            if content_type_match:
                score += weights['content_type']
        
        # Vérifier la pertinence du sujet
        if profile['subject_performance']:
            subject = recommendation['subject']
            if subject in profile['subject_performance'].get('score', {}):
                subject_score = profile['subject_performance']['score'][subject]
                if subject_score < 0.7:  # Donner priorité aux sujets nécessitant de l'amélioration
                    score += weights['subject_relevance']
        
        return score

    def _analyze_student_profile(self, df):
        """Analyse le profil d'apprentissage de l'étudiant"""
        recent_df = df.sort_values('timestamp').tail(10)
        
        return {
            "performance": {
                "average_score": recent_df["score"].mean(),
                "completion_rate": recent_df["completion_rate"].mean(),
                "success_rate": recent_df["success_rate"].mean()
            },
            "learning_style": self._get_dominant_style(df),
            "subject_performance": self._analyze_subject_performance(df),
            "difficulty_level": self._calculate_optimal_difficulty(df)
        }

    def _get_dominant_style(self, df):
        """Détermine le style d'apprentissage dominant"""
        style_performance = df.groupby("content_type")["success_rate"].mean()
        return style_performance.idxmax() if not style_performance.empty else "visual"

    def _analyze_subject_performance(self, df):
        """Analyse les performances par sujet"""
        return df.groupby("subject").agg({
            "score": "mean",
            "success_rate": "mean",
            "completion_rate": "mean"
        }).to_dict()

    def _calculate_optimal_difficulty(self, df):
        """Calcule le niveau de difficulté optimal"""
        avg_score = df["score"].mean()
        if avg_score < 0.6:
            return "débutant"
        elif avg_score < 0.8:
            return "intermédiaire"
        else:
            return "avancé"

    def _create_recommendation_prompt(self, profile, subject):
        """Crée un prompt pour Gemini"""
        # Définir le type de ressources selon le style d'apprentissage
        resource_type = self._get_resource_type_for_style(profile['learning_style'])
        
        # Construire la description des préférences
        preferences_desc = ""
        if "module" in profile:
            preferences_desc += f"\nModule spécifique: {profile['module']}"
        if "desired_difficulty" in profile:
            preferences_desc += f"\nNiveau de difficulté souhaité: {profile['desired_difficulty']}/5"
        if "preferred_duration" in profile:
            preferences_desc += f"\nDurée de session préférée: {profile['preferred_duration']} minutes"
        if "preferred_content_types" in profile:
            preferences_desc += f"\nTypes de contenu préférés: {', '.join(profile['preferred_content_types'])}"
        if "learning_goal" in profile and profile['learning_goal']:
            preferences_desc += f"\nObjectif d'apprentissage: {profile['learning_goal']}"
        
        prompt = f"""En tant qu'expert en éducation, génère des recommandations de contenu d'apprentissage personnalisées avec des liens réels et vérifiés.

Profil de l'étudiant:
- Style d'apprentissage: {profile['learning_style']}
- Niveau de difficulté optimal: {profile['difficulty_level']}
- Performance moyenne: {profile['performance']['average_score']:.2f}
- Taux de réussite: {profile['performance']['success_rate']:.2f}
{preferences_desc}

{f'Matière ciblée: {subject}' if subject else 'Toutes les matières'}

Pour un style d'apprentissage {profile['learning_style']}, fournis des recommandations de type {resource_type}.

IMPORTANT: Utilise UNIQUEMENT des liens réels et vérifiés provenant de :
- YouTube (youtube.com)
- Khan Academy (khanacademy.org)
- Coursera (coursera.org)
- edX (edx.org)
- MIT OpenCourseWare (ocw.mit.edu)
- FUN-MOOC (fun-mooc.fr)

Génère 5 recommandations de contenu au format JSON avec les champs suivants:
- id: identifiant unique (format: SUBJ001)
- title: titre exact de la ressource
- subject: matière
- module: module spécifique
- type: type de contenu ({profile['learning_style']})
- difficulty: niveau de difficulté (1-5)
- description: description détaillée
- objectives: liste d'objectifs d'apprentissage
- duration: durée estimée en minutes
- resource_url: lien RÉEL et VÉRIFIÉ vers la ressource
- resource_type: type de ressource (video, document, audio, exercice)
- additional_resources: liste de ressources complémentaires avec leurs URLs réels
- prerequisites: liste des prérequis nécessaires
- next_steps: suggestions pour la suite de l'apprentissage

Les recommandations doivent être parfaitement adaptées au profil et aux préférences de l'étudiant."""

        return prompt

    def _get_resource_type_for_style(self, learning_style):
        """Détermine le type de ressources approprié pour chaque style d'apprentissage"""
        resource_mapping = {
            "visual": "vidéos éducatives (YouTube, Khan Academy, Coursera) et infographies",
            "audio": "podcasts éducatifs, cours audio et enregistrements de conférences",
            "text": "documents PDF, articles académiques, et guides d'étude",
            "practical": "exercices interactifs, projets pratiques, et tutoriels pas à pas"
        }
        return resource_mapping.get(learning_style, "ressources mixtes")

    def _generate_recommendations_with_gemini(self, prompt):
        """Génère des recommandations en utilisant Gemini"""
        all_recommendations = []
        try:
            # Configuration de sécurité pour Gemini
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]

            valid_domains = [
                "youtube.com", "youtu.be",
                "khanacademy.org",
                "coursera.org",
                "edx.org",
                "ocw.mit.edu",
                "fun-mooc.fr"
            ]

            # Première tentative : générer plusieurs réponses
            responses = []
            for _ in range(2):
                try:
                    response = self.model.generate_content(
                        prompt,
                        safety_settings=safety_settings,
                        generation_config={
                            "temperature": 0.7,
                            "top_p": 0.8,
                            "top_k": 40
                        }
                    )
                    responses.append(response.text)
                except Exception as e:
                    print(f"Erreur lors de la génération: {str(e)}")
                    continue

            # Traiter les réponses
            for content_str in responses:
                try:
                    start_idx = content_str.find('[')
                    end_idx = content_str.rfind(']') + 1
                    if start_idx != -1 and end_idx != -1:
                        recommendations = json.loads(content_str[start_idx:end_idx])
                        if recommendations and isinstance(recommendations, list):
                            for rec in recommendations:
                                url = rec.get('resource_url', '').lower()
                                if any(domain in url for domain in valid_domains):
                                    if 'additional_resources' in rec:
                                        valid_resources = []
                                        for res in rec['additional_resources']:
                                            res_url = res.get('url', '').lower()
                                            if any(domain in res_url for domain in valid_domains):
                                                valid_resources.append(res)
                                        rec['additional_resources'] = valid_resources
                                    all_recommendations.append(rec)
                except Exception as e:
                    print(f"Erreur lors du traitement de la réponse: {str(e)}")
                    continue

            # Deuxième tentative si nécessaire
            if len(all_recommendations) < 3:
                try:
                    strict_prompt = prompt + "\nIMPORTANT: Assurez-vous que TOUS les liens sont des URLs réelles et valides des plateformes spécifiées."
                    response = self.model.generate_content(
                        strict_prompt,
                        safety_settings=safety_settings,
                        generation_config={
                            "temperature": 0.5,
                            "top_p": 0.9,
                            "top_k": 40
                        }
                    )
                    content_str = response.text
                    start_idx = content_str.find('[')
                    end_idx = content_str.rfind(']') + 1
                    if start_idx != -1 and end_idx != -1:
                        new_recommendations = json.loads(content_str[start_idx:end_idx])
                        for rec in new_recommendations:
                            url = rec.get('resource_url', '').lower()
                            if any(domain in url for domain in valid_domains):
                                all_recommendations.append(rec)
                except Exception as e:
                    print(f"Erreur lors de la deuxième tentative: {str(e)}")

            # Dernière tentative avec YouTube uniquement
            if len(all_recommendations) < 3:
                try:
                    youtube_prompt = f"""Générez 3 recommandations de vidéos YouTube éducatives pour le sujet suivant.
                    Utilisez UNIQUEMENT des liens YouTube réels et vérifiés.
                    Format JSON attendu : {{"id": "XXX", "title": "titre exact", "resource_url": "lien YouTube"}}
                    """
                    response = self.model.generate_content(youtube_prompt)
                    content_str = response.text
                    start_idx = content_str.find('[')
                    end_idx = content_str.rfind(']') + 1
                    if start_idx != -1 and end_idx != -1:
                        youtube_recommendations = json.loads(content_str[start_idx:end_idx])
                        for rec in youtube_recommendations:
                            url = rec.get('resource_url', '').lower()
                            if "youtube.com" in url or "youtu.be" in url:
                                all_recommendations.append(rec)
                except Exception as e:
                    print(f"Erreur lors de la tentative YouTube: {str(e)}")

            # Retourner les recommandations uniques
            seen_urls = set()
            unique_recommendations = []
            for rec in all_recommendations:
                url = rec.get('resource_url')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_recommendations.append(rec)

            return unique_recommendations[:5]

        except Exception as e:
            print(f"Erreur générale lors de la génération des recommandations: {str(e)}")
            try:
                # Dernier recours : appel simple
                simple_prompt = "Donnez-moi 3 liens YouTube éducatifs populaires et vérifiés au format JSON"
                response = self.model.generate_content(simple_prompt)
                content_str = response.text
                start_idx = content_str.find('[')
                end_idx = content_str.rfind(']') + 1
                if start_idx != -1 and end_idx != -1:
                    return json.loads(content_str[start_idx:end_idx])
            except:
                print("Échec de la dernière tentative")
                return []  # Retourner une liste vide en dernier recours

    def _get_beginner_recommendations(self, subject=None, preferences=None):
        """Fournit des recommandations pour les débutants"""
        with open(self.content_file, "r", encoding='utf-8') as f:
            content_data = json.load(f)
        
        recommendations = content_data["content_items"]
        if subject:
            recommendations = [r for r in recommendations if r["subject"] == subject]
        
        # Filtrer pour les contenus de niveau débutant
        recommendations = [r for r in recommendations if r["difficulty"] <= 2]
        return recommendations[:5]

    def adapt_difficulty(self, student_id, content_id):
        """Adapte la difficulté du contenu en fonction des performances de l'étudiant"""
        with open(self.learning_data_file, "r", encoding='utf-8') as f:
            learning_data = json.load(f)

        # Analyser les performances récentes
        student_records = [r for r in learning_data["learning_records"] 
                         if r["student_id"] == student_id and r["content_id"] == content_id]
        
        if not student_records:
            return "difficulty_unchanged"

        # Calculer la performance moyenne
        df = pd.DataFrame(student_records)
        avg_performance = df["score"].mean()

        # Ajuster la difficulté
        if avg_performance > 0.85:
            return "increase_difficulty"
        elif avg_performance < 0.6:
            return "decrease_difficulty"
        else:
            return "maintain_difficulty"

    def get_content_stats(self, content_id=None):
        """Obtient les statistiques d'utilisation du contenu"""
        with open(self.learning_data_file, "r", encoding='utf-8') as f:
            learning_data = json.load(f)

        df = pd.DataFrame(learning_data["learning_records"])
        
        if content_id:
            df = df[df["content_id"] == content_id]

        if df.empty:
            return {
                "status": "error",
                "message": "Aucune donnée disponible"
            }

        stats = {
            "total_views": len(df),
            "average_score": df["score"].mean(),
            "completion_rate": df["completion_rate"].mean(),
            "average_time_spent": df["time_spent"].mean(),
            "success_rate_by_type": df.groupby("content_type")["success_rate"].mean().to_dict(),
            "difficulty_distribution": df["difficulty_level"].value_counts().to_dict()
        }

        return stats

    def _calculate_content_relevance(self, content, student_profile):
        """Calcule la pertinence du contenu pour l'étudiant"""
        score = 0.0
        
        # Correspondance du type de contenu
        if content["type"] == student_profile["preferred_type"]:
            score += 0.4
        
        # Correspondance de la difficulté
        diff_match = 1 - abs(content["difficulty"] - student_profile["avg_difficulty"]) / 5
        score += 0.3 * diff_match
        
        # Correspondance du sujet
        if content["subject"] in student_profile["strong_subjects"]:
            score += 0.3
        
        return score 