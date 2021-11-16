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
