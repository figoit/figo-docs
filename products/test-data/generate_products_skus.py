import json
import random
import string
from datetime import datetime, timezone

CHARACTERS = string.ascii_letters + string.digits


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
SIZES = ["XP", "PP", "P", "M", "G", "GG", "XG", "XXG"]
SEGMENTS = [
    {"id": "seg-1", "name": "Moda", "slug": "moda"},
]
CATEGORIES = [
    {"id": "cat-1", "name": "Moda Casual", "slug": "moda-casual"},
    {"id": "cat-2", "name": "Moda Profissional", "slug": "moda-prof"},
    {"id": "cat-3", "name": "Moda Out-of-style", "slug": "moda-out-of-style"},
    {"id": "cat-4", "name": "Lançamentos", "slug": "moda-lancamentos"},
]

def export_file(filename, rows):
    print(f"\nGerados {len(rows)} documentos no total.")

    # Salva os dados em um arquivo JSON, um objeto por linha
    with open(filename, 'w', encoding='utf-8') as f:
        for doc in rows:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')

    print(f"Massa de dados salva com sucesso no arquivo '{filename}'.")

def generate_id():
    """Gera um código alfanumérico aleatório como string."""
    return ''.join(random.choice(CHARACTERS) for _ in range(24))

def generate_ean():
    """Gera um código EAN-13 numérico aleatório como string."""
    return ''.join([str(random.randint(0, 9)) for _ in range(13)])

def generate_code():
    """Gera um código EAN-13 numérico aleatório como string."""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def generate_product(brand: dict, product_type: str):
    """
    Gera um único documento do Elasticsearch para um produto com uma cor específica,
    contendo múltiplos SKUs para diferentes tamanhos.
    """
    now_iso = datetime.now(timezone.utc).isoformat()[:-13]

    # 1. Escolhe a base para o conceito do produto
    material = random.choice(PRODUCT_TYPES[product_type])
    model = random.choice(MODELS)

    # 2. Sorteia quantas cores e tamanhos dos SKUs deste produto (1 a 3)
    num_colors = random.randint(1, 3)
    chosen_colors = random.sample(COLORS, num_colors)

    num_sizes_for_color = random.randint(1, 3)
    sizes_to_generate = random.sample(SIZES, num_sizes_for_color)

    # 3. Gera um SKU para cada cor e tamanho
    skus_for_document = []

    main_sku = True
    for color in chosen_colors:
        for size in sizes_to_generate:
            price_from = round(random.uniform(49.90, 499.90), 2)
            sale_price = round(price_from * random.uniform(0.7, 0.95), 2) if random.random() > 0.5 else price_from

            sku = {
                "id": generate_id(),
                "updatedAt": now_iso,
                "active": True,
                "code": f"{brand['name'][:3].upper()}-{product_type[:3].upper()}-{color[:3].upper()}-{size}-{generate_code()}",
                "ean": generate_ean(),
                "mainSku": main_sku,
                "pricing": {
                    "updatedAt": now_iso,
                    "priceFrom": price_from if price_from > sale_price else None,
                    "salePrice": sale_price
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
                            "key": "Cor",
                            "value": color,
                            "type": "text",
                            "unit": None,
                            "displayOrder": 2
                        },
                        {
                            "key": "Tamanho",
                            "value": size,
                            "type": "text",
                            "unit": None,
                            "displayOrder": 3
                        },
                        {
                            "key": "Modelo",
                            "value": model,
                            "type": "text",
                            "unit": None,
                            "displayOrder": 4
                        },
                        {
                            "key": "Origem",
                            "value": "Nacional",
                            "type": "text",
                            "unit": None,
                            "displayOrder": 5
                        }
                    ]
                },
                "images": [
                    {
                        "small": "/images/sku-tshirt-print-g-01-small.jpg",
                        "medium": "/images/sku-tshirt-print-g-01-medium.jpg",
                        "large": "/images/sku-tshirt-print-g-01-large.jpg",
                        "zoom": "/images/sku-tshirt-print-g-01-zoom.jpg",
                        "order": 1,
                        "main": True
                    }
                ]
            }
            skus_for_document.append(sku)
            main_sku = False

    product = {
        "id": generate_id(),
        "createdAt": now_iso,
        "updatedAt": now_iso,
        "active": True,
        "name": f"{product_type} {model} {material}",
        "description": f"{product_type} {model} {material} {brand['name']}",
        "keywords": f"{product_type} {model} {material} {brand['name']}".lower(),
        "segments": [random.choice(SEGMENTS)],
        "brand": brand,
        "categories": [random.choice(CATEGORIES)],
        "characteristics": {
            "Marca": brand['name'],
            "Modelo": model,
            "Tipo": product_type,
        },
        "technicalSpecifications": {
            "Origem": "Nacional",
            "Material": material,
        },
        "skus": skus_for_document,
    }

    return product

