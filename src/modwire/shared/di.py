from dependency_injector import containers, providers

from modwire.shared import code


class SharedContainer(containers.DeclarativeContainer):
    code_package_writer = providers.Singleton(code.CodePackageWriter)
    queryable_map_reader = providers.Singleton(code.QueryableCodeMapReader)