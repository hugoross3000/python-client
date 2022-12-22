from abc import abstractmethod
from typing import List, Optional, Set

from steamship import Block, File, SteamshipError, Tag, Task, TaskState
from steamship.base.mime_types import MimeTypes
from steamship.invocable import InvocableResponse
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.blockifier import Blockifier
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput

TRANSCRIPT_ID = "transcript_id"


class Transcriber(Blockifier):
    @abstractmethod
    def start_transcription(
        self, audio_file: PluginRequest[RawDataPluginInput], mime_type: MimeTypes
    ) -> str:
        """Transcribe an audio file and turn it into a transcription and optional Tags."""
        raise NotImplementedError()

    @abstractmethod
    def get_transcript(self, transcript_id: str) -> (Optional[str], Optional[List[Tag]]):
        """Method to retrieve the transcript and optional Tags. If the transcription is not ready, return None"""
        raise NotImplementedError()

    @abstractmethod
    def supported_mime_types(self) -> Set[MimeTypes]:
        raise NotImplementedError()

    def _get_transcript(self, transcript_id: str) -> InvocableResponse:
        transcript, tags = self.get_transcript(transcript_id)
        if transcript is None and tags is None:
            return InvocableResponse(
                status=Task(
                    state=TaskState.running,
                    remote_status_message="Transcription is ongoing.",
                    remote_status_input={"transcript_id": transcript_id},
                )
            )
        else:
            return InvocableResponse(
                data=BlockAndTagPluginOutput(
                    file=File(
                        blocks=[
                            Block(
                                text=transcript,
                                tags=tags,
                            )
                        ]
                    )
                )
            )

    def run(
        self, request: PluginRequest[RawDataPluginInput]
    ) -> InvocableResponse[BlockAndTagPluginOutput]:

        if request.is_status_check:
            if TRANSCRIPT_ID not in request.status.remote_status_input:
                raise SteamshipError(message="Status check requests need to provide a valid job id")
            transcript_id = request.status.remote_status_input[TRANSCRIPT_ID]
            return self._get_transcript(transcript_id)

        else:
            supported_mime_types = self.supported_mime_types()
            if request.data.default_mime_type not in supported_mime_types:
                raise SteamshipError(
                    "Unsupported mimeType. "
                    f"The following mimeTypes are supported: {supported_mime_types}"
                )

            transcript_id = self.start_transcription(
                audio_file=request.data.data, mime_type=request.data.default_mime_type
            )
            return self._get_transcript(transcript_id)
