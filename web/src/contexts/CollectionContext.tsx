import {
	createContext,
	useContext,
	useEffect,
	useState,
	type PropsWithChildren,
} from "react";
import {
	addCollectionEntry,
	ApiError,
	getCollection,
	removeCollectionEntry,
	updateCollectionEntry,
} from "../services/apiClient";
import type {
	CollectionEntry,
	CollectionQueryParams,
	CollectionSort,
	CollectionStatus,
	CreateCollectionEntryRequest,
	UpdateCollectionEntryRequest,
} from "../types/api";
import { useAuth } from "./AuthContext";

const PAGE_SIZE = 12;

interface CollectionContextValue {
	entries: CollectionEntry[];
	total: number;
	page: number;
	pageCount: number;
	statusFilter: CollectionStatus | "";
	sort: CollectionSort;
	loading: boolean;
	error: string | null;
	setStatusFilter: (status: CollectionStatus | "") => void;
	setSort: (sort: CollectionSort) => void;
	setPage: (page: number) => void;
	refresh: () => void;
	addEntry: (payload: CreateCollectionEntryRequest) => Promise<void>;
	updateEntry: (itemId: number, payload: UpdateCollectionEntryRequest) => Promise<void>;
	removeEntry: (itemId: number) => Promise<void>;
}

const CollectionContext = createContext<CollectionContextValue | null>(null);

function CollectionProvider({ children }: PropsWithChildren) {
	const { token, isLoading: authLoading } = useAuth();
	const [entries, setEntries] = useState<CollectionEntry[]>([]);
	const [total, setTotal] = useState(0);
	const [page, setPage] = useState(1);
	const [statusFilter, setStatusFilterState] = useState<CollectionStatus | "">("");
	const [sort, setSortState] = useState<CollectionSort>("date");
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [reloadKey, setReloadKey] = useState(0);

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
			size: PAGE_SIZE,
		};

		async function loadCollection(): Promise<void> {
			setLoading(true);
			setError(null);
			try {
				const response = await getCollection(accessToken, parameters, controller.signal);
				setEntries(response.items);
				setTotal(response.total);
				const lastPage = Math.max(1, Math.ceil(response.total / PAGE_SIZE));
				if (page > lastPage) {
					setPage(lastPage);
				}
			} catch (caughtError: unknown) {
				if (controller.signal.aborted) {
					return;
				}
				setEntries([]);
				setTotal(0);
				setError(
					caughtError instanceof ApiError
						? caughtError.message
						: "Impossible de charger ta collection. Réessaie plus tard.",
				);
			} finally {
				if (!controller.signal.aborted) {
					setLoading(false);
				}
			}
		}

		void loadCollection();
		return () => controller.abort();
	}, [token, authLoading, statusFilter, sort, page, reloadKey]);

	function changeStatusFilter(status: CollectionStatus | ""): void {
		setStatusFilterState(status);
		setPage(1);
	}

	function changeSort(nextSort: CollectionSort): void {
		setSortState(nextSort);
		setPage(1);
	}

	function refresh(): void {
		setReloadKey((currentKey) => currentKey + 1);
	}

	async function addEntry(payload: CreateCollectionEntryRequest): Promise<void> {
		if (!token) {
			throw new ApiError("Connecte-toi pour modifier ta collection.", 401);
		}
		await addCollectionEntry(token, payload);
		setPage(1);
		refresh();
	}

	async function updateEntry(
		itemId: number,
		payload: UpdateCollectionEntryRequest,
	): Promise<void> {
		if (!token) {
			throw new ApiError("Connecte-toi pour modifier ta collection.", 401);
		}
		await updateCollectionEntry(token, itemId, payload);
		refresh();
	}

	async function removeEntry(itemId: number): Promise<void> {
		if (!token) {
			throw new ApiError("Connecte-toi pour modifier ta collection.", 401);
		}
		await removeCollectionEntry(token, itemId);
		if (entries.length === 1 && page > 1) {
			setPage((currentPage) => currentPage - 1);
			return;
		}
		refresh();
	}

	return (
		<CollectionContext.Provider
			value={{
				entries,
				total,
				page,
				pageCount: Math.max(1, Math.ceil(total / PAGE_SIZE)),
				statusFilter,
				sort,
				loading,
				error,
				setStatusFilter: changeStatusFilter,
				setSort: changeSort,
				setPage,
				refresh,
				addEntry,
				updateEntry,
				removeEntry,
			}}
		>
			{children}
		</CollectionContext.Provider>
	);
}

function useCollection(): CollectionContextValue {
	const context = useContext(CollectionContext);
	if (context === null) {
		throw new Error("useCollection doit être utilisé dans CollectionProvider");
	}
	return context;
}

export { CollectionProvider, useCollection };