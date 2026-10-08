import { Link } from "react-router-dom";
import type { Item } from "../types/api";

interface ExerciseDetailContentProps {
	item: Item;
	isAuthenticated: boolean;
	isAdding: boolean;
	isAdded: boolean;
	actionError: string | null;
	onAdd: () => void;
	returnTo: string;
	returnScrollY: number | null;
}

function ExerciseDetailContent({
	item,
	isAuthenticated,
	isAdding,
	isAdded,
	actionError,
	onAdd,
	returnTo,
	returnScrollY,
}: ExerciseDetailContentProps) {
	return (
		<article className="exercise-detail">
			<Link
				className="detail-back-link"
				to={returnTo}
				state={returnScrollY === null ? undefined : { scrollY: returnScrollY }}
			>
				<span aria-hidden="true">←</span> Retour au catalogue
			</Link>
			<div className="exercise-detail-layout">
				<figure className="exercise-detail-figure">
					{item.image_url ? (
						<img
							src={item.image_url}
							alt={`Illustration de l'exercice ${item.name}`}
						/>
					) : (
						<div
							className="exercise-detail-image-placeholder"
							role="img"
							aria-label={`Image indisponible pour ${item.name}`}
						>
							{item.category}
						</div>
					)}
					<figcaption>{item.category}</figcaption>
				</figure>
				<div className="exercise-detail-copy">
					<p className="item-card-category">{item.category}</p>
					<h2>{item.name}</h2>
					<p className="exercise-detail-description">{item.description}</p>
					<dl className="exercise-detail-facts">
						<div>
							<dt>Groupe musculaire</dt>
							<dd>{item.muscle_group}</dd>
						</div>
						<div>
							<dt>Équipement</dt>
							<dd>{item.equipment}</dd>
						</div>
						<div>
							<dt>Difficulté</dt>
							<dd>{item.difficulty}</dd>
						</div>
					</dl>
					{isAuthenticated ? (
						<button
							className="detail-action-link detail-add-button"
							type="button"
							disabled={isAdding || isAdded}
							onClick={onAdd}
						>
							{isAdded ? "Ajouté à ta collection" : isAdding ? "Ajout…" : "Ajouter à ma collection"}
						</button>
					) : (
						<Link
							className="detail-action-link"
							to="/login"
							state={{ from: `/items/${item.id}` }}
						>
							Se connecter pour ajouter <span aria-hidden="true">→</span>
						</Link>
					)}
					{actionError && <p className="auth-error" role="alert">{actionError}</p>}
				</div>
			</div>
		</article>
	);
}

export default ExerciseDetailContent;