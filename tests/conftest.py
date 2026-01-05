import openai
import pytest
from aiohttp import ClientSession
from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams


@pytest.fixture(scope="module")
def tokens():
    return [1, 2, 3, 4, 5]


@pytest.fixture(scope="function")
def db_client():
    client = QdrantClient(host="localhost", port=6333)
    client.create_collection(
        collection_name="test",
        vectors_config=VectorParams(size=4, distance=Distance.DOT),
    )
    client.upsert(
        collection_name="test",
        points=[
            PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"doc": "test.pdf"}),
            PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"doc": "test2.pdf"}),
            PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"doc": "test3.pdf"}),
        ],
    )
    yield client
    client.delete_collection(collection_name="test")
    client.close()


@pytest.fixture(scope="function")
async def async_db_client():
    client = AsyncQdrantClient(host="localhost", port=6333)
    await client.create_collection(
        collection_name="test",
        vectors_config=VectorParams(size=4, distance=Distance.DOT),
    )
    await client.upsert(
        collection_name="test",
        points=[
            PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"doc": "test.pdf"}),
        ],
    )
    yield client
    await client.delete_collection(collection_name="test")
    await client.close()


class LLMClient:
    def invoke(self, query):
        return openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": query}],
        )


@pytest.fixture
def llm_client():
    return LLMClient()


@pytest.fixture
async def test_client():
    async with ClientSession() as client:
        yield client
