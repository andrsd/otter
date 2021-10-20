import os
from otter.plugins.model_inspector import components
from otter.plugins.model_inspector.pyhit import hit


class InputReader:
    """
    Reader for creating Component objects from input file.

    Args:
        file_name[str]: The input file to open.
    """

    # Maps input file "type" to the python component type to construct
    COMPONENT_TYPES = dict()
    for c in ['FlowChannel',
              'FlowChannel1Phase',
              'FlowChannel2Phase']:
        COMPONENT_TYPES[c] = components.FlowChannel
    for c in ['HeatStructure',
              'HeatStructurePlate',
              'HeatStructureCylindrical',
              'HeatStructureFromFile3D']:
        COMPONENT_TYPES[c] = components.HeatStructure
    for c in ['FreeBoundary',
              'InletMassFlowRateTemperature1Phase',
              'InletMassFlowRateTemperature2Phase',
              'InletVelocityDensity1Phase',
              'InletVelocityDensity2Phase',
              'InletStagnationPressureTemperature1Phase',
              'InletStagnationPressureTemperature2Phase',
              'InletStagnationEnthalpyMomentum1Phase',
              'InletStagnationEnthalpyMomentum2Phase',
              'Outlet1Phase',
              'Outlet2Phase',
              'SolidWall',
              'SolidWall1Phase',
              'SolidWall2Phase']:
        COMPONENT_TYPES[c] = components.Boundary
    for c in ['Branch',
              'FlowJunction',
              'JunctionOneToOne',
              'Pump1Phase',
              'VolumeBranch',
              'VolumeJunction1Phase',
              'VolumeJunction2Phase',
              'WetWell',
              'WetWellStratified']:
        COMPONENT_TYPES[c] = components.Junction
    for c in ['FormLossFromExternalApp1Phase',
              'FormLossFromFunction1Phase',
              'FormLossFromFunction2Phase',
              'HeatGeneration',
              'HeatSourceFromTotalPower',
              'HeatTransferFromExternalAppHeatFlux1Phase',
              'HeatTransferFromExternalAppTemperature1Phase',
              'HeatTransferFromExternalAppTemperature2Phase',
              'HeatTransferFromHeatFlux1Phase',
              'HeatTransferFromHeatFlux2Phase',
              'HeatTransferFromHeatStructure1Phase',
              'HeatTransferFromHeatStructure2Phase',
              'HeatTransferFromSpecifiedTemperature1Phase',
              'HeatTransferFromSpecifiedTemperature2Phase',
              'PrescribedReactorPower',
              'PointKineticsReactorPower',
              'ReactivityFeedback',
              'TotalPower']:
        COMPONENT_TYPES[c] = components.InvisibleComponent

    def __init__(self):
        self._components = None

    def load(self, file_name):
        self._components = dict()
        if file_name:
            if not os.path.isfile(file_name):
                raise IOError("""The supplied input file '{}' does
                    not exist.""".format(file_name))
            with open(file_name, 'r') as f:
                data = f.read()

            try:
                root = hit.parse(os.path.abspath(file_name), data)
            except Exception as err:
                print('{}'.format(err))
                return
            self.__traverse(root)
            for c in self._components.values():
                c.create()

        return self._components

    def getComponent(self, name):
        if name in self._components:
            return self._components[name]
        else:
            return None

    def __traverse(self, node):
        """
        Traverse though the tree and build components
        """
        if node.type() == 'Section' and node.path() == 'Components':
            for child in node.children():
                obj = self.__buildComponent(child)
                if obj is not None:
                    self._components[obj.name] = obj
        else:
            for child in node.children():
                self.__traverse(child)

    def __buildComponent(self, node):
        """
        Builds the component

        Args:
            node[in]: parameters read from the input file
        """
        if node.type() == 'Section':
            node_name = node.path()
            # build a dictionary with parameters
            params = {}
            for child in node.children():
                if child.type() == 'Field':
                    params[child.path()] = child.param()

            ctype = params['type']
            obj_type = self.COMPONENT_TYPES[ctype]
            obj = obj_type(self, node_name, params)
            return obj
        else:
            return None
