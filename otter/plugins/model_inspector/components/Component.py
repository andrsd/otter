import re
import vtk


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
        self._caption_actor = None

    @staticmethod
    def toArray(param):
        """
        Convert input string into an array of items.
        """
        if isinstance(param, str):
            str_in = re.sub(r' +', ' ', param.strip())
            return [float(s) for s in re.split('\s+', str_in)]
        elif isinstance(param, float):
            return [param]
        else:
            return param

    @staticmethod
    def toLength(param):
        if isinstance(param, str):
            str_len = param.strip()
            larr = re.split('\s+', str_len)
            if len(larr) > 1:
                return sum([float(s) for s in larr])
            else:
                return float(str_len)
        else:
            return param

    @staticmethod
    def parseConnection(str_in):
        """
        Determine the component connections.
        """
        m = re.match(r"(.+):(in|out)", str_in)
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

    def getCaptionActor(self):
        return self._caption_actor

    def _createCaptionActor(self):
        actor = vtk.vtkCaptionActor2D()
        actor.SetCaption(self._name)
        actor.SetPosition(25., 25.)
        actor.SetWidth(0.5)
        actor.SetHeight(0.05)
        actor.SetVisibility(False)
        actor.BorderOff()
        actor.ThreeDimensionalLeaderOff()
        actor.LeaderOn()
        return actor
