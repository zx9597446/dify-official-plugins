from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.sagemaker_text_rerank import SageMakerReRankTool


class SageMakerProvider(ToolProvider):
    def validate_credentials(self, credentials: dict) -> None:
        try:
            for _ in SageMakerReRankTool.from_credentials(
                credentials
            ).invoke_from_executor(
                tool_parameters={
                    "sagemaker_endpoint": "",
                    "query": "misaka mikoto",
                    "candidate_texts": "hello$$$hello world",
                    "topk": 5,
                    "aws_region": "",
                },
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
