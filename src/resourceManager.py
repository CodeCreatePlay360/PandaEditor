import os
import panda3d.core as p3d
from loader.gltf_loader import load_model as gltf_loader


class ResourceManager(object):
    def __init__(self, *args, **kwargs):
        object.__init__(self)
        
        self.__loader = p3d.Loader.getGlobalPtr()
        
    def load_model(self, path, loader_options=None, use_cached=False,
                   instanced=False, *args, **kwargs):   
        """
        path = path of model on disk,
        
        loader_options = see panda3d.core.LoaderOption api for info on this,
        
        use_cached = attempts to load a model from .ModelPool ram cache if 
        possible, otherwise if the bam cache is enabled 
        (via the `model-cache-dir` config variable), then that will be
        consulted next, and if both caches fail, the file will be loaded 
        from disk. If use_cached is False, then neither cache will be
        consulted or updated,
        
        instanced = return an instance of this model from modelpool,
        
        is_character = is this character an animated character ? if this 
        then you can also send a list of animations in kwargs, all animations
        should be in same directory as character.
        """

        node = None
        loader_options = loader_options if loader_options else p3d.LoaderOptions()
        loader_options.setFlags(loader_options.getFlags() & ~p3d.LoaderOptions.LFReportErrors)
        
        if use_cached:
            loader_options.setFlags(loader_options.getFlags() & ~p3d.LoaderOptions.LFNoCache)
            
        if instanced:
            loader_options.setFlags(loader_options.getFlags() | p3d.LoaderOptions.LFAllowInstance)
        
        if os.path.isfile(path):
            ext = os.path.splitext(path)[-1]
            if ext == ".gltf" or ext == ".glb":
                node = gltf_loader(path, *args, **kwargs)
            else:
                node = self.__loader.loadSync(p3d.Filename(path),
                                                loader_options)
        else:
            print("not a file {0}".format(path))

        result = None if not node else node
        return result
    
    def load_texture(self,
                     path,
                     cube_map=False,
                     loader_options=None,
                     readMipmaps = False,
                     minfilter = None, magfilter = None,
                     anisotropicDegree = None,
                     multiview = None,
                     *args, **kwargs):
                         
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
        if not cube_map:
            alpha_path = kwargs.pop("alpha_path")
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
                
        # finally return the results
        result = None if not texture else texture
        return result
            
    def load_font(self, font):
        pass
    
    def load_sound(self):
        pass
            
    @property
    def loader(self):
        return self.__loader
