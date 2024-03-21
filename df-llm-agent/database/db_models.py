from tortoise.models import Model
from tortoise.fields import (SmallIntField, IntField, FloatField, CharField, TextField, DatetimeField, JSONField)


class DbVersion(Model):

    class Meta:
        table = "db_version"

    id = IntField(pk=True, autoincrement=True)
    version = CharField(max_length=64, null=True)
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)


class ChatTopic(Model):

    class Meta:
        table = "chat_topic"

    id = IntField(pk=True, autoincrement=True)
    user_id = IntField()
    name = CharField(max_length=256, null=True)
    type = SmallIntField()
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)


class Chat(Model):

    class Meta:
        table = "chat"

    id = IntField(pk=True, autoincrement=True)
    chat_topic_id = IntField()
    input = TextField()
    output = TextField()
    output_all = JSONField()
    engine = CharField(max_length=64, null=True)
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)


class Score(Model):

    class Meta:
        table = "score"

    id = IntField(pk=True, autoincrement=True)
    user_id = IntField(null=False)
    type = SmallIntField()
    obj_id = IntField()
    score = SmallIntField()
    feedback = TextField()
    user_name = CharField(max_length=64)
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)


class LlmConfig(Model):

    class Meta:
        table = "llm_config"

    id = IntField(pk=True, autoincrement=True)
    user_id = IntField(null=False)
    platform = CharField(max_length=64, null=False)
    model = CharField(max_length=64, null=False)
    model_info = CharField(max_length=255, null=True)
    key = CharField(max_length=64, null=False)
    value = CharField(max_length=256, null=False)
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)
