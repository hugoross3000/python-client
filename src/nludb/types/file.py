from typing import List
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponse

class FileUploadType:
  file = "file"
  url = "url"

@dataclass
class FileUploadRequest(NludbRequest):
  type: str
  name: str
  convert: bool = False

@dataclass
class FileUploadResponse(NludbResponse):
  fileId: str

  @staticmethod
  def safely_from_dict(d: any) -> "FileUploadResponse":
    return FileUploadResponse(
      fileId = d.get('fileId', None)
    )

@dataclass
class FileDeleteRequest(NludbRequest):
  fileId: str

@dataclass
class FileDeleteResponse(NludbResponse):
  fileId: str

  @staticmethod
  def safely_from_dict(d: any) -> "FileDeleteResponse":
    return FileDeleteResponse(
      fileId = d.get('fileId', None)
    )

@dataclass
class FileConvertRequest(NludbRequest):
  fileId: str

@dataclass
class FileConvertResponse(NludbResponse):
  fileId: str

  @staticmethod
  def safely_from_dict(d: any) -> "FileConvertResponse":
    return FileConvertResponse(
      fileId = d.get('fileId', None)
    )

@dataclass
class Block(NludbRequest):
  blockId: str
  type: str
  value: str

  @staticmethod
  def safely_from_dict(d: any) -> "Block":
    return Block(
      blockId = d.get('blockId', None),
      type = d.get('type', None),
      value = d.get('value', None)
    )

@dataclass
class FileQueryRequest(NludbRequest):
  fileId: str

@dataclass
class FileQueryResponse(NludbResponse):
  fileId: str
  blocks: List[Block]

  @staticmethod
  def safely_from_dict(d: any) -> "FileQueryResponse":
    return FileQueryResponse(
      fileId = d.get('fileId', None),
      blocks = [Block.safely_from_dict(block) for block in d.get('blocks', None)]
    )
