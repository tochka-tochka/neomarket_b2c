import pytest
import responses
from src.tests.fixtures import test_order, test_address, test_payment_method
from src.services.orders.admin_orders import fulfill_order
from src.models.orders import FailedFulfillAttempts

@pytest.fixture
def mock_b2b_fulfill(responses):
    b2b_url = "http://localhost:8010/api/v1/inventory/fulfill"
    responses.add(
        method=responses.POST,
        url=b2b_url,
        json={
          "order_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
          "status": "PROCESSED",
          "processed_at": "2026-05-31T12:49:10.918Z"
        },
        status=200
    )
    return responses

@pytest.fixture
def mock_b2b_failed_fulfill(responses):
    b2b_url = "http://localhost:8010/api/v1/inventory/fulfill"
    responses.add(
        method=responses.POST,
        url=b2b_url,
        status=503
    )
    return responses

@pytest.mark.django_db
class TestOrderFulfill():

    def test_delivered_status_triggers_fulfill_to_b2b(self, mock_b2b_fulfill, test_order):
        # Если запрос по B2B_URL не выполняется, то тест выполнется с ошибкой - 
        # AssertionError: Not all requests have been executed [('POST', 'http://localhost:8010/api/v1/inventory/fulfill')]
        fulfill_order(test_order.id)

    def test_fulfill_failure_retried_asynchronously(self, mock_b2b_failed_fulfill, test_order):
        fulfill_order(test_order.id)

        attempt = FailedFulfillAttempts.objects.all().first()
        assert attempt is not None
        assert attempt.payload["order_id"] == str(test_order.id)
        