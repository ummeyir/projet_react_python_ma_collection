import {
	createContext,
	useContext,
	useState,
	type PropsWithChildren,
} from "react";
import {
	addCollectionEntry,
	ApiError,
	removeCollectionEntry,
	updateCollectionEntry,
} from "../services/apiClient";
import type {
	CollectionEntry,
	CollectionSort,
	CollectionStatus,
	CreateCollectionEntryRequest,
	UpdateCollectionEntryRequest,
} from "../types/api";
import useCollectionEntries from "../hooks/useCollectionEntries.tsx";
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
	const [page, setPage] = useState(1);
	const [statusFilter, setStatusFilterState] = useState<CollectionStatus | "">("");
	const [sort, setSortState] = useState<CollectionSort>("date");
	const [reloadKey, setReloadKey] = useState(0);
	const { entries, total, loading, error } = useCollectionEntries({
		token,
		authLoading,
		statusFilter,
		sort,
		page,
		pageSize: PAGE_SIZE,
		reloadKey,
		setPage,
	});

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