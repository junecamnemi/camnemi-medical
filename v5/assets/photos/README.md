# assets/photos — 사진 슬롯 (PH) + 성형 광고 이미지 (AD-01)

실제 사진은 **두 장뿐**이다: `amc-campus.webp`(이 폴더, Hero 배경) 와 `../doctor-chea.webp`(Coordinator, 실사 정본 — 합성·보정 금지).
그 밖의 모든 사진 자리는 **AI 일러스트**이고, 캡션 `Illustrative image`가 이미 예약되어 있다.
파일이 없는 PH / AD 슬롯은 공개 화면에서 **접혀 있다**(빈 칸이 "coming soon"처럼 보이지 않도록). `?preview` 또는 `#preview`로 열면 점선 프레임과 안내가 보인다.

| ID | 위치 | 데스크톱 비율 | 모바일 비율 | 파일명 / 형식 | 내용 | 캡션 |
|---|---|---|---|---|---|---|
| PH-01 | `#why-amc` C. 갤러리 2행 1칸 | 4:3 | 4:3 | `ph-01.webp` | 병원 국제환자 라운지(분위기) | Illustrative image |
| PH-02 | `#why-amc` C. 갤러리 2행 2칸 | 4:3 | 4:3 | `ph-02.webp` | 밝은 영상검사실 / 스캐너(환자 없음) | Illustrative image |
| PH-03 | `#why-amc` C. 갤러리 2행 3칸 | 4:3 | 4:3 | `ph-03.webp` | 의료진 회의 장면(실존 인물 아님) | Illustrative image |
| PH-04 | `#camnemi-korea` 하단 왼쪽 | 16:10 | 4:3 | `ph-04.webp` | 코디네이터가 방문객을 맞이 / 동행 | Illustrative image |
| PH-05 | `#camnemi-korea` 하단 오른쪽 | 16:10 | 4:3 | `ph-05.webp` | 여러 언어로 대화(통역·언어 조율 분위기) | Illustrative image |
| AD-01 (이미지) | `#programs` Plastic Surgery 카드 오른쪽 | 4:5 | 4:5 (영상이 있으면 모바일은 9:16 영상) | `ad-01.webp` | 소피아 광고 이미지 — **AI 생성 모델** | Illustrative AI-generated image |

PH 갤러리 줄(PH-01~03, PH-04~05)은 그 줄의 슬롯 하나라도 채워져야 나타난다.

## 내용 규칙 (모든 PH / AD)
- AI 일러스트임이 분명한 화풍. 실존 환자·실존 AMC 직원·Dr. Chea 얼굴을 합성하지 않는다.
- 전후 비교, 수술 결과 묘사, 상처·피, 환자 후기 장면 금지.
- 글자를 넣지 않는다(특히 가격·기간·"best/No.1"·순위). 로고는 AMC / Camnemi 공식 파일만.
- 색감은 tokens.css 팔레트(navy / sky / white)와 어울리게.
- AD-01: 결과·전후·"best"·"guarantee"·가격 문구 금지. 모델이 AI 생성임을 캡션(`Illustrative AI-generated image`)으로 밝힌다(이미 예약됨).

## 채우는 법
1. 파일을 이 폴더에 넣는다(긴 변 1600px 이상 권장, webp).
2. `src.html`의 해당 `<figure class="slot ph" data-ph="PH-0x" data-src="">`에 `data-src="assets/photos/ph-0x.webp"`를 넣는다. `data-alt`는 그림 내용에 맞게 고친다.
3. AD-01은 `data-src="assets/photos/ad-01.webp"` + (영상이 있으면) `data-video`, `data-poster`를 넣고 **`data-ready="true"`**로 바꿔야 공개된다. `data-ready="false"`인 동안은 `?preview`에서만 프레임이 보이고, 공개 화면에서는 카드가 텍스트 + MG-04 윤곽선 모션만 보여준다.
4. 비율은 CSS 변수(`--r-d`, `--r-m`)로 고정되어 있다. 다른 비율 파일은 `object-fit:cover`로 잘린다.
