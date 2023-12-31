from model import Batch, OrderLine
from datetime import date


def test_orderline_mapper_can_load_lines(session):
    session.execute(
        'INSERT INTO order_lines (orderid, sku, qty) VALUES '
        '("order1", "RED-CHAIR", 12),'
        '("order2", "RED-TABLE", 13),'
        '("order3", "BLUE-LIPSTICK", 14)'
    )
    expected = [
        OrderLine("order1", "RED-CHAIR", 12),
        OrderLine("order2", "RED-TABLE", 13),
        OrderLine("order3", "BLUE-LIPSTICK", 14),
    ]
    assert session.query(OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(session):
    new_line = OrderLine("order1", "DECORATIVE-WIDGET", 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute('SELECT orderid, sku, qty FROM "order_lines"'))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]


def test_retrieving_batches(session):
    session.execute(
        'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        ' VALUES ("batch1", "sku1", 100, null)'
    )
    session.execute(
        'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        ' VALUES ("batch2", "sku2", 200, "2011-04-11")'
    )
    expected = [
        Batch("batch1", "sku1", 100, eta=None),
        Batch("batch2", "sku2", 200, eta=date(2011, 4, 11)),
    ]
    assert session.query(Batch).all() == expected


def test_saving_batches(session):
    batch = Batch("batch1", "sku1", 100, eta=None)
    session.add(batch)
    session.commit()
    rows = list(
        session.execute(
            'SELECT reference, sku, _purchased_quantity, eta FROM "batches"'
        )
    )
    assert rows == [("batch1", "sku1", 100, None)]


def test_retrieving_allocations(session):
    session.execute(
        'INSERT INTO order_lines (orderid, sku, qty) VALUES ("order1", "sku1", 12)'
    )
    [[olid]] = session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        dict(orderid="order1", sku="sku1"),
    )
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        ' VALUES ("batch1", "sku1", 100, null)'
    )
    [[bid]] = session.execute(
        "SELECT id FROM batches WHERE reference=:ref AND sku=:sku",
        dict(ref="batch1", sku="sku1"),
    )
    session.execute(
        "INSERT INTO allocations (orderline_id, batch_id) VALUES (:olid, :bid)",
        dict(olid=olid, bid=bid),
    )

    batch = session.query(Batch).one()

    assert batch._allocations == {OrderLine("order1", "sku1", 12)}
