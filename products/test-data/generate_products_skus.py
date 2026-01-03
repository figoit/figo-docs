import json
import random
import uuid
from datetime import datetime, timezone

# --- 1. CONFIGURAÇÃO ---
# Quantidade de "conceitos" de produto a serem gerados (ex: "Camiseta Nike").
# O número final de documentos será maior, pois cada conceito pode ter várias cores.
TOTAL_PRODUCT_CONCEPTS = 20000

# Quantas marcas e tipos de produto devem ser sorteados dos pools de dados abaixo.
NUM_PRODUCT_TYPES_TO_USE = 13
NUM_BRANDS_TO_USE = 17


# --- 2. POOLS DE DADOS ---
BRANDS = [
    {"id": "1", "name": "Xinguilingui"},
    {"id": "2", "name": "Nike"},
    {"id": "3", "name": "Adidas"},
    {"id": "4", "name": "Vestem"},
    {"id": "5", "name": "Puma"},
    {"id": "6", "name": "Reserva"},
    {"id": "7", "name": "Hering"},
    {"id": "8", "name": "Zara"},
    {"id": "9", "name": "Lacoste"},
    {"id": "10", "name": "Levi's"},
    {"id": "11", "name": "Piticas"},
    {"id": "12", "name": "Calvin Klein"},
    {"id": "13", "name": "Louis Vuitton"},
    {"id": "14", "name": "Hugo Boss"},
    {"id": "15", "name": "Emporio Armani"},
    {"id": "16", "name": "Michael Kros"},
    {"id": "17", "name": "Tommy Hilfiger"},
]

# Tipos de produtos com materiais associados para o campo 'specifications'
PRODUCT_TYPES = {
    "Camiseta": ["Algodão", "Poliéster", "Malha Fria"],
    "Calça": ["Jeans", "Sarja", "Moletom"],
    "Blusa": ["Seda", "Viscose", "Crepe", "Corta Vento"],
    "Saia": ["Couro Sintético", "Tafetá", "Linho"],
    "Vestido": ["Viscolycra", "Canelado", "Renda"],
    "Cueca": ["Microfibra", "Modal", "Algodão Pima"],
    "Calcinha": ["Renda", "Lycra", "Cotton", "Sexy"],
    "Jaqueta": ["Nylon", "Couro", "Jeans"],
    "Meia": ["Lã", "Poli-algodão", "Acrílico"],
    "Bermuda": ["Tactel", "Moletinho", "Sarja"],
    "Moletom": ["Fleece", "Algodão Mescla"],
    "Sapato": ["Couro", "Camurça"],
    "Tênis": ["Lona", "Material Sintético"]
}

MODELS = ['Basic', 'Daily', 'Slim', 'Regular', 'Comfort', 'Classic', 'Styled']
COLORS = ["Preto", "Branco", "Azul Marinho", "Cinza Mescla", "Vermelho", "Verde Musgo", "Amarelo", "Rosa", "Bege", "Rosa Choque"]
SIZES = ["PP", "P", "M", "G", "GG", "XG"]
SEGMENTS = [
    {"id": "seg-1", "name": "Moda", "slug": "moda"},
]
CATEGORIES = [
    {"id": "cat-1", "name": "Moda Casual", "slug": "moda-casual"},
    {"id": "cat-2", "name": "Moda Profissional", "slug": "moda-prof"},
    {"id": "cat-3", "name": "Moda Out-of-style", "slug": "moda-out-of-style"},
    {"id": "cat-4", "name": "Lançamentos", "slug": "moda-lancamentos"},
]

def generate_ean():
    """Gera um código EAN-13 numérico aleatório como string."""
    return ''.join([str(random.randint(0, 9)) for _ in range(13)])

