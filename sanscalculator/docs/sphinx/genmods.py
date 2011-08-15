from __future__ import with_statement
import os.path

MODULE_TEMPLATE=""".. Autogenerated by genmods.py

******************************************************************************
%(name)s
******************************************************************************

:mod:`%(package)s.%(module)s`
==============================================================================

.. automodule:: %(package)s.%(module)s
   :members:
   :undoc-members:
   :inherited-members:
   :show-inheritance:

"""

INDEX_TEMPLATE=""".. Autogenerated by genmods.py

.. _api-index:

##############################################################################
   %(package_name)s
##############################################################################

.. only:: html

   :Release: |version|
   :Date: |today|

.. toctree::

   %(rsts)s
"""


def genfiles(package, package_name, modules, dir='api'):

    if not os.path.exists(dir):
        os.makedirs(dir)

    for module,name in modules:
        with open(os.path.join(dir,module+'.rst'), 'w') as f:
            f.write(MODULE_TEMPLATE%locals())

    rsts = "\n   ".join(module+'.rst' for module,name in modules)
    with open(os.path.join(dir,'index.rst'),'w') as f:
        f.write(INDEX_TEMPLATE%locals())


modules=[
    ('instrument', 'Instrument'),
    ('slit_length_calculator', 'Slit Length Calculator'),
    ('kiessig_calculator', 'Kiessig Calculator'),
    ('resolution_calculator', 'Resolution Calculator')
]
package='sans.calculator'
package_name='Reference'
genfiles(package, package_name, modules)

if __name__ == "__main__":
    genfiles(package, package_name, modules, dir='api')
    print "Sphinx: generate .rst files complete..."