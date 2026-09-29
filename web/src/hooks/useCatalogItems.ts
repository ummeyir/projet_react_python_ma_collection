import { useEffect, useState } from "react";
import { ApiError, getItems } from "../services/apiClient";
import type { Item, ParametresItems } from "../types/api";

interface CatalogItemsState {
	items: Item[];
	categories: string[];
	total: number;
	loading: boolean;
	error: string | null;
	retry: () => void;
}

function useCatalogItems(
	query: string,
	category: string,
	page: number,
	size: number,
): CatalogItemsState {
	const [items, setItems] = useState<Item[]>([]);
	const [categories, setCategories] = useState<string[]>([]);
	const [total, setTotal] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [retryKey, setRetryKey] = useState(0);

	useEffect(() => {
		const controller = new AbortController();
		const parameters: ParametresItems = {
			q: query.trim() || undefined,
			category: category || undefined,
			page,
			size,
		};

		async function loadItems(): Promise<void> {
			setLoading(true);
			setError(null);

			try {
				const response = await getItems(parameters, controller.signal);
				setItems(response.items);
				setCategories(response.categories);
				setTotal(response.total);
			} catch (caughtError: unknown) {
				if (controller.signal.aborted) {
					return;
				}

				setItems([]);
				setTotal(0);
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

		void loadItems();
		return () => controller.abort();
	}, [query, category, page, size, retryKey]);

	return {
		items,
		categories,
		total,
		loading,
		error,
		retry: () => setRetryKey((currentKey) => currentKey + 1),
	};
}

export default useCatalogItems;