# Import all API modules to make them available to the main handler
# This ensures that when the main handler imports from 'src.api',
# all the modules are loaded and available

from src.api import user_api
from src.api import block_api
from src.api import week_api
from src.api import day_api
from src.api import exercise_api
from src.api import workout_api
from src.api import relationship_api
from src.api import set_api
