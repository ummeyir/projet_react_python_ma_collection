interface CatalogPaginationProps {
	page: number;
	pageCount: number;
	onPageChange: (page: number) => void;
}

function CatalogPagination({ page, pageCount, onPageChange }: CatalogPaginationProps) {
	return (
		<nav className="catalog-pagination" aria-label="Pagination du catalogue">
			<button
				type="button"
				disabled={page === 1}
				onClick={() => onPageChange(page - 1)}
			>
				Précédent
			</button>
			<span>
				Page {page} sur {pageCount}
			</span>
			<button
				type="button"
				disabled={page === pageCount}
				onClick={() => onPageChange(page + 1)}
			>
				Suivant
			</button>
		</nav>
	);
}

export default CatalogPagination;