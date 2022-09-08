import os
from utils import src_path
os.environ["PYSDL2_DLL_PATH"] = src_path(".\\src\\dll")
from poggendorff_checker.poggendorff_checker import *