import contextlib
import io
import json
import os
import unittest
import urllib.error
from unittest.mock import patch

import free_ai_review as review


class ReviewTests(unittest.TestCase):
    def run_case(self, provider="openrouter", key=None, response=None, error=None, prompt="Smoke test"):
        secret = review.PROVIDERS.get(provider, ("UNUSED",))[0]
        key = key or "test-secret-" + "a" * 40
        env = {"PROVIDER": provider, "PROMPT": prompt, secret: key}
        stream = io.StringIO()
        with patch.dict(os.environ, env, clear=True), patch.object(review.urllib.request, "urlopen") as opened, contextlib.redirect_stdout(stream):
            if error:
                opened.side_effect = error
            else:
                opened.return_value.__enter__.return_value = io.BytesIO(json.dumps(response or {}).encode())
            try:
                result = review.main()
            except SystemExit as exc:
                result = exc.code
        return result, opened, stream.getvalue()

    def test_success_has_one_request_and_fixed_free_model(self):
        for provider in review.PROVIDERS:
            data = {"choices": [{"message": {"content": "OK"}}]}
            result, opened, output = self.run_case(provider, response=data)
            self.assertEqual(result, 0)
            opened.assert_called_once()
            request = opened.call_args.args[0]
            body = json.loads(request.data)
            self.assertEqual(opened.call_args.kwargs["timeout"], 100)
            self.assertEqual(request.get_header("User-agent"), "Fisher-Free-AI-Review/1.0")
            self.assertEqual(body["model"], review.PROVIDERS[provider][2])
            self.assertEqual(body["max_tokens"], 512)
            self.assertIn("Provider output: OK", output)

    def test_short_masked_or_whitespace_keys_make_no_request(self):
        for key in ("sk-or-v1-244", "test-secret-" + "a" * 30 + "\u2022", "test-secret-" + "a" * 30 + " x"):
            result, opened, _ = self.run_case(key=key)
            self.assertIsInstance(result, str)
            opened.assert_not_called()

    def test_invalid_provider_or_prompt_makes_no_request(self):
        for args in ({"provider": "paid-provider"}, {"prompt": " "}, {"prompt": "a" * 1001}):
            result, opened, _ = self.run_case(**args)
            self.assertIsInstance(result, str)
            opened.assert_not_called()

    def test_error_diagnostics_redact_key_and_do_not_retry(self):
        key = "test-secret-" + "x" * 40
        error = urllib.error.HTTPError("https://openrouter.ai", 403, "Forbidden", {}, io.BytesIO(json.dumps({"error": {"code": "permissions_error", "message": "Invalid key " + key}}).encode()))
        result, opened, output = self.run_case(key=key, error=error)
        self.assertEqual(result, 1)
        opened.assert_called_once()
        self.assertIn("permissions_error", output)
        self.assertNotIn(key, output)

    def test_timeout_stops_without_retry(self):
        result, opened, output = self.run_case(error=TimeoutError())
        self.assertEqual(result, 1)
        opened.assert_called_once()
        self.assertIn("without retry or paid fallback", output)

    def test_empty_answer_is_failure(self):
        result, opened, _ = self.run_case(response={"choices": []})
        self.assertEqual(result, 1)
        opened.assert_called_once()

    def test_provider_output_cannot_emit_workflow_commands(self):
        result, _, output = self.run_case(response={"choices": [{"message": {"content": "::error::injected\nOK"}}]})
        self.assertEqual(result, 0)
        self.assertNotIn("\n::error::", output)
        self.assertIn("Provider output: ::error::injected", output)


if __name__ == "__main__":
    unittest.main()
