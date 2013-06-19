import os
from ctypes import *

API_VERSION = 1

#################################################################################
## helpers

def enum(*sequential, **named): # is a helper function to create enums
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

class LibraryHandle(object): # is used to open and close external library

    # we need to distinguish between windows and other operating systems
    import _ctypes
    dlopen  = _ctypes.LoadLibrary if os.name in ("nt", "ce") else _ctypes.dlopen
    dlclose = _ctypes.FreeLibrary if os.name in ("nt", "ce") else _ctypes.dlclose

    # instance
    def __init__(self):
        self.handle = None
        
    def __del__(self):
        self.close()
            
    def __nonzero__(self):
        return self.handle is not None

    # library
    def open(self, path):
        self.close()
        self.handle = LibraryHandle.dlopen(path)
        
    def close(self):
        if self.handle is not None:
            handle, self.handle = self.handle, None
            LibraryHandle.dlclose(handle)


#################################################################################
## objects of the following types are passed to python

ParameterFlags = enum(
    Orientation   = 0x01,
    Magnetic      = 0x02,
    Unfittable    = 0x04,
    Integer       = 0x08,
    Polydisperse  = 0x10,
    RepeatCount   = 0x20 | 0x04,
    Repeated      = 0x40)

c_double_p = POINTER(c_double)
c_cmodel_p = c_void_p # pointer to unspecified data which can be used by external library (for each created c-model)

class c_parameter_info(Structure):
    _fields_ = [
        ("name"       , c_char_p),
        ("description", c_char_p),
        ("unit"       , c_char_p),
        ("default"    , c_double),
        ("dispmin"    , c_double),
        ("dispmax"    , c_double),
        ("flags"      , c_size_t)]
c_parameter_info_p = POINTER(c_parameter_info)

class c_model_info(Structure):
    _fields_ = [
        ("version"        , c_size_t),
        ("name"           , c_char_p),
        ("description"    , c_char_p),
        ("parameter_count", c_size_t),
        ("parameters"     , c_parameter_info_p)]    
c_model_info_p     = POINTER(c_model_info)


#################################################################################
## objects of the following types are passed to external library

ParameterType = enum(
    End          = 0x00000000,
    Simple       = 0xAAAAAAA1,
    Polydisperse = 0xAAAAAAA2)
        
c_data_p       = c_void_p
c_parameters_p = c_void_p

class c_end_parameter(Structure):
    _fields_ = [
        ("type" , c_size_t)]
    # instance
    def __init__(self):
        self.type  = ParameterType.End

class c_simple_parameter(Structure):
    _fields_ = [
        ("type" , c_size_t),
        ("value", c_double)]
    # instance
    def __init__(self, value):
        self.type  = ParameterType.Simple
        self.value = value

class c_polydisperse_parameter(Structure):
    _fields_ = [
        ("type"   , c_size_t),
        ("length" , c_size_t),
        ("values" , c_double_p),
        ("weights", c_double_p)]
    # instance
    def __init__(self, values_weights):
        self.type    = ParameterType.Polydisperse

        # we need to ensure that a polydisperse parameter always
        # contains one array for values and one for weights
        if isinstance(values_weights, (int, long, float)):
            self.length  = 1
            self.values  = (c_double * 1)(values_weights)
            self.weights = (c_double * 1)(1)
        else:        
            values  = values_weights.values
            weights = values_weights.weights
            if len(values) != len(weights):
                raise ValueError('len(weights)')
            
            self.length  = len(values)
            self.values  = (c_double * self.length)(*values )
            self.weights = (c_double * self.length)(*weights)
            
c_end_parameter_p          = POINTER(c_end_parameter)
c_simple_parameter_p       = POINTER(c_simple_parameter)
c_polydisperse_parameter_p = POINTER(c_polydisperse_parameter)


#################################################################################
## only objects of the following types should be used to access external models

class ModelInfo(object): # describes external model
    # instance
    def __init__(self, name, description, parameters):
        self.name        = name
        self.description = description
        self.parameters  = parameters # list of ParameterInfo

        # the following lists define the type of the parameters 
        self.orientation  = [p.name for p in parameters if p.flags & ParameterFlags.Orientation ]
        self.magnetic     = [p.name for p in parameters if p.flags & ParameterFlags.Magnetic    ]
        self.unfittable   = [p.name for p in parameters if p.flags & ParameterFlags.Unfittable  ]
        self.integer      = [p.name for p in parameters if p.flags & ParameterFlags.Integer     ]
        self.polydisperse = [p.name for p in parameters if p.flags & ParameterFlags.Polydisperse]
        
