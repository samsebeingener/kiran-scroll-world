# Object Transform Registry — Scroll World

Реестр **механик смены объекта / формы** внутри видео-ноги. Коды ниже — объектные механики (как предмет меняется), а не жанровые type-коды из `cinematic-transition-contract.md` (fly / whip / orbit / push и т.п.). На одном leg можно сочетать: cinematic type задаёт камеру/переход, object transform — что происходит с субъектом.

## Soft timing (не хард-блок)

1. **Приоритет:** длительность, выбранная пользователем (в т.ч. **4s**) > таблица comfort.
2. Таблица `comfort_sec` / `warn_below_sec` — **мягкие рекомендации**, не гейт-блокер. Пользователь может взять 4s для любой механики.
3. На Gate Pitch / First Video: если `duration_sec < warn_below_sec` (или ниже comfort) — **предупредить по-русски** в чате («на 4s лучше упростить / сжать / сменить механику»), затем **адаптировать** mechanic + EN prompt, **не отказывать**.
4. На коротком клипе опираться на `on_short_clip` и `short_clip_variant`, а не на «нельзя».

## Кто что читает

| Роль | Берёт из реестра | Не тащит |
|------|------------------|----------|
| **Journey** | `code`, `name_ru`, `for_journey`, `when`, `comfort_sec`, `warn_below_sec`, `on_short_clip` | длинные EN `prompt_examples` |
| **Video** | `prompt_examples` (нормальная длительность) + `short_clip_variant` (4–5s) + forbidden | дублировать весь journey-текст |

## Связь с cinematic-transition-contract

- **Genre / camera type** (контракт cinematic) — язык движения камеры и шва между кадрами.
- **Object mechanic** (этот реестр) — язык смены идентичности / материала / масштаба объекта.
- Не подменять одно другим: «fly forward» без object_transform ≠ валидная смена формы; object_transform без camera path — слабый slideshow.

## Глобальный запрет

- **forbidden для всех кодов:** голый crossfade / dissolve-only между двумя статичными формами без действия, жеста, veil, snap, exit/reenter или иной явной механики из реестра.

---

### `snap_cut_reveal`

- **name_ru:** Щелчок / whip-скрытие → новая форма
- **for_journey:** В середине клипа резкий snap или whip закрывает кадр и мгновенно открывает уже новую форму объекта. Ощущение «моргнул — другой предмет».
- **when:** Нужна чёткая смена идентичности без долгого морфа; комфортно на коротких клипах; акцент на ритме, а не на пластике.
- **comfort_sec:** 4–5
- **warn_below_sec:** null
- **on_short_clip:** preferred — 4s идеальны; держать один snap mid-clip, без второго морфа после.
- **forbidden:** dissolve-only; медленный continuous morph без snap; два snap подряд без читаемой новой формы.
- **prompt_examples:**

  Mid-clip hard snap: camera holds the subject centered; at the beat a whip-pan or cut-to-black obscures the frame for a fraction of a second, then the same framing reveals the new object fully formed, same scale and anchor point. No soft dissolve between shapes — the reveal is instantaneous after the obscure.

  Whip-obscure variant: a fast horizontal whip motion smears the first form into motion blur, then the smear clears to the second form already solid in place. Lighting and background stay continuous so the snap reads as object change, not scene change.

- **short_clip_variant:** One mid-clip whip-obscure into an immediate solid reveal of the new form; keep camera locked, single beat, no secondary morph — entire identity swap lands inside 4–5 seconds.

---

### `veil_reveal`

- **name_ru:** Действие + завеса (туман / руки / вспышка) → раскрытие
- **for_journey:** Объект меняется, пока его закрывает mist, руки, flare или другая завеса; после действия зритель видит уже новую форму. Смена спрятана в жест, не в голый морф.
- **when:** Нужна мотивированная смена (жест, ритуал, свет) и мягкое «открытие» новой идентичности.
- **comfort_sec:** 5–7
- **warn_below_sec:** 4
- **on_short_clip:** ok — сжать veil: короче mist/hands/flare, быстрее clear; не отказывать.
- **forbidden:** dissolve без действия; завеса без финального чёткого reveal новой формы.
- **prompt_examples:**

  The subject performs a clear action (raise hands, strike light, blow mist). Soft volumetric mist or cupped hands briefly veil the object; while obscured the form is already the new identity. Mist clears or hands open to a sharp, fully readable reveal — continuous camera, no crossfade between two still plates.

  Flare-veil variant: a bright lens flare or light bloom blooms over the subject as the action peaks, then falls away to expose the transformed object in the same pose and framing. The bloom is the cover for the change; the end state is solid and lit, not half-dissolved.

