import pandas as pd
from weaviate_ingredients import IngredientDatabase

df = pd.read_parquet("hf://datasets/foodvisor-nyu/labeled-food-ingredients/data/train-00000-of-00001.parquet")

unique_ingredients = df['ingredient'].unique().tolist()

# Initialize the database
db = IngredientDatabase(schema_path="schema.yaml")

# Iterate over unique ingredients and add them to the database
for ingredient, class_, reason, int_label, prompt in zip(df['ingredient'], df['class'], df['reason'], df['int_label'], df['prompt']):
    ingredient_data = {
        "name": ingredient,
        "safety_class": class_,
        "reason": reason,
        "int_label": int_label,
        "prompt": prompt
    }

    db.add_ingredient(ingredient_data)

# Save the database
db.save()