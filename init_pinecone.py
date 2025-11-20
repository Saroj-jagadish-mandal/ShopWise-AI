import pinecone
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key='')

# Create index
pc.create_index(
    name='amazon-products',
    dimension=1536,  # OpenAI embedding dimension
    metric='cosine',
    spec=ServerlessSpec(
        cloud='aws',
        region='us-east-1'
    )
)