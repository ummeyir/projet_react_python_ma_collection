import type { Item } from "../types/api";

interface ItemCardProps {
	item: Item;
}

function ItemCard({ item }: ItemCardProps) {
	return (
		<article className="item-card">
			<img
				className="item-card-image"
				src={item.image_url}
				alt={`Illustration de l'exercice ${item.titre}`}
				loading="lazy"
			/>
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
				</dl>
			</div>
		</article>
	);
}

export default ItemCard;
