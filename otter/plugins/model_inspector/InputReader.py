import os
import sys
import importlib.util
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

    def __init__(self):
        self._components = None
        self._pps = None
        self._ent_3d_map = None

    def load(self, file_name):
        self._components = dict()
        self._pps = dict()
        self._ent_3d_map = dict()
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
            self._createMapTo3DSpace()
            self._mapPPSToPoints()

    def getComponents(self):
        return self._components

    def getPPS(self):
        return self._pps

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
        elif node.type() == 'Section' and node.path() == 'Postprocessors':
            for child in node.children():
                pps = self.__buildPPS(child)
                if pps is not None:
                    self._pps[pps['name']] = pps
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
            node_name = node.fullpath().split("Components/", 1)[1]
            # build a dictionary with parameters
            params = {}
            for child in node.children():
                if child.type() == 'Field':
                    params[child.path()] = child.param()

            if 'type' in params:
                ctype = params['type']
                obj_type = getattr(components, self.COMPONENT_TYPES[ctype])
                obj = obj_type(self, node_name, params)
                return obj
            else:
                # group syntax
                for child in node.children():
                    obj = self.__buildComponent(child)
                    if obj is not None:
                        self._components[obj.name] = obj
        else:
            return None

    def __buildPPS(self, node):
        """
        Build the PPS
        """
        if node.type() == 'Section':
            node_name = node.fullpath().split("Postprocessors/", 1)[1]
            # build a dictionary with parameters
            params = {}
            for child in node.children():
                if child.type() == 'Field':
                    params[child.path()] = child.param()

            if 'type' in params:
                if params['type'] == 'PointValue':
                    obj = {
                        'name': node_name,
                        'point': components.Component.toArray(params['point'])
                    }
                    return obj
                elif params['type'] == 'SideAverageValue':
                    obj = {
                        'name': node_name,
                        'boundary': params['boundary']
                    }
                    return obj

        return None

    def _createMapTo3DSpace(self):
        """
        Map boundaries, junctions and flow channel ends to physical points
        """
        self._ent_3d_map = {}
        for obj in self._components.values():
            if isinstance(obj, components.Boundary):
                self._ent_3d_map[obj.name] = obj.getPoint()
            elif isinstance(obj, components.Junction):
                self._ent_3d_map[obj.name] = obj.getPoint()
            elif isinstance(obj, components.FlowChannel):
                self._ent_3d_map[obj.name + ':in'] = obj.getPoint('in')
                self._ent_3d_map[obj.name + ':out'] = obj.getPoint('out')

    def _mapPPSToPoints(self):
        for obj in self._pps.values():
            if 'boundary' in obj:
                pt = self._ent_3d_map[obj['boundary']]
                obj['point'] = pt

    @staticmethod
    def loadSyntax(file_path):
        directory, file_name = os.path.split(file_path)
        module_name, ext = os.path.splitext(file_name)
        sys.path.append(directory)
        temp = importlib.import_module(module_name)
        sys.path.remove(directory)

        if hasattr(temp, 'component_types'):
            comp_types = getattr(temp, 'component_types')
            for str_type, comps in comp_types.items():
                for c in comps:
                    InputReader.COMPONENT_TYPES[c] = str_type
