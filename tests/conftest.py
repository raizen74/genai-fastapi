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
    client.delete_collection(collection_name="test")
    client.create_collection(
        collection_name="test",
        vectors_config=VectorParams(size=4, distance=Distance.DOT),
    )
    client.upsert(
        collection_name="test",
        points=[
            PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"doc": "test.pdf"}),
        ],
    )
    yield client
    client.close()


@pytest.fixture(scope="function")
async def async_db_client():
    client = AsyncQdrantClient(host="localhost", port=6333)
    await client.delete_collection(collection_name="test")
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
