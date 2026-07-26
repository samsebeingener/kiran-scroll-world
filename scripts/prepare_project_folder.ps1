param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,
    [Parameter(Mandatory = $true)]
    [string]$Slug
)

$ErrorActionPreference = "Stop"
$dest = Join-Path $ProjectRoot "projects\scroll-world\$Slug"

$dirs = @(
    "",
    "assets\storyboard",
    "assets\frames",
    "assets\video\legs",
    "assets\encoded",
    "src",
    "fragments",
    "05-image-prompts"
)

foreach ($d in $dirs) {
    $path = if ($d) { Join-Path $dest $d } else { $dest }
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}

@"
# Scroll World — новая сессия

slug: $Slug
"@ | Set-Content -Encoding utf8 (Join-Path $dest "01-handoff.md")

@"
{
  "slug": "$Slug",
  "status": "brief",
  "frames": null,
  "media_aspect_ratio": null,
  "storyboard_resolution": "2K",
  "video_model": "bytedance/seedance-2-mini",
  "insert_placement": null,
  "video_resolution": "480p",
  "video_duration": 4,
  "integration_mode": "demo-page"
}
"@ | Set-Content -Encoding utf8 (Join-Path $dest "project.meta.json")

@"
# Pipeline fix queue

status: empty
"@ | Set-Content -Encoding utf8 (Join-Path $dest "pipeline-fix-queue.md")

Write-Host "Created $dest"
