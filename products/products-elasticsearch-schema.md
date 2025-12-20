# Elasticsearch - Products Schema

Será criado dois indexes para a base de produtos no Elasticsearch: um para detalhes de produtos e outro para busca de produtos.

- **Index Principal de Produtos:** index com o mapeamento completo do produto e seus SKUs, visando buscas a partir dos identificadores do produto ou de seus SKUs.
- **Index de Busca de Produtos:** index com o mapeamento de SKUs visando a busca a partir das variações de produtos, cada produto pode gerar um ou mais documentos nesse index dependendo do segmento (agrupamento dos SKUs de acordo com o atributo segregador).

## Carga

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
- `skusAttributes`:
    - visa salvar todos os atributos dos SKUs
    - suportará pesquisas mais elaboradas dos SKUs com o custo de performance por ser um nested
    - deve ser utilizado caso o segmento precise de um filtro avançado
- `priceRange`:
    - visa suportar pesquisa por faixas de valor fixo (oferecido na maioria dos ecommerces)
    - podemos limitar as variações disponíveis e gerar menos impacto nas consultas
    - exemplo de valor: `0-100`, `100-500`, `500-1000`
- `price.saleValue`:
    - terá o valor do SKU agregador
    - suportará pesquisa de ranges de valor customizado (caso necessário) e ordenação do resultado pelo preço

