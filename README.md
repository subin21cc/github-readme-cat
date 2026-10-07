<div align="center">

# github-readme-cat

**Pixel-art cats that walk across your GitHub profile README.**
The more you code, the faster they go.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./examples/cat-dark.svg">
  <img alt="A pixel cat walking" src="./examples/cat-light.svg">
</picture>

English | [한국어](./README.ko.md)

</div>

## Features

- 🐾 **A real cat walk**: a 4-beat walk cycle (hind leg, then front leg on the same side), a swaying tail and blinking eyes
- 🎨 **Make it your cat**: 8 ready-made cats, or pick your own colors, coat pattern, eyes (even odd eyes), folded ears, a short tail and a collar. Up to three cats share one lane
- 📈 **Moves with your activity**: no contributions → the cat stands and waits, 1-9 → it walks, 10+ → it hurries
- 🌗 **Light and dark themes** for GitHub's color modes
- ⚡ **No server**: a GitHub Action writes plain SVG files into your own repo, so they never break

<img alt="Three cats with different coats" src="./examples/cats.svg">

## Quick start

1. Open your profile repository (the one named after your username, e.g. `octocat/octocat`).
2. Add `.github/workflows/readme-cat.yml`:

```yaml
name: readme-cat

on:
  schedule:
    - cron: "0 0 * * *"   # every day
  workflow_dispatch:

permissions:
  contents: write

jobs:
  cat:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: subin21cc/github-readme-cat@v1
        with:
          coats: orange        # e.g. orange,black,tabby
      - name: Commit
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add github-readme-cat
          git commit -m "update readme cat" && git push || echo "no changes"
```

3. Run it once from the **Actions** tab (`Run workflow`), then put this in your `README.md`:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./github-readme-cat/cat-dark.svg">
  <img alt="pixel cat" src="./github-readme-cat/cat-light.svg">
</picture>
```

## Options

| Input | Default | Description |
|---|---|---|
| `coats` | `orange` | Comma-separated cats, up to 3. See [Make it your cat](#make-it-your-cat) |
| `width` | `720` | Width of the lane all cats share (at least 240 px per cat, so standing cats never overlap) |
| `days` | `7` | How many recent days of contributions to count |
| `username` | repo owner | Whose contributions drive the cats |
| `output_dir` | `github-readme-cat` | Where `cat-light.svg` and `cat-dark.svg` are written |
| `github_token` | `github.token` | Token used to read the contribution count |

## Make it your cat

<img alt="A calico with folded ears and a red collar, a siamese with odd eyes and a short tail, and a tuxedo cat" src="./examples/custom.svg">

Each cat in `coats` is a preset, options, or both. Options override the preset:

```yaml
coats: "calico ears=fold collar=red, siamese eyes=blue/amber tail=short, tuxedo collar=#4a90d9"
```

**Presets:** `orange`, `black`, `tabby`, `gray`, `white`, `tuxedo`, `calico`, `siamese`

| Option | Values | |
|---|---|---|
| `fur` | color | Main coat color |
| `stripe` | color | Stripes, or the second color of `calico` / `siamese` |
| `belly` | color | Chest, belly and paws |
| `eyes` | color, or `left/right` | `eyes=green`, odd eyes: `eyes=blue/amber` |
| `pattern` | `tabby`, `solid`, `tuxedo`, `calico`, `siamese` | Where the colors go |
| `ears` | `pointed`, `fold` | |
| `tail` | `long`, `short` | |
| `collar` | color, `none` | Collar with a little bell |

A color is `#rrggbb`, `#rgb` or a name: `black`, `white`, `gray`, `cream`, `brown`, `orange`, `red`, `pink`, `purple`, `blue`, `green`, `yellow`, `amber`, `copper`.

Want it to look like your own cat? Pick colors from a photo:

```yaml
coats: "fur=#c08552 stripe=#7a4a2a belly=cream eyes=green"
```

<img alt="A custom brown tabby with green eyes" src="./examples/my-cat.svg">

## Moods

| Contributions in `days` | Mood |
|---|---|
| 0 | Stands still, tail swishing slowly |
| 1-9 | Walks |
| 10+ | Hurries |

<img alt="Three idle cats" src="./examples/idle.svg">

## Run locally

Python 3 only, no dependencies:

```bash
python3 src/cat.py --coats orange,black --contributions 12 --theme dark --out cat.svg
```

## License

[MIT](./LICENSE). The cat is original pixel art drawn for this project.
