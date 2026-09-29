import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError } from "../services/apiClient";
import { useAuth } from "../contexts/AuthContext";

function Login() {
	const { login } = useAuth();
	const navigate = useNavigate();
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [isSubmitting, setIsSubmitting] = useState(false);

	async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
		event.preventDefault();
		setError(null);
		setIsSubmitting(true);

		try {
			await login({ email, password });
			navigate("/", { replace: true });
		} catch (caughtError: unknown) {
			setError(
				caughtError instanceof ApiError
					? caughtError.message
					: "Impossible de se connecter. Vérifiez que l'API est démarrée.",
			);
		} finally {
			setIsSubmitting(false);
		}
	}

	return (
		<main className="app-shell">
			<header className="page-header">
				<p className="eyebrow">ESPACE PERSONNEL</p>
				<h1>
					<Link className="brand-link" to="/">
						Ma Collection
					</Link>
				</h1>
			</header>

			<section className="auth-panel" aria-labelledby="login-heading">
				<p className="section-index">BON RETOUR</p>
				<h2 id="login-heading">Connexion</h2>
				<p className="auth-intro">Retrouve tes exercices et ta progression.</p>

				<form className="auth-form" onSubmit={handleSubmit}>
					<label className="auth-field" htmlFor="login-email">
						<span>Adresse e-mail</span>
						<input
							id="login-email"
							type="email"
							autoComplete="email"
							value={email}
							onChange={(event) => setEmail(event.target.value)}
							required
						/>
					</label>
					<label className="auth-field" htmlFor="login-password">
						<span>Mot de passe</span>
						<input
							id="login-password"
							type="password"
							autoComplete="current-password"
							value={password}
							onChange={(event) => setPassword(event.target.value)}
							required
						/>
					</label>
					{error && (
						<p className="auth-error" role="alert">
							{error}
						</p>
					)}
					<button className="auth-submit" type="submit" disabled={isSubmitting}>
						{isSubmitting ? "Connexion…" : "Se connecter"}
					</button>
				</form>

				<p className="auth-footer">
					Pas encore de compte ? <Link to="/register">Créer un compte</Link>
				</p>
			</section>
		</main>
	);
}

export default Login;
