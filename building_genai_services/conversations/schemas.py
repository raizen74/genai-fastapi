from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ConversationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    model_type: str


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(ConversationBase):
    pass


class ConversationOut(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conversation_id: int
    prompt_content: str
    response_content: str


class MessageOut(MessageCreate):
    id: int
    created_at: datetime
    updated_at: datetime
