# LookLearnFind — Minnesota election images

Four AI illustrations in the quiet photographic election-page series. Display **AI illustration** in HTML; no credit or page text is painted into the images.

## JPEGs

Each key appears once in `masters/` at **3600 × 2400** and once in `web/` at **1800 × 1200**.

| Key | Scene | Web bytes |
| --- | --- | ---: |
| s7-minnesota | Northern lake, dock, mist and golden birches | 326654 |
| mn-capitol | Minnesota State Capitol across an autumn lawn | 274380 |
| mn-senate | Mississippi River, stone arch bridge and mill ruins at dusk | 273461 |
| mn-01 | Grain bin, cut soybean fields, gravel road and two blank wooden boards | 271725 |

Masters use JPEG quality 90. Web files use quality 80 and are each below 350000 bytes. All JPEGs are progressive, use 4:2:0 chroma subsampling and include an sRGB ICC profile.

## Production notes

The built-in image generation tool returned **1536 × 1024** for each scene. The requested dimensions are **Lanczos upscales** from those originals: 2.34375× for masters and 1.171875× for web. These are not native 3600 × 2400 generations. No sharpening, compositing or creative retouching was applied after generation. The untagged RGB source data was treated as sRGB when exported.

The exact generation prompts are in `prompts/`. `manifest.json` records the dimensions, bytes, quality settings, checksums and suggested focal points.

## Visual review

- PASS — No living people, faces, human silhouettes or human reflections were found.
- PASS — No readable text, numerals, logos or flags were found.
- PASS — No party-color signals or campaign branding were found. Both farm boards are blank natural wood.
- PASS — Primary subjects are arranged near the middle. The lower corners retain low-detail ground, lawn or water for the page overlays.

The Capitol's small architectural statuary is part of the building ornament. Landmark scenes are generated interpretations and are not documentary photographs or surveyed architectural reproductions. The no-text and no-people checks are manual visual judgments. Actual HTML overlay sizes were not supplied, so final overlay fit is not verified.

Only the earlier Michigan tile was visible in this conversation; the other companion sets were matched through the supplied style description.

Architectural context consulted: [Minnesota Historical Society](https://www.mnhs.org/capitol/learn/architecture), [Stone Arch Bridge](https://www.minneapolisparks.org/parks-destinations/historical_sites/stone_arch_bridge/) and [Mill Ruins Park](https://www.minneapolisparks.org/parks-destinations/parks-lakes/mill_ruins_park/). No retrieved photograph is included in the artwork or package.
