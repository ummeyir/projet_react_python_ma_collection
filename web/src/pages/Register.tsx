import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { ApiError } from "../services/apiClient";
import { useAuth } from "../contexts/AuthContext";

function Register() {
	const { register } = useAuth();
	const [username, setUsername] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [isRegistered, setIsRegistered] = useState(false);

	async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
		event.preventDefault();
		setError(null);
		setIsSubmitting(true);

		try {
			await register({ username, email, password });
			setIsRegistered(true);
		} catch (caughtError: unknown) {
			setError(
				caughtError instanceof ApiError
					? caughtError.message
					: "Impossible de créer le compte. Vérifiez que l'API est démarrée.",
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

			<section className="auth-panel" aria-labelledby="register-heading">
				<p className="section-index">NOUVEAU COMPTE</p>
				<h2 id="register-heading">Inscription</h2>
				{isRegistered ? (
					<div className="auth-success" role="status">
						<p>Ton compte est créé. Tu peux maintenant te connecter.</p>
						<Link className="auth-submit auth-submit-link" to="/login">
							Continuer vers la connexion
					</Link>
					</div>
				) : (
					<>
						<p className="auth-intro">Crée ton compte pour commencer ta collection.</p>
						<form className="auth-form" onSubmit={handleSubmit}>
							<label className="auth-field" htmlFor="register-username">
								<span>Nom d'utilisateur</span>
								<input
									id="register-username"
									autoComplete="username"
									minLength={3}
									maxLength={50}
									pattern="[A-Za-z0-9_.-]+"
									value={username}
									onChange={(event) => setUsername(event.target.value)}
									required
								/>
							</label>
							<label className="auth-field" htmlFor="register-email">
								<span>Adresse e-mail</span>
								<input
									id="register-email"
									type="email"
									autoComplete="email"
									value={email}
									onChange={(event) => setEmail(event.target.value)}
									required
								/>
							</label>
							<label className="auth-field" htmlFor="register-password">
								<span>Mot de passe</span>
								<input
									id="register-password"
									type="password"
									autoComplete="new-password"
									minLength={8}
									maxLength={128}
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
								{isSubmitting ? "Création du compte…" : "Créer mon compte"}
							</button>
						</form>
						<p className="auth-footer">
							Déjà inscrit ? <Link to="/login">Se connecter</Link>
						</p>
					</>
				)}
			</section>
		</main>
	);
}

export default Register;
