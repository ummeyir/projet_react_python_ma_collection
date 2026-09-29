import { useCallback, useState } from "react";

function useLocalStorage<T>(cle: string, valeurInitiale: T): [T, (valeur: T) => void] {
	const [valeur, setValeur] = useState<T>(() => {
		try {
			const valeurStockee = window.localStorage.getItem(cle);
			return valeurStockee === null
				? valeurInitiale
				: (JSON.parse(valeurStockee) as T);
		} catch {
			return valeurInitiale;
		}
	});

	const enregistrerValeur = useCallback(
		(nouvelleValeur: T): void => {
			setValeur(nouvelleValeur);
			try {
				if (nouvelleValeur === null) {
					window.localStorage.removeItem(cle);
				} else {
					window.localStorage.setItem(cle, JSON.stringify(nouvelleValeur));
				}
			} catch {
				return;
			}
		},
		[cle],
	);

	return [valeur, enregistrerValeur];
}

export default useLocalStorage;