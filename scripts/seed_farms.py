# scripts/seed_farms.py
import argparse
import os
import random
from typing import List, Dict

import httpx
from faker import Faker

fake = Faker("pt_BR")

UFS = [
    "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS",
    "MG","PA","PB","PR","PE","PI","RJ","RN","RO","RS","RR","SC","SE","SP","TO"
]

def gen_areas() -> tuple[float, float, float]:
    """
    Gera (area_total, area_agricultable, area_vegetation) em hectares
    garantindo area_agricultable + area_vegetation <= area_total.
    """
    total = round(random.uniform(50, 5000), 2)
    # proporções razoáveis
    p_agri = random.uniform(0.2, 0.9)
    p_veg  = random.uniform(0.05, 0.6)
    # se estourar, reduz vegetação para caber
    if p_agri + p_veg > 0.98:
        p_veg = max(0.0, 0.98 - p_agri)
    agri = round(total * p_agri, 2)
    veg  = round(total * p_veg, 2)
    # por segurança absoluta, se ainda passou, aparar veg
    if agri + veg > total:
        veg = round(max(0.0, total - agri), 2)
    return total, agri, veg

def random_farm_name() -> str:
    # nomes simples e legíveis para demonstração
    base = random.choice(["Fazenda", "Sítio", "Chácara", "Haras"])
    adjs = ["Azul", "Verde", "Boa Vista", "Santa Clara", "São José", "Nova Esperança", "Primavera", "Pitangueira"]
    return f"{base} {random.choice(adjs)}"

def fetch_producers(base_url: str) -> List[Dict]:
    url = base_url.rstrip("/") + "/api/producers"
    with httpx.Client(timeout=10.0) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.json()

def create_farm(base_url: str, payload: Dict) -> Dict | None:
    url = base_url.rstrip("/") + "/api/farms"
    with httpx.Client(timeout=10.0) as client:
        r = client.post(url, json=payload)
        if r.status_code == 201:
            return r.json()
        print(f"⚠ erro ao criar fazenda: {r.status_code} {r.text}")
        return None

def main(per_producer: int, base_url: str, seed: int | None):
    if seed is not None:
        random.seed(seed)

    producers = fetch_producers(base_url)
    if not producers:
        print("⚠ Nenhum produtor encontrado. Crie produtores primeiro (seed_producers.py).")
        return

    total_created = 0
    for p in producers:
        pid = p["id"]
        for i in range(per_producer):
            total, agri, veg = gen_areas()
            city = fake.city()
            state = random.choice(UFS)
            name = f"{random_farm_name()} {i+1}"

            payload = {
                "producer_id": pid,
                "name": name,
                "city": city,
                "state": state,
                "area_total": total,
                "area_agricultable": agri,
                "area_vegetation": veg,
            }
            created = create_farm(base_url, payload)
            if created:
                print(f"✔ Produtor {pid} -> Fazenda {created['id']} ({city}/{state}) "
                      f"[total={total} agri={agri} veg={veg}]")
                total_created += 1

    print(f"\nResumo: {total_created} fazendas criadas (per_producer={per_producer}, produtores={len(producers)}).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed de fazendas por produtor via API")
    parser.add_argument("--per-producer", type=int, default=2, help="quantidade de fazendas por produtor (default: 2)")
    parser.add_argument("--base-url", type=str, default=os.getenv("SEED_BASE_URL", "http://localhost:8000"),
                        help="URL base da API (default: http://localhost:8000)")
    parser.add_argument("--seed", type=int, default=None, help="seed para repetibilidade (opcional)")
    args = parser.parse_args()
    main(args.per_producer, args.base_url, args.seed)
