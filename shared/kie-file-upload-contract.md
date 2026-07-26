# Scroll World — Kie File Upload (official)

Docs: https://docs.kie.ai/file-upload-api/quickstart

## Base URL

```text
https://kieai.redpandaai.co
```

Env override: `KIE_FILE_UPLOAD_BASE` (default above).  
**Not** `https://api.kie.ai` — jobs API and file upload hosts differ.

## Auth

```http
Authorization: Bearer <KIE_API_KEY>
```

Same key as image/video jobs (`KIE_API_KEY` in `.env`).

## Methods

| Method | Endpoint | When |
|--------|----------|------|
| **Stream** (default for local frames) | `POST /api/file-stream-upload` | Local PNG/MP4; multipart `file` + `uploadPath` + optional `fileName` |
| URL | `POST /api/file-url-upload` | Already-public HTTPS URL; JSON `{ fileUrl, uploadPath, fileName? }` |
| Base64 | `POST /api/file-base64-upload` | Small files ≤10MB; JSON `{ base64Data: data:…;base64,…, uploadPath, fileName? }` |

### Stream (official shape)

```bash
curl -X POST "https://kieai.redpandaai.co/api/file-stream-upload" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@/path/to/frame.png" \
  -F "uploadPath=scroll-world/<slug>" \
  -F "fileName=001-frame-01.png"
```

Do **not** set `Content-Type: application/json` on stream requests.

### Response

Prefer `data.fileUrl` (then `data.downloadUrl`) as HTTPS input for `first_frame_url` / `last_frame_url` in Seedance video jobs.

```json
{
  "success": true,
  "code": 200,
  "data": {
    "fileUrl": "https://…",
    "downloadUrl": "https://…",
    "fileId": "…",
    "expiresAt": "…"
  }
}
```

## Retention

Uploads are **temporary** (docs: deleted after ~3 days; URL validity ~24h). Upload frames **immediately before** `createTask` for video — do not reuse stale URLs days later.

## Plugin scripts

| Script | Role |
|--------|------|
| `scripts/kie_file_upload.py` | Client + CLI (`--method stream\|url\|base64`) |
| `scripts/kie_upload.py` | Alias CLI |
| `scripts/kie_seedance_2_mini.py` | Uploads start/end via `upload_stream` then creates Seedance task |

```bash
python scripts/kie_file_upload.py --file assets/frames/001-frame-01.png \
  --upload-path scroll-world/<slug> --file-name 001-frame-01.png
```

## Defaults

- `uploadPath`: `scroll-world` or `scroll-world/<project-slug>`
- `fileName`: local basename (versioned `NNN-frame-II.png` / `NNN-leg-LL.mp4`)
- Overwrite: same `uploadPath`+`fileName` may overwrite on CDN — for versions use unique `fileName` (already true with `001`/`002` prefixes)
