from __future__ import annotations

import time
import logging
import re
from typing import Any

from django.conf import settings
from openai import OpenAI
from twisted.internet import threads
from twisted.python.failure import Failure

from .characters import Character

FALLBACK_REPLY = "I lose my train of thought for a moment."
LLM_TIMEOUT_SECONDS = 20.0
LOG = logging.getLogger(__name__)
BUSY_TEMPLATE = "{npc_name} is thinking, please wait."


def _llm_gateway_call(prompt: str, *, trace_id: str | None = None) -> str:
    del trace_id

    api_key = getattr(settings, "LLM_API_KEY", None)
    if not api_key:
        raise RuntimeError("missing_llm_api_key")

    client = OpenAI(
        api_key=api_key,
        base_url=getattr(settings, "LLM_API_BASE", None) or None,
    )
    response = client.chat.completions.create(
        model=getattr(settings, "LLM_MODEL_NAME", "gpt-4o-mini"),
        messages=[
            {
                "role": "system",
                "content": getattr(
                    settings,
                    "LLM_SYSTEM_PROMPT",
                    "You are a helpful NPC in a text adventure.",
                ),
            },
            {"role": "user", "content": prompt},
        ],
        timeout=LLM_TIMEOUT_SECONDS,
    )

    reply_text = ""
    if response.choices and response.choices[0].message:
        reply_text = (response.choices[0].message.content or "").strip()
    if not reply_text:
        raise RuntimeError("empty_llm_reply")
    return reply_text


def _llm_reply_deferred(prompt: str, *, trace_id: str | None = None):
    return threads.deferToThread(_llm_gateway_call, prompt, trace_id=trace_id)


class LLMNPC(Character):

    def at_object_creation(self):
        super().at_object_creation()
        self.ndb.is_thinking = False

    def at_init(self):
        super().at_init()
        if getattr(self.ndb, "is_thinking", None) is None:
            self.ndb.is_thinking = False

    def at_heard_say(self, speaker, message: str, **kwargs):
        if not isinstance(message, str) or not message:
            return
        if not self.should_respond(speaker, message, **kwargs):
            return

        if getattr(self.ndb, "is_thinking", False):
            self._emit_busy()
            return

        self.ndb.is_thinking = True
        prompt = self.build_prompt(speaker, message, **kwargs)
        try:
            self._call_llm(prompt, speaker=speaker, message=message, **kwargs)
        except Exception as err:
            self._on_llm_error(err, speaker=speaker, message=message, **kwargs)

    def should_respond(self, speaker, message: str, **kwargs) -> bool:
        if not message or not isinstance(message, str):
            return False

        if speaker is self or kwargs.get("from_obj") is self:
            return False

        if not self._is_say_payload(**kwargs):
            return False

        return self._is_explicitly_addressed(message)

    def _is_say_payload(self, **kwargs) -> bool:
        if kwargs.get("is_system"):
            return False

        msg_type = (
            kwargs.get("msg_type")
            or kwargs.get("message_type")
            or kwargs.get("event_type")
            or ""
        )
        if msg_type:
            normalized = str(msg_type).strip().lower()
            return normalized in {"say", "speech", "at_say"}

        if kwargs.get("channel") or kwargs.get("is_channel"):
            return False

        return True

    def _is_explicitly_addressed(self, message: str) -> bool:
        npc_name = str(self.key or "").strip()
        if not npc_name:
            return False

        message_norm = message.casefold()
        npc_name_norm = npc_name.casefold()
        pattern = rf"(?<!\w){re.escape(npc_name_norm)}(?!\w)"
        return bool(re.search(pattern, message_norm))

    def build_prompt(self, speaker, message: str, **kwargs) -> str:
        return str(message)

    def _call_llm(self, prompt: str, **kwargs):
        trace_id = kwargs.get("trace_id") or f"{self.id}-{int(time.time() * 1000)}"
        callback_kwargs = dict(kwargs)
        callback_kwargs["trace_id"] = trace_id

        deferred = _llm_reply_deferred(prompt, trace_id=trace_id)
        deferred.addCallback(self._on_llm_success, **callback_kwargs)
        deferred.addErrback(self._on_llm_error, **callback_kwargs)
        return deferred

    def _emit_reply(self, text: str):
        line = f'{self.key} says, "{text}"'
        if self.location:
            self.location.msg_contents(line, from_obj=self)
        else:
            self.msg(line)

    def _emit_busy(self):
        line = BUSY_TEMPLATE.format(npc_name=self.key)
        if self.location:
            self.location.msg_contents(line, from_obj=self)
        else:
            self.msg(line)

    def _on_llm_success(self, reply_text: str, **kwargs):
        self.ndb.is_thinking = False
        cleaned = (reply_text or "").strip()
        if not cleaned:
            return self._on_llm_error(RuntimeError("empty_llm_reply"), **kwargs)
        self._emit_reply(cleaned)
        return cleaned

    def _on_llm_error(self, error: Exception | Failure, **kwargs):
        self.ndb.is_thinking = False

        exc: Any = error.value if isinstance(error, Failure) else error
        trace_id = kwargs.get("trace_id", "unknown")
        speaker = kwargs.get("speaker")
        speaker_key = getattr(speaker, "key", "unknown")
        LOG.error(
            "LLMNPC call failed trace_id=%s npc=%s speaker=%s error=%r",
            trace_id,
            self.key,
            speaker_key,
            exc,
        )

        self._emit_reply(FALLBACK_REPLY)
        return None
