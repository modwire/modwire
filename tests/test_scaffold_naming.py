from pathlib import Path

from modwire.shared.scaffolding.services.scaffold import Scaffold


SCAFFOLDINGS_ROOT = Path(__file__).resolve().parents[1] / "src" / "scaffoldings"


def test_django_api_project_does_not_generate_app_scope_package():
    scaffold = Scaffold(SCAFFOLDINGS_ROOT / "projects" / "django-api")

    package = scaffold.build_package(
        project_name="sample-api",
        project_package="core",
        project_title="Sample",
    )

    assert "core/api.py" in package.files
    assert "core/settings.py" in package.files
    assert "core/di.py" not in package.files
    assert ".modwire/boundaries.yaml" in package.files
    assert ".modwire/shape.yaml" in package.files
    assert package.files[".env"].count("DATABASE_URL=") == 1
    assert "DATABASE_URL=sqlite:///.dev/db.sqlite" in package.files[".env"]
    assert '"wireup.integration.django.apps.WireupConfig"' in package.files["core/settings.py"]
    assert '"wireup.integration.django.wireup_middleware"' in package.files["core/settings.py"]
    assert "WIREUP = WireupSettings(injectables=local_service_modules(), auto_inject_views=False)" in package.files[
        "core/settings.py"
    ]
    assert not any(path.startswith("platform/") for path in package.files)
    assert not any("/api/health/" in path for path in package.files)

    boundaries = package.files[".modwire/boundaries.yaml"]
    assert 'match: "core"' in boundaries
    assert 'match: "*/api"' in boundaries
    assert 'match: "*/services"' in boundaries
    assert 'match: "*/models"' in boundaries
    assert "module_tag: app" in boundaries
    assert "module_tag: project" in boundaries
    assert "backward-flow" in boundaries
    assert "no-cycles" in boundaries
    assert "no-reentry" in boundaries


def test_django_api_app_uses_snake_case_operation_ids_and_pascal_case_classes():
    scaffold = Scaffold(SCAFFOLDINGS_ROOT / "modules" / "django-api-app")

    package = scaffold.build_package(
        app_name="billing",
        model_name="Invoice",
    )

    controller = package.files["api/invoice/controller.py"]
    assert "from ninja_extra import ControllerBase, api_controller, route" in controller
    assert "@route.get" in controller
    assert "@route.post" in controller
    assert "from wireup import Inject" in controller
    assert "from wireup.integration.django import inject" in controller
    assert "@inject" in controller
    assert "http_get" not in controller
    assert "http_post" not in controller
    assert "core.di" not in controller
    assert "project_package" not in controller
    assert " import get" not in controller
    assert "return get(" not in controller
    assert "class InvoiceController" in controller
    assert "InvoiceService" in controller
    assert "from .schemas import InvoiceIn, InvoiceOut, InvoicePatchIn" in controller
    assert "response=InvoiceOut" in controller
    assert "response=list[InvoiceOut]" in controller
    assert "response={204: None}" in controller
    assert "def get(" in controller
    assert "def update(" in controller
    assert "def partial_update(" in controller
    assert "def delete(" in controller
    assert "return service.create(**data.model_dump())" in controller
    assert "return service.get(invoice_id)" in controller
    assert "return service.update(invoice_id, **data.model_dump())" in controller
    assert "return service.update(invoice_id, **data.model_dump(exclude_unset=True))" in controller
    assert "return Status(204, None)" in controller
    assert "return 201," not in controller
    assert 'operation_id="list_invoices"' in controller
    assert 'operation_id="get_invoice"' in controller
    assert 'operation_id="create_invoice"' in controller
    assert 'operation_id="update_invoice"' in controller
    assert 'operation_id="partial_update_invoice"' in controller
    assert 'operation_id="delete_invoice"' in controller
    assert 'operation_id="listInvoices"' not in controller
    assert 'operation_id="createInvoice"' not in controller
    schemas = package.files["api/invoice/schemas.py"]
    assert "class InvoiceIn(Schema):" in schemas
    assert "class InvoicePatchIn(Schema):" in schemas
    assert "class InvoiceOut(ModelSchema):" in schemas
    assert "@injectable" in package.files["services/invoice.py"]
    assert not any(path.startswith(".modwire/") for path in package.files)


def test_django_api_app_normalizes_model_name_to_pascal_case_and_snake_case():
    scaffold = Scaffold(SCAFFOLDINGS_ROOT / "modules" / "django-api-app")

    package = scaffold.build_package(
        app_name="billing",
        model_name="invoice_item",
    )

    assert "api/invoice_item/controller.py" in package.files
    assert "models/invoice_item.py" in package.files
    assert "services/invoice_item.py" in package.files
    assert "admin/invoice_item.py" in package.files

    controller = package.files["api/invoice_item/controller.py"]
    assert "class InvoiceItemController" in controller
    assert "InvoiceItemService" in controller
    assert "InvoiceItemIn" in controller
    assert "InvoiceItemPatchIn" in controller
    assert "InvoiceItemOut" in controller
    assert 'operation_id="list_invoice_items"' in controller
    assert "invoice_item_id" in controller

    assert "class InvoiceItem(models.Model):" in package.files["models/invoice_item.py"]
    assert "class InvoiceItemService:" in package.files["services/invoice_item.py"]

    schemas = package.files["api/invoice_item/schemas.py"]
    assert "class InvoiceItemIn(Schema):" in schemas
    assert "class InvoiceItemPatchIn(Schema):" in schemas
    assert "class InvoiceItemOut(ModelSchema):" in schemas
