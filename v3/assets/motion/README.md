# Motion graphic slots (medical.camnemi.com/v2)

Drop finished files in this folder, set `data-src` on the matching `<figure class="mg" data-mg="MG-0x">` in `src.html`
(e.g. `data-src="assets/motion/mg-01.mp4" data-poster="assets/motion/mg-01.jpg"`), then run `python build.py`.

| Slot  | Location                            | Desktop | Mobile | Suggested file |
|-------|-------------------------------------|---------|--------|----------------|
| MG-01 | Band directly under the hero        | 21:9    | 4:3    | mg-01.mp4      |
| MG-02 | Official Agency section (AMC intro) | 16:9    | 4:3    | mg-02.mp4      |
| MG-03 | Top of "What AMC offers"            | 21:9    | 4:3    | mg-03.mp4      |
| MG-04 | Top of "Five steps, one ticket"     | 21:9    | 4:3    | mg-04.mp4      |

Formats: MP4 (H.264) or WebM, silent, loopable, about 3 MB or less each; or Lottie (.json/.lottie); or a still image. Supply a poster frame too (used for reduced-motion users).
Content rules: no prices, durations, rankings, patient volumes, success rates or eligibility promises. Palette from tokens.css (navy/sky, no gradients or shadows).
