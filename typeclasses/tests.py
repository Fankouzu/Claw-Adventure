from __future__ import annotations

from unittest.mock import Mock, patch

from evennia.utils.create import create_object
from typeclasses.llm_npc import CmdAskNPC
from typeclasses.llm_npc import LLMNPC
from evennia.utils.test_resources import EvenniaTest
from evennia.utils.utils import class_from_module
from twisted.internet import defer
from twisted.internet.defer import Deferred


class TestLLMNPC(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.npc = create_object(
            "typeclasses.llm_npc.LLMNPC",
            key="LLMNPC",
            location=self.room1,
        )
        self.room1.msg_contents = Mock()

    def test_success_trigger_addressed_say_calls_llm_and_emits_reply(self):
        msg = "LLMNPC, hello"
        with patch("typeclasses.llm_npc._llm_reply_deferred") as seam:
            seam.return_value = defer.succeed("mock reply")

            self.npc.at_heard_say(self.char1, msg)

        seam.assert_called_once()
        called_prompt = seam.call_args.args[0]
        self.assertEqual(called_prompt, msg)
        self.assertIn("trace_id", seam.call_args.kwargs)

        self.room1.msg_contents.assert_called_once()
        emitted_line = self.room1.msg_contents.call_args.args[0]
        self.assertEqual(emitted_line, 'LLMNPC says, "mock reply"')
        self.assertIs(self.room1.msg_contents.call_args.kwargs.get("from_obj"), self.npc)
        self.assertFalse(getattr(self.npc.ndb, "is_thinking", True))

    def test_short_typeclass_path_creates_llm_npc(self):
        resolved = class_from_module("llm_npc.LLMNPC")

        self.assertIs(resolved, self.npc.__class__)

    def test_llmnpc_create_preserves_non_latin_key(self):
        npc, errors = LLMNPC.create("暴躁小二", location=self.room1)

        self.assertEqual(errors, [])
        self.assertIsNotNone(npc)
        self.assertEqual(npc.key, "暴躁小二")
        self.assertEqual(npc.db_key, "暴躁小二")
        npc.delete()

    def test_at_msg_receive_parses_tuple_say_payload(self):
        self.npc.key = "暴躁的小二"
        payload = ("小二，来壶酒", {"type": "say"})

        with patch("typeclasses.llm_npc._llm_reply_deferred") as seam:
            seam.return_value = defer.succeed("mock reply")
            self.npc.at_msg_receive(payload, from_obj=self.char1)

        seam.assert_called_once()
        self.assertEqual(seam.call_args.args[0], "小二，来壶酒")

    def test_fuzzy_matching_accepts_partial_chinese_keyword(self):
        self.npc.key = "暴躁的小二"

        self.assertTrue(self.npc._is_explicitly_addressed("小二，给我切两斤牛肉"))
        self.assertFalse(self.npc._is_explicitly_addressed("掌柜的，出来一下"))

    def test_ask_command_forces_npc_interaction(self):
        self.npc.key = "暴躁的小二"
        command = CmdAskNPC()
        command.caller = self.char1
        command.obj = self.npc
        command.lhs = "小二"
        command.rhs = "给我切两斤牛肉"
        command.args = "小二 = 给我切两斤牛肉"

        with patch("typeclasses.llm_npc._llm_reply_deferred") as seam:
            seam.return_value = defer.succeed("mock reply")
            command.func()

        seam.assert_called_once()
        self.assertEqual(seam.call_args.args[0], "给我切两斤牛肉")

    def test_ignore_path_non_addressed_say_does_nothing(self):
        msg = "hello everyone"
        with patch("typeclasses.llm_npc._llm_reply_deferred") as seam:
            seam.return_value = defer.succeed("should not be used")
            self.npc.at_heard_say(self.char1, msg)

        seam.assert_not_called()
        self.room1.msg_contents.assert_not_called()
        self.assertFalse(getattr(self.npc.ndb, "is_thinking", True))

    def test_lock_path_second_addressed_input_emits_busy_and_does_not_queue_llm(self):
        d: Deferred[str] = Deferred()
        with patch("typeclasses.llm_npc._llm_reply_deferred") as seam:
            seam.return_value = d

            self.npc.at_heard_say(self.char1, "LLMNPC, first")
            self.assertTrue(getattr(self.npc.ndb, "is_thinking", False))
            seam.assert_called_once()

            self.npc.at_heard_say(self.char1, "LLMNPC, second")

            self.assertEqual(seam.call_count, 1)
            self.room1.msg_contents.assert_called_once()
            busy_line = self.room1.msg_contents.call_args.args[0]
            self.assertEqual(busy_line, "LLMNPC is thinking, please wait.")

            d.callback("mock reply")

        self.assertEqual(self.room1.msg_contents.call_count, 2)
        reply_line = self.room1.msg_contents.call_args_list[1].args[0]
        self.assertEqual(reply_line, 'LLMNPC says, "mock reply"')
        self.assertFalse(getattr(self.npc.ndb, "is_thinking", True))

    def test_fallback_error_path_llm_failure_emits_fallback_and_releases_lock(self):
        msg = "LLMNPC, are you there?"
        with patch("typeclasses.llm_npc._llm_reply_deferred") as seam:
            seam.return_value = defer.fail(RuntimeError("boom"))

            self.npc.at_heard_say(self.char1, msg)

        seam.assert_called_once()
        self.room1.msg_contents.assert_called_once()
        emitted_line = self.room1.msg_contents.call_args.args[0]
        self.assertEqual(emitted_line, 'LLMNPC says, "I lose my train of thought for a moment."')
        self.assertFalse(getattr(self.npc.ndb, "is_thinking", True))

    def test_malformed_payload_non_string_does_not_crash_or_call_llm(self):
        class ExplodingBoolPayload:
            def __bool__(self):
                raise TypeError("malformed payload")

        payload = ExplodingBoolPayload()
        with patch("typeclasses.llm_npc._llm_reply_deferred") as seam:
            self.npc.at_heard_say(self.char1, payload)

        seam.assert_not_called()
        self.room1.msg_contents.assert_not_called()
        self.assertFalse(getattr(self.npc.ndb, "is_thinking", True))

    def test_from_obj_none_and_speaker_none_is_ignored(self):
        msg = "LLMNPC, status?"
        with patch("typeclasses.llm_npc._llm_reply_deferred") as seam:
            self.npc.at_heard_say(None, msg, from_obj=None)

        seam.assert_not_called()
        self.room1.msg_contents.assert_not_called()
        self.assertFalse(getattr(self.npc.ndb, "is_thinking", True))

    def test_sync_llm_setup_error_releases_lock_for_next_attempt(self):
        addressed = "LLMNPC, hello"
        with patch.object(self.npc, "_call_llm", side_effect=RuntimeError("setup boom")) as fail_call:
            self.npc.at_heard_say(self.char1, addressed)
        fail_call.assert_called_once()
        self.assertEqual(self.room1.msg_contents.call_count, 1)
        fallback_line = self.room1.msg_contents.call_args_list[0].args[0]
        self.assertEqual(fallback_line, 'LLMNPC says, "I lose my train of thought for a moment."')
        self.assertFalse(getattr(self.npc.ndb, "is_thinking", True))

        with patch("typeclasses.llm_npc._llm_reply_deferred") as seam:
            seam.return_value = defer.succeed("recovered")
            self.npc.at_heard_say(self.char1, addressed)

        seam.assert_called_once()
        self.assertEqual(self.room1.msg_contents.call_count, 2)
        recovered_line = self.room1.msg_contents.call_args_list[1].args[0]
        self.assertEqual(recovered_line, 'LLMNPC says, "recovered"')
        self.assertFalse(getattr(self.npc.ndb, "is_thinking", True))
