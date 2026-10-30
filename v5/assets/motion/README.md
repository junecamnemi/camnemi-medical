# assets/motion — 모션그래픽 슬롯 (MG) + 성형 광고 영상 (AD-01 영상)

`src.html`의 `<figure class="slot mg" data-mg="MG-0x" data-src="" data-poster="" data-alt="…">`를 채운다.
파일이 없을 때는 **인라인 SVG/CSS 모션이 기본 화면**이다(공개 페이지에서 빈 칸으로 보이지 않음). 점선 프레임과 파일 안내는 `?preview` 또는 `#preview`로 열 때만 보인다.

| ID | 위치 (섹션) | 데스크톱 비율 | 모바일 비율(≤700px) | 파일명 / 형식 | 기본 화면(파일 없을 때) | 내용 규칙 |
|---|---|---|---|---|---|---|
| MG-01 | `#why-amc` C. 갤러리 첫 칸 | 21:9 | 4:5 | `mg-01.mp4`(H.264) 또는 `.webm`, 포스터 `mg-01-poster.webp` | 해외 각지 → 서울(AMC) 경로 SVG, 혜성 선, "Seoul, Korea"/"International Healthcare Center" 태그 | AMC 캠퍼스·서울·국제진료 분위기. 숫자를 넣는다면 `#amc-numbers`에 있는 값만(43 / 19,152 / 52,838 / 11,377 / 654,536 / 6 / 1989 / 88 / 3,500+). 순위 숫자·병상 수·성과 수치 금지 |
| MG-02 | `#programs` Video Consultation 카드 상단 | 16:9 | 16:10 | `mg-02.mp4` (+ `mg-02-poster.webp`) | You · Local physician · AMC physician 세 점을 잇는 실시간 연결선 | 화상 연결 장면. "local physician" 동석이 보이게. 실존 의사 얼굴 금지(AI 일러스트·아이콘) |
| MG-03 | `#programs` Health Checkup 카드 상단 | 16:9 | 4:3 | `mg-03.mp4` (+ 포스터) | 검진 항목 8개 아이콘(CT, MR, PET, Gastroscopy, Colonoscopy, Echocardiography, Treadmill, Ultrasonography) 순차 등장 | 항목 이름은 위 8개(AMC 검진센터 설명)만. **"당일 / same-day / single day / 하루" 등 기간 표현 금지**, 소요 시간 표시 금지 |
| MG-04 | `#programs` Plastic Surgery 카드 오른쪽 | 4:3 | 4:3 | `mg-04.mp4` (+ 포스터) | 얼굴 옆선 윤곽선 라인 드로잉 | 추상 윤곽선만. 전후 비교, 결과 묘사, 실제 환자 금지. AD-01이 공개되면(아래) 공개 화면에서는 AD-01이 이 자리를 대신한다 |
| MG-05 | `#camnemi-korea` 여정 경로 | 21:8 | 3:4 | `mg-05.mp4` (+ 포스터) | Home country → Inquiry → AMC medical review → Arrival → Accompaniment 경로선 + 이동 점 | 단계 이름은 이 5개 그대로. **기간·시간·일수 표기 금지** |
| AD-01 (영상) | `#programs` Plastic Surgery 카드 오른쪽 (모바일에서만 재생) | — | 9:16 | `ad-01.mp4` + 세로 포스터 `ad-01-poster.webp`(9:16) | 없음(접혀 있음) | 소피아 광고 영상, AI 생성 모델. 이미지(4:5)는 `assets/photos/README.md` 참고. 결과·전후·"best"·가격 금지 |

## 채우는 법
1. 파일을 이 폴더에 넣는다(상대 경로만 사용).
2. `src.html`에서 해당 figure의 `data-src="assets/motion/mg-0x.mp4"`, `data-poster="assets/motion/mg-0x-poster.webp"`를 채운다.
   - `.mp4/.webm` → `<video muted loop playsinline>`로 교체, 화면에 보일 때만 재생.
   - `.json/.lottie` → 페이지가 `dotlottie-player`를 이미 제공할 때만 재생. **CDN은 로드하지 않는다**(라이브러리/CDN 금지). 없으면 `data-poster`를 보여준다.
   - 그 밖(이미지) → `<img>`.
3. `prefers-reduced-motion`이면 영상 대신 `data-poster`를 보여 준다. 포스터가 없으면 슬롯은 기본 SVG 화면을 유지한다.
4. 파일이 들어가면 기본 SVG 모션은 숨겨진다. MG-03 / MG-05의 항목 목록은 스크린리더용으로 남는다.
5. 비율은 CSS 변수(`--r-d` 데스크톱, `--r-m` 모바일)로 고정되어 있으니 파일을 그 비율로 만든다(다르면 `object-fit:cover`로 잘린다).
6. AD-01 영상: `data-video="assets/motion/ad-01.mp4"`, `data-poster="assets/motion/ad-01-poster.webp"`, 그리고 **`data-ready="true"`**로 바꿔야 공개된다.

## 공통 규칙
- 색은 tokens.css 팔레트(navy / sky / white 계열)만. 새 색·이모지 금지.
- 영상에 소리 없음(무음 자동재생). 깜빡임 3회/초 초과 금지.
- 문구를 넣는다면 사이트 본문과 같은 사실만. 가격·기간·성공률·"No.1/best"·병상 수 금지.