- **short_clip_variant:** Compress the veil: quick hand-cover or short mist burst mid-clip, almost immediate clear to the new solid form; keep the action readable but cut veil duration so the full beat fits 4–5s.

---

### `exit_reenter`

- **name_ru:** Уход из кадра → возврат в новой форме
- **for_journey:** Объект целиком уходит за край кадра (или в глубину), затем возвращается уже как новая форма. Смена = смена «входа», не морф на месте.
- **when:** Хочется чистой смены без пластики на экране; объект может «переодеться» вне кадра.
- **comfort_sec:** 5–7
- **warn_below_sec:** 4
- **on_short_clip:** ok if snappy — быстрый exit, почти сразу re-enter; без долгих пауз вне кадра.
- **forbidden:** dissolve на месте; уход без возврата новой формы; два объекта одновременно в кадре без мотивации.
- **prompt_examples:**

  The current object exits frame decisively (slide off-screen or retreat into depth until gone). Brief empty beat with continuous environment, then the new form re-enters from the opposite or same edge into the previous anchor. No morph while visible — identity changes off-screen.

  Depth exit: subject walks or drifts away until lost in haze or past a doorway, then the new form approaches back into the same focal plane and scale. Camera may ease slightly but keeps geography stable so re-entry reads as the same «slot».

- **short_clip_variant:** Snappy exit within the first second, near-immediate re-enter as the new form into the same anchor; no lingering empty hold — pack the round-trip into 4–5s.

---

### `silhouette_match`

- **name_ru:** Морф с общей силуэтной / якорной формой
- **for_journey:** Форма меняется, но контур, поза или якорь (центр, ось) остаются узнаваемыми — морф читается как развитие одного силуэта, а не прыжок к чужой геометрии.
- **when:** Малый–средний дельта формы; нужна плавная связь «тот же объект, другая детализация».
- **comfort_sec:** 5–7
- **warn_below_sec:** 4
- **on_short_clip:** ok small delta — только близкие силуэты; иначе сжать или сменить на snap/veil.
- **forbidden:** полный plastic rebuild без общего силуэта; dissolve двух несвязанных контуров.
- **prompt_examples:**

  Continuous morph where the outer silhouette and main anchor stay locked: edges breathe and detail rebuilds inside a shared outline. Camera holds the anchor; lighting stays consistent so the eye tracks one shape becoming another, not a blend of two unrelated plates.

  Pose-matched morph: shared stance and center mass throughout; surface and secondary parts rearrange while the silhouette envelope barely shifts. End state snaps to a crisp final silhouette that still rhymes with the start.

- **short_clip_variant:** Small-delta silhouette morph only — keep outline almost constant, quick internal detail change, finish solid by 4–5s; avoid large topology jumps.

---

### `material_transmute`

- **name_ru:** Тот же объект, смена материала
- **for_journey:** Геометрия и идентичность объекта сохраняются; меняется вещество (металл↔стекло, камень↔жидкость, матовое↔зеркало). Читается как алхимия поверхности.
- **when:** Важно сохранить узнаваемый объект, но сменить тактильность / материал / отражения.
- **comfort_sec:** 4–6
- **warn_below_sec:** null
- **on_short_clip:** good at 4s — быстрый sweep материала по поверхности.
- **forbidden:** смена силуэта под видом «материала»; голый crossfade двух разных мешей.
- **prompt_examples:**

  Same object geometry and framing throughout. A material front sweeps across the surface: roughness, reflectivity, and subsurface shift (e.g. matte clay to polished metal, stone to clear glass) while edges and silhouette stay fixed. Specular highlights update continuously with the new material.

  Localized transmute: the change starts at a contact point or light hit and propagates until the whole object wears the new substance. No reshape — only shader/material story, ending in a stable, fully transmute finish.

- **short_clip_variant:** Fast material sweep across the unchanged mesh in one continuous pass; finish fully transmute by 4–5s with stable highlights — ideal short-clip mechanic.

---

### `assembly_build`

