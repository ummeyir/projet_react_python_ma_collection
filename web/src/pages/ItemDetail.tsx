import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, addCollectionEntry, getItem } from "../services/apiClient";
import { useAuth } from "../contexts/AuthContext";
import type { Item } from "../types/api";

function ItemDetail() {
	const { isAuthenticated, token } = useAuth();
	const { itemId } = useParams();
	const [item, setItem] = useState<Item | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [retryKey, setRetryKey] = useState(0);
	const [addedItemId, setAddedItemId] = useState<number | null>(null);
	const [actionError, setActionError] = useState<string | null>(null);
	const [isAdding, setIsAdding] = useState(false);

	async function addToCollection(item: Item): Promise<void> {
		if (!token) return;
		setActionError(null);
		setIsAdding(true);
		try {
			await addCollectionEntry(token, { item_id: item.id, status: "a_decouvrir" });
			setAddedItemId(item.id);
		} catch (caughtError: unknown) {
			setActionError(
				caughtError instanceof ApiError
					? caughtError.message
					: "Impossible d'ajouter cet exercice à ta collection.",
			);
		} finally {
			setIsAdding(false);
		}
	}

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
									alt={`Illustration de l'exercice ${item.name}`}
								/>
							) : (
								<div
									className="exercise-detail-image-placeholder"
									role="img"
									aria-label={`Image indisponible pour ${item.name}`}
								>
									{item.category}
								</div>
							)}
							<figcaption>{item.category}</figcaption>
						</figure>
						<div className="exercise-detail-copy">
							<p className="item-card-category">{item.category}</p>
							<h2>{item.name}</h2>
							<p className="exercise-detail-description">{item.description}</p>
							<dl className="exercise-detail-facts">
								<div>
									<dt>Groupe musculaire</dt>
									<dd>{item.muscle_group}</dd>
								</div>
								<div>
									<dt>Équipement</dt>
									<dd>{item.equipment}</dd>
								</div>
								<div>
									<dt>Difficulté</dt>
									<dd>{item.difficulty}</dd>
								</div>
							</dl>
							{isAuthenticated ? (
								<button
									className="detail-action-link detail-add-button"
									type="button"
									disabled={isAdding || addedItemId === item.id}
									onClick={() => addToCollection(item)}
								>
									{addedItemId === item.id
										? "Ajouté à ta collection"
										: isAdding
											? "Ajout…"
											: "Ajouter à ma collection"}
								</button>
							) : (
								<Link
									className="detail-action-link"
									to="/login"
									state={{ from: `/items/${item.id}` }}
								>
									Se connecter pour ajouter <span aria-hidden="true">→</span>
								</Link>
							)}
							{actionError && <p className="auth-error" role="alert">{actionError}</p>}
						</div>
					</div>
				</article>
			) : null}
		</main>
	);
}

export default ItemDetail;
