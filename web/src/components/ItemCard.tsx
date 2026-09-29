import type { Item } from "../types/api";
import { Link } from "react-router-dom";

interface ItemCardProps {
	item: Item;
}

function ItemCard({ item }: ItemCardProps) {
	return (
		<article className="item-card">
			{item.image_url ? (
				<img
					className="item-card-image"
					src={item.image_url}
					alt={`Illustration de l'exercice ${item.titre}`}
					loading="lazy"
				/>
			) : (
				<div
					className="item-card-image item-card-image-placeholder"
					role="img"
					aria-label={`Image indisponible pour ${item.titre}`}
				>
					<span>{item.categorie}</span>
				</div>
			)}
			<div className="item-card-content">
				<p className="item-card-category">{item.categorie}</p>
				<h3>{item.titre}</h3>
				<p className="item-card-description">{item.description}</p>
				<dl className="item-card-details">
					<div>
						<dt>Muscles</dt>
						<dd>{item.groupe_musculaire}</dd>
					</div>
					<div>
						<dt>Matériel</dt>
						<dd>{item.equipement}</dd>
					</div>
					<div>
						<dt>Difficulté</dt>
						<dd>{item.difficulty}</dd>
					</div>
				</dl>
				<Link className="item-card-link" to={`/items/${item.id}`}>
					Voir la fiche
					<span aria-hidden="true">→</span>
				</Link>
			</div>
		</article>
	);
}

export default ItemCard;