class ParameterInfo(object): # ModelInfo.parameters contains ParameterInfo for each parameter
    # instance
    def __init__(self, name, description, unit, default, dispmin, dispmax, flags):
        self.name        = name
        self.description = description
        self.unit        = unit
        self.default     = default
        self.dispmin     = dispmin
        self.dispmax     = dispmax
        self.flags       = flags
       
class PluginModel(object): # represents a concrete model with all its parameters. It's used for simulations.
    # instance
    def __init__(self, factory, id, model_info, parameters):
        self.factory    = factory    # factory object which created this PluginModel
        self.id         = id         # instance id
        self.model_info = model_info # should be of type ModelInfo
        self.parameters = parameters # instance of PluginModelParameterCollection

    def __del__(self):
        self.destroy()
        
    # model information
    def get_model_info(self):
        return self.model_info
        
    # model instantiation
    def destroy(self):
        self.factory.destroy_model(self)

    # calculations
    def calculate_q(self, q):
        return self.factory.calculate_q(self, q)
        
    def calculate_qxqy(self, qx, qy):
        return self.factory.calculate_qxqy(self, qx, qy)
        
    def calculate_qxqyqz(self, qx, qy, qz):
        return self.factory.calculate_qxqyqz(self, qx, qy, qz)
        
    def calculate_ER(self):
        return self.factory.calculate_ER(self)
        
    def calculate_VR(self):
        return self.factory.calculate_VR(self)

class PluginModelParameterCollection(object): # allows access to parameters either as PluginModel.parameters.name or PluginModel.parameters["name"]
    # instance
    def __init__(self, parameters):
        self.__dict__.update(parameters)        
    def __len__(self):
        return len(self.__dict__)
    def __getattr__(self, name):
        return self.__dict__[name]
    def __setattr__(self, name, value):
        if not name in self.__dict__:
            raise AttributeError(name)
        self.__dict__[name] = value
    def __delattr__(self, name):
        raise Exception()
    def __getitem__(self, name):
        return self.__dict__[name]
    def __setitem__(self, name, value):
        if not name in self.__dict__:
            raise AttributeError(name)
        self.__dict__[name] = value
    def __iter__(self):
        return iter(self.__dict__)
    
class PolydisperseParameter(object): # if a parameter is flagged as polydisperse then PluginModel.parameters.x will have "values" and "weights" attributes
    # instance
    def __init__(self, values, weights=None):
        self.values = values
        if weights is not None:
            self.weights = weights
        else:
            w = 1.0 / len(values)
            self.weights = [w for v in values]

