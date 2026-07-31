# Camera Movement Registry — Scroll World

Источник промптов: [aicameramovements.com](https://aicameramovements.com/) / гайд «Гайд движения камеры для видео».

## Как читать

| Агент | Читает | Не читает |
|-------|--------|-----------|
| **Journey** | `id`, `name_ru`, `for_journey` | `prompt_snippet` |
| **Video** | `id` + `prompt_snippet` (вставка в секцию CAMERA PATH) | длинные RU-описания |

### Бюджет на leg

- Максимум **1 primary** + до **2 secondary** (всего ≤ **3** движения на leg).
- Не ставить два агрессивных хода рядом (например `whip_pan_*` + `crash_zoom_*`).
- **Zoom ≠ dolly:** zoom меняет фокусное (масштаб линзы), dolly — физическое приближение/отъезд камеры. Не путать в journey и в промпте.

---

## Combination rules

### Категории гармонии (можно комбинировать)

| Паттерн | Примеры | Зачем |
|---------|---------|--------|
| Slow reveal | `static_shot` / `slow_zoom_*` + `tilt_*` / `pan_*` | Спокойное раскрытие кадра |
| Lateral + height | `truck_*` / `slider_*` + `pedestal_*` / `crane_*` | Параллакс + смена высоты |
| Subject-follow | `tracking_shot` / `follow_shot_from_behind` / `side_tracking_shot` + мягкий `pan_*` | Сопровождение героя |
| Approach stack | `dolly_in` + `slow_zoom_in` (осторожно, не crash) | Усиление приближения без удара |
| Aerial establish | `drone_pull_back` / `helicopter_style_aerial` + `pan_*` | Широкий aerial + обзор |
| Orbit pair | `arc_*` / `clockwise_orbit` + `slow_zoom_*` | Смена угла + лёгкий масштаб |
| Pass layers | `push_past` / `pass_through_movement` + `dolly_in` | Проход сквозь слой / барьер |

`harmonizes_with` у каждого хода — ориентир; secondary должен быть мягче primary по `pace`.

### Конфликты (не ставить вместе как primary+secondary)

| Конфликт | Почему |
|----------|--------|
| Два aggressive (`whip_pan_*`, `crash_zoom_*`, `chase_shot`, `fast_zoom_*` + crash) | Перегруз blur / punch, модель «ломает» кадр |
| `zoom_*` + `dolly_*` в одном направлении без явной цели | Модель смешивает lens zoom и physical push |
| `static_shot` / `locked_camera_time_lapse` + любой physical travel | Противоречие «locked» vs движение |
| `body_mounted_snorricam` + `orbit_*` / `crane_*` | Разные системы крепления / пути |
| `first_person_view` + `helicopter_style_aerial` / `earth_zoom_out` | Разный масштаб POV |
| `infinite_zoom` / `earth_zoom_out` + любой второй агрессивный ход | Specials уже доминируют весь leg |
| `tilt_shift_miniature_view` + `handheld_shot` | Стабильная miniature vs organic sway |

**Aggressive ids (не стакать друг с другом):**  
`whip_pan_right`, `whip_pan_left`, `crash_zoom_in`, `crash_zoom_out`, `fast_zoom_in`, `fast_zoom_out`, `chase_shot`, `infinite_zoom`, `earth_zoom_out`.

---

## Moves

### `static_shot`
- **name_en:** Static shot
- **name_ru:** Статичный кадр
- **for_journey:** Камера полностью зафиксирована: без пана, наклона и физического хода. Кадр держит одну композицию до конца куска.
- **prompt_snippet:** Camera: locked-off static shot. Movement: hold one fixed camera position for the full clip. Speed: still and steady. Framing: keep the same angle, height, lens distance and composition. End: finish with the same framing and camera position.
- **category:** pan_tilt
- **pace:** slow
- **harmonizes_with:** [slow_zoom_in, slow_zoom_out, locked_camera_time_lapse, tilt_shift_miniature_view]
- **conflicts_with:** [dolly_in, dolly_out, truck_left, truck_right, chase_shot, whip_pan_left, whip_pan_right, crash_zoom_in, crash_zoom_out]

### `pan_right`
- **name_en:** Pan right
- **name_ru:** Пан вправо
- **for_journey:** Камера поворачивается вправо с одной точки. Горизонт ровный; справа входит новое пространство.
- **prompt_snippet:** Camera: pan right. Movement: rotate the camera horizontally from left to right from one fixed point. Speed: smooth constant rotation. Framing: keep the horizon level while new space enters from the right side of the frame. End: settle on a clear final composition.
- **category:** pan_tilt
- **pace:** medium
- **harmonizes_with:** [tilt_up, tilt_down, slow_zoom_in, slow_zoom_out, static_shot, pedestal_up, pedestal_down]
- **conflicts_with:** [whip_pan_left, whip_pan_right, crash_zoom_in, crash_zoom_out]

### `pan_left`
- **name_en:** Pan left
- **name_ru:** Пан влево
- **for_journey:** Камера поворачивается влево с одной точки. Горизонт ровный; слева входит новое пространство.
- **prompt_snippet:** Camera: pan left. Movement: rotate the camera horizontally from right to left from one fixed point. Speed: smooth constant rotation. Framing: keep the horizon level while new space enters from the left side of the frame. End: settle on a clear final composition.
- **category:** pan_tilt
- **pace:** medium
- **harmonizes_with:** [tilt_up, tilt_down, slow_zoom_in, slow_zoom_out, static_shot, pedestal_up, pedestal_down]
- **conflicts_with:** [whip_pan_left, whip_pan_right, crash_zoom_in, crash_zoom_out]

### `whip_pan_right`
- **name_en:** Whip pan right
- **name_ru:** Резкий пан вправо
- **for_journey:** Быстрый рывок камеры вправо с коротким motion blur. Старт на одном читаемом кадре, приземление на второй цель.
- **prompt_snippet:** Camera: whip pan right. Movement: rotate rapidly from the starting direction toward a new target on the right. Speed: fast snap with brief motion blur during the rotation. Framing: begin on one readable composition and land on a second readable target. End: settle into a sharp final frame.
- **category:** pan_tilt
- **pace:** fast
- **harmonizes_with:** [static_shot, slow_zoom_out]
- **conflicts_with:** [whip_pan_left, crash_zoom_in, crash_zoom_out, fast_zoom_in, fast_zoom_out, chase_shot, infinite_zoom, earth_zoom_out]

### `whip_pan_left`
- **name_en:** Whip pan left
- **name_ru:** Резкий пан влево
- **for_journey:** Быстрый рывок камеры влево с коротким motion blur. Старт на одном читаемом кадре, приземление на второй цель.
- **prompt_snippet:** Camera: whip pan left. Movement: rotate rapidly from the starting direction toward a new target on the left. Speed: fast snap with brief motion blur during the rotation. Framing: begin on one readable composition and land on a second readable target. End: settle into a sharp final frame.
- **category:** pan_tilt
- **pace:** fast
- **harmonizes_with:** [static_shot, slow_zoom_out]
- **conflicts_with:** [whip_pan_right, crash_zoom_in, crash_zoom_out, fast_zoom_in, fast_zoom_out, chase_shot, infinite_zoom, earth_zoom_out]

### `tilt_up`
- **name_en:** Tilt up
- **name_ru:** Наклон вверх
- **for_journey:** Камера наклоняется вверх с одной точки. Вертикальный объект или архитектура остаются в центре по мере подъёма кадра.
- **prompt_snippet:** Camera: tilt up. Movement: rotate the camera upward from one fixed point. Speed: smooth constant tilt. Framing: keep the vertical subject or architecture centered as the frame travels upward. End: land on the upper target.
- **category:** pan_tilt
- **pace:** medium
- **harmonizes_with:** [pan_left, pan_right, slow_zoom_in, slow_zoom_out, pedestal_up, crane_up]
- **conflicts_with:** [whip_pan_left, whip_pan_right, crash_zoom_in, crash_zoom_out]

### `tilt_down`
- **name_en:** Tilt down
- **name_ru:** Наклон вниз
- **for_journey:** Камера наклоняется вниз с одной точки. Вертикальный объект или архитектура остаются в центре по мере спуска кадра.
- **prompt_snippet:** Camera: tilt down. Movement: rotate the camera downward from one fixed point. Speed: smooth constant tilt. Framing: keep the vertical subject or architecture centered as the frame travels downward. End: land on the lower target.
- **category:** pan_tilt
- **pace:** medium
- **harmonizes_with:** [pan_left, pan_right, slow_zoom_in, slow_zoom_out, pedestal_down, crane_down]
- **conflicts_with:** [whip_pan_left, whip_pan_right, crash_zoom_in, crash_zoom_out]

### `slow_zoom_in`
- **name_en:** Slow zoom in
- **name_ru:** Медленный зум внутрь
- **for_journey:** Плавно увеличивается фокусное — кадр сужается к цели. Цель остаётся читаемой, финал — стабильный крупный план. Это зум линзы, не тележка.
- **prompt_snippet:** Camera: slow zoom in. Movement: slowly increase lens focal length toward a tighter frame. Speed: gradual and even. Framing: keep the main visual target readable as it becomes larger in frame. End: finish on a stable tighter composition.
- **category:** zoom_lens
- **pace:** slow
- **harmonizes_with:** [pan_left, pan_right, tilt_up, tilt_down, static_shot, arc_left, arc_right]
- **conflicts_with:** [crash_zoom_in, crash_zoom_out, fast_zoom_in, dolly_in]

### `slow_zoom_out`
- **name_en:** Slow zoom out
- **name_ru:** Медленный зум наружу
- **for_journey:** Плавно уменьшается фокусное — кадр расширяется, вокруг цели появляется пространство. Это зум линзы, не отъезд тележки.
- **prompt_snippet:** Camera: slow zoom out. Movement: slowly decrease lens focal length toward a wider frame. Speed: gradual and even. Framing: keep the main visual target readable as more surrounding space appears. End: finish on a stable wider composition.
- **category:** zoom_lens
- **pace:** slow
- **harmonizes_with:** [pan_left, pan_right, tilt_up, tilt_down, static_shot, crane_up, drone_pull_back]
- **conflicts_with:** [crash_zoom_in, crash_zoom_out, fast_zoom_out, dolly_out]

### `fast_zoom_in`
- **name_en:** Fast zoom in
- **name_ru:** Быстрый зум внутрь
- **for_journey:** Резкое увеличение фокусного к цели. Цель в центре или читаема; финал — стабильный более крупный кадр.
- **prompt_snippet:** Camera: fast zoom in. Movement: quickly increase lens focal length toward the main visual target. Speed: quick decisive zoom. Framing: keep the target centered or clearly readable during the scale change. End: finish on a stable tighter composition.
- **category:** zoom_lens
- **pace:** fast
- **harmonizes_with:** [static_shot, pan_left, pan_right]
- **conflicts_with:** [crash_zoom_in, crash_zoom_out, whip_pan_left, whip_pan_right, chase_shot, dolly_in]

### `fast_zoom_out`
- **name_en:** Fast zoom out
- **name_ru:** Быстрый зум наружу
- **for_journey:** Резкое уменьшение фокусного от цели — быстро открывается окружение. Финал — стабильный широкий кадр.
- **prompt_snippet:** Camera: fast zoom out. Movement: quickly decrease lens focal length away from the main visual target. Speed: quick decisive zoom. Framing: keep the target readable as the surrounding space appears. End: finish on a stable wider composition.
- **category:** zoom_lens
- **pace:** fast
- **harmonizes_with:** [static_shot, pan_left, pan_right]
- **conflicts_with:** [crash_zoom_in, crash_zoom_out, whip_pan_left, whip_pan_right, chase_shot, dolly_out]

### `crash_zoom_in`
- **name_en:** Crash zoom in
- **name_ru:** Crash-зум внутрь
- **for_journey:** Ударный рывок линзы к цели — очень быстрый punch. Цель читаема; финал — смелый крупный кадр. Не комбинировать с whip pan.
- **prompt_snippet:** Camera: crash zoom in. Movement: snap the lens rapidly toward the main visual target. Speed: very fast and punchy. Framing: keep the target readable through the sudden scale change. End: land on a bold tighter composition.
- **category:** zoom_lens
- **pace:** fast
- **harmonizes_with:** [static_shot]
- **conflicts_with:** [whip_pan_left, whip_pan_right, crash_zoom_out, fast_zoom_in, fast_zoom_out, chase_shot, infinite_zoom, earth_zoom_out]

### `crash_zoom_out`
- **name_en:** Crash zoom out
- **name_ru:** Crash-зум наружу
- **for_journey:** Ударный рывок линзы от цели — punch-расширение кадра. Не комбинировать с whip pan и другими crash/fast zoom.
- **prompt_snippet:** Camera: crash zoom out. Movement: snap the lens rapidly away from the main visual target. Speed: very fast and punchy. Framing: keep the target readable as the surrounding space appears. End: land on a bold wider composition.
- **category:** zoom_lens
- **pace:** fast
- **harmonizes_with:** [static_shot]
- **conflicts_with:** [whip_pan_left, whip_pan_right, crash_zoom_in, fast_zoom_in, fast_zoom_out, chase_shot, infinite_zoom, earth_zoom_out]

### `dolly_in`
- **name_en:** Dolly in
- **name_ru:** Тележка вперёд
- **for_journey:** Камера физически едет прямо к субъекту. Высота, направление линзы и позиция героя стабильны — меняется только дистанция. Не путать с zoom in.
- **prompt_snippet:** Camera: dolly in. Movement: move the camera physically forward in a straight line toward the main subject. Speed: smooth controlled push. Framing: keep camera height, lens direction and subject position consistent while distance closes. End: finish in a tighter composition.
- **category:** dolly_track
- **pace:** medium
- **harmonizes_with:** [tilt_up, tilt_down, pan_left, pan_right, push_past, pedestal_up]
- **conflicts_with:** [slow_zoom_in, fast_zoom_in, crash_zoom_in, dolly_out]

### `dolly_out`
- **name_en:** Dolly out
- **name_ru:** Тележка назад
- **for_journey:** Камера физически отъезжает по прямой от субъекта — в кадр входит окружение. Не путать с zoom out.
- **prompt_snippet:** Camera: dolly out. Movement: move the camera physically backward in a straight line away from the main subject. Speed: smooth controlled retreat. Framing: keep lens direction and camera height consistent while more environment enters frame. End: finish in a wider composition.
- **category:** dolly_track
- **pace:** medium
- **harmonizes_with:** [tilt_up, tilt_down, pan_left, pan_right, pedestal_down]
- **conflicts_with:** [slow_zoom_out, fast_zoom_out, crash_zoom_out, dolly_in]

### `truck_right`
- **name_en:** Truck right
- **name_ru:** Трак вправо
- **for_journey:** Камера едет горизонтально вправо по прямой; линза смотрит в ту же сторону, сцена скользит по кадру.
- **prompt_snippet:** Camera: truck right. Movement: move the camera physically to the right on a straight horizontal path. Speed: smooth constant lateral travel. Framing: keep the lens facing the same direction while the scene slides across frame. End: finish on a clean lateral composition.
- **category:** physical
- **pace:** medium
- **harmonizes_with:** [pedestal_up, pedestal_down, slow_zoom_in, slow_zoom_out, tilt_up, tilt_down]
- **conflicts_with:** [whip_pan_left, whip_pan_right, crash_zoom_in, crash_zoom_out, slider_left]

### `truck_left`
- **name_en:** Truck left
- **name_ru:** Трак влево
- **for_journey:** Камера едет горизонтально влево по прямой; линза смотрит в ту же сторону, сцена скользит по кадру.
- **prompt_snippet:** Camera: truck left. Movement: move the camera physically to the left on a straight horizontal path. Speed: smooth constant lateral travel. Framing: keep the lens facing the same direction while the scene slides across frame. End: finish on a clean lateral composition.
- **category:** physical
- **pace:** medium
- **harmonizes_with:** [pedestal_up, pedestal_down, slow_zoom_in, slow_zoom_out, tilt_up, tilt_down]
- **conflicts_with:** [whip_pan_left, whip_pan_right, crash_zoom_in, crash_zoom_out, slider_right]

### `pedestal_up`
- **name_en:** Pedestal up
- **name_ru:** Пьедестал вверх
- **for_journey:** Вся камера поднимается вертикально по прямой; линза остаётся ровной и смотрит в том же направлении.
- **prompt_snippet:** Camera: pedestal up. Movement: move the entire camera vertically upward in a straight line. Speed: smooth constant lift. Framing: keep the lens level and pointed in the same direction during the vertical move. End: finish with the higher framing clearly readable.
- **category:** physical
- **pace:** medium
- **harmonizes_with:** [truck_left, truck_right, slider_left, slider_right, pan_left, pan_right, dolly_in]
- **conflicts_with:** [crash_zoom_in, crash_zoom_out, whip_pan_left, whip_pan_right]

### `pedestal_down`
- **name_en:** Pedestal down
- **name_ru:** Пьедестал вниз
- **for_journey:** Вся камера опускается вертикально по прямой; линза остаётся ровной и смотрит в том же направлении.
- **prompt_snippet:** Camera: pedestal down. Movement: move the entire camera vertically downward in a straight line. Speed: smooth constant descent. Framing: keep the lens level and pointed in the same direction during the vertical move. End: finish with the lower framing clearly readable.
- **category:** physical
- **pace:** medium
- **harmonizes_with:** [truck_left, truck_right, slider_left, slider_right, pan_left, pan_right, dolly_out]
- **conflicts_with:** [crash_zoom_in, crash_zoom_out, whip_pan_left, whip_pan_right]

### `slider_right`
- **name_en:** Slider right
- **name_ru:** Слайдер вправо
- **for_journey:** Короткий плавный сдвиг камеры вправо на слайдере. Виден параллакс слоёв переднего плана, субъекта и фона.
- **prompt_snippet:** Camera: slider right. Movement: slide the camera a small distance to the right. Speed: slow controlled constant motion. Framing: keep foreground, subject and background layers readable as parallax shifts. End: finish on a refined composition with the new right-side angle visible.
- **category:** physical
- **pace:** slow
- **harmonizes_with:** [pedestal_up, pedestal_down, slow_zoom_in, slow_zoom_out, tilt_up, tilt_down, static_shot]
- **conflicts_with:** [truck_left, whip_pan_left, whip_pan_right, crash_zoom_in, crash_zoom_out]

### `slider_left`
- **name_en:** Slider left
- **name_ru:** Слайдер влево
- **for_journey:** Короткий плавный сдвиг камеры влево на слайдере. Виден параллакс слоёв переднего плана, субъекта и фона.
- **prompt_snippet:** Camera: slider left. Movement: slide the camera a small distance to the left. Speed: slow controlled constant motion. Framing: keep foreground, subject and background layers readable as parallax shifts. End: finish on a refined composition with the new left-side angle visible.
- **category:** physical
- **pace:** slow
- **harmonizes_with:** [pedestal_up, pedestal_down, slow_zoom_in, slow_zoom_out, tilt_up, tilt_down, static_shot]
- **conflicts_with:** [truck_right, whip_pan_left, whip_pan_right, crash_zoom_in, crash_zoom_out]

### `push_past`
- **name_en:** Push past / pass-by
- **name_ru:** Проезд мимо / push past
- **for_journey:** Камера едет вперёд мимо переднего объекта, края или проёма. Передний план проходит близко к линзе, пространство за ним открывается.
- **prompt_snippet:** Camera: push past. Movement: move forward past a visible foreground object, edge or opening. Speed: smooth forward glide. Framing: let the foreground pass close to the lens while the space beyond becomes clearer. End: arrive inside or beyond the foreground layer.
- **category:** physical
- **pace:** medium
- **harmonizes_with:** [dolly_in, pass_through_movement, slow_zoom_in, tracking_shot]
- **conflicts_with:** [crash_zoom_in, crash_zoom_out, whip_pan_left, whip_pan_right, static_shot]

### `arc_right`
- **name_en:** Arc right
- **name_ru:** Дуга вправо
- **for_journey:** Камера идёт по пологой дуге вокруг субъекта вправо. Дистанция и высота стабильны, меняется угол.
- **prompt_snippet:** Camera: arc right. Movement: move on a shallow curved path around the main subject toward the right side. Speed: smooth measured curve. Framing: keep distance, height and subject readability consistent while the angle changes. End: finish from a new right-side angle.
- **category:** physical
- **pace:** medium
- **harmonizes_with:** [slow_zoom_in, slow_zoom_out, pedestal_up, pedestal_down, tilt_up, tilt_down]
- **conflicts_with:** [clockwise_orbit, counterclockwise_orbit, whip_pan_left, whip_pan_right, crash_zoom_in]

### `arc_left`
- **name_en:** Arc left
- **name_ru:** Дуга влево
- **for_journey:** Камера идёт по пологой дуге вокруг субъекта влево. Дистанция и высота стабильны, меняется угол.
- **prompt_snippet:** Camera: arc left. Movement: move on a shallow curved path around the main subject toward the left side. Speed: smooth measured curve. Framing: keep distance, height and subject readability consistent while the angle changes. End: finish from a new left-side angle.
- **category:** physical
- **pace:** medium
- **harmonizes_with:** [slow_zoom_in, slow_zoom_out, pedestal_up, pedestal_down, tilt_up, tilt_down]
- **conflicts_with:** [clockwise_orbit, counterclockwise_orbit, whip_pan_left, whip_pan_right, crash_zoom_in]

### `clockwise_orbit`
- **name_en:** Clockwise orbit
- **name_ru:** Орбита по часовой
- **for_journey:** Камера кружит по часовой вокруг субъекта на постоянном радиусе. Субъект в центре, фон вращается вокруг него.
- **prompt_snippet:** Camera: clockwise orbit. Movement: circle clockwise around the main subject at a consistent radius. Speed: smooth controlled orbit. Framing: keep the subject centered while the background rotates around them. End: complete the intended arc or full circle with stable framing.
- **category:** physical
- **pace:** medium
- **harmonizes_with:** [slow_zoom_in, slow_zoom_out, pedestal_up]
- **conflicts_with:** [counterclockwise_orbit, arc_left, arc_right, body_mounted_snorricam, whip_pan_left, whip_pan_right, crash_zoom_in]

### `counterclockwise_orbit`
- **name_en:** Counterclockwise orbit
- **name_ru:** Орбита против часовой
- **for_journey:** Камера кружит против часовой вокруг субъекта на постоянном радиусе. Субъект в центре, фон вращается вокруг него.
- **prompt_snippet:** Camera: counterclockwise orbit. Movement: circle counterclockwise around the main subject at a consistent radius. Speed: smooth controlled orbit. Framing: keep the subject centered while the background rotates around them. End: complete the intended arc or full circle with stable framing.
- **category:** physical
- **pace:** medium
- **harmonizes_with:** [slow_zoom_in, slow_zoom_out, pedestal_up]
- **conflicts_with:** [clockwise_orbit, arc_left, arc_right, body_mounted_snorricam, whip_pan_left, whip_pan_right, crash_zoom_in]

### `tracking_shot`
- **name_en:** Tracking shot
- **name_ru:** Трекинг
- **for_journey:** Камера движется по сцене вместе с субъектом в его темпе. Субъект читаем, окружение уходит мимо.
- **prompt_snippet:** Camera: tracking shot. Movement: move through the scene with the main subject. Speed: match the subject's pace. Framing: keep the subject consistently readable while the environment moves around them. End: maintain a clear moving composition.
- **category:** dolly_track
- **pace:** medium
- **harmonizes_with:** [pan_left, pan_right, slow_zoom_in, push_past, side_tracking_shot]
- **conflicts_with:** [static_shot, locked_camera_time_lapse, crash_zoom_in, whip_pan_left, whip_pan_right]

### `follow_shot_from_behind`
- **name_en:** Follow shot from behind
- **name_ru:** Следование сзади
- **for_journey:** Камера идёт сзади субъекта по маршруту на высоте плеч. Спина/плечо/голова ведут кадр, путь впереди читаем.
- **prompt_snippet:** Camera: follow shot from behind. Movement: move behind the subject along their route at shoulder height. Speed: match the subject's pace. Framing: keep the back, shoulder or head as the foreground guide while the route ahead stays readable. End: continue following with the subject leading the frame.
- **category:** dolly_track
- **pace:** medium
- **harmonizes_with:** [tracking_shot, low_tracking_shot, slow_zoom_in, push_past]
- **conflicts_with:** [reverse_tracking_shot, body_mounted_snorricam, static_shot, crash_zoom_in]

### `reverse_tracking_shot`
- **name_en:** Reverse tracking shot
- **name_ru:** Обратный трекинг
- **for_journey:** Камера пятится спиной вперёд перед идущим субъектом. Лицо и корпус стабильны, фон уходит назад.
- **prompt_snippet:** Camera: reverse tracking shot. Movement: move backward in front of the walking subject. Speed: match the subject's forward pace. Framing: keep front-facing face and body framing stable as the background moves behind them. End: hold a clear front-facing moving composition.
- **category:** dolly_track
- **pace:** medium
- **harmonizes_with:** [tracking_shot, slow_zoom_in, pan_left, pan_right]
- **conflicts_with:** [follow_shot_from_behind, body_mounted_snorricam, static_shot, crash_zoom_in]

### `side_tracking_shot`
- **name_en:** Side tracking shot
- **name_ru:** Боковой трекинг
- **for_journey:** Камера едет параллельно субъекту вдоль его движения. Профиль или три четверти на стабильной дистанции.
- **prompt_snippet:** Camera: side tracking shot. Movement: move parallel beside the subject along their direction of travel. Speed: match the subject's motion. Framing: keep the subject in side profile or three-quarter profile at a stable distance. End: continue the parallel movement with clear horizontal motion.
- **category:** dolly_track
- **pace:** medium
- **harmonizes_with:** [tracking_shot, low_tracking_shot, vehicle_tracking_shot, slow_zoom_in]
- **conflicts_with:** [static_shot, whip_pan_left, whip_pan_right, crash_zoom_in]

### `low_tracking_shot`
- **name_en:** Low tracking shot
- **name_ru:** Низкий трекинг
- **for_journey:** Камера едет у земли или ниже пояса вдоль пути субъекта. Низкая деталь читаема, плоскость пола/земли проходит через кадр.
- **prompt_snippet:** Camera: low tracking shot. Movement: move at ground or below-waist height alongside the subject's movement path. Speed: match the subject, footsteps or wheels. Framing: keep the low detail readable while the ground plane moves through frame. End: finish with the low perspective clearly maintained.
- **category:** dolly_track
- **pace:** medium
- **harmonizes_with:** [side_tracking_shot, tracking_shot, chase_shot, vehicle_tracking_shot]
- **conflicts_with:** [helicopter_style_aerial, crane_up, static_shot, earth_zoom_out]

### `vehicle_tracking_shot`
- **name_en:** Vehicle tracking shot
- **name_ru:** Трекинг с транспортом
- **for_journey:** Камера едет вместе с машиной/транспортом по маршруту. Транспорт стабилен в кадре, дорога и окружение уходят мимо.
- **prompt_snippet:** Camera: vehicle tracking shot. Movement: move with the vehicle along its route. Speed: match the vehicle's pace. Framing: keep the vehicle stable in frame while the road or environment moves past. End: maintain a clear moving vehicle composition.
- **category:** dolly_track
- **pace:** medium
- **harmonizes_with:** [side_tracking_shot, chase_shot, low_tracking_shot, drone_push_in]
- **conflicts_with:** [static_shot, body_mounted_snorricam, locked_camera_time_lapse]

### `chase_shot`
- **name_en:** Chase shot
- **name_ru:** Погоня
- **for_journey:** Быстрое близкое следование за движущимся субъектом по маршруту действия. Энергичный reframing, субъект остаётся в кадре.
- **prompt_snippet:** Camera: chase shot. Movement: follow a moving subject quickly along the action route. Speed: fast, reactive and physically close. Framing: keep the subject visible while allowing energetic reframing. End: stay connected to the subject in motion.
- **category:** dolly_track
- **pace:** fast
- **harmonizes_with:** [low_tracking_shot, handheld_shot, vehicle_tracking_shot]
- **conflicts_with:** [whip_pan_left, whip_pan_right, crash_zoom_in, crash_zoom_out, fast_zoom_in, fast_zoom_out, static_shot, infinite_zoom]

### `body_mounted_snorricam`
- **name_en:** Body-mounted Snorricam
- **name_ru:** Сноррикам / камера на теле
- **for_journey:** Камера жёстко связана с торсом или лицом субъекта. Субъект крупно в центре лицом к камере, фон крутится вокруг него.
- **prompt_snippet:** Camera: body-mounted Snorricam. Movement: keep the camera fixed relative to the subject's torso or face while the subject moves. Speed: match the subject's body motion. Framing: keep the subject close, centered and facing the camera as the background moves around them. End: finish with the subject still locked in frame.
- **category:** human_camera
- **pace:** medium
- **harmonizes_with:** [handheld_shot]
- **conflicts_with:** [clockwise_orbit, counterclockwise_orbit, crane_up, crane_down, drone_push_in, drone_pull_back, follow_shot_from_behind, reverse_tracking_shot]

### `handheld_shot`
- **name_en:** Handheld shot
- **name_ru:** Ручная камера
- **for_journey:** Камера на высоте оператора с естественным живым движением тела. Субъект читаем, лёгкий sway и микроправки кадра.
- **prompt_snippet:** Camera: handheld shot. Movement: hold the camera at human operator height with natural body movement. Speed: responsive and organic. Framing: keep the subject readable while the frame has subtle sway and micro-adjustments. End: finish with a natural handheld composition.
- **category:** human_camera
- **pace:** medium
- **harmonizes_with:** [chase_shot, tracking_shot, follow_shot_from_behind, first_person_view]
- **conflicts_with:** [tilt_shift_miniature_view, locked_camera_time_lapse, static_shot, helicopter_style_aerial]

### `crane_up`
- **name_en:** Crane up
- **name_ru:** Кран вверх
- **for_journey:** Плавный подъём камеры через открытое пространство. Субъект или локация читаемы по мере роста масштаба.
- **prompt_snippet:** Camera: crane up. Movement: travel smoothly upward through open space. Speed: slow controlled vertical lift. Framing: keep the subject or location readable as the camera rises. End: finish with the higher scale clearly visible.
- **category:** drone_crane
- **pace:** slow
- **harmonizes_with:** [pan_left, pan_right, slow_zoom_out, tilt_up, drone_pull_back]
- **conflicts_with:** [body_mounted_snorricam, low_tracking_shot, crash_zoom_in, whip_pan_left]

### `crane_down`
- **name_en:** Crane down
- **name_ru:** Кран вниз
- **for_journey:** Плавный спуск камеры через открытое пространство к нижнему субъекту или точке назначения.
- **prompt_snippet:** Camera: crane down. Movement: travel smoothly downward through open space. Speed: slow controlled vertical descent. Framing: keep the subject or location readable as the camera descends. End: finish with the lower subject or destination clearly visible.
- **category:** drone_crane
- **pace:** slow
- **harmonizes_with:** [pan_left, pan_right, slow_zoom_in, tilt_down, drone_push_in]
- **conflicts_with:** [body_mounted_snorricam, crash_zoom_out, whip_pan_right]

### `drone_push_in`
- **name_en:** Drone push in
- **name_ru:** Дрон наезд
- **for_journey:** Дрон плавно летит вперёд через открытое пространство к субъекту или точке назначения. Маршрут и цель читаемы.
- **prompt_snippet:** Camera: drone push in. Movement: fly smoothly forward through open space toward the subject or destination. Speed: controlled aerial glide. Framing: keep the route and destination readable as the camera approaches. End: arrive at a closer aerial composition.
- **category:** drone_crane
- **pace:** medium
- **harmonizes_with:** [crane_down, pan_left, pan_right, slow_zoom_in, helicopter_style_aerial]
- **conflicts_with:** [body_mounted_snorricam, first_person_view, static_shot, crash_zoom_in]

### `drone_pull_back`
- **name_en:** Drone pull back
- **name_ru:** Дрон отъезд
- **for_journey:** Дрон плавно отлетает назад от субъекта — открывается ландшафт. Финал — более широкий aerial-кадр.
- **prompt_snippet:** Camera: drone pull back. Movement: fly smoothly backward away from the subject or destination. Speed: controlled aerial retreat. Framing: keep the subject readable as more landscape appears. End: finish on a wider aerial composition.
- **category:** drone_crane
- **pace:** medium
- **harmonizes_with:** [crane_up, pan_left, pan_right, slow_zoom_out, helicopter_style_aerial]
- **conflicts_with:** [body_mounted_snorricam, first_person_view, static_shot, crash_zoom_out]

### `helicopter_style_aerial`
- **name_en:** Helicopter-style aerial shot
- **name_ru:** Вертолётный aerial
- **for_journey:** Движение с большой высоты по широкой плавной траектории. Ландшафт или далёкий движущийся субъект читаемы в широком масштабе.
- **prompt_snippet:** Camera: helicopter-style aerial shot. Movement: move from high altitude along a broad gradual flight path. Speed: steady controlled aerial motion. Framing: keep the landscape or distant moving subject readable at wide scale. End: finish on a stable high-altitude composition.
- **category:** drone_crane
- **pace:** slow
- **harmonizes_with:** [drone_pull_back, drone_push_in, pan_left, pan_right, crane_up]
- **conflicts_with:** [first_person_view, handheld_shot, low_tracking_shot, body_mounted_snorricam]

### `first_person_view`
- **name_en:** First-person view
- **name_ru:** От первого лица (FPV)
- **for_journey:** Камера идёт вперёд на высоте глаз персонажа. В кадре — руки, руки/края тела как физическая привязка зрителя.
- **prompt_snippet:** Camera: first-person view. Movement: move forward at human eye height from the character's perspective. Speed: natural walking or reaching pace. Framing: use visible hands, arms or body edges as the viewer's physical reference. End: arrive at the next point of action from the same point of view.
- **category:** specials
- **pace:** medium
- **harmonizes_with:** [handheld_shot, push_past, pass_through_movement]
- **conflicts_with:** [helicopter_style_aerial, earth_zoom_out, drone_pull_back, drone_push_in, body_mounted_snorricam]

### `tilt_shift_miniature_view`
- **name_en:** Tilt-shift miniature view
- **name_ru:** Tilt-shift / миниатюра
- **for_journey:** Высокий угловой взгляд с узкой полосой резкости на ключевой зоне и мягким блюром сверху и снизу — эффект миниатюры.
- **prompt_snippet:** Camera: tilt-shift miniature view. Movement: hold or glide from a high angled view over the scene. Speed: small precise movement. Framing: keep a narrow band of sharp focus across the key subject area with soft blur above and below. End: finish with the miniature-scale view intact.
- **category:** specials
- **pace:** slow
- **harmonizes_with:** [static_shot, slider_left, slider_right, crane_up, drone_pull_back]
- **conflicts_with:** [handheld_shot, chase_shot, whip_pan_left, whip_pan_right, crash_zoom_in]

### `infinite_zoom`
- **name_en:** Infinite zoom
- **name_ru:** Бесконечный зум
- **for_journey:** Непрерывный зум в точный центр цели с ускорением. Круглая цель в центре расширяется, пока следующий визуальный мир не заполнит кадр. Обычно один primary на весь leg.
- **prompt_snippet:** Camera: infinite zoom. Movement: zoom continuously inward toward the exact center target. Speed: smooth accelerating zoom. Framing: keep the circular target centered as it expands. End: finish when the next visual world fills the frame.
- **category:** specials
- **pace:** fast
- **harmonizes_with:** []
- **conflicts_with:** [whip_pan_left, whip_pan_right, crash_zoom_in, crash_zoom_out, fast_zoom_in, chase_shot, earth_zoom_out, dolly_in]

### `earth_zoom_out`
- **name_en:** Earth zoom out
- **name_ru:** Отъезд до планеты
- **for_journey:** Уход вверх от стартовой точки через улицу, город, ландшафт до масштаба планеты. Исходная точка остаётся в центре. Обычно один primary на весь leg.
- **prompt_snippet:** Camera: earth zoom out. Movement: pull upward from the starting point through street, city, landscape and planet scale. Speed: rapid expanding zoom out. Framing: keep the original location centered as scale grows. End: finish on a planet-scale view with the starting point still implied at center.
- **category:** specials
- **pace:** fast
- **harmonizes_with:** []
- **conflicts_with:** [whip_pan_left, whip_pan_right, crash_zoom_in, crash_zoom_out, infinite_zoom, first_person_view, chase_shot, low_tracking_shot]

### `locked_camera_time_lapse`
- **name_en:** Locked-camera time-lapse
- **name_ru:** Таймлапс с зафиксированной камерой
- **for_journey:** Камера стоит на месте, время сжато — движение проходит через стабильный кадр. Горизонт и композиция не меняются.
- **prompt_snippet:** Camera: locked-camera time-lapse. Movement: hold one fixed camera position while time moves rapidly forward. Speed: fast time compression with a stable camera. Framing: keep the same composition and horizon as motion passes through the frame. End: finish from the same camera angle with visible passage of time.
- **category:** specials
- **pace:** fast
- **harmonizes_with:** [static_shot, tilt_shift_miniature_view]
- **conflicts_with:** [dolly_in, dolly_out, tracking_shot, handheld_shot, chase_shot, truck_left, truck_right]

### `pass_through_movement`
- **name_en:** Pass-through movement
- **name_ru:** Проход сквозь
- **for_journey:** Камера едет к видимому объекту, поверхности или барьеру и продолжает в пространство за ним. Проём/поверхность — центр перехода.
- **prompt_snippet:** Camera: pass-through movement. Movement: move forward toward a visible object, surface or barrier and continue into the space beyond. Speed: smooth centered glide. Framing: keep the opening or surface centered as the transition point. End: arrive inside the revealed space beyond.
- **category:** specials
- **pace:** medium
- **harmonizes_with:** [push_past, dolly_in, first_person_view, drone_push_in]
- **conflicts_with:** [static_shot, locked_camera_time_lapse, whip_pan_left, whip_pan_right, crash_zoom_out]

---

## Index (46)

| # | id | category | pace |
|---|-----|----------|------|
| 1 | `static_shot` | pan_tilt | slow |
| 2 | `pan_right` | pan_tilt | medium |
| 3 | `pan_left` | pan_tilt | medium |
| 4 | `whip_pan_right` | pan_tilt | fast |
| 5 | `whip_pan_left` | pan_tilt | fast |
| 6 | `tilt_up` | pan_tilt | medium |
| 7 | `tilt_down` | pan_tilt | medium |
| 8 | `slow_zoom_in` | zoom_lens | slow |
| 9 | `slow_zoom_out` | zoom_lens | slow |
| 10 | `fast_zoom_in` | zoom_lens | fast |
| 11 | `fast_zoom_out` | zoom_lens | fast |
| 12 | `crash_zoom_in` | zoom_lens | fast |
| 13 | `crash_zoom_out` | zoom_lens | fast |
| 14 | `dolly_in` | dolly_track | medium |
| 15 | `dolly_out` | dolly_track | medium |
| 16 | `truck_right` | physical | medium |
| 17 | `truck_left` | physical | medium |
| 18 | `pedestal_up` | physical | medium |
| 19 | `pedestal_down` | physical | medium |
| 20 | `slider_right` | physical | slow |
| 21 | `slider_left` | physical | slow |
| 22 | `push_past` | physical | medium |
| 23 | `arc_right` | physical | medium |
| 24 | `arc_left` | physical | medium |
| 25 | `clockwise_orbit` | physical | medium |
| 26 | `counterclockwise_orbit` | physical | medium |
| 27 | `tracking_shot` | dolly_track | medium |
| 28 | `follow_shot_from_behind` | dolly_track | medium |
| 29 | `reverse_tracking_shot` | dolly_track | medium |
| 30 | `side_tracking_shot` | dolly_track | medium |
| 31 | `low_tracking_shot` | dolly_track | medium |
| 32 | `vehicle_tracking_shot` | dolly_track | medium |
| 33 | `chase_shot` | dolly_track | fast |
| 34 | `body_mounted_snorricam` | human_camera | medium |
| 35 | `handheld_shot` | human_camera | medium |
| 36 | `crane_up` | drone_crane | slow |
| 37 | `crane_down` | drone_crane | slow |
| 38 | `drone_push_in` | drone_crane | medium |
| 39 | `drone_pull_back` | drone_crane | medium |
| 40 | `helicopter_style_aerial` | drone_crane | slow |
| 41 | `first_person_view` | specials | medium |
| 42 | `tilt_shift_miniature_view` | specials | slow |
| 43 | `infinite_zoom` | specials | fast |
| 44 | `earth_zoom_out` | specials | fast |
| 45 | `locked_camera_time_lapse` | specials | fast |
| 46 | `pass_through_movement` | specials | medium |
