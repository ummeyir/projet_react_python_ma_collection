import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import ExerciseDetailContent from "../components/ExerciseDetailContent";
import { ApiError, addCollectionEntry, getItem } from "../services/apiClient";
import { useAuth } from "../contexts/AuthContext";
import type { Item } from "../types/api";

function ItemDetail() {
	const { isAuthenticated, token } = useAuth();
	const { itemId } = useParams();
	const location = useLocation();
	const returnTo =
		typeof location.state?.from === "string" ? location.state.from : "/";
	const returnScrollY =
		typeof location.state?.scrollY === "number" ? location.state.scrollY : null;
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
					<Link className="detail-action-link" to={returnTo}>
						Retour au catalogue <span aria-hidden="true">→</span>
					</Link>
				</section>
			) : item ? (
				<ExerciseDetailContent
					item={item}
					isAuthenticated={isAuthenticated}
					isAdding={isAdding}
					isAdded={addedItemId === item.id}
					actionError={actionError}
					onAdd={() => addToCollection(item)}
					returnTo={returnTo}
					returnScrollY={returnScrollY}
				/>
			) : null}
		</main>
	);
}

export default ItemDetail;
