import { useEffect, useState, type Dispatch, type SetStateAction } from "react";
import { ApiError, getCollection } from "../services/apiClient";
import type { CollectionQueryParams, CollectionSort, CollectionStatus, CollectionEntry } from "../types/api";

interface UseCollectionEntriesOptions {
	token: string | null;
	authLoading: boolean;
	statusFilter: CollectionStatus | "";
	sort: CollectionSort;
	page: number;
	pageSize: number;
	reloadKey: number;
	setPage: Dispatch<SetStateAction<number>>;
}

interface CollectionEntriesState {
	entries: CollectionEntry[];
	total: number;
	loading: boolean;
	error: string | null;
}

function useCollectionEntries({
	token,
	authLoading,
	statusFilter,
	sort,
	page,
	pageSize,
	reloadKey,
	setPage,
}: UseCollectionEntriesOptions): CollectionEntriesState {
	const [entries, setEntries] = useState<CollectionEntry[]>([]);
	const [total, setTotal] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		const controller = new AbortController();
		if (authLoading) {
			setLoading(true);
			return () => controller.abort();
		}
		if (!token) {
			setEntries([]);
			setTotal(0);
			setError(null);
			setLoading(false);
			return () => controller.abort();
		}

		const accessToken = token;
		const parameters: CollectionQueryParams = {
			status: statusFilter || undefined,
			sort,
			page,
			size: pageSize,
		};

		async function loadCollection(): Promise<void> {
			setLoading(true);
			setError(null);
			try {
				const response = await getCollection(accessToken, parameters, controller.signal);
				setEntries(response.items);
				setTotal(response.total);
				const lastPage = Math.max(1, Math.ceil(response.total / pageSize));
				if (page > lastPage) setPage(lastPage);
			} catch (caughtError: unknown) {
				if (controller.signal.aborted) return;
				setEntries([]);
				setTotal(0);
				setError(
					caughtError instanceof ApiError
						? caughtError.message
						: "Impossible de charger ta collection. Réessaie plus tard.",
				);
			} finally {
				if (!controller.signal.aborted) setLoading(false);
			}
		}

		void loadCollection();
		return () => controller.abort();
	}, [token, authLoading, statusFilter, sort, page, pageSize, reloadKey, setPage]);

	return { entries, total, loading, error };
}

export default useCollectionEntries;