def generate_grouped_sku_from_product(product):
    # 1. Agrupa os SKUs pela cor
    skus_by_color = {}

    for sku in product['skus']:
        sku_color = sku['attributes']['color']

        if sku_color in skus_by_color:
            skus_by_color[sku_color].append(sku)
        else:
            skus_by_color[sku_color] = [sku]

    # 2. Cria os documentos para agrupar os SKUs por cor para o index de listagem de produtos
    splitted_products = []
    for color in skus_by_color:
        skus = skus_by_color[color]
        first_sku = skus[0]
        first_sku_pricing = first_sku['pricing']
        first_sku_sale_price = first_sku['pricing']['salePrice']

        document = {
            "productId": product['id'],
            "createdAt": product['createdAt'],
            "updatedAt": product['updatedAt'],
            "active": product['active'],
            "skuId": first_sku['id'], # campo apenas para a massa de dados para utilizar como ID do documento
            "skuCode": first_sku['code'],
            "name": product['name'],
            "keywords": product['keywords'],
            "segments": product['segments'],
            "brand": product['brand'],
            "categories": product['categories'],
            "pricing": first_sku_pricing,
            "priceRange": f"{int(first_sku_sale_price // 50) * 50}-{(int(first_sku_sale_price // 50) + 1) * 50}",
            "images": first_sku['images'][0],
            "skus": skus
        }

        splitted_products.append(document)

    return splitted_products

def generate_products_data():
    """ Gera a massa de produtos para os indexes de detalhes de produto e pesquisa de produtos. """
    print("Iniciando a geração de massa de dados para produtos de moda para os dois indexes...")

    # Seleciona um subconjunto aleatório de marcas e tipos de produtos para usar
    selected_brands = random.sample(BRANDS, min(NUM_BRANDS_TO_USE, len(BRANDS)))
    selected_product_types = random.sample(list(PRODUCT_TYPES.keys()), min(NUM_PRODUCT_TYPES_TO_USE, len(PRODUCT_TYPES)))

    all_products_data = []

    # Loop para criar "conceitos" de produto
    for i in range(TOTAL_PRODUCT_CONCEPTS):
        print(f"Gerando conceito de produto {i + 1}/{TOTAL_PRODUCT_CONCEPTS}...")

        # 1. Escolhe a base para o conceito do produto
        brand = random.choice(selected_brands)
        product_type = random.choice(selected_product_types)

        # 2. Gera o produto com seus SKUs
        product_doc = generate_product(brand, product_type)
        all_products_data.append(product_doc)

    # 3. Exporta os produtos gerados
    export_file("products-details-index-fashion-data.json", all_products_data)

    # 4. Gera os documentos para o index de pesquisa de produtos (SKUs agrupados por cor)
    all_grouped_skus_data = []

    print("\nGerando massa dos SKUs agrupando por cor")
    for product in all_products_data:
        grouped_skus = generate_grouped_sku_from_product(product)
        for sku in grouped_skus:
            all_grouped_skus_data.append(sku)

    # 5. Exporta os SKUs agrupados
    export_file("products-search-index-fashion-data.json", all_grouped_skus_data)

def main():
    generate_products_data()

if __name__ == "__main__":
    main()
