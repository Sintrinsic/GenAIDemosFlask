import pytest

from chat.openAI_client import OpenAIClient
from helloworld.application import application


@pytest.fixture
def client():
    return application.test_client()


def test_response(client):
    result = client.get()
    assert result.status_code == 200


def test_api_creds(client):
    OpenAIClient.getInstance()
