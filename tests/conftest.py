import site
import os
here = __file__
here = os.path.dirname(here)
site.addsitedir(os.path.join(os.path.dirname(here), 'python'))