from pathlib import Path

from modwire.shared.scaffolding.services.scaffold import Scaffold


SCAFFOLDINGS_ROOT = Path(__file__).resolve().parents[1] / "src" / "scaffoldings"


def test_django_api_project_uses_snake_case_operation_ids():
    scaffold = Scaffold(SCAFFOLDINGS_ROOT / "projects" / "django-api")

    package = scaffold.build_package(
        project_name="sample-api",
        project_package="core",
        project_title="Sample",
        base_app="platform",
    )

    controller = package.files["platform/api/health/controller.py"]
    assert 'operation_id="get_health"' in controller
    assert 'operation_id="getHealth"' not in controller


def test_django_api_app_uses_snake_case_operation_ids_and_pascal_case_classes():
    scaffold = Scaffold(SCAFFOLDINGS_ROOT / "modules" / "django-api-app")

    package = scaffold.build_package(
        app_name="billing",
        model_name="Invoice",
        project_package="core",
    )

    controller = package.files["billing/api/invoice/controller.py"]
    assert "class InvoiceController" in controller
    assert "InvoiceService" in controller
    assert "response=Out" in controller
    assert "return get(InvoiceService).create(**data.model_dump())" in controller
    assert "return 201," not in controller
    assert 'operation_id="list_invoices"' in controller
    assert 'operation_id="create_invoice"' in controller
    assert 'operation_id="listInvoices"' not in controller
    assert 'operation_id="createInvoice"' not in controller
