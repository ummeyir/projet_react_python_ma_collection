import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from models.item import Item


EXERCISES = [
    {"id": 1, "category": "Pectoraux", "name": "Développé couché", "muscle_group": "Pectoraux", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Exercice de base pour la poitrine.", "image_url": "/images/exercises/pec/developpe-coucher.jpg"},
    {"id": 2, "category": "Pectoraux", "name": "Développé incliné", "muscle_group": "Pectoraux", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Travaille surtout la partie supérieure de la poitrine.", "image_url": "/images/exercises/pec/developpe-incline-barre.jpg"},
    {"id": 3, "category": "Pectoraux", "name": "Pec fly", "muscle_group": "Pectoraux", "equipment": "Haltères", "difficulty": "Débutant", "description": "Ouverture du torse et étirement musculaire.", "image_url": "/images/exercises/pec/pec-fly.jpg"},
    {"id": 4, "category": "Pectoraux", "name": "Dips", "muscle_group": "Pectoraux", "equipment": "Barres parallèles", "difficulty": "Avancé", "description": "Très efficace pour les pectoraux et les triceps.", "image_url": "/images/exercises/pec/dips.jpg"},
    {"id": 5, "category": "Pectoraux", "name": "Pompes", "muscle_group": "Pectoraux", "equipment": "Poids du corps", "difficulty": "Débutant", "description": "Exercice polyvalent pour la poitrine et les triceps.", "image_url": "/images/exercises/pec/pompe.png"},
    {"id": 6, "category": "Dos", "name": "Tractions", "muscle_group": "Dos", "equipment": "Barre de traction", "difficulty": "Intermédiaire", "description": "Développe la force du dos et des bras.", "image_url": "/images/exercises/dos/traction.jpg"},
    {"id": 7, "category": "Dos", "name": "Rowing barre", "muscle_group": "Dos", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Travaille les trapèzes et les lats.", "image_url": "/images/exercises/dos/rowing-barre.webp"},
    {"id": 8, "category": "Dos", "name": "Tirage horizontal", "muscle_group": "Dos", "equipment": "Machine", "difficulty": "Débutant", "description": "Focus sur les muscles du dos avec un mouvement guidé.", "image_url": "/images/exercises/dos/tirage-poulie-basse.jpg"},
    {"id": 9, "category": "Dos", "name": "Rowing à un bras", "muscle_group": "Dos", "equipment": "Haltère", "difficulty": "Intermédiaire", "description": "Améliore la stabilité et la traction.", "image_url": "/images/exercises/dos/rowing-un-bras.webp"},
    {"id": 10, "category": "Dos", "name": "Pull-over", "muscle_group": "Dos", "equipment": "Haltère ou machine", "difficulty": "Débutant", "description": "Exercice de contraction large du dos.", "image_url": "/images/exercises/dos/pull-over.webp"},
    {"id": 23, "category": "Dos", "name": "Shrugs", "muscle_group": "Trapèzes", "equipment": "Barre ou haltères", "difficulty": "Débutant", "description": "Renforce les trapèzes.", "image_url": "/images/exercises/dos/Shrugs.jpg"},
    {"id": 11, "category": "Jambes", "name": "Squat", "muscle_group": "Jambes", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Le mouvement de base pour le développement des jambes.", "image_url": "/images/exercises/jambe/squat.avif"},
    {"id": 12, "category": "Jambes", "name": "Fente avant", "muscle_group": "Jambes", "equipment": "Haltères", "difficulty": "Débutant", "description": "Travaille les quadriceps et les fessiers.", "image_url": "/images/exercises/jambe/fente.jpg"},
    {"id": 13, "category": "Jambes", "name": "Leg press", "muscle_group": "Jambes", "equipment": "Machine", "difficulty": "Débutant", "description": "Exercice très efficace pour les cuisses.", "image_url": "/images/exercises/jambe/leg-press.avif"},
    {"id": 14, "category": "Jambes", "name": "Soulevé de terre", "muscle_group": "Jambes", "equipment": "Barre", "difficulty": "Avancé", "description": "Travaille la puissance globale et le posterior chain.", "image_url": "/images/exercises/jambe/deadlift.jpg"},
    {"id": 15, "category": "Jambes", "name": "Good morning", "muscle_group": "Jambes", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Focalise sur les ischio-jambiers et le bas du dos.", "image_url": "/images/exercises/jambe/goodmorning.jpg"},
    {"id": 16, "category": "Jambes", "name": "Hip thrust", "muscle_group": "Fessiers", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Excellente activation des fessiers.", "image_url": "/images/exercises/jambe/hip-trust.jpg"},
    {"id": 17, "category": "Jambes", "name": "Leg extension", "muscle_group": "Jambes", "equipment": "Machine", "difficulty": "Débutant", "description": "Isolent les quadriceps en sécurité.", "image_url": "/images/exercises/jambe/Extension_de_jambes.jpg"},
    {"id": 18, "category": "Jambes", "name": "Leg curl", "muscle_group": "Ischio-jambiers", "equipment": "Machine", "difficulty": "Débutant", "description": "Travail isolé des ischio-jambiers.", "image_url": "/images/exercises/jambe/leg-curl.webp"},
    {"id": 19, "category": "Épaules", "name": "Presse militaire", "muscle_group": "Épaules", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Développe les épaules et la stabilité du tronc.", "image_url": "/images/exercises/epaule/shoulder-press.jpg"},
    {"id": 20, "category": "Épaules", "name": "Élévation latérale", "muscle_group": "Épaules", "equipment": "Haltères", "difficulty": "Débutant", "description": "Cible directement le deltoïde moyen.", "image_url": "/images/exercises/epaule/elevation_lateral.jpg"},
    {"id": 21, "category": "Épaules", "name": "Arnold press", "muscle_group": "Épaules", "equipment": "Haltères", "difficulty": "Intermédiaire", "description": "Variation dynamique pour les épaules.", "image_url": "/images/exercises/epaule/arnold-press.jpg"},
    {"id": 22, "category": "Épaules", "name": "Rear delt fly", "muscle_group": "Épaules", "equipment": "Haltères", "difficulty": "Débutant", "description": "Travaille les épaules arrière.", "image_url": "/images/exercises/epaule/Rear_delt_fly.jpg"},
    {"id": 24, "category": "Bras", "name": "Curl barre", "muscle_group": "Biceps", "equipment": "Barre", "difficulty": "Débutant", "description": "Exercice classique pour les biceps.", "image_url": "/images/exercises/bras/Curl_barre.jpg"},
    {"id": 25, "category": "Bras", "name": "Curl haltères", "muscle_group": "Biceps", "equipment": "Haltères", "difficulty": "Débutant", "description": "Isoler les biceps avec un amplitude complète.", "image_url": "/images/exercises/bras/curl.png"},
    {"id": 26, "category": "Bras", "name": "Curl marteau", "muscle_group": "Biceps", "equipment": "Haltères", "difficulty": "Débutant", "description": "Travaille les biceps et les avant-bras.", "image_url": "/images/exercises/bras/Curl_marteau.jpg"},
    {"id": 27, "category": "Bras", "name": "Extension triceps poulie", "muscle_group": "Triceps", "equipment": "Poulie", "difficulty": "Débutant", "description": "Un des meilleurs mouvements isolés pour les triceps.", "image_url": "/images/exercises/bras/extension_triceps_poulie.png"},
    {"id": 28, "category": "Bras", "name": "Dips triceps", "muscle_group": "Triceps", "equipment": "Barres parallèles", "difficulty": "Intermédiaire", "description": "Exercice puissant pour les triceps.", "image_url": "/images/exercises/bras/dips_triceps.jpg"},
    {"id": 29, "category": "Bras", "name": "Overhead triceps extension", "muscle_group": "Triceps", "equipment": "Haltère ou poulie", "difficulty": "Intermédiaire", "description": "Isolent les triceps avec une longueur de muscle optimale.", "image_url": "/images/exercises/bras/overhead_extention_poulie.jpg"},
    {"id": 30, "category": "Abdominaux", "name": "Crunch", "muscle_group": "Abdominaux", "equipment": "Poids du corps", "difficulty": "Débutant", "description": "Exercice de base pour les abdominaux.", "image_url": "/images/exercises/abdominaux/crunch.webp"},
    {"id": 31, "category": "Abdominaux", "name": "Abdo sur machine", "muscle_group": "Abdominaux", "equipment": "Machine", "difficulty": "Débutant", "description": "Contrôle et charge sur les abdominaux.", "image_url": "/images/exercises/abdominaux/abdo_machine.jpg"},
    {"id": 32, "category": "Abdominaux", "name": "Planche", "muscle_group": "Abdominaux", "equipment": "Poids du corps", "difficulty": "Intermédiaire", "description": "Stabilise le tronc et les abdominaux.", "image_url": "/images/exercises/abdominaux/planche.webp"},
    {"id": 33, "category": "Abdominaux", "name": "Mountain climber", "muscle_group": "Abdominaux", "equipment": "Poids du corps", "difficulty": "Intermédiaire", "description": "Travaille les abdominaux et le cardio.", "image_url": "/images/exercises/cardio/moutain_climber.avif"},
    {"id": 34, "category": "Cardio", "name": "Rameur", "muscle_group": "Cardio", "equipment": "Machine", "difficulty": "Débutant", "description": "Exercice cardio complet et intense.", "image_url": "/images/exercises/cardio/rameur.jpg"},
    {"id": 35, "category": "Cardio", "name": "Tapis de course", "muscle_group": "Cardio", "equipment": "Tapis", "difficulty": "Débutant", "description": "Cardio accessible et efficace.", "image_url": "/images/exercises/cardio/tapis_course.gif"},
    {"id": 36, "category": "Cardio", "name": "Burpees", "muscle_group": "Cardio", "equipment": "Poids du corps", "difficulty": "Intermédiaire", "description": "Exercice complet pour la résistance et le cardio.", "image_url": "/images/exercises/cardio/burpees.jpg"},
    {"id": 37, "category": "Full body", "name": "Kettlebell swing", "muscle_group": "Full body", "equipment": "Kettlebell", "difficulty": "Intermédiaire", "description": "Travaille les jambes, les fessiers et le dos.", "image_url": "/images/exercises/cardio/kettlebell3.jpg"},
    {"id": 38, "category": "Jambes", "name": "Box squat", "muscle_group": "Jambes", "equipment": "Barre", "difficulty": "Intermédiaire", "description": "Variation du squat avec contrôle de la profondeur.", "image_url": "/images/exercises/jambe/box_squat.jpg"},

]


async def seed_items(session: AsyncSession) -> None:
    for exercise in EXERCISES:
        item_id = exercise["id"]
        item = await session.get(Item, item_id)
        if item is None:
            session.add(Item(**exercise))
        elif "image_url" in exercise and item.image_url != exercise["image_url"]:
            item.image_url = exercise["image_url"]
    await session.commit()


async def main() -> None:
    from db.database import async_session_maker, create_db_and_tables, engine

    try:
        await create_db_and_tables()
        async with async_session_maker() as session:
            await seed_items(session)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
