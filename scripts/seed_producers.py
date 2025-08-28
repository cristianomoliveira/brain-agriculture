# scripts/seed_producers.py
import argparse
import os
import random
import httpx
from faker import Faker

fake = Faker("pt_BR")

def gen_valid_cpf() -> str:
    # Gera CPF válido (só dígitos)
    nums = [random.randint(0, 9) for _ in range(9)]
    # 1º dígito
    s = sum(nums[i] * (10 - i) for i in range(9))
    d1 = (s * 10) % 11
    d1 = 0 if d1 == 10 else d1
    # 2º dígito
    nums10 = nums + [d1]
    s = sum(nums10[i] * (11 - i) for i in range(10))
    d2 = (s * 10) % 11
    d2 = 0 if d2 == 10 else d2
    cpf = "".join(str(d) for d in nums + [d1, d2])
    # Evitar CPFs com todos dígitos iguais (não geramos, mas por segurança)
    if len(set(cpf)) == 1:
        return gen_valid_cpf()
    return cpf

def main(n: int, base_url: str):
    url = base_url.rstrip("/") + "/api/producers"
    created = 0
    with httpx.Client(timeout=10.0) as client:
        for _ in range(n):
            cpf = gen_valid_cpf()
            name = fake.name()
            r = client.post(url, json={"cpf_cnpj": cpf, "name": name})
            if r.status_code == 201:
                data = r.json()
                print(f"✔ criado: id={data['id']} cpf={data['cpf_cnpj']} name={data['name']}")
                created += 1
            elif r.status_code == 400 and "já cadastrado" in r.text:
                # em caso raro de colisão, tentar outro CPF
                cpf = gen_valid_cpf()
                r = client.post(url, json={"cpf_cnpj": cpf, "name": name})
                if r.status_code == 201:
                    data = r.json()
                    print(f"✔ criado: id={data['id']} cpf={data['cpf_cnpj']} name={data['name']}")
                    created += 1
                else:
                    print(f"⚠ falha após colisão: {r.status_code} {r.text}")
            else:
                print(f"⚠ erro: {r.status_code} {r.text}")
    print(f"\nResumo: {created}/{n} produtores criados.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed de produtores via API")
    parser.add_argument("--n", type=int, default=20, help="quantidade de produtores")
    parser.add_argument(
        "--base-url",
        type=str,
        default=os.getenv("SEED_BASE_URL", "http://localhost:8000"),
        help="URL base da API (default: http://localhost:8000)",
    )
    args = parser.parse_args()
    main(args.n, args.base_url)
