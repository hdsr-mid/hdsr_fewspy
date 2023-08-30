from hdsr_fewspy.api import Api
from hdsr_fewspy.constants.choices import DefaultPiSettingsChoices
from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.constants.choices import TimeZoneChoices
from hdsr_fewspy.constants.pi_settings import PiSettings
from hdsr_fewspy._version import __version__

# silence flake8
Api = Api
PiSettings = PiSettings
OutputChoices = OutputChoices
TimeZoneChoices = TimeZoneChoices
DefaultPiSettingsChoices = DefaultPiSettingsChoices
__version__ = __version__
