from fewspy.constants.custom_types import ResponseType
from typing import List

import logging


logger = logging.getLogger(__name__)


class MemoryBase:
    def run(self, responses: List[ResponseType]):
        raise NotImplementedError


class XmlMemory(MemoryBase):
    def run(self, responses: List[ResponseType], **kwargs):
        print(1)


class JsonMemory(MemoryBase):
    def run(self, responses: List[ResponseType], **kwargs):
        print(1)


class PdDataFrameMemory(MemoryBase):
    def run(self, responses: List[ResponseType], **kwargs):
        print(1)