class PluginModelFactory(object): # does the hard work

    # instance
    def __init__(self, path=None):
        # library
        self.path      = None               # path to loaded external library
        self._modelLib = LibraryHandle()    # handle to external library
        self._cdll     = None               # helper object which provides access to external methods for loaded library
        # functions
        self._get_model_info   = None
        self._create_model     = None
        self._destroy_model    = None
        self._calculate_q      = None
        self._calculate_qxqy   = None
        self._calculate_qxqyqz = None
        self._calculate_ER     = None
        self._calculate_VR     = None
        # created models
        self._next_model_id  = 1            # every model created will get a new id
        self._created_models = {}           # id -> c-model (used to allow us to unload current library on demand)
        
        # load library
        if path is not None:
            self.load(path)
 
    def __del__(self):
        self.unload()
        
    # load and unload library
    def load(self, path):
        if self._modelLib:
            self.unload()

        # open library
        self._created_models = {}
        self._modelLib.open(path)
        self._cdll = CDLL(None, handle=self._modelLib.handle)
        self.path  = path
        try:
            def loadfunction(cdll, name, restype, argtypes, default=None):
                try:
                    f = cdll[name]
                    f.restype  = restype
                    f.argtypes = argtypes
                    return f
                except:
                    if default:
                        return default
                    raise

            def default_create_model(data):
                return None
            def default_destroy_model(cmodel):
                pass
            def default_calculate(cmodel, cparameter_ptrs, n, iq_data, qx=None, qy=None, qz=None):
                nan = float('nan')
                for k in xrange(n):
                    iq_data[k] = nan
                    
            # load functions
            self._get_model_info   = loadfunction(self._cdll, 'get_model_info'  , c_model_info_p, [])
            # model instantiation
            self._create_model     = loadfunction(self._cdll, 'create_model'    , c_cmodel_p, [c_data_p  ], default=default_create_model )
            self._destroy_model    = loadfunction(self._cdll, 'destroy_model'   , None      , [c_cmodel_p], default=default_destroy_model)
            # I/Q calculations
            self._calculate_q      = loadfunction(self._cdll, 'calculate_q'     , None, [c_cmodel_p, c_parameters_p, c_size_t, c_double_p, c_double_p                        ], default=default_calculate)
            self._calculate_qxqy   = loadfunction(self._cdll, 'calculate_qxqy'  , None, [c_cmodel_p, c_parameters_p, c_size_t, c_double_p, c_double_p, c_double_p            ], default=default_calculate)
            self._calculate_qxqyqz = loadfunction(self._cdll, 'calculate_qxqyqz', None, [c_cmodel_p, c_parameters_p, c_size_t, c_double_p, c_double_p, c_double_p, c_double_p], default=default_calculate)
            # other calculations
            self._calculate_ER     = loadfunction(self._cdll, 'calculate_ER'    , c_double, [c_cmodel_p, c_parameters_p])
            self._calculate_VR     = loadfunction(self._cdll, 'calculate_VR'    , c_double, [c_cmodel_p, c_parameters_p])
        except:
            try:
                self.unload()
            except:
                pass
            raise
        
    def unload(self):
        # destroy existing c-models
        if self._destroy_model is not None:
            for cmodel in self._created_models.itervalues():
                self._destroy_model(cmodel)
        self._created_models = {}
        # reset functions
        self._get_model_info   = None
        self._create_model     = None
        self._destroy_model    = None
        self._calculate_q      = None
        self._calculate_qxqy   = None
        self._calculate_qxqyqz = None
        self._calculate_ER     = None
        self._calculate_VR     = None
        # close library
        self._modelLib.close()
        self._cdll = None
        self.path  = None

    # model information
    def get_model_info(self): # generates an instance of ModelInfo
        # get model info
        cmi = self._get_model_info().contents
        if cmi.version != API_VERSION:
            raise Exception()

        # get parameter info
        parameters = []
        for i in xrange(cmi.parameter_count):
            parameter = cmi.parameters[i]
            parameters.extend([ParameterInfo(
                parameter.name,
                parameter.description,
                parameter.unit,
                parameter.default,
                parameter.dispmin,
                parameter.dispmax,
                parameter.flags)])
                                
        return ModelInfo(
            cmi.name,
            cmi.description,
            parameters)

    # model instantiation
    def create_model(self, data=None): # creates a concrete model (PluginModel) which can have an individual set of parameter values
        if self._create_model is None:
            raise Exception()

        # increment id
        current_id          = self._next_model_id
        self._next_model_id += 1
        
        # create cmodel
        self._created_models[current_id] = self._create_model(data)

        model_info         = self.get_model_info()
        default_parameters = PluginModelParameterCollection({
            p.name : (p.default if not p.flags & ParameterFlags.Polydisperse else PolydisperseParameter([p.default]))
            for p in model_info.parameters})

        return PluginModel(self, current_id, model_info, default_parameters)
        
    def destroy_model(self, model): # destroys a concrete model
        if not model.id in self._created_models:
            raise ValueError('model.id')
        if self._destroy_model is None:
            raise Exception()
        
        try:
            cmodel = self._created_models[model.id]
            self._destroy_model(cmodel)
        finally:
            self._created_models.pop(model.id)
            model.id         = None
            model.factory    = None
            model.model_info = None
            model.parameters = None
        
    # helper
    def _get_cparameters(self, model_info, parameters): # creates a c-array which holds parameter values (expected by c-model)
        cparameter_objs = [
            c_simple_parameter(getattr(parameters, p.name)) if not p.flags & ParameterFlags.Polydisperse else c_polydisperse_parameter(getattr(parameters, p.name))
            for p in model_info.parameters]
        cparameter_objs.extend([c_end_parameter()])
        cparameter_ptrs = (c_void_p * len(cparameter_objs))(*[addressof(p) for p in cparameter_objs])
        return cparameter_objs, cparameter_ptrs
    
    # I/Q calculations
    def calculate_q(self, model, q):
        if not model.id in self._created_models:
            raise ValueError('model.id')
        if self._calculate_q is None:
            raise Exception()

        cmodel = self._created_models[model.id]
        cparameter_objs, cparameter_ptrs = self._get_cparameters(model.model_info, model.parameters)
        
        if q is None:
            self._calculate_q(cmodel, cparameter_ptrs, 0, None, None)
            return []

        n       = len(q)
        iq_data = (c_double * n)()
        q_data  = (c_double * n)(*q)
        self._calculate_q(cmodel, cparameter_ptrs, n, iq_data, q_data)
        return list(iq_data)
        
    def calculate_qxqy(self, model, qx, qy):
        if not model.id in self._created_models:
            raise ValueError('model.id')
        if self._calculate_qxqy is None:
            raise Exception()

        cmodel = self._created_models[model.id]
        cparameter_objs, cparameter_ptrs = self._get_cparameters(model.model_info, model.parameters)

        if (qx is None) or (qy is None):
            self._calculate_qxqy(cmodel, cparameter_ptrs, 0, None, None, None)
            return []

        nx = len(qx)
        ny = len(qy)
        if nx != ny:
            raise Exception()
        
        n = nx
        iq_data = (c_double * n)()
        qx_data = (c_double * n)(*qx)
        qy_data = (c_double * n)(*qy)
        self._calculate_qxqy(cmodel, cparameter_ptrs, n, iq_data, qx_data, qy_data)
        return list(iq_data)
        
    def calculate_qxqyqz(self, model, qx, qy, qz):
        if not model.id in self._created_models:
            raise ValueError('model.id')
        if self._calculate_qxqyqz is None:
            raise Exception()

        cmodel = self._created_models[model.id]
        cparameter_objs, cparameter_ptrs = self._get_cparameters(model.model_info, model.parameters)

        if (qx is None) or (qy is None) or (qz is None):
            self._calculate_qxqyqz(cmodel, cparameter_ptrs, 0, None, None, None, None)
            return []

        nx = len(qx)
        ny = len(qy)
        nz = len(qz)
        if (nx != ny) or (nx != nz):
            raise Exception()

        n = nx
        iq_data = (c_double * n)()
        qx_data = (c_double * n)(*qx)
        qy_data = (c_double * n)(*qy)
        qz_data = (c_double * n)(*qz)
        self._calculate_qxqyqz(cmodel, cparameter_ptrs, n, iq_data, qx_data, qy_data, qz_data)
        return list(iq_data)

    # other calculations
    def calculate_ER(self, model):
        if not model.id in self._created_models:
            raise ValueError('model.id')
        if self._calculate_ER is None:
            raise Exception()
        
        cmodel = self._created_models[model.id]
        cparameter_objs, cparameter_ptrs = self._get_cparameters(model.model_info, model.parameters)
        
        return self._calculate_ER(cmodel, cparameter_ptrs)
        
    def calculate_VR(self, model):
        if not model.id in self._created_models:
            raise ValueError('model.id')
        if self._calculate_VR is None:
            raise Exception()
        
        cmodel = self._created_models[model.id]
        cparameter_objs, cparameter_ptrs = self._get_cparameters(model.model_info, model.parameters)
        
        return self._calculate_VR(cmodel, cparameter_ptrs)


