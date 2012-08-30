
def importPluginModulesIn(directory):
    import glob, imp
    from os.path import join, basename, splitext
    modules = {}
    for path in glob.glob(join(directory,'[!_]*.py')): # list .py files not starting with '_'
        name, ext = splitext(basename(path))
        modules[name] = imp.load_source(name, path)
    return modules   


def findPluginCreator(category, loaded_plugins):
    assert category in loaded_plugins, "No generator is called '%s' in ./plugin/!" % category
    return loaded_plugins[category].NewPlugin
