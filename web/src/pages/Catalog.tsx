import { useState } from "react";
import { Link } from "react-router-dom";
import CatalogFilters from "../components/CatalogFilters";
import CatalogPagination from "../components/CatalogPagination";
import ItemCard from "../components/ItemCard";
import { useAuth } from "../contexts/AuthContext";
import useDebounce from "../hooks/useDebounce";
import useCatalogItems from "../hooks/useCatalogItems";

const PAGE_SIZE = 12;

function Catalog() {
	const { isAuthenticated, user, logout } = useAuth();
	const [search, setSearch] = useState("");
	const [category, setCategory] = useState("");
	const [page, setPage] = useState(1);
	const debouncedSearch = useDebounce(search);
	const { items, categories, total, loading, error, retry } = useCatalogItems(
		debouncedSearch,
		category,
		page,
		PAGE_SIZE,
	);
	const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

	return (
		<main className="app-shell">
			<header className="page-header">
				<div className="page-brand">
					<p className="eyebrow">ENTRAÎNEMENT · CATALOGUE</p>
					<h1>Ma Collection</h1>
				</div>
				<nav className="auth-nav" aria-label="Compte utilisateur">
					{isAuthenticated ? (
						<>
							<Link className="auth-nav-link" to="/collection">
								Ma collection
							</Link>
							<Link className="auth-nav-link" to="/stats">
								Statistiques
							</Link>
							<span className="auth-user">{user?.email}</span>
							<button className="auth-nav-button" type="button" onClick={logout}>
								Se déconnecter
							</button>
						</>
					) : (
						<>
							<Link className="auth-nav-link" to="/login">
								Se connecter
							</Link>
							<Link className="auth-nav-link auth-nav-primary" to="/register">
								Créer un compte
							</Link>
						</>
					)}
				</nav>
			</header>

			<section className="catalog" aria-labelledby="catalogue-heading">
				<div className="catalog-heading">
					<div>
						<p className="section-index">01 / MUSCULATION</p>
						<h2 id="catalogue-heading">Les exercices</h2>
					</div>
					<p className="catalog-count" aria-live="polite">
						<strong>{total.toString().padStart(2, "0")}</strong>
						<span>exercices</span>
					</p>
				</div>

				<CatalogFilters
					search={search}
					category={category}
					categories={categories}
					onSearchChange={(value) => {
						setSearch(value);
						setPage(1);
					}}
					onCategoryChange={(value) => {
						setCategory(value);
						setPage(1);
					}}
				/>

				{loading ? (
					<p className="catalog-state" role="status">
						Chargement du catalogue…
					</p>
				) : error ? (
					<div className="catalog-error" role="alert">
						<p>{error}</p>
						<button type="button" onClick={retry}>
							Réessayer
						</button>
					</div>
				) : items.length > 0 ? (
					<div className="exercise-grid">
						{items.map((item) => (
							<ItemCard key={item.id} item={item} />
						))}
					</div>
				) : (
					<p className="empty-state" role="status">
						Aucun exercice ne correspond à ces filtres.
					</p>
				)}

				{!loading && !error && total > PAGE_SIZE && (
					<CatalogPagination
						page={page}
						pageCount={pageCount}
						onPageChange={setPage}
					/>
				)}
			</section>
		</main>
	);
}

export default Catalog;
