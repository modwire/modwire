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
    assert package.files[".env"].count("DATABASE_URL=") == 1
    assert "DATABASE_URL=sqlite:///.dev/db.sqlite" in package.files[".env"]
    assert not any(path.startswith("platform/") for path in package.files)
    assert not any("/api/health/" in path for path in package.files)


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
    assert "http_get" not in controller
    assert "http_post" not in controller
    assert "core.di" not in controller
    assert "project_package" not in controller
    assert " import get" not in controller
    assert "return get(" not in controller
    assert "class InvoiceController" in controller
    assert "InvoiceService" in controller
    assert "response=Out" in controller
    assert "return InvoiceService().create(**data.model_dump())" in controller
    assert "return 201," not in controller
    assert 'operation_id="list_invoices"' in controller
    assert 'operation_id="create_invoice"' in controller
    assert 'operation_id="listInvoices"' not in controller
    assert 'operation_id="createInvoice"' not in controller
