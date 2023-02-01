import logging
from typing import Any, Dict, Optional

from steamship.base.client import Client
from steamship.data.plugin.plugin_instance import CreatePluginInstanceRequest, PluginInstance
from steamship.data.tags.tag_constants import GenerationTag, TagKind, TagValueKey
from steamship.utils.prompt_utils import interpolate_template
from steamship.utils.tagging_utils import tag_then_fetch_first_block_tag


class PromptGenerationPluginInstance(PluginInstance):
    """An instance of a configured prompt completion service such as GPT-3.

    The `generate` method synchronously invokes the prompt against a set of variables that parameterize it.
    The return value is a single string.

    Example Usage:
       llm = Steamship.use('prompt-generation-default', config={ "temperature": 0.9 })
       PROMPT = "Greet {name} as if he were a {relation}."
       greeting = llm.generate(PROMPT, {"name": "Ted", "relation": "old friend"})
    """

    def generate(
        self, prompt: str, variables: Optional[Dict] = None, clean_output: bool = True
    ) -> str:
        """Complete the provided prompt, interpolating any variables."""

        prompt_text = interpolate_template(prompt, variables)

        generation_tag = tag_then_fetch_first_block_tag(
            self, prompt_text, TagKind.GENERATION, GenerationTag.PROMPT_COMPLETION
        )

        try:
            generation = generation_tag.value[TagValueKey.STRING_VALUE]
            if clean_output:
                return self._clean_output(generation)
            else:
                return generation
        except Exception as e:
            logging.error(
                "generate() got unexpected response shape back. This suggests an error rather an merely an empty response."
            )
            logging.exception(e)
            raise e
        return ""

    @staticmethod
    def create(
        client: Client,
        plugin_id: str = None,
        plugin_handle: str = None,
        plugin_version_id: str = None,
        plugin_version_handle: str = None,
        handle: str = None,
        fetch_if_exists: bool = True,
        config: Dict[str, Any] = None,
    ) -> "PromptGenerationPluginInstance":
        """Create a plugin instance

        When handle is empty the engine will automatically assign one
        fetch_if_exists controls whether we want to re-use an existing plugin instance or not."""
        req = CreatePluginInstanceRequest(
            handle=handle,
            plugin_id=plugin_id,
            plugin_handle=plugin_handle,
            plugin_version_id=plugin_version_id,
            plugin_version_handle=plugin_version_handle,
            fetch_if_exists=fetch_if_exists,
            config=config,
        )

        return client.post(
            "plugin/instance/create", payload=req, expect=PromptGenerationPluginInstance
        )

    def _clean_output(self, text: str):
        """Remove any leading/trailing whitespace and partial sentences.

        This assumes that your generated output will include consistent punctuation. You may
        want to alter this method to better fit the format of your generated text.
        """
        last_punc = -1
        for i, c in enumerate(reversed(text)):
            if c in '.!?"':
                last_punc = len(text) - i
                break
        if last_punc != -1:
            result = text[: last_punc + 1]
        else:
            result = text
        return result.strip()
