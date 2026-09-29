import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

function ProtectedRoute() {
	const { isAuthenticated, isLoading } = useAuth();
	const location = useLocation();

	if (isLoading) {
		return (
			<main className="app-shell">
				<p className="catalog-state" role="status">
					Vérification de la session…
				</p>
			</main>
		);
	}

	if (!isAuthenticated) {
		return <Navigate to="/login" replace state={{ from: location.pathname }} />;
	}

	return <Outlet />;
}

export default ProtectedRoute;