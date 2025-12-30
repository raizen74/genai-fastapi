from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from building_genai_services.database import (
    Conversation,
    ConversationRepository,
    ConversationService,
    DBSessionDep,
    MessageRepository,
)
from building_genai_services.schemas import (
    ConversationCreate,
    ConversationOut,
    ConversationUpdate,
    MessageCreate,
    MessageOut,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


async def get_conversation(
    conversation_id: int,
    session: DBSessionDep,
) -> Conversation:
    conversation = await ConversationRepository(session).get(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return conversation

# conversation_id and session will be injected automatically into get_conversation and the result will be provided to the endpoint function
GetConversationDep = Annotated[Conversation, Depends(get_conversation)]

async def store_message(
    prompt_content: str,
    response_content: str,
    conversation_id: int,
    session: AsyncSession,
) -> None:
    print("Storing message in background...")
    message = MessageCreate(
        conversation_id=conversation_id,
        prompt_content=prompt_content,
        response_content=response_content,
    )
    await MessageRepository(session).create(message)


@router.get("")
async def list_conversations_controller(
    session: DBSessionDep,
    skip: int = 0,
    take: int = 100,
) -> list[ConversationOut]:
    conversations = await ConversationRepository(session).list(skip, take)
    return [ConversationOut.model_validate(c) for c in conversations]


@router.get("/{conversation_id}")
async def get_conversation_controller(
    conversation: GetConversationDep,
) -> ConversationOut:
    return ConversationOut.model_validate(conversation)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_conversation_controller(
    conversation: ConversationCreate,
    session: DBSessionDep,
) -> ConversationOut:
    new_conversation = await ConversationRepository(session).create(
        conversation,
    )
    return ConversationOut.model_validate(new_conversation)


@router.put("/{conversation_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_conversation_controller(
    conversation: GetConversationDep,
    updated_conversation: ConversationUpdate,
    session: DBSessionDep,
) -> ConversationOut:
    print(f"{conversation.id = }")
    print(f"{updated_conversation = }")
    updated_conversation = await ConversationRepository(session).update(
        conversation.id,
        updated_conversation,
    )
    return ConversationOut.model_validate(updated_conversation)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_controller(
    conversation: GetConversationDep,
    session: DBSessionDep,
) -> None:
    await ConversationRepository(session).delete(conversation.id)

@router.get("/{conversation_id}/messages")
async def list_conversation_messages_controller(
    conversation: GetConversationDep,
    session: DBSessionDep,
) -> list[MessageOut]:
    messages = await ConversationService(session).list_messages(conversation.id)
    return [MessageOut.model_validate(m) for m in messages]
