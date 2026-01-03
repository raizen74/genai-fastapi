import openai
import pytest


def chunk(tokens: list[int], chunk_size: int) -> list[list[int]]:
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than 0")
    return [tokens[i : i + chunk_size] for i in range(0, len(tokens), chunk_size)]


def test_token_chunking_small(tokens):
    result = chunk(tokens, chunk_size=2)
    assert result == [[1, 2], [3, 4], [5]]


def test_token_chunking_large(tokens):
    result = chunk(tokens, chunk_size=5)
    assert result == [[1, 2, 3, 4, 5]]


@pytest.mark.parametrize(
    "tokens, chunk_size, expected",
    [
        ([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),  # valid
        ([1, 2, 3, 4, 5], 3, [[1, 2, 3], [4, 5]]),  # valid
        ([1, 2, 3, 4, 5], 1, [[1], [2], [3], [4], [5]]),  # valid
        ([], 3, []),  # valid/empty input
        ([1, 2, 3], 5, [[1, 2, 3]]),  # boundary input
        ([1, 2, 3, 4, 5], 0, "ValueError"),  # invalid (chunk_size <= 0)
        ([1, 2, 3, 4, 5], -1, "ValueError"),  # invalid (chunk_size <= 0)
        (
            list(range(10000)),
            1000,
            [
                list(range(i, i + 1000))  # huge data
                for i in range(0, 10000, 1000)
            ],
        ),
    ],
)
def test_token_chunking(tokens, chunk_size, expected):
    if expected == "ValueError":
        with pytest.raises(ValueError):
            chunk(tokens, chunk_size)
    else:
        assert chunk(tokens, chunk_size) == expected


def test_query_points(db_client):
    result = db_client.query_points(
        collection_name="test",
        query=[0.18, 0.81, 0.75, 0.12],
        limit=1,
    )
    assert result is not None


@pytest.mark.asyncio
async def test_async_query_points(async_db_client: AsyncQdrantClient):
    result = await async_db_client.query_points(
        collection_name="test",
        query=[0.18, 0.81, 0.75, 0.12],
        limit=1,
    )
    assert result is not None


def calculate_recall(expected: list[int], retrieved: list[int]) -> int:
    true_positives = len(set(expected) & set(retrieved))
    return true_positives / len(expected)


def calculate_precision(expected: list[int], retrieved: list[int]) -> int:
    true_positives = len(set(expected) & set(retrieved))
    return true_positives / len(retrieved)


@pytest.mark.parametrize(
    "query_vector, expected_ids",
    [
        ([0.1, 0.2, 0.3, 0.4], [1, 2, 3]),
        ([0.2, 0.3, 0.4, 0.5], [2, 1, 3]),
        ([0.3, 0.4, 0.5, 0.6], [3, 2, 1]),
    ],
)
def test_retrieval_subsystem(db_client, query_vector, expected_ids):
    response = db_client.query_points(
        collection_name="test",
        query=query_vector,
        limit=3,
    )
    retrieved_ids = [point[1][0].id for point in response]
    recall = calculate_recall(expected_ids, retrieved_ids)
    precision = calculate_precision(expected_ids, retrieved_ids)
    assert recall >= 0.66
    assert precision >= 0.66


# @pytest.mark.asyncio
# async def test_upload_file(test_client, db_client):
#     file_data = {"file": ("test.txt", b"Test file content", "text/plain")}
#     # response = await test_client.post("/generate/upload", files=file_data)
#     # assert response.status_code == 200
#     points = await db_client.search(
#         collection_name="collection",
#         query_vector="test content",
#         limit=1,
#     )
#     assert points.get("status") == "success"
#     assert points.get("payload").get("doc_name") == "test.txt"


def test_fake(mocker, llm_client):
    class FakeOpenAIClient:
        @staticmethod
        def create(model, messages):
            return {"choices": [{"message": {"content": "fake response"}}]}

    mocker.patch.object(openai, "ChatCompletion", new=FakeOpenAIClient)
    result = llm_client.invoke("test query")
    assert result == {"choices": [{"message": {"content": "fake response"}}]}


# def test_stub(mocker, llm_client):
#     stub = mocker.Mock()
#     stub.process.return_value = "stubbed response"
#     result = llm_client.invoke(stub)
#     assert result == "stubbed response"


# def test_spy(mocker, llm_client):
#     spy = mocker.spy(llm_client, 'send_request')
#     spy.return_value = "some_value"
#     llm_client.invoke("some query")
#     spy.call_count == 1

# def test_mock(mocker, llm_client):
#     mock = mocker.Mock()
#     llm_client.invoke(mock)
#     mock.process.assert_called_once_with("some query")
