import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, getItem } from "../services/apiClient";
import type { Item } from "../types/api";

function ItemDetail() {
	const { itemId } = useParams();
	const [item, setItem] = useState<Item | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [retryKey, setRetryKey] = useState(0);

	useEffect(() => {
		const controller = new AbortController();

		async function loadItem(): Promise<void> {
			setLoading(true);
			setError(null);
			const parsedItemId = Number(itemId);

			if (!Number.isInteger(parsedItemId) || parsedItemId < 1) {
				setItem(null);
				setError("L'identifiant de l'exercice est invalide.");
				setLoading(false);
				return;
			}

			try {
				setItem(await getItem(parsedItemId, controller.signal));
			} catch (caughtError: unknown) {
				if (controller.signal.aborted) {
					return;
				}

				setItem(null);
				setError(
					caughtError instanceof ApiError
						? caughtError.message
						: "Impossible de contacter l'API. Vérifiez qu'elle est démarrée.",
				);
			} finally {
				if (!controller.signal.aborted) {
					setLoading(false);
				}
			}
		}

		void loadItem();
		return () => controller.abort();
	}, [itemId, retryKey]);

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

			{loading ? (
				<p className="catalog-state" role="status">
					Chargement de la fiche…
				</p>
			) : error ? (
				<section className="detail-not-found" role="alert">
					<p className="section-index">FICHE EXERCICE</p>
					<h2>Fiche indisponible</h2>
					<p>{error}</p>
					<button
						className="detail-retry-button"
						type="button"
						onClick={() => setRetryKey((currentKey) => currentKey + 1)}
					>
						Réessayer
					</button>
					<Link className="detail-action-link" to="/">
						Retour au catalogue <span aria-hidden="true">→</span>
					</Link>
				</section>
			) : item ? (
				<article className="exercise-detail">
					<Link className="detail-back-link" to="/">
						<span aria-hidden="true">←</span> Retour au catalogue
					</Link>
					<div className="exercise-detail-layout">
						<figure className="exercise-detail-figure">
							{item.image_url ? (
								<img
									src={item.image_url}
									alt={`Illustration de l'exercice ${item.titre}`}
								/>
							) : (
								<div
									className="exercise-detail-image-placeholder"
									role="img"
									aria-label={`Image indisponible pour ${item.titre}`}
								>
									{item.categorie}
								</div>
							)}
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
								<div>
									<dt>Difficulté</dt>
									<dd>{item.difficulty}</dd>
								</div>
							</dl>
							<Link className="detail-action-link" to="/">
								Explorer les exercices <span aria-hidden="true">→</span>
							</Link>
						</div>
					</div>
				</article>
			) : null}
		</main>
	);
}

export default ItemDetail;
