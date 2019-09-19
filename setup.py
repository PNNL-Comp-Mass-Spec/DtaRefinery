"""
1) run setup.py py2exe
2) Copy those files and directories into newly created dist directory
    Directories:
        examples
        mpl-data
        aux_xtandem_module
    Files:
        dta_refinery.exe.manifest
        dtaRefineryIcon48x48.ico
        default_settings.xml
        run_example_shift_by_median.bat
        run_example_lowess.bat
        run_example_numpy_spline.bat
        run_example_R_spline.bat
        README.txt
"""

from distutils.core import setup
import py2exe

opts = {
    'py2exe': {"includes": ["matplotlib.numerix.fft",
                            "matplotlib.numerix.linear_algebra",
                            "matplotlib.numerix.random_array",
                            "matplotlib.backends.backend_tkagg"],
               'excludes': [],
               ##                'dll_excludes': ['libgdk-win32-2.0-0.dll',
               ##                                 'libgobject-2.0-0.dll']
               }
}

setup(console=["dta_refinery.py"], options=opts, requires=['numpy', 'matplotlib', 'wxPython'])
