import { useState } from "react";
import ItemCard from "../components/ItemCard";
import useDebounce from "../hooks/useDebounce";
import { exercises } from "../data/exercises";

function Catalog() {
	const [search, setSearch] = useState("");
	const [category, setCategory] = useState("");
	const debouncedSearch = useDebounce(search);
	const normalizedSearch = debouncedSearch.trim().toLocaleLowerCase("fr");
	const categories = [...new Set(exercises.map((item) => item.categorie))].sort();
	const visibleExercises = exercises.filter((item) => {
		const searchableText = [
			item.titre,
			item.categorie,
			item.description,
			item.groupe_musculaire,
			item.equipement,
		]
			.join(" ")
			.toLocaleLowerCase("fr");

		return (
			searchableText.includes(normalizedSearch) &&
			(category === "" || item.categorie === category)
		);
	});

	return (
		<main className="app-shell">
			<header className="page-header">
				<p className="eyebrow">ENTRAÎNEMENT · CATALOGUE</p>
				<h1>Ma Collection</h1>
			</header>

			<section className="catalog" aria-labelledby="catalogue-heading">
				<div className="catalog-heading">
					<div>
						<p className="section-index">01 / MUSCULATION</p>
						<h2 id="catalogue-heading">Les exercices</h2>
					</div>
					<p className="catalog-count" aria-live="polite">
						<strong>{visibleExercises.length.toString().padStart(2, "0")}</strong>
						<span>exercices</span>
					</p>
				</div>

				<div className="catalog-controls">
					<label className="search-field">
						<span>Rechercher</span>
						<input
							type="search"
							value={search}
							onChange={(event) => setSearch(event.target.value)}
							placeholder="Ex. squat, pectoraux, haltères"
						/>
					</label>
					<label className="category-field">
						<span>Groupe musculaire</span>
						<select
							value={category}
							onChange={(event) => setCategory(event.target.value)}
						>
							<option value="">Toutes les catégories</option>
							{categories.map((categoryName) => (
								<option key={categoryName} value={categoryName}>
									{categoryName}
								</option>
							))}
						</select>
					</label>
				</div>

				{visibleExercises.length > 0 ? (
					<div className="exercise-grid">
						{visibleExercises.map((item) => (
							<ItemCard key={item.id} item={item} />
						))}
					</div>
				) : (
					<p className="empty-state" role="status">
						Aucun exercice ne correspond à cette recherche.
					</p>
				)}
			</section>
		</main>
	);
}

export default Catalog;
