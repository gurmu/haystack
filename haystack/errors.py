"""Custom Errors for Haystack"""

from typing import Optional

from haystack.telemetry import send_custom_event


class HaystackError(Exception):
    """
    Any error generated by Haystack.

    This error wraps its source transparently in such a way that its attributes
    can be accessed directly: for example, if the original error has a `message` attribute,
    `HaystackError.message` will exist and have the expected content.
    If send_message_in_event is set to True (default), the message will be sent as part of a telemetry event reporting the error.
    The messages of errors that might contain user-specific information will not be sent, e.g., DocumentStoreError or OpenAIError.
    """

    def __init__(
        self, message: Optional[str] = None, docs_link: Optional[str] = None, send_message_in_event: bool = True
    ):
        payload = {"message": message} if send_message_in_event else {}
        send_custom_event(event=f"{type(self).__name__} raised", payload=payload)
        super().__init__()
        if message:
            self.message = message
        self.docs_link = None

    def __getattr__(self, attr):
        # If self.__cause__ is None, it will raise the expected AttributeError
        getattr(self.__cause__, attr)

    def __str__(self):
        if self.docs_link:
            docs_message = f"\n\nCheck out the documentation at {self.docs_link}"
            return self.message + docs_message
        return self.message

    def __repr__(self):
        return str(self)


class ModelingError(HaystackError):
    """Exception for issues raised by the modeling module"""

    def __init__(self, message: Optional[str] = None, docs_link: Optional[str] = "https://haystack.deepset.ai/"):
        super().__init__(message=message, docs_link=docs_link)


class PipelineError(HaystackError):
    """Exception for issues raised within a pipeline"""

    def __init__(
        self,
        message: Optional[str] = None,
        docs_link: Optional[str] = "https://docs.haystack.deepset.ai/docs/pipelines",
    ):
        super().__init__(message=message, docs_link=docs_link)


class PipelineSchemaError(PipelineError):
    """Exception for issues arising when reading/building the JSON schema of pipelines"""

    def __init__(self, message: Optional[str] = None):
        super().__init__(message=message)


class PipelineConfigError(PipelineError):
    """Exception for issues raised within a pipeline's config file"""

    def __init__(
        self,
        message: Optional[str] = None,
        docs_link: Optional[str] = "https://docs.haystack.deepset.ai/docs/pipelines#yaml-file-definitions",
    ):
        super().__init__(message=message, docs_link=docs_link)


class DocumentStoreError(HaystackError):
    """Exception for issues that occur in a document store"""

    def __init__(self, message: Optional[str] = None, send_message_in_event: bool = False):
        super().__init__(message=message, send_message_in_event=send_message_in_event)


class FilterError(DocumentStoreError):
    """Exception for issues that occur building complex filters"""

    def __init__(self, message: Optional[str] = None):
        super().__init__(message=message)


class PineconeDocumentStoreError(DocumentStoreError):
    """Exception for issues that occur in a Pinecone document store"""

    def __init__(self, message: Optional[str] = None):
        super().__init__(message=message)


class DuplicateDocumentError(DocumentStoreError, ValueError):
    """Exception for Duplicate document"""

    def __init__(self, message: Optional[str] = None):
        super().__init__(message=message)


class NodeError(HaystackError):
    """Exception for issues that occur in a node"""

    def __init__(self, message: Optional[str] = None, send_message_in_event: bool = True):
        super().__init__(message=message, send_message_in_event=send_message_in_event)


class AudioNodeError(NodeError):
    """Exception for issues that occur in a node of the audio module"""

    def __init__(self, message: Optional[str] = None):
        super().__init__(message=message)


class OpenAIError(NodeError):
    """Exception for issues that occur in the OpenAI APIs"""

    def __init__(
        self, message: Optional[str] = None, status_code: Optional[int] = None, send_message_in_event: bool = False
    ):
        super().__init__(message=message, send_message_in_event=send_message_in_event)
        self.status_code = status_code


class OpenAIRateLimitError(OpenAIError):
    """
    Rate limit error for OpenAI API (status code 429)
    See https://help.openai.com/en/articles/5955604-how-can-i-solve-429-too-many-requests-errors
    See https://help.openai.com/en/articles/5955598-is-api-usage-subject-to-any-rate-limits
    """

    def __init__(self, message: Optional[str] = None, send_message_in_event: bool = False):
        super().__init__(message=message, status_code=429, send_message_in_event=send_message_in_event)


class CohereError(NodeError):
    """Exception for issues that occur in the Cohere APIs"""

    def __init__(
        self, message: Optional[str] = None, status_code: Optional[int] = None, send_message_in_event: bool = False
    ):
        super().__init__(message=message, send_message_in_event=send_message_in_event)
        self.status_code = status_code


class ImageToTextError(NodeError):
    """Exception for issues that occur in the ImageToText node"""

    def __init__(self, message: Optional[str] = None):
        super().__init__(message=message)
