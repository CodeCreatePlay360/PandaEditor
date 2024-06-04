import os
import panda3d.core as p3d
from utils.moduleImporter import import_modules
from loader.gltf_loader import load_model as gltf_loader
from game.resources import RuntimeScript, Component


class ResourceHandler(object):
    def __init__(self):
        """ResourceHandler is responsible for importing, loading and unloading
        resources (models, sounds, scripts etc.) from disk."""
        
        object.__init__(self)
        self.__loader = p3d.Loader.getGlobalPtr()
        
    def load_scripts(self, paths):
        components = []
        scripts_data = import_modules(paths)
        runtimescripts = {}
        comps = {}
        
        # cache
        obj = obj_type = cls_instance = None
        
        for path, mod, cls_name in scripts_data:
            # only import modules  if module name and class name match
            if hasattr(mod, cls_name):
                obj = getattr(mod, cls_name)
                obj_type = None

                # try getting last parent class 
                try:
                    obj_type = obj.__mro__[1]
                except AttributeError:
                    pass

                # object must be a runtime script, component or editor plugin
                cls_instance = None
                try:
                    if obj_type == RuntimeScript:
                        cls_instance = obj(cls_name, path)
                        
                    elif obj_type == Component:
                        cls_instance = None

                except Exception as exception:
                    print(exception)
                    
                # collect instances
                if cls_instance is None:
                    if obj_type == Component:
                        comps[path] = obj
                else:
                    if isinstance(cls_instance, RuntimeScript):
                        runtimescripts[path] = cls_instance
        
        return runtimescripts, comps
    
    def load_model(self, path, loader_options=None, use_cached=False,
                   instanced=False, create_np=True, *args, **kwargs):
        """
        path = path of model on disk,
        
        loader_options = see panda3d.core.LoaderOption api for info on this,
        
        use_cached = attempts to load a model from .ModelPool ram cache if 
        possible, otherwise if the bam cache is enabled 
        (via the `model-cache-dir` config variable), then that will be
        consulted next, and if both caches fail, the file will be loaded 
        from disk. If, use_cached is False, then neither cache will be
        consulted nor updated.
        
        instanced = return an instance of this model from modelpool.
        
        is_character = is this character an animated character ? if this 
        then you can also send a list of animations in kwargs, all animations
        should be in same directory as character.
        """
        
        # TODO - convert path to OS-independent
        
        node = None

        if os.path.isfile(path):
            ext = os.path.splitext(path)[-1]
            if ext == ".gltf" or ext == ".glb":
                node = gltf_loader(path, *args, **kwargs)
                node = p3d.NodePath(node)

            else:
                loader_options = loader_options if loader_options else p3d.LoaderOptions()
                loader_options.setFlags(loader_options.getFlags() & ~p3d.LoaderOptions.LFReportErrors)

                if use_cached:
                    loader_options.setFlags(loader_options.getFlags() & ~p3d.LoaderOptions.LFNoCache)

                if instanced:
                    loader_options.setFlags(loader_options.getFlags() | p3d.LoaderOptions.LFAllowInstance)
                
                node = self.__loader.loadSync(p3d.Filename(path), loader_options)
                if create_np:
                    node = p3d.NodePath(node)
        else:
            print("Not a file {0}".format(path))

        result = None if not node else node
        return result

    def load_texture(self,
                     path,
                     cube_map=False,
                     loader_options=None,
                     readMipmaps=False,
                     minfilter=None, magfilter=None,
                     anisotropicDegree=None,
                     multiview=None,
                     *args, **kwargs):
                         
        if not os.path.isfile(path):
            print("Unable to load texture, path is not a file {0}".format(path))
            return

        loader_options = loader_options if loader_options else p3d.LoaderOptions()

        # ____________________________________________________________________
        if multiview:
            flags = loader_options.getTextureFlags()

            if multiview:
                flags |= p3d.LoaderOptions.TFMultiview
            else:
                flags &= ~p3d.LoaderOptions.TFMultiview

            loader_options.setTextureFlags(flags)

        # ____________________________________________________________________
        texture = None
        if not cube_map:
            alpha_path = kwargs.pop("alpha_path", None)
            if alpha_path:
                texture = p3d.TexturePool.loadTexture(path, alpha_path, 0, 0,
                                                      readMipmaps, loader_options)
            else:
                texture = p3d.TexturePool.loadTexture(path, 0, readMipmaps,
                                                      loader_options)

        if cube_map:
            texture_pattern = kwargs.pop("texture_pattern")
            texture = p3d.TexturePool.loadCubeMap(texture_pattern,
                                                  readMipmaps,
                                                  loader_options)

        # ____________________________________________________________________
        if texture:
            if minfilter is not None:
                texture.setMinfilter(minfilter)
            if magfilter is not None:
                texture.setMagfilter(magfilter)
            if anisotropicDegree is not None:
                texture.setAnisotropicDegree(anisotropicDegree)

        # finally, return the results
        result = None if not texture else texture
        return result

    def load_font(self, font):
        pass

    def load_sound(self):
        pass

    @property
    def loader(self):
        return self.__loader
