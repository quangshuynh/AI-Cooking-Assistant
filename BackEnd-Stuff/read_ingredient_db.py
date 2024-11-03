import pandas as pd
import weaviate

df = pd.read_parquet("hf://datasets/foodvisor-nyu/labeled-food-ingredients/data/train-00000-of-00001.parquet")

unique_ingredients = df['ingredient'].unique().tolist()

client = weaviate.connect_to_local()

# Insert each unique ingredient into the Weaviate database
for index, row in df.iterrows():
    # Prepare properties for insertion
    properties = {
        "ingredient": row['ingredient'],
        "class": row['class'],
        "reason": row['reason'],
        "int_label": row['int_label'],
        "prompt": row['prompt']
    }

    # Insert into the Ingredient collection
    try:
        collection = client.collections.get("Ingredient")
        new_uuid = collection.data.insert(
            properties=properties
        )
        print(f"Inserted ingredient: {row['ingredient']} with UUID: {new_uuid}")

    finally:
        client.close()

"""
response = jeopardy.query.near_text(
    query="animals in movies",
    limit=2,
    return_metadata=MetadataQuery(distance=True)
)

for o in response.objects:
    print(o.properties)
    print(o.metadata.distance)
"""
# TODO: everything
