#!/usr/bin/env python3
"""Kie.ai File Upload API — https://docs.kie.ai/file-upload-api/quickstart

Base: https://kieai.redpandaai.co
Auth: Authorization: Bearer <KIE_API_KEY>

Methods:
  POST /api/file-stream-upload   — local binary (recommended for PNG/MP4)
  POST /api/file-url-upload     — remote HTTPS URL
  POST /api/file-base64-upload  — small files ≤10MB (Data URL)

Files are temporary (~3 days / URL ~24h). Prefer fileUrl from response.
"""

from __future__ import annotations

import argparse
import base64
import mimetypes
import os
import time
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError as exc:
    raise SystemExit("Install requests: pip install requests") from exc

from kie_common import load_api_key

DEFAULT_UPLOAD_BASE = "https://kieai.redpandaai.co"
DEFAULT_UPLOAD_PATH = "scroll-world"


class KieFileUploadClient:
    """Official Kie File Upload client (separate from jobs API base)."""

    def __init__(
        self,
        api_key: str | None = None,
        upload_base: str | None = None,
        workspace: Path | str | None = None,
    ) -> None:
        self.api_key = load_api_key(api_key, workspace=workspace)
        self.upload_base = (
            upload_base or os.getenv("KIE_FILE_UPLOAD_BASE") or DEFAULT_UPLOAD_BASE
        ).rstrip("/")
        # Docs: Authorization only — do NOT set Content-Type for multipart stream.
        self._auth_headers = {"Authorization": f"Bearer {self.api_key}"}

    def _extract_file_url(self, body: dict[str, Any]) -> str:
        """Prefer data.fileUrl (canonical public URL), then downloadUrl."""
        if body.get("success") is False and body.get("code") not in (200, None):
            raise RuntimeError(f"Kie upload failed: {body.get('msg', body)}")
        code = body.get("code")
        if code is not None and code != 200:
            raise RuntimeError(f"Kie upload failed: {body.get('msg', body)}")
        data = body.get("data") or {}
        url = data.get("fileUrl") or data.get("downloadUrl")
        if not url or not str(url).startswith("http"):
            raise RuntimeError(f"No fileUrl/downloadUrl in response: {body}")
        return str(url)

    def _wrap(self, body: dict[str, Any]) -> dict[str, Any]:
        url = self._extract_file_url(body)
        body = dict(body)
        body["publicUrl"] = url
        data = body.get("data") or {}
        body["fileUrl"] = data.get("fileUrl") or url
        body["downloadUrl"] = data.get("downloadUrl")
        body["fileId"] = data.get("fileId")
        body["expiresAt"] = data.get("expiresAt")
        return body

    def upload_stream(
        self,
        local_path: Path | str,
        upload_path: str = DEFAULT_UPLOAD_PATH,
        file_name: str | None = None,
        timeout: float = 300,
    ) -> dict[str, Any]:
        """POST /api/file-stream-upload — local files (docs: recommended for large/local)."""
        local_path = Path(local_path)
        if not local_path.is_file():
            raise FileNotFoundError(local_path)

        name = file_name or local_path.name
        mime, _ = mimetypes.guess_type(name)
        mime = mime or "application/octet-stream"

        last_err: Exception | None = None
        for attempt in range(1, 4):
            try:
                with local_path.open("rb") as fh:
                    files: dict[str, Any] = {
                        "file": (name, fh, mime),
                        "uploadPath": (None, upload_path),
                    }
                    if file_name or name:
                        files["fileName"] = (None, name)
                    resp = requests.post(
                        f"{self.upload_base}/api/file-stream-upload",
                        headers=self._auth_headers,
                        files=files,
                        timeout=timeout,
                    )
                break
            except requests.RequestException as exc:
                last_err = exc
                if attempt < 3:
                    time.sleep(2 * attempt)
                    continue
                if local_path.stat().st_size <= 10 * 1024 * 1024:
                    print(
                        f"WARN: stream upload failed ({exc}); falling back to base64",
                        flush=True,
                    )
                    return self.upload_base64(
                        local_path, upload_path=upload_path, file_name=name, timeout=timeout
                    )
                raise
        else:
            if last_err:
                raise last_err
            raise RuntimeError("upload_stream failed without response")
        if resp.status_code == 401:
            raise RuntimeError("401 Unauthorized — check KIE_API_KEY")
        if not resp.ok:
            raise RuntimeError(f"Stream upload failed HTTP {resp.status_code}: {resp.text}")
        return self._wrap(resp.json())

    def upload_from_url(
        self,
        file_url: str,
        upload_path: str = DEFAULT_UPLOAD_PATH,
        file_name: str | None = None,
        timeout: float = 120,
    ) -> dict[str, Any]:
        """POST /api/file-url-upload — remote publicly accessible URL."""
        payload: dict[str, Any] = {
            "fileUrl": file_url,
            "uploadPath": upload_path,
        }
        if file_name:
            payload["fileName"] = file_name

        resp = requests.post(
            f"{self.upload_base}/api/file-url-upload",
            headers={**self._auth_headers, "Content-Type": "application/json"},
            json=payload,
            timeout=timeout,
        )
        if resp.status_code == 401:
            raise RuntimeError("401 Unauthorized — check KIE_API_KEY")
        if not resp.ok:
            raise RuntimeError(f"URL upload failed HTTP {resp.status_code}: {resp.text}")
        return self._wrap(resp.json())

    def upload_base64(
        self,
        local_path: Path | str,
        upload_path: str = DEFAULT_UPLOAD_PATH,
        file_name: str | None = None,
        timeout: float = 300,
    ) -> dict[str, Any]:
        """POST /api/file-base64-upload — small files ≤10MB as Data URL."""
        local_path = Path(local_path)
        if not local_path.is_file():
            raise FileNotFoundError(local_path)
        mime, _ = mimetypes.guess_type(local_path.name)
        mime = mime or "application/octet-stream"
        raw = local_path.read_bytes()
        if len(raw) > 10 * 1024 * 1024:
            raise ValueError(
                f"File too large for base64 ({len(raw)} bytes); use upload_stream"
            )
        data_url = f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"
        name = file_name or local_path.name
        payload = {
            "base64Data": data_url,
            "uploadPath": upload_path,
            "fileName": name,
        }
        resp = requests.post(
            f"{self.upload_base}/api/file-base64-upload",
            headers={**self._auth_headers, "Content-Type": "application/json"},
            json=payload,
            timeout=timeout,
        )
        if resp.status_code == 401:
            raise RuntimeError("401 Unauthorized — check KIE_API_KEY")
        if not resp.ok:
            raise RuntimeError(f"Base64 upload failed HTTP {resp.status_code}: {resp.text}")
        return self._wrap(resp.json())

    def upload_local(
        self,
        local_path: Path | str,
        upload_path: str = DEFAULT_UPLOAD_PATH,
        file_name: str | None = None,
    ) -> str:
        """Stream upload for local images/video; return HTTPS fileUrl."""
        meta = self.upload_stream(
            local_path, upload_path=upload_path, file_name=file_name or Path(local_path).name
        )
        return meta["publicUrl"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload file to Kie CDN (docs.kie.ai/file-upload-api/quickstart)"
    )
    parser.add_argument("--file", type=Path, default=None, help="Local file (stream/base64)")
    parser.add_argument("--url", type=str, default=None, help="Remote HTTPS URL (url-upload)")
    parser.add_argument("--method", choices=["stream", "url", "base64", "auto"], default="auto")
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--upload-path", default=DEFAULT_UPLOAD_PATH)
    parser.add_argument("--file-name", default=None)
    parser.add_argument("--json", action="store_true", help="Print full JSON response")
    args = parser.parse_args()

    client = KieFileUploadClient(workspace=args.workspace)
    method = args.method
    if method == "auto":
        if args.url:
            method = "url"
        elif args.file:
            method = "stream"
        else:
            raise SystemExit("Provide --file and/or --url")

    if method == "stream":
        if not args.file:
            raise SystemExit("--file required for stream")
        meta = client.upload_stream(args.file, args.upload_path, args.file_name)
    elif method == "base64":
        if not args.file:
            raise SystemExit("--file required for base64")
        meta = client.upload_base64(args.file, args.upload_path, args.file_name)
    elif method == "url":
        if not args.url:
            raise SystemExit("--url required for url method")
        meta = client.upload_from_url(args.url, args.upload_path, args.file_name)
    else:
        raise SystemExit(f"Unknown method: {method}")

    if args.json:
        import json

        print(json.dumps(meta, ensure_ascii=False, indent=2))
    else:
        print(meta["publicUrl"])


if __name__ == "__main__":
    main()
