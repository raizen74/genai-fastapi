from io import BytesIO
from typing import Annotated

import httpx
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    File,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from loguru import logger
from PIL import Image

from building_genai_services.common.session import DBSessionDep
from building_genai_services.conversations import GetConversationDep, store_message
from building_genai_services.rag import (
    get_rag_content,
    get_urls_content,
    pdf_text_extractor,
    save_file,
    vector_service,
)

from .models import (
    # generate_3d_geometry,
    generate_audio,
    generate_image,
    generate_text,
    generate_text_vllm,
    generate_video,
    # load_3d_model,
    load_audio_model,
    load_image_model,
    load_text_model,
    load_video_model,
)
from .schemas import (
    TextModelRequest,
    TextModelResponse,
    VoicePresets,
)
from .utils import (
    audio_array_to_buffer,
    export_to_video_buffer,
    img_to_bytes,
    # mesh_to_obj_buffer,
)

router = APIRouter(prefix="/generate", tags=["Generation"])

@router.post("/message/{conversation_id}")
async def stream_llm_controller(
    request: Request,
    prompt: str,
    background_task: BackgroundTasks,
    session: DBSessionDep,
    conversation: GetConversationDep,
):
    print(f"{conversation.id = }")
    pipe = load_text_model()
    output = generate_text(pipe, prompt, 0.01)
    background_task.add_task(
        store_message,
        prompt,
        output,
        conversation.id,
        session,
    )
    res = TextModelResponse(
        model="tinyLlama",
        temperature=0.01,
        content=output,
        ip=request.client.host,
    )

    logger.info(f"{res.model_dump =}")
    logger.info(f"{res.model_dump_json =}")
    return res


@router.post("/text", response_model_exclude_defaults=True)
async def serve_text_to_text_controller(
    request: Request,
    body: TextModelRequest = Body(...),
    urls_content: str = Depends(get_urls_content),
    rag_content: str = Depends(get_rag_content),
) -> TextModelResponse:
    logger.info(f"{body.model =}")
    logger.info(f"{urls_content =}")
    if body.model not in ["tinyLlama", "gemma2b"]:
        raise HTTPException(
            detail=f"Model {body.model} is not supported",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    prompt = body.prompt + " " + urls_content + rag_content
    pipe = load_text_model()
    output = generate_text(pipe, prompt, body.temperature)
    res = TextModelResponse(
        model=body.model,
        temperature=body.temperature,
        content=output,
        ip=request.client.host,
    )

    logger.info(f"{res.model_dump =}")
    logger.info(f"{res.model_dump_json =}")
    return res


@router.post("/text/vllm")
async def serve_vllm_text_to_text_controller(
    request: Request,
    body: TextModelRequest,
) -> TextModelResponse:
    logger.info(f"{body.model =}")
    output = await generate_text_vllm(body.prompt, body.temperature)
    return TextModelResponse(
        model=body.model,
        temperature=body.temperature,
        content=output,
        ip=request.client.host,
    )


@router.get(
    "/audio",
    responses={status.HTTP_200_OK: {"content": {"audio/wav": {}}}},
    response_class=StreamingResponse,
)
def serve_text_to_audio_model_controller(
    prompt: str,
    preset: VoicePresets = "v2/en_speaker_1",
):
    processor, model = load_audio_model()
    output, sample_rate = generate_audio(processor, model, prompt, preset)
    return StreamingResponse(
        audio_array_to_buffer(output, sample_rate),
        media_type="audio/wav",
    )


@router.get(
    "/image",
    responses={status.HTTP_200_OK: {"content": {"image/png": {}}}},
    response_class=Response,
)
def serve_text_to_image_model_controller(prompt: str):
    pipe = load_image_model()
    output = generate_image(pipe, prompt)
    return Response(content=img_to_bytes(output), media_type="image/png")


@router.post(
    "/video",
    responses={status.HTTP_200_OK: {"content": {"video/mp4": {}}}},
    response_class=StreamingResponse,
)
def serve_image_to_video_model_controller(image: bytes = File(...), num_frames: int = 25):
    image = Image.open(BytesIO(image))
    model = load_video_model()
    frames = generate_video(model, image, num_frames)
    return StreamingResponse(export_to_video_buffer(frames), media_type="video/mp4")


# def serve_text_to_3d_model_controller(
#     prompt: str,
#     num_inference_steps: int = 25,
# ):
#     model = load_3d_model()
#     mesh = generate_3d_geometry(model, prompt, num_inference_steps)
#     response = StreamingResponse(mesh_to_obj_buffer(mesh), media_type="model/obj")
#     response.headers["Content-Disposition"] = f"attachment; filename={prompt}.obj"
#     return response


@router.get(
    "/generate/bentoml/image",
    responses={status.HTTP_200_OK: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def serve_bentoml_text_to_image_controller(prompt: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:5000/generate",
            json={"prompt": prompt},
        )
    return Response(content=response.content, media_type="image/png")

@router.post("/upload")
async def file_upload_controller(
    file: Annotated[UploadFile, File(description="Uploaded PDF documents")],
    bg_text_processor: BackgroundTasks,
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            detail=f"Only uploading PDF documents are supported",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    try:
        filepath = await save_file(file)
        bg_text_processor.add_task(pdf_text_extractor, filepath)
        bg_text_processor.add_task(
            vector_service.store_file_content_in_db,
            filepath.replace("pdf", "txt"),
            512,
            "knowledgebase",
            768,
        )

    except Exception as e:
        raise HTTPException(
            detail=f"An error occurred while saving file - Error: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return {"filename": file.filename, "message": "File uploaded successfully"}
