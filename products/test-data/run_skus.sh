INDEX_NAME="marketplace-skus-fashion"

while IFS= read -r line; do
  curl -X POST "localhost:9200/$INDEX_NAME/_doc" -H 'Content-Type: application/json' -d"$line"
done < skus.json
