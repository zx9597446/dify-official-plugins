from typing import Generator, Optional
import httpx
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeBadRequestError,
    InvokeError
)

from dify_plugin import TTSModel
from ..common_fishaudio import FishAudio

class FishAudioText2SpeechModel(TTSModel):
    """
    Model class for Fish.audio Text to Speech model.
    """

    def get_tts_model_voices(self, model: str, credentials: dict, language: Optional[str] = None) -> Optional[list]:
        api_base = credentials.get("api_base", "https://api.fish.audio")
        api_key = credentials.get("api_key")
        use_public_models = credentials.get("use_public_models", "false") == "true"

        params = {
            "self": str(not use_public_models).lower(),
            "page_size": "100",
        }

        if language is not None:
            if "-" in language:
                language = language.split("-")[0]
            params["language"] = language

        results = httpx.get(
            f"{api_base}/model",
            headers={"Authorization": f"Bearer {api_key}"},
            params=params,
        )

        results.raise_for_status()
        data = results.json()

        return [{"name": i["title"], "value": i["_id"]} for i in data["items"]]

    def _invoke(
        self,
        model: str,
        tenant_id: str,
        credentials: dict,
        content_text: str,
        voice: str,
        user: Optional[str] = None,
    ) -> bytes | Generator[bytes, None, None]:
        """
        Invoke text2speech model

        :param model: model name
        :param tenant_id: user tenant id
        :param credentials: model credentials
        :param voice: model timbre
        :param content_text: text content to be translated
        :param user: unique user id
        :return: text translated to audio file
        """

        return self._tts_invoke_streaming(
            model=model,
            credentials=credentials,
            content_text=content_text,
            voice=voice,
        )

    def validate_credentials(
            self, model: str, credentials: dict, user: Optional[str] = None
    ) -> None:
        """
        Validate credentials for text2speech model

        :param credentials: model credentials
        :param user: unique user id
        """

        try:
            self.get_tts_model_voices(
                model=model,
                credentials={
                    "api_key": credentials["api_key"],
                    "api_base": credentials["api_base"],
                    # Disable public models will trigger a 403 error if user is not logged in
                    "use_public_models": "false",
                },
            )
        except Exception as ex:
            raise CredentialsValidateFailedError(str(ex))

    def _tts_invoke_streaming(self, model: str, credentials: dict, content_text: str, voice: str) -> Generator[bytes, None, None]:
        """
        Invoke streaming text2speech model
        :param model: model name
        :param credentials: model credentials
        :param content_text: text content to be translated
        :param voice: ID of the reference audio (if any)
        :return: generator yielding audio chunks
        """

        try:
            word_limit = self._get_model_word_limit(model, credentials) or 500
            if len(content_text) > word_limit:
                sentences = self._split_text_into_sentences(content_text, max_length=word_limit)
            else:
                sentences = [content_text.strip()]

            for i in range(len(sentences)):
                yield from self._tts_invoke_streaming_sentence(
                    credentials=credentials, content_text=sentences[i], voice=voice
                )

        except Exception as ex:
            raise InvokeBadRequestError(str(ex))

    def _tts_invoke_streaming_sentence(self, credentials: dict, content_text: str, voice: Optional[str] = None) -> Generator[bytes, None, None]:
        """
        Invoke streaming text2speech model

        :param credentials: model credentials
        :param content_text: text content to be translated
        :param voice: ID of the reference audio (if any)
        :return: generator yielding audio chunks
        """
        api_key = credentials.get("api_key")
        api_base = credentials.get("api_base", "https://api.fish.audio")
        latency = credentials.get("latency", "normal")
        client = FishAudio(api_key=api_key, url_base=api_base)
        return client.tts(content=content_text, voice=voice, latency=latency)

    @property
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        """
        Map model invoke error to unified error
        The key is the error type thrown to the caller
        The value is the error type thrown by the model,
        which needs to be converted into a unified error type for the caller.

        :return: Invoke error mapping
        """
        return {
            InvokeBadRequestError: [
                httpx.HTTPStatusError,
            ],
        }
