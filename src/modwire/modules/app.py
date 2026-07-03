from modwire.shared import ModwireApplication


class ModulesApplication(ModwireApplication):
    def run(self):
        print("Running Modwire Modules CLI...")

    def scaffold(self, name: str, target: str):
        pass

    def add_layer(self, name: str):
        pass

    def remove_layer(self, name: str):
        pass

    def add_package(self, name: str, layer: str):
        pass

    def remove_package(self, name: str, layer: str):
        pass
