# assets/awards — 수상 배지 슬롯 (AW)

`src.html` `#amc-awards`의 `<figure class="slot aw" data-aw="AW-xx" data-src="" data-alt="…">`를 채운다.
배지 하나 = **판 하나 + 전문과 하나**. 각 카드 옆에 같은 내용이 텍스트로 이미 있으므로(스크린리더·이미지 미도착 대비) 이미지가 없어도 정보는 빠지지 않는다.
파일이 없을 때 공개 화면은 장식용 SVG 메달(순위·판 약어)을 보여주고, 점선 프레임 + 안내는 `?preview`에서만 보인다.

| ID | 판 (출판사) | 전문과 | 순위 표기 | 파일명 | 비율 |
|---|---|---|---|---|---|
| AW-01 | Best Specialized Hospitals Asia-Pacific 2026 (Newsweek × Statista) | Cardiology | #1 in Asia-Pacific list | `aw-01.webp` | 1:1 |
| AW-02 | 〃 | Cardiac Surgery | #1 in Asia-Pacific list | `aw-02.webp` | 1:1 |
| AW-03 | 〃 | Neurology | #1 in Asia-Pacific list | `aw-03.webp` | 1:1 |
| AW-04 | 〃 | Endocrinology | #1 in Asia-Pacific list | `aw-04.webp` | 1:1 |
| AW-05 | 〃 | Orthopedics | #1 in Asia-Pacific list | `aw-05.webp` | 1:1 |
| AW-06 | World's Best Specialized Hospitals 2027 (Newsweek) | Endocrinology | #2 | `aw-06.webp` | 1:1 |
| AW-07 | 〃 | Gastroenterology | #5 | `aw-07.webp` | 1:1 |
| AW-08 | 〃 | Urology | #5 | `aw-08.webp` | 1:1 |
| AW-09 | 〃 | Oncology | #6 | `aw-09.webp` | 1:1 |
| AW-10 | 〃 | Neurology | #9 | `aw-10.webp` | 1:1 |
| AW-11 | 〃 | Nephrology | #9 | `aw-11.webp` | 1:1 |

출처: `_ref_v4_CHANGES.md` §5 (rankings.newsweek.com, AP 2026 / World 2027, 2026-10-29~30 확인). 데스크톱·모바일 비율 모두 1:1(`--r-d:1/1`), 이미지는 `object-fit:contain`.

## 배지에 반드시 들어갈 것
- 출판사명(Newsweek 또는 Newsweek × Statista)
- 판 연도(Asia-Pacific **2026** / World **2027**)
- "by specialty"
- 전문과 이름(위 표 그대로)
- 순위 — AP 1위는 **"#1 in Asia-Pacific list"** 형태만. 세계판은 "#2", "#5" … 숫자만.

## 금지
- "world #1", "Korea's #1 hospital", 종합 순위(세계 28위 등), "No.1 / best / world-class"(판 이름 속 "Best"는 예외), 성과·생존율·만족도 수치.
- Newsweek/Statista 공식 로고·배지 사용 권한이 없으면 공식 배지를 복제하지 않는다 → **CEO 확인 필요**(CHANGES_V5 §6).

## 채우는 법
1. `aw-xx.webp`(투명 배경 권장, 최소 600×600) 를 이 폴더에 넣는다.
2. 해당 figure에 `data-src="assets/awards/aw-xx.webp"`를 넣는다. `data-alt`는 이미 배지 내용 그대로 적혀 있다(바꿀 필요 없음).
3. 로더가 `<img>`로 교체하고 SVG 메달·점선을 숨긴다.