def generate_product_document(product_id: str, base_name: str, brand: dict, product_type: str, material: str, model: str, color: str):
    """
    Gera um único documento do Elasticsearch para um produto com uma cor específica,
    contendo múltiplos SKUs para diferentes tamanhos.
    """
    now_iso = datetime.now(timezone.utc).isoformat()[:-6]
    # document_name = f"{base_name} Cor {color}"
    document_name = f"{base_name}"

    skus_for_document = []

    # Gera de 2 a todos os tamanhos disponíveis para esta cor
    num_sizes_for_color = random.randint(2, len(SIZES))
    sizes_to_generate = random.sample(SIZES, num_sizes_for_color)

    for size in sizes_to_generate:
        # Cada SKU tem seu próprio ID e EAN, mas compartilha o productId
        sku = {
            "id": str(uuid.uuid4()),
            "updatedAt": now_iso,
            "active": True,
            "code": f"{brand['name'][:3].upper()}-{product_type[:3].upper()}-{color[:3].upper()}-{size}",
            "ean": generate_ean(),
            "pricing": { # O schema indica que este preço está desabilitado (enabled: false)
                "updatedAt": now_iso,
                "priceFrom": 0.0,
                "salePrice": 0.0
            },
            "attributes": {
                "color": color,
                "size": size,
                "model": f"{model}",
                "voltage": None,
                "specifications": [
                    {
                        "key": "Material",
                        "value": material,
                        "type": "text",
                        "unit": None,
                        "displayOrder": 1
                    },
                    {
                        "key": "Origem",
                        "value": "Nacional",
                        "type": "text",
                        "unit": None,
                        "displayOrder": 2
                    }
                ]
            }
        }
        skus_for_document.append(sku)

    # Coleta todos os valores de atributos para o campo de busca
    skus_attributes_values = set()
    for s in skus_for_document:
        skus_attributes_values.add(s['attributes']['color'])
        skus_attributes_values.add(s['attributes']['size'])
        skus_attributes_values.add(s['attributes']['model'])
        for spec in s['attributes']['specifications']:
            skus_attributes_values.add(spec['value'])

    # --- Monta o documento final ---
    price_from = round(random.uniform(49.90, 499.90), 2)
    sale_value = round(price_from * random.uniform(0.7, 0.95), 2) if random.random() > 0.5 else price_from

    document = {
        "createdAt": now_iso,
        "updatedAt": now_iso,
        "active": True,
        "productId": product_id,
        "skuCode": [s['code'] for s in skus_for_document][0], # Usa o primeiro como referência
        "name": document_name,
        "keywords": f"{product_type} {brand['name']} {color}",
        "segments": [random.choice(SEGMENTS)],
        "brand": brand,
        "categories": [random.choice(CATEGORIES)],
        "price": {
            "updatedAt": now_iso,
            "promotionalValue": price_from,
            "saleValue": sale_value
        },
        "priceRange": f"{int(sale_value // 50) * 50}-{(int(sale_value // 50) + 1) * 50}",
        "images": {
            "small": "", "medium": "", "large": ""
        },
        "skus": skus_for_document,
    }

    return document

def main():
    """Função principal para gerar e salvar os dados dos produtos."""
    print("Iniciando a geração de massa de dados para produtos de moda...")

    # Seleciona um subconjunto aleatório de marcas e tipos de produtos para usar
    selected_brands = random.sample(BRANDS, min(NUM_BRANDS_TO_USE, len(BRANDS)))
    selected_product_types = random.sample(list(PRODUCT_TYPES.keys()), min(NUM_PRODUCT_TYPES_TO_USE, len(PRODUCT_TYPES)))

    all_products_data = []

    # Loop para criar "conceitos" de produto
    for i in range(TOTAL_PRODUCT_CONCEPTS):
        print(f"Gerando conceito de produto {i + 1}/{TOTAL_PRODUCT_CONCEPTS}...")

        # 1. Escolhe a base para o conceito do produto
        product_type = random.choice(selected_product_types)
        material = random.choice(PRODUCT_TYPES[product_type])
        model = random.choice(MODELS)
        brand = random.choice(selected_brands)
        base_name = f"{product_type} {model} {material}"
        # base_name = f"{product_type} {model} {material} {brand['name']}"

        # ID do produto é o mesmo para todas as variações de cor
        product_id = str(uuid.uuid4())

        # 2. Sorteia quantas cores este produto terá (1 a 3)
        num_colors = random.randint(1, 3)
        chosen_colors = random.sample(COLORS, num_colors)

        # 3. Gera um DOCUMENTO SEPARADO para cada cor
        for color in chosen_colors:
            product_doc = generate_product_document(product_id, base_name, brand, product_type, material, model, color)
            all_products_data.append(product_doc)

    output_filename = 'products-fashion-data.json'
    print(f"\nGerados {len(all_products_data)} documentos no total.")

    # Salva os dados em um arquivo JSON, um objeto por linha
    with open(output_filename, 'w', encoding='utf-8') as f:
        for doc in all_products_data:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')

    print(f"Massa de dados salva com sucesso no arquivo '{output_filename}'.")


if __name__ == "__main__":
    main()
