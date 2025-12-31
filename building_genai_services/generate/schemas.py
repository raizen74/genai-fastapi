from datetime import datetime
from typing import Annotated, Literal, TypeAlias
from uuid import uuid4

from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    HttpUrl,
    IPvAnyAddress,
    PositiveInt,
    computed_field,
    validate_call,
)

from .utils import count_tokens

VoicePresets = Literal["v2/en_speaker_1", "v2/en_speaker_9"]

SupportedTextModels: TypeAlias = Literal["tinyLlama", "gemma2b"]
TokenCount = Annotated[int, Field(ge=0)]
PriceTable: TypeAlias = dict[SupportedTextModels, float]
price_table: PriceTable = {"tinyLlama": 0.0030, "gemma2b": 0.0200}

ImageSize = Annotated[
    tuple[PositiveInt, PositiveInt],
    "Width and height of an image in pixels",
]
SupportedImageModels = Annotated[
    Literal["tinysd", "sd1.5"],
    "Supported Image Generation Models",
]


@validate_call
def is_square_image(value: ImageSize) -> ImageSize:
    if value[0] / value[1] != 1:
        raise ValueError("Only square images are supported")
    if value[0] not in [512, 1024]:
        raise ValueError(f"Invalid output size: {value} - expected 512 or 1024")
    return value


@validate_call
def is_valid_inference_step(
    num_inference_steps: int,
    model: SupportedImageModels,
) -> int:
    if model == "tinysd" and num_inference_steps > 2000:
        raise ValueError(
            "TinySD model cannot have more than 2000 inference steps",
        )
    return num_inference_steps


OutputSize = Annotated[ImageSize, AfterValidator(is_square_image)]
InferenceSteps = Annotated[
    int,
    AfterValidator(
        lambda v, values: is_valid_inference_step(v, values["model"]),
    ),
]


class ModelRequest(BaseModel):
    prompt: Annotated[str, Field(min_length=1, max_length=4000)]


class ModelResponse(BaseModel):
    request_id: Annotated[
        str, Field(default_factory=lambda: uuid4().hex)
    ]  # default_factory creates uuid4 on the fly
    # no defaults set for ip field
    # raise ValidationError if a valid IP address or None is not provided.
    ip: Annotated[str, IPvAnyAddress] | None
    content: Annotated[str | None, Field(min_length=0, max_length=10000)]
    created_at: datetime = datetime.now()


class TextModelRequest(BaseModel):
    model: Literal["tinyLlama", "gemma2b"]
    prompt: str
    temperature: float = 0.1


class TextModelResponse(ModelResponse):
    model: SupportedTextModels
    temperature: Annotated[float, Field(ge=0.0, le=1.0, default=0.1)]
    # price: Annotated[float, Field(ge=0, default=0.0)]

    @computed_field
    def tokens(self) -> TokenCount:
        # content may be None; ensure we pass a string to the tokenizer
        return count_tokens(self.content or "")

    @computed_field
    def cost(self) -> float:
        return price_table[self.model] * self.tokens


class ImageModelRequest(ModelRequest):
    model: SupportedImageModels
    output_size: OutputSize
    num_inference_steps: InferenceSteps = 200


class ImageModelResponse(ModelResponse):
    size: ImageSize
    url: Annotated[str, HttpUrl] | None = None
