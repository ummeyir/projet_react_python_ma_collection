import { useEffect, useState, type FormEvent } from "react";
import { ApiError } from "../services/apiClient";
import { useCollection } from "../contexts/CollectionContext";
import type { CollectionEntry, CollectionStatus } from "../types/api";

interface CollectionEntryCardProps {
	entry: CollectionEntry;
}

const statusLabels: Record<CollectionStatus, string> = {
	a_decouvrir: "À découvrir",
	en_cours: "En cours",
	termine: "Terminé",
};

function CollectionEntryCard({ entry }: CollectionEntryCardProps) {
	const { updateEntry, removeEntry } = useCollection();
	const [status, setStatus] = useState<CollectionStatus>(entry.status);
	const [rating, setRating] = useState(entry.rating?.toString() ?? "");
	const [comment, setComment] = useState(entry.comment ?? "");
	const [error, setError] = useState<string | null>(null);
	const [isSaving, setIsSaving] = useState(false);
	const [isRemoving, setIsRemoving] = useState(false);

	useEffect(() => {
		setStatus(entry.status);
		setRating(entry.rating?.toString() ?? "");
		setComment(entry.comment ?? "");
	}, [entry.status, entry.rating, entry.comment]);

	async function saveEntry(event: FormEvent<HTMLFormElement>): Promise<void> {
		event.preventDefault();
		setError(null);
		setIsSaving(true);
		try {
			await updateEntry(entry.id, {
				status,
				rating: rating === "" ? null : Number(rating),
				comment: comment.trim() || null,
			});
		} catch (caughtError: unknown) {
			setError(
				caughtError instanceof ApiError
					? caughtError.message
					: "Impossible d'enregistrer cette entrée.",
			);
		} finally {
			setIsSaving(false);
		}
	}

	async function deleteEntry(): Promise<void> {
		setError(null);
		setIsRemoving(true);
		try {
			await removeEntry(entry.id);
		} catch (caughtError: unknown) {
			setError(
				caughtError instanceof ApiError
					? caughtError.message
					: "Impossible de supprimer cette entrée.",
			);
		} finally {
			setIsRemoving(false);
		}
	}

	return (
		<article className="collection-entry">
			<div className="collection-entry-heading">
				<div>
					<p className="item-card-category">{entry.item.category}</p>
					<h3>{entry.item.name}</h3>
				</div>
				<time dateTime={entry.added_at}>
					Ajouté le {new Date(entry.added_at).toLocaleDateString("fr-FR")}
				</time>
			</div>
			<p className="collection-entry-description">{entry.item.description}</p>
			<form className="collection-entry-form" onSubmit={saveEntry}>
				<label className="auth-field">
					<span>Statut</span>
					<select value={status} onChange={(event) => setStatus(event.target.value as CollectionStatus)}>
						{Object.entries(statusLabels).map(([value, label]) => (
							<option key={value} value={value}>
								{label}
							</option>
						))}
					</select>
				</label>
				<label className="auth-field">
					<span>Note</span>
					<select value={rating} onChange={(event) => setRating(event.target.value)}>
						<option value="">Sans note</option>
						{[1, 2, 3, 4, 5].map((value) => (
							<option key={value} value={value}>
								{value} / 5
							</option>
						))}
					</select>
				</label>
				<label className="auth-field collection-comment-field">
					<span>Commentaire</span>
					<textarea
						value={comment}
						onChange={(event) => setComment(event.target.value)}
						maxLength={2000}
						rows={3}
					/>
				</label>
				{error && <p className="auth-error" role="alert">{error}</p>}
				<div className="collection-entry-actions">
					<button className="auth-submit" type="submit" disabled={isSaving || isRemoving}>
						{isSaving ? "Enregistrement…" : "Enregistrer"}
					</button>
					<button
						className="collection-remove-button"
						type="button"
						disabled={isSaving || isRemoving}
						onClick={deleteEntry}
					>
						{isRemoving ? "Suppression…" : "Retirer de ma collection"}
					</button>
				</div>
			</form>
		</article>
	);
}

export default CollectionEntryCard;