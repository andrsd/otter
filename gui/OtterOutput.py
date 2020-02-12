

def argToText(name, value, level):
    """
    Convert a parameter into a string representation of python dictionary key for outputting

    @param name [string] - name of the parameter
    @param value [string] - parameter value
    @param level [int] - indentation level
    """

    s = ""
    if isinstance(value, str):
        s += "    " * level + "'{}': '{}',\n".format(name, value)
    elif isinstance(value, dict):
        s += "    " * level + "'{}':\n".format(name)
        s += groupToText(value, level + 1)
    else:
        s += "    " * level + "'{}': {},\n".format(name, value)
    return s


def groupToText(args, level):
    """
    Convert a group of parameters into a string representation of python dictionary for outputting

    @param args [dict] - dictionary that will be converted into a string
    @param level [int] - indentation level
    """

    s = "    " * level + "{\n"
    for key, val in list(args.items()):
        s += argToText(key, val, level + 1)
    s += "    " * level + "},\n"
    return s
