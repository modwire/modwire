from modwire.shared import ModwireApplication


class LayersApplication(ModwireApplication):
    def run(self):
        print("Running Modwire Layers CLI...")

    def scaffold(self, name: str, layout: str, language: str):
        pass

    def add_layer(self, name: str):
        pass

    def remove_layer(self, name: str):
        pass

    def add_package(self, name: str, layer: str):
        pass

    def remove_package(self, name: str, layer: str):
        pass
