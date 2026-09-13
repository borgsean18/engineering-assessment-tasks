from datetime import date

import pytest

from tests.conftest import HARBOUR_ID, METRO_ID, RIVERSIDE_ID


def test_list_change_orders(client):
    res = client.get(f"/projects/{RIVERSIDE_ID}/change-orders")
    assert res.status_code == 200
    orders = res.json()
    assert {o["reference"] for o in orders} == {
        "CO-001",
        "CO-002",
        "CO-003",
        "CO-004",
        "CO-005",
        "CO-006",
        "CO-007",
        "CO-008",
    }
    assert "costDelta" in orders[0]
    assert "scheduleDeltaDays" in orders[0]


def test_list_change_orders_filter_status(client):
    res = client.get(f"/projects/{RIVERSIDE_ID}/change-orders", params={"status": "approved"})
    assert res.status_code == 200
    orders = res.json()
    assert len(orders) == 4
    assert orders[0]["reference"] == "CO-001"
    assert orders[0]["costDelta"] == 2500000.0


def test_list_change_orders_unknown_project_404(client):
    res = client.get("/projects/nope/change-orders")
    assert res.status_code == 404


def test_list_change_orders_filter_invalid_status_422(client):
    res = client.get(
        f"/projects/{RIVERSIDE_ID}/change-orders",
        params={"status": "not-a-status"},
    )
    assert res.status_code == 422


# Creation tests against Harbour, which is seeded with no change orders and no work
# packages, so they cannot disturb the Riverside counts asserted in test_projects.py.


def _payload(**overrides):
    """A minimal valid create body; override single fields per test."""
    body = {
        "reference": "CO-100",
        "title": "Additional groundworks",
        "costDelta": 125000.0,
        "scheduleDeltaDays": 14,
        "status": "submitted",
    }
    body.update(overrides)
    return body


def test_create_change_order(client):
    res = client.post(
        f"/projects/{HARBOUR_ID}/change-orders",
        json=_payload(reference="CO-101"),
    )
    assert res.status_code == 201
    body = res.json()
    assert body["id"]
    assert body["reference"] == "CO-101"
    assert body["title"] == "Additional groundworks"
    assert body["costDelta"] == 125000.0
    assert body["scheduleDeltaDays"] == 14
    assert body["status"] == "submitted"
    assert body["raisedDate"] == date.today().isoformat()

    listed = client.get(f"/projects/{HARBOUR_ID}/change-orders").json()
    assert "CO-101" in {o["reference"] for o in listed}


def test_create_change_order_defaults_status_and_raised_date(client):
    res = client.post(
        f"/projects/{HARBOUR_ID}/change-orders",
        json={
            "reference": "CO-102",
            "title": "Site access works",
            "costDelta": 5000.0,
            "scheduleDeltaDays": 2,
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "draft"
    assert body["raisedDate"] == date.today().isoformat()


def test_create_change_order_links_work_package(client):
    res = client.post(
        f"/projects/{METRO_ID}/change-orders",
        json=_payload(reference="CO-103", workPackageCode="WP-01"),
    )
    assert res.status_code == 201
    body = res.json()
    assert body["workPackageCode"] == "WP-01"
    assert body["workPackageId"] is not None


def test_create_change_order_reference_unique_per_project_not_globally(client):
    # CO-001 is already used on Riverside; the constraint is scoped to a project.
    res = client.post(f"/projects/{HARBOUR_ID}/change-orders", json=_payload(reference="CO-001"))
    assert res.status_code == 201


def test_create_change_order_unknown_project_404(client):
    res = client.post("/projects/nope/change-orders", json=_payload())
    assert res.status_code == 404
    assert res.json()["detail"] == "Project not found"


def test_create_change_order_duplicate_reference_409(client):
    first = client.post(f"/projects/{HARBOUR_ID}/change-orders", json=_payload(reference="CO-200"))
    assert first.status_code == 201
    res = client.post(f"/projects/{HARBOUR_ID}/change-orders", json=_payload(reference="CO-200"))
    assert res.status_code == 409
    assert "CO-200" in res.json()["detail"]


def test_create_change_order_work_package_from_another_project_422(client):
    # WP-01 exists, but on Riverside and Metro - not on Harbour.
    res = client.post(
        f"/projects/{HARBOUR_ID}/change-orders",
        json=_payload(reference="CO-201", workPackageCode="WP-01"),
    )
    assert res.status_code == 422


def test_create_change_order_unknown_work_package_422(client):
    res = client.post(
        f"/projects/{HARBOUR_ID}/change-orders",
        json=_payload(reference="CO-202", workPackageCode="WP-NOPE"),
    )
    assert res.status_code == 422


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("costDelta", 0),
        ("costDelta", -125000.0),
        ("scheduleDeltaDays", 0),
        ("scheduleDeltaDays", -14),
    ],
)
def test_create_change_order_non_positive_impact_422(client, field, value):
    body = _payload(reference="CO-300")
    body[field] = value
    res = client.post(f"/projects/{HARBOUR_ID}/change-orders", json=body)
    assert res.status_code == 422


@pytest.mark.parametrize("bad_status", ["approved", "rejected", "not-a-status"])
def test_create_change_order_status_not_valid_for_new_change_422(client, bad_status):
    res = client.post(
        f"/projects/{HARBOUR_ID}/change-orders",
        json=_payload(reference="CO-301", status=bad_status),
    )
    assert res.status_code == 422


@pytest.mark.parametrize("missing", ["reference", "title", "costDelta", "scheduleDeltaDays"])
def test_create_change_order_missing_required_field_422(client, missing):
    body = _payload(reference="CO-302")
    del body[missing]
    res = client.post(f"/projects/{HARBOUR_ID}/change-orders", json=body)
    assert res.status_code == 422


@pytest.mark.parametrize("field", ["reference", "title"])
def test_create_change_order_blank_text_422(client, field):
    body = _payload(reference="CO-303")
    body[field] = ""
    res = client.post(f"/projects/{HARBOUR_ID}/change-orders", json=body)
    assert res.status_code == 422