- **name_ru:** Сборка из частей
- **for_journey:** Детали слетаются / встают на место и собирают целый объект. Финал — собранная форма, не морф целого в целое.
- **when:** Тема сборки, механизма, ритуала «собрать»; нужен конструктивный beat.
- **comfort_sec:** 5–8
- **warn_below_sec:** 4
- **on_short_clip:** simple only — мало частей, быстрый snap-together; не полный сложный kit.
- **forbidden:** dissolve готового объекта; бесконечный разлёт без финальной сборки.
- **prompt_examples:**

  Separate parts enter from depth or sides and lock into a clear final assembly with satisfying contact. Camera favors the growing whole; motion is purposeful, not random scatter. End on a complete, solid object with no floating leftover pieces.

  Magnetic assembly: pieces accelerate into sockets along short arcs, each click readable, last piece completes the silhouette. Lighting sells hard surfaces meeting; no morph of a finished object — only construction.

- **short_clip_variant:** Simple assembly only — few large parts, fast lock-in to a complete form within 4–5s; skip intricate multi-stage kits.

---

### `portal_identity`

- **name_ru:** Проход сквозь портал = смена идентичности
- **for_journey:** Объект проходит через портал, арку, кольцо света или проём; на выходе — другая идентичность. Портал = граница смены.
- **when:** Нужна сюжетная «дверь» между формами; смена привязана к порогу пространства.
- **comfort_sec:** 6–8
- **warn_below_sec:** 5
- **on_short_clip:** prefer ≥6 — на 4s сжать: ближе портал, короче подход/выход; не блок.
- **forbidden:** смена без пересечения порога; dissolve посреди пустого кадра.
- **prompt_examples:**

  Subject approaches a defined portal (ring of light, doorway, circular rift). As it crosses the threshold, identity becomes the new form on the far side; camera may follow through or hold the portal plane. Continuity of motion through the gate sells the change — not a blend of two stills.

  Threshold wipe by geometry: the portal edge occludes the old form; emerging volume is already the new identity, fully solid after clearing the rim. Environment beyond the portal can shift slightly but the mechanic is the pass-through.

- **short_clip_variant:** Place the portal close; short approach, immediate cross, quick settle as new form — compress travel so the identity change still reads inside 4–5s (prefer longer when possible).

---

### `scale_shift`

- **name_ru:** Макро ↔ микро
- **for_journey:** Масштаб объекта или мира резко меняется: камера/объект уходят в макро-деталь или наоборот в крошечный масштаб. Смысл — сдвиг масштаба, не смена «другого меша» без масштаба.
- **when:** Нужен wow масштаба (город→песчинка, насекомое→монумент); дельта должна быть мотивирована камерой или объектом.
- **comfort_sec:** 6–9
- **warn_below_sec:** 5
- **on_short_clip:** small shift only at 4s — умеренный zoom/scale; не полный cosmos↔atom.
- **forbidden:** простое crossfade двух масштабов без непрерывного push/pull; текст на кадре.
- **prompt_examples:**

  Continuous scale journey: camera pushes into a detail until it becomes the new world-scale environment, or pulls back until the former hero is tiny in frame. Motion is one smooth scale path with parallax; end framing makes the new scale unmistakable.

  Object-driven scale: the subject itself grows or shrinks relative to a fixed reference (hand, doorway, horizon) while camera eases to keep composition. Transition is continuous scale, not a cut between two unrelated sizes.

- **short_clip_variant:** Small scale shift only — modest push-in or pull-back to a nearby scale rung; land a clear new scale read by 4–5s without extreme macro↔cosmos jumps.

---

### `erosion_melt`

- **name_ru:** Таяние / стирание от начала к концу
- **for_journey:** Форма постепенно тает, осыпается или стирается от старта к финалу; конец — новая форма, остаток или пустота с заменой. Долгий процесс разрушения→замены.
- **when:** Тема распада, времени, эрозии; есть бюджет секунд на читаемый melt.
- **comfort_sec:** 7–10
- **warn_below_sec:** 6
- **on_short_clip:** WARN → veil/snap — на 4s рекомендовать `veil_reveal` / `snap_cut_reveal`; если пользователь настаивает — сильно сжать erase в один beat.
- **forbidden:** мгновенный dissolve без erosion path; бесконечный melt без конечной читаемой формы.
- **prompt_examples:**

  Progressive erosion: the starting form melts, flakes, or is wiped away along a clear direction (top-down, wind-driven, heat). Under or after the loss, the end form emerges or remains. Timing sells decay — continuous matter loss, not a soft A/B blend.

  Melt-to-replace: surface liquefies and drains while the new solid builds in the same anchor as liquid clears. Keep camera stable enough to read both the decay front and the emerging identity.

