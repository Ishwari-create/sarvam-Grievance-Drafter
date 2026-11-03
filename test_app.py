import os
import unittest
from io import BytesIO

os.environ.setdefault("SARVAM_API_KEY", "test-key")

import app as app_module


class TranscribeRouteTests(unittest.TestCase):
    def test_transcribe_uses_supported_model_and_wav_content_type(self):
        captured = {}

        class FakeSpeechToText:
            @staticmethod
            def transcribe(**kwargs):
                captured.update(kwargs)
                class Response:
                    transcript = "hello from the complaint"
                return Response()

        class FakeClient:
            speech_to_text = FakeSpeechToText()

        original_client = app_module.client
        app_module.client = FakeClient()
        try:
            client = app_module.app.test_client()
            response = client.post(
                "/transcribe",
                data={
                    "audio": (BytesIO(b"fake-audio-bytes"), "recording.webm", "audio/webm")
                },
                content_type="multipart/form-data",
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(captured["model"], "saaras:v2")
            self.assertEqual(captured["file"][2], "audio/wav")
        finally:
            app_module.client = original_client


if __name__ == "__main__":
    unittest.main()
