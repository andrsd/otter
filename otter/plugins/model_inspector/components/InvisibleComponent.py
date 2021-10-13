from .Component import Component


class InvisibleComponent(Component):
    """
    Auxiliary component for components that do not have visual representation
    (i.e. PrescribedReactorPower)
    """

    def __init__(self, reader, name, params):
        super().__init__(reader, name, params)

    def create(self):
        pass

    @property
    def type(self):
        return None

    def getActor(self):
        return []