#################################################################################
## Tests/Demos

def Test():
    # PluginModelFactory can be used to load and unload an external c-model
    factory = PluginModelFactory()
    #factory.load(r'C:\Users\davidm\Desktop\SasView\CPlugin\SampleModel\Debug\SampleModel.dll')
    factory.load(r'C:\Users\davidm\Desktop\SasView\CPlugin\SimpleModel\Debug\SimpleModel.dll')

    # ModelInfo provides information of all paramters
    model_info = factory.get_model_info()

    print
    print 'name:        ', model_info.name
    print 'description: ', model_info.description
    print
    
    for p in model_info.parameters:
        print 'parameter: %-15s default: %11f' % (p.name, p.default)
        
    print
    print 'orientation: ', model_info.orientation
    print 'magnetic:    ', model_info.magnetic
    print 'unfittable:  ', model_info.unfittable
    print 'integer:     ', model_info.integer
    print 'polydisperse:', model_info.polydisperse
    print

    # a concrete model can be created which holds the model information and default/modified parameter values
    model = factory.create_model()

    # "model.parameters" can be used as a dictionary or parameters can be accessed directly
    if 'radius' in model_info.polydisperse:
        model.parameters.radius.values  = [10.0, 20.0]
        model.parameters.radius.weights = [ 0.5,  0.5]
    else:
        model.parameters.radius = 5.0

    print 'q     ', model.calculate_q(     [1, 2])
    print 'qxqy  ', model.calculate_qxqy(  [1, 2], [1, 2])
    print 'qxqyqz', model.calculate_qxqyqz([1, 2], [1, 2], [1, 2])
    print 'er    ', model.calculate_ER()
    print 'vr    ', model.calculate_VR()
    print
    
    # a single value can be assigned to a polydisperse parameter
    model.parameters['radius'] = 10.0
    
    print 'er    ', model.calculate_ER()
    print 'vr    ', model.calculate_VR()
    print

    # when factory and model become out of scope, the model and library will be released 

print '---'
Test()
print 'done'