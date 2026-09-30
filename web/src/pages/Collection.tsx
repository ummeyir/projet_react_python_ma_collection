import { Link } from "react-router-dom";
import CollectionEntryCard from "../components/CollectionEntryCard.tsx";
import { useCollection } from "../contexts/CollectionContext";
import type { CollectionStatus } from "../types/api";

const statusOptions: { value: CollectionStatus; label: string }[] = [
	{ value: "a_decouvrir", label: "À découvrir" },
	{ value: "en_cours", label: "En cours" },
	{ value: "termine", label: "Terminé" },
];

function Collection() {
	const {
		entries,
		total,
		page,
		pageCount,
		statusFilter,
		sort,
		setStatusFilter,
		setSort,
		setPage,
		loading,
		error,
		refresh,
	} = useCollection();

	return (
		<main className="app-shell private-page">
			<header className="page-header">
				<div className="page-brand">
					<p className="eyebrow">ESPACE PERSONNEL</p>
					<h1>Ma collection</h1>
				</div>
				<nav className="auth-nav" aria-label="Navigation privée">
					<Link className="auth-nav-link" to="/">Catalogue</Link>
					<Link className="auth-nav-link" to="/stats">Statistiques</Link>
				</nav>
			</header>

			<section className="collection-page" aria-labelledby="collection-heading">
				<div className="private-heading">
					<div>
						<p className="section-index">SUIVI PERSONNEL</p>
						<h2 id="collection-heading">Mes exercices</h2>
					</div>
					<p className="catalog-count" aria-live="polite">
						<strong>{total.toString().padStart(2, "0")}</strong>
						<span>entrées</span>
					</p>
				</div>

				<div className="collection-filters">
					<label className="auth-field">
						<span>Filtrer par statut</span>
						<select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as CollectionStatus | "")}>
							<option value="">Tous les statuts</option>
							{statusOptions.map((option) => (
								<option key={option.value} value={option.value}>{option.label}</option>
							))}
						</select>
					</label>
					<label className="auth-field">
						<span>Trier par</span>
						<select value={sort} onChange={(event) => setSort(event.target.value as "date" | "rating")}>
							<option value="date">Date d'ajout</option>
							<option value="rating">Note</option>
						</select>
					</label>
				</div>

				{loading ? (
					<p className="catalog-state" role="status">Chargement de ta collection…</p>
				) : error ? (
					<div className="catalog-error" role="alert">
						<p>{error}</p>
						<button type="button" onClick={refresh}>Réessayer</button>
					</div>
				) : entries.length > 0 ? (
					<div className="collection-list">
						{entries.map((entry) => <CollectionEntryCard key={entry.id} entry={entry} />)}
					</div>
				) : (
					<div className="collection-empty-state" role="status">
						<h3>Ta collection est vide</h3>
						<p>Ajoute un exercice depuis le catalogue pour commencer ton suivi.</p>
						<Link className="auth-submit auth-submit-link" to="/">Parcourir les exercices</Link>
					</div>
				)}

				{!loading && !error && pageCount > 1 && (
					<nav className="catalog-pagination" aria-label="Pagination de la collection">
						<button type="button" disabled={page === 1} onClick={() => setPage(page - 1)}>
							Précédent
						</button>
						<span>Page {page} sur {pageCount}</span>
						<button type="button" disabled={page === pageCount} onClick={() => setPage(page + 1)}>
							Suivant
						</button>
					</nav>
				)}
			</section>
		</main>
	);
}

export default Collection;