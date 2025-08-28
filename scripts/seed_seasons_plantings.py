# scripts/seed_seasons_plantings.py
import argparse
import os
import random
from typing import Iterable, List, Dict

import httpx

CULTURES = [
    "Soja", "Milho", "Café", "Algodão", "Trigo", "Cana-de-açúcar", "Arroz", "Feijão",
    "Girassol", "Sorgo"
]

def ensure_season(base_url: str, name: str) -> Dict:
    url = base_url.rstrip("/") + "/api/seasons"
    with httpx.Client(timeout=10.0) as client:
        r = client.post(url, json={"name": name})
        r.raise_for_status()
        return r.json()

def list_seasons(base_url: str) -> List[Dict]:
    url = base_url.rstrip("/") + "/api/seasons"
    with httpx.Client(timeout=10.0) as client:
        return client.get(url).json()

def list_farms(base_url: str) -> List[Dict]:
    url = base_url.rstrip("/") + "/api/farms"
    with httpx.Client(timeout=10.0) as client:
        return client.get(url).json()

def create_planting(base_url: str, payload: Dict) -> bool:
    url = base_url.rstrip("/") + "/api/plantings"
    with httpx.Client(timeout=10.0) as client:
        r = client.post(url, json=payload)
        if r.status_code == 201:
            return True
        # 400 quando já existe (unicidade)
        print(f"⚠ erro ao criar plantio: {r.status_code} {r.text}")
        return False

def seasons_from_years(years: Iterable[int]) -> list[str]:
    return [f"Safra {y}" for y in years]

def main(year_start: int, year_end: int, min_cult: int, max_cult: int, base_url: str, seed: int | None):
    if seed is not None:
        random.seed(seed)

    # garante saf ras
    names = seasons_from_years(range(year_start, year_end + 1))
    created = []
    for n in names:
        created.append(ensure_season(base_url, n))
    print(f"✔ Safras garantidas: {[s['name'] for s in created]}")

    # busca IDs úteis
    seasons = list_seasons(base_url)
    farms = list_farms(base_url)
    if not farms:
        print("⚠ Nenhuma fazenda encontrada. Rode o seed de fazendas primeiro.")
        return

    # mapeia nome -> id
    season_id_by_name = {s["name"]: s["id"] for s in seasons}

    total_plantings = 0
    for farm in farms:
        farm_id = farm["id"]
        # escolhe aleatoriamente algumas safras para essa fazenda
        chosen_seasons = random.sample(names, k=random.randint(1, len(names)))
        for sname in chosen_seasons:
            season_id = season_id_by_name[sname]
            # escolhe culturas (1..N), sem repetição
            n_c = random.randint(min_cult, max_cult)
            for culture in random.sample(CULTURES, k=min(n_c, len(CULTURES))):
                payload = {"farm_id": farm_id, "season_id": season_id, "culture": culture}
                ok = create_planting(base_url, payload)
                if ok:
                    total_plantings += 1
                    print(f"✔ Fazenda {farm_id} - {sname} -> {culture}")

    print(f"\nResumo: {total_plantings} plantios criados.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed de Safras e Plantios via API")
    parser.add_argument("--year-start", type=int, default=2021, help="ano inicial (default: 2021)")
    parser.add_argument("--year-end", type=int, default=2025, help="ano final (default: 2025)")
    parser.add_argument("--min-cult", type=int, default=1, help="mínimo de culturas por fazenda/safra (default: 1)")
    parser.add_argument("--max-cult", type=int, default=3, help="máximo de culturas por fazenda/safra (default: 3)")
    parser.add_argument("--base-url", type=str, default=os.getenv("SEED_BASE_URL", "http://localhost:8000"),
                        help="URL base da API (default: http://localhost:8000)")
    parser.add_argument("--seed", type=int, default=None, help="seed para repetibilidade (opcional)")
    args = parser.parse_args()
    main(args.year_start, args.year_end, args.min_cult, args.max_cult, args.base_url, args.seed)
