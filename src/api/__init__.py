# Import all API modules to make them available to the main handler
# This ensures that when the main handler imports from 'src.api',
# all the modules are loaded and available

from src.api import user
from src.api import block
from src.api import week
from src.api import day
from src.api import exercise
from src.api import workout
from src.api import relationship
from src.api import set