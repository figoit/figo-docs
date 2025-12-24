# Elasticsearch - Products Schema

Benchmarks utilizados:

- Vestem:
	- Não pesquisa pelo atributo, somente o nome do produto (ex.: nome escrito bege mas a cor no atributo é marrom)
	- Pesquisa: https://vestem.com/BPML473/
	- Variações de cores do produto:
		- Preta: https://vestem.com/blusa-manga-longa-moletom-maya-preto-bpml473.out.c0002-vestem/product/176011/?sku=1219743
		- Marrom: https://vestem.com/blusa-manga-longa-moletom-maya-bege-bpml473.out.c0040-vestem/product/176012/?sku=1219745
- Reserva:
	- Parece estar pesquisando pelo nome e pelos atributos (menor prioridade)
	- Pesquisa: https://www.usereserva.com/camisa%20ml%20pf%20oxford%20color?_q=camisa%20ml%20pf%20oxford%20color&map=ft
	- Variações:
		- https://www.usereserva.com/camisa-ml-pf-oxford-color0046781/p?skuId=119577
		- https://www.usereserva.com/camisa-ml-pf-oxford-color0046781/p?skuId=119570
		- https://www.usereserva.com/camisa-ml-pf-oxford-color0046781/p?skuId=119563

## Estratégia

Será criado dois indexes para a base de produtos no Elasticsearch: um para detalhes de produtos e outro para busca de produtos.

- Produto: pai e filho
- SKUs: agrupamentos de SKU pelo atributo segregador

Indexes:

- **Index Principal de Produtos:** index com o mapeamento completo do produto e seus SKUs, visando buscas a partir dos identificadores do produto ou de seus SKUs.
- **Index de Busca de Produtos:** index com o mapeamento de SKUs visando a busca a partir das variações de produtos, cada produto pode gerar um ou mais documentos nesse index dependendo do segmento (agrupamento dos SKUs de acordo com o atributo segregador).

### Carga

No processo de carga de produtos do marketplace será necessário alimentar o index principal de produtos com o mapeamento completo do produto e todos os indexes de busca de produtos dos segmentos em que o produto está vinculado.

Sendo assim, cada produto no processo de carga terá que atualizar pelo menos dois indexes: index principal de produto e index de busca de produto do seu segmento.

## Index Principal de Produtos

Index com a finalidade de ter todas as informações do produto e seus SKUs para ser utilizados no processo em que necessida do detalhamento completo do produto (ex.: página de produto, administração do produto).

Nesse index, a expectativa é que as consultas sejam realizado pelos identificadores do produo mas tem é disponibilizado campos auxiliares para buscar alguns atributos identificadores do SKU.

### Consultas para Suportar

Esse index foi montado visando suportar consultas pelos seguintes campos:

- ID produto
- nome
- keyword
- marca
- ID categoria
- ID segmento
- ID SKU
- código SKU
- EAN SKU

### Schema para Mapeamento do Index

[Schema do Index](./elasticsearch-products-index.schema.json)

O ID do documento no index será o ID do produto no banco de dados.

Descritivos de alguns campos:

- `categoriesIds`:
    - visa salvar os IDs da hierarquia de categorias que o produto está inserindo
    - suportará a busca pelo ID da categoria desejada
    - filtrar apenas o ID da categoria mais aninhada no filtro para encontrar os produtos de uma determinada classificação (departamento, categoria ou subcategoria)
- `segmentsIds`:
    - visa salvar os IDs dos segmentos em que o produto está vinculado
    - suportará a busca pelo ID do segmento desejado
- `skusIds`:
    - visa salvar os IDs dos SKUs
    - suportará a busca pelo ID do SKU
- `skusEans`:
    - visa salvar os EANs dos SKUs
    - suportará a busca por EAN
- `skusIdentifiers`:
    - visa salvar de forma concatenada os principais campos de busca do SKU
    - suportará pesquisa de diferentes campos do SKU

### Consultas

Busca pelo nome:

```json
{
	"query": {
		"match": {
			"name": "camiseta estampada"
		}
	}
}
```

Busca pelo código SKU:

```json
{
	"query": {
		"term": {
			"skusCodes": {
				"value": "URBAN-TS-PRINT-M-01"
			}
		}
	}
}
```

Busca pelo EAN:

```json
{
	"query": {
		"term": {
			"skusEans": {
				"value": "789000000001"
			}
		}
	}
}
```

Busca pelos identificadores (código SKU, EAN):

```json
{
	"query": {
		"term": {
			"skusIdentifiers": {
				"value": "789000000001"
			}
		}
	}
}
```

Busca pela marca:

```json
{
	"query": {
		"match": {
			"brand.name": "Moda Viva"
		}
	}
}
```

