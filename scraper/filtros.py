import re
import unicodedata

# Termos de busca usados um a um contra a tool `pesquisar_concursos` do PCI MCP.
PALAVRAS_TI = [
    "tecnologia da informação",
    "analista de sistemas",
    "analista de ti",
    "desenvolvedor",
    "programador",
    "técnico em informática",
    "suporte técnico",
    "técnico em redes",
    "banco de dados",
    "segurança da informação",
    "ciência da computação",
    "sistemas de informação",
    "analista de redes",
    "webdesigner",
]

# Termos que, presentes no texto (word-boundary), confirmam relevância de TI.
# Usados para reconfirmar itens cujo cargo específico pode não bater com o termo de busca.
_TERMOS_TI_REGEX = re.compile(
    r"\b(ti|tecnologia da informacao|informatica|analista de sistemas|"
    r"analista de ti|desenvolvedor|programador|tecnico em informatica|"
    r"suporte tecnico|tecnico em redes|banco de dados|dba|"
    r"seguranca da informacao|ciencia da computacao|sistemas de informacao|"
    r"analista de redes|webdesigner|web designer)\b",
    re.IGNORECASE,
)

_TERMOS_RECIFE = ["recife", "grande recife", "regiao metropolitana do recife", "rmr"]

_TERMOS_NIVEL_MEDIO_TECNICO = ["medio", "tecnico"]

_TERMOS_ACEITA_CURSANDO = ["cursando", "em curso", "estudante", "matriculado"]


def _normalizar(texto: str) -> str:
    if not texto:
        return ""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sem_acento.lower()


def eh_relevante_ti(cargos: list[str], titulo: str) -> bool:
    texto = _normalizar(" ".join(cargos) + " " + (titulo or ""))
    return bool(_TERMOS_TI_REGEX.search(texto))


def detectar_localizacao(item: dict, veio_de_busca_cidade: bool) -> str:
    if veio_de_busca_cidade:
        return "recife_confirmado"

    uf = (item.get("uf") or "").upper()
    if uf != "PE":
        return "fora_de_escopo"

    texto = _normalizar(item.get("titulo", "") + " " + item.get("cargos_resumo", ""))
    if any(termo in texto for termo in _TERMOS_RECIFE):
        return "recife_confirmado"

    return "recife_verificar"


def detectar_escolaridade(formacao: str, cargos: list[str], titulo: str) -> str:
    formacao_norm = _normalizar(formacao or "")

    if any(termo in formacao_norm for termo in _TERMOS_NIVEL_MEDIO_TECNICO):
        return "medio_tecnico"

    if "superior" in formacao_norm:
        texto = _normalizar(" ".join(cargos) + " " + (titulo or ""))
        if any(termo in texto for termo in _TERMOS_ACEITA_CURSANDO):
            return "superior_cursando_ok"
        return "excluir"

    return "excluir"
