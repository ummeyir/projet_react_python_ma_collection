from sqlalchemy.ext.asyncio import AsyncSession

from models.item import Item


EXERCISES = [
    {"id": 1, "category": "Pectoraux", "name": "Développé couché", "muscle_group": "Pectoraux", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Exercice de base pour la poitrine."},
    {"id": 2, "category": "Pectoraux", "name": "Développé incliné", "muscle_group": "Pectoraux", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Travaille surtout la partie supérieure de la poitrine."},
    {"id": 3, "category": "Pectoraux", "name": "Écarté aux haltères", "muscle_group": "Pectoraux", "equipment": "Haltères", "difficulty": "Débutant", "description": "Ouverture du torse et étirement musculaire."},
    {"id": 4, "category": "Pectoraux", "name": "Dips", "muscle_group": "Pectoraux", "equipment": "Barres parallèles", "difficulty": "Avancé", "description": "Très efficace pour les pectoraux et les triceps."},
    {"id": 5, "category": "Pectoraux", "name": "Pompes", "muscle_group": "Pectoraux", "equipment": "Poids du corps", "difficulty": "Débutant", "description": "Exercice polyvalent pour la poitrine et les triceps."},
    {"id": 6, "category": "Dos", "name": "Tractions", "muscle_group": "Dos", "equipment": "Barre de traction", "difficulty": "Intermédiaire", "description": "Développe la force du dos et des bras."},
    {"id": 7, "category": "Dos", "name": "Rowing barre", "muscle_group": "Dos", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Travaille les trapèzes et les lats."},
    {"id": 8, "category": "Dos", "name": "Tirage vertical", "muscle_group": "Dos", "equipment": "Machine", "difficulty": "Débutant", "description": "Focus sur les muscles du dos avec un mouvement guidé."},
    {"id": 9, "category": "Dos", "name": "Rowing à un bras", "muscle_group": "Dos", "equipment": "Haltère", "difficulty": "Intermédiaire", "description": "Améliore la stabilité et la traction."},
    {"id": 10, "category": "Dos", "name": "Pull-over", "muscle_group": "Dos", "equipment": "Haltère ou machine", "difficulty": "Débutant", "description": "Exercice de contraction large du dos."},
    {"id": 11, "category": "Jambes", "name": "Squat", "muscle_group": "Jambes", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Le mouvement de base pour le développement des jambes."},
    {"id": 12, "category": "Jambes", "name": "Fente avant", "muscle_group": "Jambes", "equipment": "Haltères", "difficulty": "Débutant", "description": "Travaille les quadriceps et les fessiers."},
    {"id": 13, "category": "Jambes", "name": "Leg press", "muscle_group": "Jambes", "equipment": "Machine", "difficulty": "Débutant", "description": "Exercice très efficace pour les cuisses."},
    {"id": 14, "category": "Jambes", "name": "Soulevé de terre", "muscle_group": "Jambes", "equipment": "Barre", "difficulty": "Avancé", "description": "Travaille la puissance globale et le posterior chain."},
    {"id": 15, "category": "Jambes", "name": "Good morning", "muscle_group": "Jambes", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Focalise sur les ischio-jambiers et le bas du dos."},
    {"id": 16, "category": "Jambes", "name": "Hip thrust", "muscle_group": "Fessiers", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Excellente activation des fessiers."},
    {"id": 17, "category": "Jambes", "name": "Extension de jambes", "muscle_group": "Jambes", "equipment": "Machine", "difficulty": "Débutant", "description": "Isolent les quadriceps en sécurité."},
    {"id": 18, "category": "Jambes", "name": "Curl fémoral", "muscle_group": "Ischio-jambiers", "equipment": "Machine", "difficulty": "Débutant", "description": "Travail isolé des ischio-jambiers."},
    {"id": 19, "category": "Épaules", "name": "Presse militaire", "muscle_group": "Épaules", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Développe les épaules et la stabilité du tronc."},
    {"id": 20, "category": "Épaules", "name": "Élévation latérale", "muscle_group": "Épaules", "equipment": "Haltères", "difficulty": "Débutant", "description": "Cible directement le deltoïde moyen."},
    {"id": 21, "category": "Épaules", "name": "Arnold press", "muscle_group": "Épaules", "equipment": "Haltères", "difficulty": "Intermédiaire", "description": "Variation dynamique pour les épaules."},
    {"id": 22, "category": "Épaules", "name": "Rear delt fly", "muscle_group": "Épaules", "equipment": "Haltères", "difficulty": "Débutant", "description": "Travaille les épaules arrière."},
    {"id": 23, "category": "Épaules", "name": "Shrugs", "muscle_group": "Trapèzes", "equipment": "Barre ou haltères", "difficulty": "Débutant", "description": "Renforce les trapèzes."},
    {"id": 24, "category": "Bras", "name": "Curl barre", "muscle_group": "Biceps", "equipment": "Barre", "difficulty": "Débutant", "description": "Exercice classique pour les biceps."},
    {"id": 25, "category": "Bras", "name": "Curl haltères", "muscle_group": "Biceps", "equipment": "Haltères", "difficulty": "Débutant", "description": "Isoler les biceps avec un amplitude complète."},
    {"id": 26, "category": "Bras", "name": "Curl marteau", "muscle_group": "Biceps", "equipment": "Haltères", "difficulty": "Débutant", "description": "Travaille les biceps et les avant-bras."},
    {"id": 27, "category": "Bras", "name": "Extension triceps poulie", "muscle_group": "Triceps", "equipment": "Poulie", "difficulty": "Débutant", "description": "Un des meilleurs mouvements isolés pour les triceps."},
    {"id": 28, "category": "Bras", "name": "Dips triceps", "muscle_group": "Triceps", "equipment": "Barres parallèles", "difficulty": "Intermédiaire", "description": "Exercice puissant pour les triceps."},
    {"id": 29, "category": "Bras", "name": "Overhead triceps extension", "muscle_group": "Triceps", "equipment": "Haltère ou poulie", "difficulty": "Intermédiaire", "description": "Isolent les triceps avec une longueur de muscle optimale."},
    {"id": 30, "category": "Abdominaux", "name": "Crunch", "muscle_group": "Abdominaux", "equipment": "Poids du corps", "difficulty": "Débutant", "description": "Exercice de base pour les abdominaux."},
    {"id": 31, "category": "Abdominaux", "name": "Abdo sur machine", "muscle_group": "Abdominaux", "equipment": "Machine", "difficulty": "Débutant", "description": "Contrôle et charge sur les abdominaux."},
    {"id": 32, "category": "Abdominaux", "name": "Planche", "muscle_group": "Abdominaux", "equipment": "Poids du corps", "difficulty": "Intermédiaire", "description": "Stabilise le tronc et les abdominaux."},
    {"id": 33, "category": "Abdominaux", "name": "Mountain climber", "muscle_group": "Abdominaux", "equipment": "Poids du corps", "difficulty": "Intermédiaire", "description": "Travaille les abdominaux et le cardio."},
    {"id": 34, "category": "Cardio", "name": "Rameur", "muscle_group": "Cardio", "equipment": "Machine", "difficulty": "Débutant", "description": "Exercice cardio complet et intense."},
    {"id": 35, "category": "Cardio", "name": "Tapis de course", "muscle_group": "Cardio", "equipment": "Tapis", "difficulty": "Débutant", "description": "Cardio accessible et efficace."},
    {"id": 36, "category": "Cardio", "name": "Burpee", "muscle_group": "Cardio", "equipment": "Poids du corps", "difficulty": "Intermédiaire", "description": "Exercice complet pour la résistance et le cardio."},
    {"id": 37, "category": "Full body", "name": "Kettlebell swing", "muscle_group": "Full body", "equipment": "Kettlebell", "difficulty": "Intermédiaire", "description": "Travaille les jambes, les fessiers et le dos."},
    {"id": 38, "category": "Jambes", "name": "Box squat", "muscle_group": "Jambes", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Variation du squat avec contrôle de la profondeur."},
    {"id": 39, "category": "Cardio", "name": "Marches sur tapis", "muscle_group": "Cardio", "equipment": "Tapis", "difficulty": "Débutant", "description": "Excellent pour l’endurance et la récupération."},
    {"id": 40, "category": "Dos", "name": "Remise devant", "muscle_group": "Dos", "equipment": "Barre ou machine", "difficulty": "Intermédiaire", "description": "Développe la partie supérieure du dos et le trapèze."}
]


async def seed_items(session: AsyncSession) -> None:
    for exercise in EXERCISES:
        item_id = exercise["id"]
        if await session.get(Item, item_id) is None:
            session.add(Item(**exercise))
    await session.commit()
