import weaviate
import weaviate.classes.config as wvcc

client = weaviate.connect_to_local()

try:
    # Create the Ingredient collection with properties
    collection = client.collections.create(
        name="Ingredient",
        vectorizer_config=wvcc.Configure.Vectorizer.text2vec_transformers(),  # Use text2vec-cohere for vectorization
        properties=[
            wvcc.Property(name="ingredient", data_type=wvcc.DataType.TEXT),
            wvcc.Property(name="class", data_type=wvcc.DataType.TEXT),
            wvcc.Property(name="reason", data_type=wvcc.DataType.TEXT),
            wvcc.Property(name="int_label", data_type=wvcc.DataType.INT),
            wvcc.Property(name="prompt", data_type=wvcc.DataType.TEXT)
        ]
    )
    print("Collection 'Ingredient' created successfully!")

except weaviate.exceptions.UnexpectedStatusCodeException as e:
    print(f"Error creating collection: {e}")
finally:
    client.close()