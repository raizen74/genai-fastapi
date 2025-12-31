from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from building_genai_services.common.entities import Conversation, Message
from building_genai_services.common.interfaces import Repository

from .schemas import ConversationCreate, ConversationUpdate, MessageCreate


class ConversationRepository(Repository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, skip: int, take: int) -> list[Conversation]:
        async with self.session.begin():
            result = await self.session.execute(
                select(Conversation).offset(skip).limit(take),
            )
        return [r for r in result.scalars().all()]

    async def get(self, conversation_id: int) -> Conversation | None:
        async with self.session.begin():
            result = await self.session.execute(
                select(Conversation).where(Conversation.id == conversation_id),
            )
        return result.scalars().first()

    async def create(self, conversation: ConversationCreate) -> Conversation:
        new_conversation = Conversation(**conversation.model_dump())
        async with self.session.begin():
            self.session.add(new_conversation)
            await self.session.flush()
            await self.session.refresh(new_conversation)
        return new_conversation

    async def update(
        self,
        conversation_id: int,
        updated_conversation: ConversationUpdate,
    ) -> Conversation | None:
        async with self.session.begin():
            result = await self.session.execute(
                select(Conversation).where(Conversation.id == conversation_id),
            )
            conversation = result.scalars().first()
            if not conversation:
                return None
            for key, value in updated_conversation.model_dump().items():
                setattr(conversation, key, value)
            await self.session.flush()
            await self.session.refresh(conversation)
        return conversation

    async def delete(self, conversation_id: int) -> None:
        async with self.session.begin():
            result = await self.session.execute(
                select(Conversation).where(Conversation.id == conversation_id),
            )
            conversation = result.scalars().first()
            if not conversation:
                return
            await self.session.delete(conversation)


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, message: MessageCreate) -> Message:
        new_message = Message(**message.model_dump())
        async with self.session.begin():
            self.session.add(new_message)
            await self.session.flush()
            await self.session.refresh(new_message)
        return new_message
