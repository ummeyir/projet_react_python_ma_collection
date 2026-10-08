import type { Item } from "../types/api";
import { Link, useNavigate } from "react-router-dom";

interface ItemCardProps {
	item: Item;
	returnTo: string;
}

function ItemCard({ item, returnTo }: ItemCardProps) {
	const navigate = useNavigate();

	return (
		<Link
			className="item-card"
			to={`/items/${item.id}`}
			state={{ from: returnTo }}
			onClick={(event) => {
				event.preventDefault();
				navigate(`/items/${item.id}`, {
					state: { from: returnTo, scrollY: window.scrollY },
				});
			}}
			aria-label={`Voir la fiche de ${item.name}`}
		>
			{item.image_url ? (
				<img
					className="item-card-image"
					src={item.image_url}
					alt={`Illustration de l'exercice ${item.name}`}
					loading="lazy"
				/>
			) : (
				<div
					className="item-card-image item-card-image-placeholder"
					role="img"
					aria-label={`Image indisponible pour ${item.name}`}
				>
					<span>{item.category}</span>
				</div>
			)}
			<div className="item-card-content">
				<p className="item-card-category">{item.category}</p>
				<h3>{item.name}</h3>
				<p className="item-card-description">{item.description}</p>
				<dl className="item-card-details">
					<div>
						<dt>Muscles</dt>
						<dd>{item.muscle_group}</dd>
					</div>
					<div>
						<dt>Matériel</dt>
						<dd>{item.equipment}</dd>
					</div>
					<div>
						<dt>Difficulté</dt>
						<dd>{item.difficulty}</dd>
					</div>
				</dl>
				<div className="item-card-link">
					Voir la fiche
					<span aria-hidden="true">→</span>
				</div>
			</div>
		</Link>
	);
}

export default ItemCard;
