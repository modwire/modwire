import sys
from pathlib import Path

import pytest

from modwire.modules import generate_module


def test_generate_module_uses_caller_copier_template(tmp_path: Path) -> None:
    template_root = tmp_path / "template-root"
    template_dir = template_root / "template"
    template_dir.mkdir(parents=True)
    (template_root / "copier.yml").write_text(
        "\n".join(
            [
                '_templates_suffix: ".jinja"',
                "_subdirectory: template",
                "",
                "module_name:",
                "  type: str",
                "feature:",
                "  type: str",
            ]
        ),
        encoding="utf-8",
    )
    (template_dir / "{{ module_name }}.txt.jinja").write_text(
        "{{ module_name }}:{{ feature }}",
        encoding="utf-8",
    )

    output_root = tmp_path / "generated"

    generate_module(
        "billing",
        output_root,
        template_root,
        data={"feature": "invoices"},
    )

    assert (output_root / "billing.txt").read_text(encoding="utf-8") == (
        "billing:invoices"
    )


def test_generate_module_raises_for_missing_template(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Copier template does not exist"):
        generate_module("billing", tmp_path / "generated", tmp_path / "missing")


def test_generate_module_uses_bundled_scaffolding(tmp_path: Path) -> None:
    output_root = tmp_path / "generated"

    generate_module("billing", output_root)

    assert (output_root / "billing" / "domain.py").is_file()
    assert (output_root / "billing" / "application.py").is_file()


def test_generate_module_uses_hexagonal_scaffolding(tmp_path: Path) -> None:
    output_root = tmp_path / "generated"

    generate_module("billing", output_root, scaffolding="hexagonal")

    python_module = output_root / "python" / "billing"
    expected_files = [
        "domain/models/billingaggregate.py",
        "domain/exceptions/billingaggregatevalidationerror.py",
        "domain/events/billingaggregatecreated.py",
        "ports/inbound/createbilling.py",
        "ports/inbound/billingservice.py",
        "ports/outbound/billingrepository.py",
        "adapters/inbound/billingservice.py",
        "adapters/inbound/web/billingcontroller.py",
        "adapters/inbound/amqp/createbillingconsumer.py",
        "adapters/outbound/persistence/inmemorybillingrepository.py",
        "adapters/outbound/client/billingaggregateclient.py",
    ]

    for expected_file in expected_files:
        assert (python_module / expected_file).is_file()

    assert not (python_module / "domain.py").exists()
    assert not (python_module / "ports.py").exists()
    assert not (python_module / "application.py").exists()
    assert not (python_module / "infrastructure.py").exists()
    assert not (python_module / "ui.py").exists()

    assert (
        output_root / "typescript" / "billing" / "adapters/inbound/web/BillingController.ts"
    ).is_file()
    assert (
        output_root / "php" / "src" / "Adapters/Outbound/Client/BillingAggregateClient.php"
    ).is_file()
    assert not (output_root / "php" / "src" / "Application").exists()

    sys.path.insert(0, str(output_root / "python"))
    try:
        from billing.adapters.inbound.billingservice import BillingService
        from billing.adapters.inbound.web.billingcontroller import BillingController
        from billing.adapters.outbound.persistence.inmemorybillingrepository import (
            InMemoryBillingRepository,
        )

        controller = BillingController(BillingService(InMemoryBillingRepository()))

        assert controller.create("aggregate-1", "Billing") == {
            "id": "aggregate-1",
            "name": "Billing",
        }
    finally:
        sys.path.remove(str(output_root / "python"))


def test_generate_module_uses_clean_scaffolding(tmp_path: Path) -> None:
    output_root = tmp_path / "generated"

    generate_module("orders", output_root, scaffolding="clean")

    python_module = output_root / "python" / "orders"
    expected_files = [
        "domain/entities/ordersentity.py",
        "domain/exceptions/ordersentityvalidationerror.py",
        "domain/events/orderscreated.py",
        "application/ports/ordersrepository.py",
        "application/use_cases/createorders.py",
        "infrastructure/persistence/inmemoryordersrepository.py",
        "interface/http/orderscontroller.py",
    ]

    for expected_file in expected_files:
        assert (python_module / expected_file).is_file()

    assert (
        output_root / "typescript" / "orders" / "interface/http/OrdersController.ts"
    ).is_file()
    assert (
        output_root / "php" / "src" / "Infrastructure/Persistence/InMemoryOrdersRepository.php"
    ).is_file()

    sys.path.insert(0, str(output_root / "python"))
    try:
        from orders.application.use_cases.createorders import CreateOrders
        from orders.infrastructure.persistence.inmemoryordersrepository import (
            InMemoryOrdersRepository,
        )
        from orders.interface.http.orderscontroller import OrdersController

        controller = OrdersController(CreateOrders(InMemoryOrdersRepository()))

        assert controller.create("entity-1", "Orders") == {
            "id": "entity-1",
            "name": "Orders",
        }
    finally:
        sys.path.remove(str(output_root / "python"))


def test_generate_module_uses_ddd_context_scaffolding(tmp_path: Path) -> None:
    output_root = tmp_path / "generated"

    generate_module("catalog", output_root, scaffolding="ddd_context")

    python_module = output_root / "python" / "bounded_contexts" / "catalog" / "catalog"
    expected_files = [
        "domain/aggregates/catalogaggregate.py",
        "domain/entities/catalogentity.py",
        "domain/value_objects/catalogname.py",
        "domain/events/catalogcreated.py",
        "domain/services/catalogdomainservice.py",
        "application/ports/catalogrepository.py",
        "application/use_cases/createcatalog.py",
        "infrastructure/persistence/inmemorycatalogrepository.py",
        "interface/http/catalogcontroller.py",
    ]

    for expected_file in expected_files:
        assert (python_module / expected_file).is_file()

    assert (
        output_root
        / "typescript"
        / "bounded_contexts/catalog/catalog/interface/http/CatalogController.ts"
    ).is_file()
    assert (
        output_root
        / "php"
        / "src/BoundedContexts/Catalog/Catalog/Domain/Aggregates/CatalogAggregate.php"
    ).is_file()

    sys.path.insert(0, str(output_root / "python"))
    try:
        from bounded_contexts.catalog.catalog.application.use_cases.createcatalog import (
            CreateCatalog,
        )
        from bounded_contexts.catalog.catalog.infrastructure.persistence.inmemorycatalogrepository import (
            InMemoryCatalogRepository,
        )
        from bounded_contexts.catalog.catalog.interface.http.catalogcontroller import (
            CatalogController,
        )

        controller = CatalogController(CreateCatalog(InMemoryCatalogRepository()))

        assert controller.create("aggregate-1", "Catalog") == {
            "id": "aggregate-1",
            "name": "Catalog",
        }
    finally:
        sys.path.remove(str(output_root / "python"))