Busca pela categoria:

```json
{
	"query": {
		"term": {
			"categoriesIds": "vestuario"
		}
	}
}
```

Busca do marketplace (não utilizará esse index):

```json
{
	"query": {
		"multi_match": {
			"query": "camisa elegance URBAN-TS-PRINT-M-01",
			"fields": [
				"skusIdentifiers^3",
				"name^2",
				"brand.name"
			],
			"type": "most_fields"
		}
	}
}
```

Busca do marketplace com filtro obrigatório de segmento:

```json
{
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "camisa",
            "fields": [
              "skusIdentifiers^3", // maior peso
              "name^2", 
              "brand.name"
            ],
            "type": "most_fields"
          }
        }
      ],
      "filter": [
        {
          "term": {
            "segmentsIds": "moda-verao"
          }
        }
      ]
    }
  }
}
```

## Index de Busca de Produtos

Index com a finalidade de ter as informações e a estrutura necessária utilizada na busca de produtos do marketplace.

Esse index será modelado visando a listagem de produtos onde cada produto será um agrupamento dos SKUs de um mesmo produto divididos por um atributo segregador.
Ex.: moda cria um agrupamento de SKUs para cada variação de cor.

A expectativa é a que a busca seja realizado pelos seguintes campos:

- nome
- keyword
- marca
- ID categoria
- ID segmento
- código SKU
- EAN SKU
- atributos comuns do SKU (modelo, cor, tamanho, voltagem, etc)
- atributos dinâmicos do SKU de acordo com o segmento (linha, fabricação, estilista, etc)

Os casos de usos de pesquisas que o index busca suportar:

- pesquisa pelo nome do produto
- pesquisa pelo nome da marca
- pesquisa por um departamento ou categoria selecionado
- pesquisa pelo código do SKU
- pesquisa pelo EAN do SKU
- pesquisa pelos atributos do SKU
- pesquisa por intervalo de valor
- pesquisa pela combinação dos campos citados anteriormente

Os casos de usos de pesquisa que não serão suportadas:

- pesquisa por intervalo de valores nos atributos
- contagem de produtos por categoria

### Informações Utilizadas no Frontend

Informações de produtos utilizadas no frontend do cliente:

- Nome
- Descrição 
- Marca
- Sku
- Atributos (cor, tamanho, modelo)
- Preço
- Imagens

### Schema para Mapeamento do Index

O ID do documento no index será o ID do SKU agregador (SKU com o atributo segregador) no banco de dados.
Criar estratégia para garantir que um SKU agregador foi inativado e outro novo SKU virou o agregador, nesse cenário vai acabar tendo os dois SKUs agregadores no index.

[Schema do Index](./elasticsearch-skus-index.schema.json)

Descritivos de alguns campos:

- `skuCode`:
    - código do SKU com o atributo segregador utilizado no agrupamento
    - não será utilizado nas buscas, usar campo `skusCodes` quando precisar filtrar
    - facilitar a consulta no detalhes de produto (já cair com SKU selecionado)
- `categoriesIds`:
    - visa salvar os IDs da hierarquia de categorias que o produto está inserindo
    - suportará a busca pelo ID da categoria desejada
    - filtrar apenas o ID da categoria mais aninhada no filtro para encontrar os produtos de uma determinada classificação (departamento, categoria ou subcategoria)
- `segmentsIds`:
    - visa salvar os IDs dos segmentos em que o produto está vinculado
    - suportará a busca pelo ID do segmento desejado
- `skusIds`:
    - visa salvar os IDs dos SKUs
    - suportará a busca pelo ID do SKU
- `skusEans`:
    - visa salvar os EANs dos SKUs
    - suportará a busca por EAN
- `skusIdentifiers`:
    - visa salvar de forma concatenada os principais campos de busca do SKU
    - suportará pesquisa de diferentes campos do SKU
- `skusAttributesValues`:
    - visa salvar os valores dos atributos simples (modelo, cor, tamanho, voltagem) dos SKUs
    - suportará pesquisa de atributos onde o valor do atributo é fixo, sem muitas variações
    - formato para salvar no campo: `${chave_atributo}_${valor_atributo}`
- `priceRange`:
    - visa suportar pesquisa por faixas de valor fixo (oferecido na maioria dos ecommerces)
    - podemos limitar as variações disponíveis e gerar menos impacto nas consultas
    - exemplo de valor: `0-100`, `100-500`, `500-1000`
- `price.saleValue`:
    - terá o valor do SKU agregador
    - suportará pesquisa de ranges de valor customizado (caso necessário) e ordenação do resultado pelo preço

## Análise dos Indexes

#### Configurações (Settings)

