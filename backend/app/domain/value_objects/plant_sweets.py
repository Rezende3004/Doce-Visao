"""Catálogo de doces de origem vegetal aceitos nas importações."""

PLANT_SWEETS = {
    "cocada branca": "Doces de Coco",
    "cocada queimada": "Doces de Coco",
    "doce sírio de amido": "Doces de Amido",
    "pau de mamão": "Doces de Frutas",
    "doce de mamão verde": "Doces de Frutas",
    "goiabada": "Doces de Frutas",
    "bananada": "Doces de Frutas",
    "doce de abóbora": "Doces de Vegetais",
    "paçoca de amendoim": "Doces de Oleaginosas",
    "pé de moleque": "Doces de Oleaginosas",
    "doce de caju": "Doces de Frutas",
    "doce de buriti": "Doces de Frutas",
}


def validate_plant_sweet(name: str, category: str) -> None:
    expected = PLANT_SWEETS.get(name.strip().casefold())
    if expected is None:
        raise ValueError(f"Produto fora do catálogo de doces vegetais: {name}")
    if category.strip().casefold() != expected.casefold():
        raise ValueError(f"Categoria de {name} deve ser '{expected}'")
