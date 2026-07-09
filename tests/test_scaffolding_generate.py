from click.testing import CliRunner

from modwire.shared import code
from modwire.shared.config import ScaffoldingConfig
from modwire.shared.scaffolding.app import ScaffoldingApplication
from modwire.shared.scaffolding.services import ScaffoldRepository
from modwire.cli import cli


def test_django_api_app_required_data_keys_are_declared():
    app = ScaffoldingApplication(
        repository=ScaffoldRepository(ScaffoldingConfig()),
        writer=code.CodePackageWriter(),
    )

    assert app.required_data_keys("modules/django-api-app") == ["app_name", "model_name"]


def test_cli_prompts_for_required_django_api_app_data(tmp_path):
    result = CliRunner().invoke(
        cli,
        [
            "scaffolding",
            "generate",
            "modules/django-api-app",
            str(tmp_path / "records"),
        ],
        input="records\nRecord\n",
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "records" / "apps.py").is_file()
    assert (tmp_path / "records" / "api" / "record" / "controller.py").is_file()
    assert not (tmp_path / "records" / "new_app").exists()
    assert not (tmp_path / "records" / "records").exists()


def test_explicit_app_name_and_model_name_generate_into_app_destination(tmp_path):
    app = ScaffoldingApplication(
        repository=ScaffoldRepository(ScaffoldingConfig()),
        writer=code.CodePackageWriter(),
    )

    app.generate(
        "modules/django-api-app",
        tmp_path / "records",
        {"app_name": "records", "model_name": "Record"},
    )

    assert (tmp_path / "records" / "apps.py").is_file()
    assert (tmp_path / "records" / "api" / "record" / "controller.py").is_file()
