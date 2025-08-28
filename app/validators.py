# app/validators.py
def _only_digits(s: str) -> str:
    return "".join(c for c in s if c.isdigit())

def validate_cpf(cpf: str) -> bool:
    cpf = _only_digits(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    # 1º dígito
    s = sum(int(cpf[i]) * (10 - i) for i in range(9))
    d1 = (s * 10) % 11
    d1 = 0 if d1 == 10 else d1
    # 2º dígito
    s = sum(int(cpf[i]) * (11 - i) for i in range(10))
    d2 = (s * 10) % 11
    d2 = 0 if d2 == 10 else d2
    return d1 == int(cpf[9]) and d2 == int(cpf[10])

def validate_cnpj(cnpj: str) -> bool:
    cnpj = _only_digits(cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    w1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    w2 = [6] + w1
    s1 = sum(int(d) * w for d, w in zip(cnpj[:12], w1))
    d1 = 11 - (s1 % 11)
    d1 = 0 if d1 >= 10 else d1
    s2 = sum(int(d) * w for d, w in zip(cnpj[:13], w2))
    d2 = 11 - (s2 % 11)
    d2 = 0 if d2 >= 10 else d2
    return d1 == int(cnpj[12]) and d2 == int(cnpj[13])

def validate_cpf_cnpj(value: str) -> bool:
    digits = _only_digits(value)
    if len(digits) == 11:
        return validate_cpf(digits)
    if len(digits) == 14:
        return validate_cnpj(digits)
    return False

def normalize_cpf_cnpj(value: str) -> str:
    """Mantém só dígitos para armazenar no banco."""
    return _only_digits(value)
