# Публикация на GitHub

Репозиторий: **https://github.com/mashajetruj-sketch/kiran-scroll-world**

## Перед push

1. Убедитесь, что в индексе **нет** `projects/`, `.env`, `*.mp4`, `*.png` (кроме `docs/assets/**`), персональных промптов и ключей.
2. Запустите gate:

```powershell
python scripts/validate_install.py
python -m pytest -q
```

## Первый push

```powershell
cd projects/scroll-world-kiran
git add .
git status   # проверьте список файлов
git commit -m "Initial public release: Kiran Scroll World Cursor plugin v0.1.2"
git branch -M main
git remote add origin https://github.com/mashajetruj-sketch/kiran-scroll-world.git
git push -u origin main
```

Если remote уже есть с другим URL:

```powershell
git remote set-url origin https://github.com/mashajetruj-sketch/kiran-scroll-world.git
git push -u origin main
```

## Поля репозитория (Settings → General)

| Поле | Значение |
|------|----------|
| **Description** | Cursor plugin: scroll-scrub fly-through — Kie gpt-image-2 storyboard panels + Seedance 2 Mini video legs + DOM overlays. By Nikita Kulikov. |
| **Website** | https://samsebeingener.ru/ _(опционально)_ |
| **Topics** | `cursor`, `cursor-plugin`, `scroll-scrub`, `kie-ai`, `gpt-image-2`, `seedance`, `landing-page`, `gsap` |
| **Social preview** | Upload `docs/assets/github-cover.png` |

## Topics (copy-paste)

```
cursor cursor-plugin scroll-scrub kie-ai gpt-image-2 seedance landing-page gsap scroll-world video-generation
```