- **short_clip_variant:** Strong warn at 4–5s: prefer swap to veil_reveal or snap_cut_reveal. If keeping erosion, one fast melt front and immediate solid end-state — no long decay plateau.

---

### `plastic_morph`

- **name_ru:** Полный пластический / identity rebuild
- **for_journey:** Сильная перестройка формы и идентичности на экране — пластичный морф «из одного в другое» с большой топологической дельтой. Нужно время, чтобы глаз успел.
- **when:** Большая смена формы без портала/exit; зритель должен видеть сам rebuild.
- **comfort_sec:** 8–10
- **warn_below_sec:** 6
- **on_short_clip:** not block; recommend longer or swap — предложить ≥6–8s или `snap_cut_reveal` / `silhouette_match`; на 4s — ускоренный, упрощённый morph.
- **forbidden:** dissolve-only; незавершённый half-morph в конце клипа.
- **prompt_examples:**

  Full plastic morph: topology and identity rebuild in-camera from form A to form B with continuous volume, stretching and reseating mass. Camera may orbit slightly to show the rebuild; end must be a crisp, finished B — no lingering hybrid.

  Identity rebuild with intermediate readable stages (still one continuous take): features collapse and reform while lighting tracks the changing surface. Avoid cutaways; the story is the morph itself across a comfortable duration.

- **short_clip_variant:** Do not refuse 4–5s: either recommend longer duration / swap to snap or silhouette_match, or run a highly accelerated morph with fewer intermediate stages and a hard settle on form B before the clip ends.

---

### `spin_anchor_morph`

- **name_ru:** Жест / спин + морф
- **for_journey:** Вращение, жест или spin вокруг якоря маскирует и сопровождает морф; движение тела/объекта — причина смены формы.
- **when:** Нужна динамика танца/спина; морф без «плоского» перехода.
- **comfort_sec:** 7–10
- **warn_below_sec:** 6
- **on_short_clip:** same — не блок; ускорить spin+morph или упростить дельту; рекомендовать длиннее при большой дельте.
- **forbidden:** spin без смены формы; morph без жеста при заявленном коде; dissolve под спином.
- **prompt_examples:**

  Subject spins or executes a clear anchored gesture; during the rotation the form morphs so that when the spin settles the new identity is complete. Anchor point stays in place; motion blur can hide mid-morph complexity, but the landing pose is sharp and final.

  Gesture-triggered morph: a turn, arm sweep, or object spin initiates the rebuild; plastic change rides the motion peak and finishes as the gesture resolves. Continuous take, no dissolve between start and end plates.

- **short_clip_variant:** Same policy as plastic_morph: warn soft, do not block — faster spin with smaller morph delta or quicker settle; optionally recommend longer clip or snap/veil if the identity jump is huge.

---

## Quick reference

| Code | Суть | comfort_sec | warn_below_sec | On 4s |
|------|------|-------------|----------------|-------|
| `snap_cut_reveal` | mid-clip snap / whip-obscure → new form | 4–5 | — | preferred |
| `veil_reveal` | action + mist/hands/flare → reveal | 5–7 | 4 | ok, compress veil |
| `exit_reenter` | leave frame → re-enter new form | 5–7 | 4 | ok if snappy |
| `silhouette_match` | morph with shared silhouette/anchor | 5–7 | 4 | ok small delta |
| `material_transmute` | same object, material change | 4–6 | — | good at 4s |
| `assembly_build` | parts assemble | 5–8 | 4 | simple only |
| `portal_identity` | pass through = identity change | 6–8 | 5 | prefer ≥6 |
| `scale_shift` | macro↔micro | 6–9 | 5 | small shift only at 4s |
| `erosion_melt` | melt/erase start→end | 7–10 | 6 | WARN → veil/snap |
| `plastic_morph` | full plastic/identity rebuild | 8–10 | 6 | not block; recommend longer or swap |
| `spin_anchor_morph` | gesture/spin + morph | 7–10 | 6 | same |
