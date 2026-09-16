from dataclasses import dataclass, asdict


@dataclass
class Concurso:
    id: int
    cargo: str
    orgao: str
    data_limite: str | None
    dias_restantes: int | None
    localizacao: str  # recife_confirmado | recife_verificar
    escolaridade: str  # medio_tecnico | superior_cursando_ok
    fonte: str
    link: str
    titulo_bruto: str
    vagas_salario: str | None
    formacao_bruta: str | None
    primeira_vez_visto_em: str
    ultima_vez_visto_em: str

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Concurso":
        return Concurso(**d)
