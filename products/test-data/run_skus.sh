INDEX_NAME="marketplace-skus-fashion"

while IFS= read -r line; do
  id=$(echo "$line" | jq '.skuId' | sed 's/"//g')
  echo "\nInserindo $id"
  curl -X POST "localhost:9200/$INDEX_NAME/_doc/$id" -H 'Content-Type: application/json' -d"$line"
done < products-search-index-fashion-data.json
