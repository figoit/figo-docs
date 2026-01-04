INDEX_NAME="marketplace-products"

while IFS= read -r line; do
  id=$(echo "$line" | jq '.id' | sed 's/"//g')
  echo "\nInserindo $id"
  curl -X POST "localhost:9200/$INDEX_NAME/_doc/$id" -H 'Content-Type: application/json' -d"$line"
done < products-details-index-fashion-data.json