- Analisador `pt_br_analyzer`: Foi configurado um analisador customizado para o português do Brasil.
    - Tokenizer `standard`: Divide o texto em palavras com base nas regras do Unicode.
    - Filtros:
    - lowercase: Converte todo o texto para minúsculas.
    - stemmer_plural_portugues: Utiliza um stemmer (radicalizador) para o português, o que permite que buscas por "sapato" também encontrem "sapatos".
    - asciifolding: Remove acentos e diacríticos (ex: maçã se torna maca), tornando a busca insensível a acentos.

Essa configuração é ideal para buscas de texto em português, pois normaliza os termos de busca e os dados indexados.

#### Mapeamentos (Mappings)

A estrutura dos documentos foi desenhada para otimizar tanto a busca por texto quanto a aplicação de filtros.

- Campos de Texto Buscáveis:
    - name: É o principal campo de busca, utilizando o pt_br_analyzer. Possui também um subcampo keyword para correspondências exatas, agregações e ordenação.
    - keywords: Um campo de texto para palavras-chave adicionais.

- Campos para Filtragem (Keywords):
    - brand.id, categoriesIds, segmentsIds, skusIds, skusCodes, skusEans, skusIdentifiers: São campos do tipo keyword, otimizados para filtros rápidos e exatos.

- Estratégia `copy_to`:
    - O schema utiliza a diretiva copy_to de forma inteligente para denormalizar dados. Por exemplo, o ID de cada categoria dentro do objeto categories é copiado para o campo categoriesIds no nível raiz do documento.
    - Vantagem: Isso permite filtrar produtos por ID de categoria (categoriesIds) de forma muito eficiente, sem a necessidade de realizar buscas em objetos aninhados, que são mais lentos. A mesma técnica é aplicada para segmentos e SKUs.

- Campos Desabilitados (`"enabled": false`):
    - description, categories, segments, characteristics, technicalSpecifications e a maior parte do objeto skus estão configurados com "enabled": false.
    - Impacto: O conteúdo desses campos é apenas armazenado, mas não é indexado e, portanto, não pode ser usado em buscas ou filtros. Isso é uma otimização para reduzir o tamanho do índice e acelerar a indexação, já que esses dados são ricos em detalhes, mas provavelmente só são necessários ao exibir o produto final, e não para encontrá-lo.

#### Resumo da Análise

1. Performance: O schema é otimizado para performance. A desabilitação de campos não essenciais para a busca e o uso de copy_to para criar campos de filtro denormalizados são excelentes práticas.
2. Busca em Português: A busca por nome do produto é robusta e adaptada ao idioma português, lidando com plural, acentos e caixa alta/baixa.
3. Intenção Clara: A estrutura do índice deixa clara a intenção:
    - Encontrar produtos: Principalmente pelo campo name.
    - Filtrar resultados: Por ID da marca, IDs de categorias/segmentos e identificadores dos SKUs (código, EAN).
    - Exibir detalhes: Os campos desabilitados são armazenados para que possam ser recuperados e exibidos na página de detalhes do produto, mesmo que não sejam pesquisáveis.
4. Observação: O campo segments é definido como "type": "nested" mas também está desabilitado. O tipo nested só tem efeito sobre dados indexados, portanto, nesse caso, ele se comporta como um campo object normal que não é indexado.

### Consultas

Busca pelo nome:

```json
{
	"query": {
		"match": {
			"name": "calça"
		}
	}
}
```

Busca pelo código SKU:

```json
{
	"query": {
		"term": {
			"skusCodes": {
				"value": "MJ-PRA-P"
			}
		}
	}
}
```

Busca pelo EAN:

```json
{
	"query": {
		"term": {
			"skusEans": {
				"value": "789000000001"
			}
		}
	}
}
```

Busca pelos identificadores (código SKU, EAN):

```json
{
	"query": {
		"term": {
			"skusIdentifiers": {
				"value": "789000000100"
			}
		}
	}
}
```

Busca pela marca:

```json
{
	"query": {
		"match": {
			"brand.name": "alta classe"
		}
	}
}
```

Busca pela categoria:

```json
{
	"query": {
		"term": {
			"categoriesIds": "cat-01-01"
		}
	}
}
```

Busca do marketplace com filtro obrigatório de segmento:

```json
{
	"query": {
		"bool": {
			"filter": [
				{
					"term": {
						"segmentsIds": {
							"value": "seg-01"
						}
					}
				}
			],
			"must": [
				{
					"multi_match": {
						"fields": [
							"skusIdentifiers^3",
							"name^2",
							"skusAttributesValues",
							"brand.name",
							"keywords"
						],
						"query": "blusa social G",
						"type": "most_fields"
					}
				}
			]
		}
	}
}
```
