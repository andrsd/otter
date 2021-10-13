import re


class Component(object):
    """
    Base class for components.

    Args:
        reader[InputReader]: The instance of the InputReader that is creating
                             this component.
        name[str]: The name of the object.
        params[dict]: The input parameters for the component being created.
    """
    def __init__(self, reader, name, params):
        self._reader = reader
        self._name = name
        self._params = params
        self._reader._components[name] = self
        self._color = None

    @staticmethod
    def toArray(str_in):
        """
        Convert input string into an array of items.
        """
        str_in = re.sub(r' +', ' ', str_in)
        return [float(s) for s in str_in.split(' ')]

    @staticmethod
    def parseConnection(str_in):
        """
        Determine the component connections.
        """
        m = re.match(r"([^\(]+):([^:]+)", str_in)
        return {'name': m.group(1), 'type': m.group(2)}

    @property
    def name(self):
        """
        Return the name of the component.
        """
        return self._name

    @property
    def type(self):
        """
        Return the type of the component.
        """
        return None

    @property
    def color(self):
        return self._color

    def create(self):
        """
        Create the vtkSource object(s) to be returned by getSource. (abstract)
        """
        raise NotImplementedError("""The create method must be overridden to
            build desired vtk objects.""")

    def getActor(self):
        """
        Return the vtk actor
        """
        raise NotImplementedError("""The getActor method must be overridden to
            return vtkActor object.""")

    def getSilhouetteActor(self):
        raise NotImplementedError("""The getSilhouetteActor method must be
            overridden to return vtkActor object for silhouette.""")
