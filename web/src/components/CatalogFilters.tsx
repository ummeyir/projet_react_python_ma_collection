interface CatalogFiltersProps {
	search: string;
	category: string;
	categories: string[];
	onSearchChange: (value: string) => void;
	onCategoryChange: (value: string) => void;
}

function CatalogFilters({
	search,
	category,
	categories,
	onSearchChange,
	onCategoryChange,
}: CatalogFiltersProps) {
	return (
		<div className="catalog-controls">
			<label className="search-field">
				<span>Rechercher</span>
				<input
					type="search"
					value={search}
					onChange={(event) => onSearchChange(event.target.value)}
					placeholder="Ex. squat, pectoraux, haltères"
				/>
			</label>
			<label className="category-field">
				<span>Groupe musculaire</span>
				<select value={category} onChange={(event) => onCategoryChange(event.target.value)}>
					<option value="">Toutes les catégories</option>
					{categories.map((categoryName) => (
						<option key={categoryName} value={categoryName}>
							{categoryName}
						</option>
					))}
				</select>
			</label>
		</div>
	);
}

export default CatalogFilters;