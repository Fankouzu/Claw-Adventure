from __future__ import annotations

import logging
import re
import time
import unicodedata
from typing import Any

from django.conf import settings
from evennia import logger
from evennia.commands.cmdset import CmdSet
from evennia.commands.default.muxcommand import MuxCommand
from openai import OpenAI
from twisted.internet import threads
from twisted.python.failure import Failure

from .characters import Character

FALLBACK_REPLY = "I lose my train of thought for a moment."
LLM_TIMEOUT_SECONDS = 20.0
LOG = logging.getLogger(__name__)
BUSY_TEMPLATE = "{npc_name} is thinking, please wait."
TYPECLASS_PATHS = {"typeclasses.llm_npc.LLMNPC", "llm_npc.LLMNPC"}
ASCII_WORD_RE = re.compile(r"[a-z0-9_]+")
CJK_RUN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]+")


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


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return unicodedata.normalize("NFKC", str(value)).strip().casefold()


def _extract_message_text(text: Any) -> tuple[str, dict[str, Any]]:
    payload: dict[str, Any] = {}
    raw = text

    while isinstance(raw, (tuple, list)) and len(raw) > 0:
        if len(raw) > 1 and isinstance(raw[1], dict):
            payload.update(raw[1])
        raw = raw[0]

    if raw is None:
        return "", payload
    if isinstance(raw, str):
        return raw, payload
    return str(raw), payload


def _iter_name_keywords(name: str) -> set[str]:
    normalized = _normalize_text(name)
    if not normalized:
        return set()

    keywords = {normalized}
    for token in ASCII_WORD_RE.findall(normalized):
        if len(token) >= 2:
            keywords.add(token)

    for chunk in CJK_RUN_RE.findall(normalized):
        if len(chunk) < 2:
            continue
        keywords.add(chunk)
        max_size = min(4, len(chunk))
        for size in range(2, max_size + 1):
            for idx in range(0, len(chunk) - size + 1):
                keywords.add(chunk[idx : idx + size])

    return {keyword for keyword in keywords if keyword}


def _is_llm_npc(obj: Any) -> bool:
    if not obj:
        return False
    if getattr(obj, "typeclass_path", "") in TYPECLASS_PATHS:
        return True
    return obj.__class__.__name__ == "LLMNPC"


def _find_matching_npc(caller, query: str):
    location = getattr(caller, "location", None)
    if not location:
        return None

    query_norm = _normalize_text(query)
    if not query_norm:
        return None

    exact: list[Any] = []
    fuzzy: list[Any] = []

    for obj in location.contents:
        if not _is_llm_npc(obj):
            continue

        keywords = obj._name_keywords() if hasattr(obj, "_name_keywords") else set()
        obj_key_norm = _normalize_text(getattr(obj, "key", ""))
        if query_norm == obj_key_norm or query_norm in keywords:
            exact.append(obj)
            continue

        if len(query_norm) >= 2 and any(query_norm in keyword for keyword in keywords):
            fuzzy.append(obj)

    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        return exact
    if len(fuzzy) == 1:
        return fuzzy[0]
    if len(fuzzy) > 1:
        return fuzzy
    return None


class CmdAskNPC(MuxCommand):
    key = "ask"
    locks = "cmd:all()"
    help_category = "General"
    rhs_split = ("=",)

    def func(self):
        caller = self.caller
        target_name = (self.lhs or "").strip()
        message = (self.rhs or "").strip()
        if not target_name or not message:
            caller.msg("Usage: ask <npc名字> = <对他说的话>")
            return

        target = _find_matching_npc(caller, target_name)
        if isinstance(target, list):
            caller.msg("Ask which NPC? " + ", ".join(obj.key for obj in target))
            return
        if not target:
            caller.msg(f"Could not find '{target_name}'.")
            return

        target.handle_player_input(caller, message, force=True, msg_type="ask")


class LLMNPCInteractionCmdSet(CmdSet):
    key = "LLMNPCInteraction"

    def at_cmdset_creation(self):
        self.add(CmdAskNPC())


class LLMNPC(Character):
    @classmethod
    def normalize_name(cls, name):
        return str(name).strip()

    def at_object_creation(self):
        super().at_object_creation()
        self.ndb.is_thinking = False
        self._ensure_cmdset()
        self.locks.add("call:all()")

    def at_init(self):
        super().at_init()
        if getattr(self.ndb, "is_thinking", None) is None:
            self.ndb.is_thinking = False
        self._ensure_cmdset()
        self.locks.add("call:all()")

    def at_msg_receive(self, text=None, from_obj=None, **kwargs):
        logger.log_info(
            f"LLMNPC at_msg_receive key={self.key!r} raw_text={text!r} from_obj={from_obj!r} kwargs={kwargs!r}"
        )
        message, payload = _extract_message_text(text)
        merged_kwargs = dict(payload)
        merged_kwargs.update(kwargs)
        self.handle_player_input(from_obj, message, **merged_kwargs)
        return True

    def at_heard_say(self, speaker, message: str, **kwargs):
        self.handle_player_input(speaker, message, **kwargs)

    def handle_player_input(self, speaker, message: str, force: bool = False, **kwargs) -> bool:
        if not isinstance(message, str):
            return False
        message = message.strip()
        if not message:
            return False

        if not force and not self.should_respond(speaker, message, **kwargs):
            return False

        if getattr(self.ndb, "is_thinking", False):
            self._emit_busy()
            return True

        self.ndb.is_thinking = True
        prompt = self.build_prompt(speaker, message, **kwargs)
        try:
            self._call_llm(prompt, speaker=speaker, message=message, **kwargs)
        except Exception as err:
            self._on_llm_error(err, speaker=speaker, message=message, **kwargs)
        return True

    def should_respond(self, speaker, message: str, **kwargs) -> bool:
        if not message or not isinstance(message, str):
            return False
        if not speaker or speaker is self or kwargs.get("from_obj") is self:
            return False
        if self.location and getattr(speaker, "location", None) is not self.location:
            return False

        has_account = getattr(speaker, "has_account", None)
        if has_account is False:
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
            or kwargs.get("type")
            or ""
        )
        if msg_type:
            normalized = str(msg_type).strip().lower()
            return normalized in {"say", "speech", "at_say", "ask"}

        if kwargs.get("channel") or kwargs.get("is_channel"):
            return False
        return True

    def _name_keywords(self) -> set[str]:
        keywords = _iter_name_keywords(getattr(self, "key", ""))
        try:
            for alias in self.aliases.all():
                keywords.update(_iter_name_keywords(alias))
        except Exception:
            pass
        return keywords

    def _is_explicitly_addressed(self, message: str) -> bool:
        normalized_message = _normalize_text(message)
        if not normalized_message:
            return False

        for keyword in self._name_keywords():
            if CJK_RUN_RE.search(keyword):
                if keyword in normalized_message:
                    return True
                continue

            pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"
            if re.search(pattern, normalized_message):
                return True
        return False

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

    def _ensure_cmdset(self):
        if not self.cmdset.has(LLMNPCInteractionCmdSet):
            self.cmdset.add_default(LLMNPCInteractionCmdSet, persistent=True)
