# Scroll World — Pipeline Pitfalls

- **Slideshow video** — ban prompts that only say smooth morph/fly forward; require Transition plan + anti-slideshow clause (`shared/cinematic-transition-contract.md`).
- **Postcard storyboard** — panels must be one continuous camera path, not palette-matched unrelated cards.
- **Overwrite assets** — never replace `001-*`; new gens are `002-*` (`shared/asset-versioning-contract.md`).
- **English UI to user** — questions/options/gates must be Russian with short explanations; never bare `embed` / `demo-page`.
- **Wrong Seedance mode** — do not mix `first_frame_url`/`last_frame_url` with `reference_*` arrays.
- **Thin video prompt** — Seedance 2 Mini needs **≥ 800** chars (target 1200–4000); use full template with timed beats.
- **Beats without observable end-state** — every timed beat must end with `by Xs: …` (readable visual state); bare “continue dolly” without a landable outcome is invalid (P0).
- **Settle too short / late zoom** — LANDING CONTRACT settle must be **0.4–0.6s**; no zoom, crop, or silhouette change after settle starts.
- **Beat budget violation** — e.g. 4s leg with 5 morphs/camera beats; respect skill table (4–6s → 2–3 camera beats; object-transform ≤ same caps). Use `short_clip_variant` when `duration_sec ≤ 5`.
- **Plate locks = journey paraphrase** — structured locks must come from a **live PNG read**, not copied Transition plan / `video_prompt_seed` prose (P2).
- **Tech dump in Kie prompt** — never put `480p` / `720p` / API SETTINGS / duration-as-settings into the prompt string; resolution and duration are CLI only.
- **Missing COUNT/EXCLUSIONS** — without explicit counts and exclusions Seedance invents props and subtitle/UI drift; always fill COUNT & EXCLUSIONS (P1).
- **Whole .md dumped into Kie prompt** — `generate_storyboard_panels.py` / Seedance must send **only** the ```text fence. Slug, M, grid, mode, «if Kie 2K fails…» are agent notes OUTSIDE the fence. Script extracts fence; missing fence (storyboard) or meta leak inside fence → hard fail.
- **Slice without board AR gate** — never equal-grid slice a board whose pixel AR is narrower than the contact-sheet target (e.g. Kie returned **2:1** / flipped 2×3 when asked **3:1** for 3×2×16:9). `validate_board_pixels_for_grid` must hard-fail before crop; regenerate board, do not «fix» with centre-crop.
- **Board-level centre-crop before equal-grid** — when Kie paints a full-bleed 3:1 contact sheet, cropping the board to 8:3 shifts column gutters → adjacent-panel bleed / left-sliver on cells (003-frame-06). Correct path: equal-grid on **full** board → **per-cell** crop to 16:9.
- **Slice without cell content gate** — after crop, each cell must pass empty/edge-cut/**seam** QA (`validate_sliced_cells_content`). Passing only `aspect_close` is not enough.
- **Pipeline meta in Kie prompt** — no FRAME SOURCES, previous/next leg, storyboard, preserve rendered; chain is in URLs only (`shared/kie-prompt-contract.md`).
- **Pipeline refs in Kie prompt** — never mention leg N, MP4, prior tasks, or storyboard filenames; Kie only sees two uploaded images + prompt.
- **Wrong leg order** — leg `i>0` needs active leg `i−1` in manifest; generate 0→1→…
- **Storyboard start for leg>0** — default start is prev MP4 last frame, not `frame-02` PNG.
- **Re-gen leg k without k+1…** — chain breaks; regen downstream legs after fixing leg k.
- **Baked text** — never put copy in storyboard/video prompts; use `overlays.json`.
- **Aspect mismatch** — panels and Seedance legs must share `media_aspect_ratio`; ask on intake (`shared/media-format-contract.md`).
- **9:16 parallel chain** — no second chain in another aspect; one `media_aspect_ratio` per project.
- **Architecture B** — connectors out of scope v1; use sequential first/last legs.
- **Gate skip** — never generate storyboard before plain pitch approve (`04-journey-pitch.md`); never generate all videos before Gate Storyboard + Gate First Video.
- **Skip plain pitch gate** — do not replace user-facing pitch with M/Kie/Seedance budget jargon; show `04-journey-pitch.md` verbatim; keep `04-budget.md` internal.
- **Sparse playback_chain** — forbidden; must be contiguous prefix `[1..K]` with K≤M (no gaps / non-prefix sets).
- **Paste prompt_snippet into journey** — journey uses codes / `duration_sec` / Russian pitch; do not dump EN registry `prompt_snippet` into `03-journey.md` or pitch.
- **Hard-block 4s transforms** — if `duration_sec` below registry comfort: WARN + adapt mechanic/prompt; never refuse generation solely for 4s.
- **gpt-image-2 4K traps** — `1:1` cannot be 4K (script falls back to 2K).
- **Re-slice без нужды** — кадры нарезаются автоматически внутри `generate_storyboard_panels.py`; повторный `slice_storyboard.py` — только repair. Aspect mismatch при slice — ремонт новой генерацией board, не ослаблением gate.
- **Seam quality** — first/last via prompt may drift; always Gate First Video; surgical re-prompt before full chain.
- **Single-frame seam check** — never compare only the final frame of leg `i` to
  the first frame of leg `i+1`. After every encode run
  `scripts/check_seam_compatibility.py --window 5`; inspect the complete
  `last[5] × first[5]` matrix, best pair, MAE and suggested trim. A `REVIEW`
  result blocks publish until fixed or explicitly accepted.
- **Storyboard stills in scrub** — one section per leg (`still` + `clip`); posters from encoded video first frames; no still-only bookends (`shared/scrub-still-contract.md`).
- **Seam playback** — hard cut between dive legs; hold outgoing until incoming paints; centred crop; no dive-leg crossfade (`shared/seam-playback-contract.md`). Never “fix” seams by lowering `crossfade` below 0.08 — causes white flash.
- **Fixic scope** — durable plugin fixes only; do not commit run media.
- **Manual Kie smoke** — never call `createTask` with `example.com` URLs or prompt `test`. Storyboard only via `generate_storyboard_panels.py`; video only via `kie_seedance_2_mini.py --prompt-file …`. Use `--dry-run` to validate before spend.
