import { Link, useParams } from "react-router-dom";
import { exercises } from "../data/exercises";

function ItemDetail() {
	const { itemId } = useParams();
	const item = exercises.find((exercise) => exercise.id === Number(itemId));

	return (
		<main className="app-shell">
			<header className="page-header">
				<p className="eyebrow">FICHE EXERCICE</p>
				<h1>
					<Link className="brand-link" to="/">
						Ma Collection
					</Link>
				</h1>
			</header>

			{item ? (
				<article className="exercise-detail">
					<Link className="detail-back-link" to="/">
						<span aria-hidden="true">←</span> Retour au catalogue
					</Link>
					<div className="exercise-detail-layout">
						<figure className="exercise-detail-figure">
							<img
								src={item.image_url}
								alt={`Illustration de l'exercice ${item.titre}`}
							/>
							<figcaption>{item.categorie}</figcaption>
						</figure>
						<div className="exercise-detail-copy">
							<p className="item-card-category">{item.categorie}</p>
							<h2>{item.titre}</h2>
							<p className="exercise-detail-description">{item.description}</p>
							<dl className="exercise-detail-facts">
								<div>
									<dt>Groupe musculaire</dt>
									<dd>{item.groupe_musculaire}</dd>
								</div>
								<div>
									<dt>Équipement</dt>
									<dd>{item.equipement}</dd>
								</div>
							</dl>
							<Link className="detail-action-link" to="/">
								Explorer les exercices <span aria-hidden="true">→</span>
							</Link>
						</div>
					</div>
				</article>
			) : (
				<section className="detail-not-found" role="status">
					<p className="section-index">404 / CATALOGUE</p>
					<h2>Exercice introuvable</h2>
					<p>Cette fiche n'existe pas ou n'est plus disponible.</p>
					<Link className="detail-action-link" to="/">
						Retour au catalogue <span aria-hidden="true">→</span>
					</Link>
				</section>
			)}
		</main>
	);
}

export default ItemDetail;
