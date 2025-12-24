INDEX_NAME="marketplace-products"

while IFS= read -r line; do
  curl -X POST "localhost:9200/$INDEX_NAME/_doc" -H 'Content-Type: application/json' -d"$line"
done < products.json
