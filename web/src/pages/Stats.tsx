import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { ApiError, getCollectionStats } from "../services/apiClient";
import type { CollectionStats } from "../types/api";

const statusLabels = {
	a_decouvrir: "À découvrir",
	en_cours: "En cours",
	termine: "Terminé",
} as const;

function Stats() {
	const { token } = useAuth();
	const [stats, setStats] = useState<CollectionStats | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [retryKey, setRetryKey] = useState(0);

	useEffect(() => {
		const controller = new AbortController();
		if (!token) {
			setLoading(false);
			setError("Connecte-toi pour consulter tes statistiques.");
			return () => controller.abort();
		}

		const accessToken = token;
		async function loadStats(): Promise<void> {
			setLoading(true);
			setError(null);
			try {
				setStats(await getCollectionStats(accessToken, controller.signal));
			} catch (caughtError: unknown) {
				if (controller.signal.aborted) return;
				setError(caughtError instanceof ApiError ? caughtError.message : "Impossible de charger les statistiques.");
			} finally {
				if (!controller.signal.aborted) setLoading(false);
			}
		}

		void loadStats();
		return () => controller.abort();
	}, [token, retryKey]);

	return (
		<main className="app-shell private-page">
			<header className="page-header">
				<div className="page-brand">
					<p className="eyebrow">ESPACE PERSONNEL</p>
					<h1>Statistiques</h1>
				</div>
				<nav className="auth-nav" aria-label="Navigation privée">
					<Link className="auth-nav-link" to="/collection">Ma collection</Link>
					<Link className="auth-nav-link" to="/">Catalogue</Link>
				</nav>
			</header>

			<section className="stats-page" aria-labelledby="stats-heading">
				<p className="section-index">VUE D'ENSEMBLE</p>
				<h2 id="stats-heading">Ta progression</h2>
				{loading ? (
					<p className="catalog-state" role="status">Chargement des statistiques…</p>
				) : error ? (
					<div className="catalog-error" role="alert">
						<p>{error}</p>
						<button type="button" onClick={() => setRetryKey((currentKey) => currentKey + 1)}>Réessayer</button>
					</div>
				) : stats ? (
					<>
						<dl className="stats-summary">
							<div><dt>Exercices dans ta collection</dt><dd>{stats.total}</dd></div>
							<div><dt>Note moyenne</dt><dd>{stats.average_rating?.toFixed(1) ?? "—"}</dd></div>
						</dl>
						<div className="stats-status-list">
							<h3>Répartition par statut</h3>
							{Object.entries(statusLabels).map(([status, label]) => (
								<div className="stats-status-row" key={status}>
									<span>{label}</span>
									<strong>{stats.by_status[status as keyof typeof statusLabels]}</strong>
								</div>
							))}
						</div>
					</>
				) : null}
			</section>
		</main>
	);
}

export default Stats;