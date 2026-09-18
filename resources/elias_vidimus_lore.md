# The Artisan of Glimmith — Elias Vidimus 대사 & Lore 텍스트 전수 추출

- **추출 방법**: Steam 정식판(`The Artisan of Glimmith`) 게임 파일 `Geri/Content/Paks/pakchunk0-WindowsNoEditor.pak`에서 `repak_cli`로 `Geri/Content/Localization/Game/{en,ko}/Game.locres` 두 파일을 추출한 뒤, `pylocres` 라이브러리로 바이너리를 파싱해 전체 393개 텍스트 엔트리를 en/ko 대조표로 만들고 그중 서사/세계관 관련 텍스트를 선별했습니다. (나머지는 UI 라벨, 퍼즐 규칙 설명, 옵션 메뉴, 크레딧 등 lore와 무관한 텍스트였습니다.)
- **중요 caveat**: `.locres` 내부의 항목 순서는 게임 내 실제 등장 순서(스토리 진행 순서)와 반드시 일치하지 않습니다. 아래는 게임 파일에 존재하는 **텍스트 원문 전부**이며, 편지 묶음 내부의 순서는 원문 상 서로 인접해 있어 신뢰할 수 있지만, 편지 묶음들 사이의 선후 관계(어느 편지가 게임상 먼저 오는지)는 파일 순서만으로는 확정할 수 없습니다.
- 게임 내 이름 표기: `Elias Vidimus` (한국어판: **엘리아스 비디무스**). "Vidimus"는 라틴어로 "우리가 보았다"라는 뜻으로, 실제 중세 스테인드글라스 제작에서 쓰이던 "비디무스(설계 도안)"라는 용어와 같아 스테인드글라스 복원이라는 게임 테마와 맞닿아 있는 이름입니다.

---

## 1. Elias Vidimus가 보낸 편지 (Letters)

게임 내에서 Elias는 플레이어("Artisan/장인")에게 편지 형태로 말을 건넵니다. 각 편지는 인사말 → 본문 → (진행 팁, 빨간 글씨로 강조) → 서명 순으로 구성되어 있습니다. 아래는 locres에서 서명(`~ Elias Vidimus`)이 확인된 편지 6통과, 서명 없이 등장하는(같은 문체의) 짧은 인용구 3개입니다.

**⚠️ 2026-09-18 실제 플레이 전면 정정**: 아래 "서명 없는 짧은 인용구 3개"는 독립된 편지가 아니라, 실제 게임에서는 전부 편지 A/B/D의 도입부로 이어 붙어서 하나의 편지로 출력되는 것으로 확인됐다(인용구1→편지D, 인용구2→편지B, 인용구3→편지A). 실제 플레이 순서·합쳐진 전체 원문은 `elias_letters_playthrough_log.md`를 참고할 것 — 이 문서는 로케레스에서 뽑은 "원재료" 텍스트 목록이고, 실제 조립된 형태는 플레이 로그 쪽이 최종본이다.

### 편지 A — "Well done, Artisan." (진행 축하 + 새 도안 배치 안내)

> **EN**
> **Well done, Artisan.**
> Across all of Glimmith, your restoration progress is: {0} ({1}%)
> Furthermore, I have delivered a collection of weighty designs across these lands and laid them atop crimson plinths.
> Should you rise to their challenge, you will have Glimmith's unwavering regard.
>
> With gratitude,
> ~ Elias Vidimus

> **KO**
> **훌륭합니다, 장인.**
> 글리미스 전체 복원 진행 상황: {0} ({1}%)
> 더불어 저는 묵직한 도안들을 이 땅 도처에 가져다 붉은 단상 위에 공들여 올려 두었습니다.
> 만일 그 도전에 응한다면 그대는 글리미스의 굳건한 신임과 존중을 한몸에 받게 될 것입니다.
>
> 깊은 감사와 함께,
> ~ 엘리아스 비디무스

---

### 편지 B — 10개 지역 완료 후, 창문에 숨겨진 마법

> **EN**
> Once you have fully completed ten areas, the way forward shall open.
> The windows are newly imbued with an enchantment that will reveal any artworks I've hidden too well.
>
> With shining regard,
> ~ Elias Vidimus

> **KO**
> 열 개의 구역을 빠짐없이 완성한 그때, 비로소 새로운 길이 그대 앞에 열릴 것입니다.
> 아울러 창에는 새로운 마법이 깃들어 있습니다. 제가 그토록 깊이 숨겨 두었던 작품들도 이제는 그 모습을 드러낼 것입니다.
>
> 깊은 경의를 담아,
> ~ 엘리아스 비디무스

---

### 편지 C — 유리공예 도안 지역 안내 (부분 완성만으로도 가능)

> **EN**
> **Respected Artisan,**
>     The areas ahead contain a vast collection of glasswork designs. But fear not! You need only complete a fraction of them to restore the windows.
> If ambition beckons, complete more glassworks to metallicize the frames and reveal extra challenges.
> If you thoroughly master an area, its frame will become gilded.
>
> Yours truly,
> ~ Elias Vidimus

> **KO**
> **존경하는 복원의 장인께,**
>     앞에 놓인 구역에는 실로 방대한 양의 도안들이 펼쳐져 있습니다. 그러나 염려치 마십시오. 그중 일부만으로도 창을 복원할 수 있습니다.
> 만일 야심이 그대를 이끈다면 더 많은 장식을 완성하여 창틀에 금속의 광채를 입혀주십시오. 더 많은 업적을 이룰 기회가 드러날 것입니다.
> 한 구역이 온전히 완성된다면, 그 곳의 창틀은 마침내 금빛으로 물들게 될 것입니다.
>
> 진심을 담아,
> ~ 엘리아스 비디무스

---

### 편지 D — 선택 구역(4개 창만 완료해도 진행 가능)

> **EN**
> This area is optional.
> You may proceed as soon as FOUR windows are complete.
> I commend your diligence and persistence.
>
> Yours truly,
> ~ Elias Vidimus

> **KO**
> 이 구역의 복원은 그대의 선택에 맡기겠습니다.
> 창 네 개가 완성되는 순간, 곧장 다음 장소로 나아가셔도 됩니다.
> 그대의 근면함과 흔들림 없는 끈기에 경의를 표합니다.
>
> 진심을 담아,
> ~ 엘리아스 비디무스

---

### 편지 E — 초대 수락에 대한 감사 + 유일한 부탁(규칙 준수, 색은 자유)

> **EN**
> **Dearest Esteemed Artisan,**
>     Thank you for accepting my invitation to restore the artworks of Glimmith.
> On that point, I have only one request.
> When shaping each piece of glass, you must follow the rules very closely!
> I care only about the shapes. Let your creativity run free with the colors!
>
> Yours truly,
> ~ Elias Vidimus

> **KO**
> **친애하는 복원의 장인께,**
>     글리미스의 옛 영광을 되찾아 달라는 저의 청을 기꺼이 수락해 주신 데 감사드립니다.
> 이에 관하여 그대에게 부탁드리고자 하는 바는 단 한 가지뿐입니다.
> 유리조각 하나하나를 다듬을 때에 정해진 규칙을 한 치도 벗어나지 말고 충실히 지켜 주십시오.
> 제가 중요히 여기는 것은 오직 형태입니다. 색채에 관해서만큼은 그대의 창의력과 영감을 마음껏 발휘해 주시기 바랍니다.
>
> 진심을 담아,
> ~ 엘리아스 비디무스

*(참고: 영문판에서는 "restore the artworks of Glimmith"만 쓰여 있지만, 한국어판에서는 "글리미스의 옛 영광을 되찾아 달라"는 표현이 추가되어 있어, 글리미스가 과거의 영광을 잃은 상태라는 세계관이 한국어 로컬라이징에서 더 명시적으로 드러납니다.)*

---

### 편지 F — 창틀 = 복원 진행도, 격려의 인사

> **EN**
> **Dearest Artisan,**
>     I hope this letter finds you in the best of spirits and creative fervor!
> There is much work to be done...
> These window frames show your restoration progress.
> Each glasswork you restore contributes to a window. Complete windows to progress onward.
>
> Yours truly,
> ~ Elias Vidimus

> **KO**
> **존경하는 복원의 장인께,**
>     이 편지가 그대에게 충만한 기운과 창작의 열의를 안겨 주기 바랍니다.
> 아직 해야 할 일이 많이 남아 있습니다...
> 이 창틀들은 그대가 이룬 복원의 진척을 보여 주고 있습니다.
> 그대가 복원하는 유리 장식 하나하나가 창을 채워 나갑니다. 창을 온전히 완성시켜 다음 여정을 이어가기 바랍니다.
>
> 진심을 담아,
> ~ 엘리아스 비디무스

---

### 서명 없이 등장하는 짧은 인용구 (같은 문체, 로딩화면/삽입구로 추정)

이 세 문장은 게임 파일 안에서 위 편지들과 떨어져 있고 서명이 붙어 있지 않지만, 문체와 "Artisan"을 부르는 방식이 동일한 Elias의 어투입니다.

> **EN — "Esteemed Artisan,"**
> I apologize for the preponderance of constraints I've laid upon your work. Many further rules are yet to come.
>
> **KO**
> 존경하는 복원의 장인께,
> 제가 그대의 작업에 지나친 제한을 둔 것은 아닌지 염려되는군요. 허나 앞으로 그대가 마주할 규칙은 아직도 많습니다.
>
> **⚠️ 2026-09-18 실제 플레이로 정정**: 이 문장은 독립된 인용구가 아니라, 실제 게임에서는 **편지 D(위 "선택 구역" 편지)의 도입부**로 이어 붙어서 하나의 편지로 출력됨(트리거 ID `AGeri/Puzzles/Data/FourWindows`). 로케레스 안에서는 별도 문자열 키였지만 UI가 여러 키를 이어 하나의 편지로 조립하는 구조. 합쳐진 전체 원문은 `elias_letters_playthrough_log.md` #3 참고.

> **EN — "Great Artisan of Glimmith,"**
> The isle ahead houses the most difficult restorations of any. They are yours, should you wish to attempt them.
>
> **KO**
> 영예로운 글리미스의 장인께,
> 앞에 놓인 섬에는 그 어느 것과도 견줄 수 없는 험난한 복원의 과업이 기다리고 있습니다. 그대에게 뜻이 있다면 그 모든 도전과 영광이 그대의 몫이 될 것입니다.
>
> **⚠️ 2026-09-18 실제 플레이로 정정**: 이 문장도 독립 인용구가 아니라 **편지 B("10개 구역 완성" 편지)의 도입부**로 이어 붙어서 출력됨. "앞에 놓인 섬"은 나선형 섬(Spiral Island)을 가리키는 것으로 추정. 합쳐진 전체 원문은 `elias_letters_playthrough_log.md` #5 참고. **이로써 서명 없는 독립 인용구 3개는 전부 오해였고, 실제로는 각각 다른 서명편지의 도입부였음이 확인됨.**

> **EN — "Great Artisan of Glimmith,"**
> Your skill shines through every pane of glass you've touched.
>
> **KO**
> 영예로운 글리미스의 장인께,
> 그대의 손길이 닿은 모든 유리 한 장, 한 장에서 그대의 솜씨가 빛나고 있습니다.
>
> **⚠️ 2026-09-18 실제 플레이로 정정**: 이 문장도 독립 인용구가 아니라, 실제로는 **편지 A(위 "Well done, Artisan" 편지)의 도입부**로 이어 붙어서 하나의 편지로 출력됨 (성 지역 완료 후 "완벽한 윈도우" 지점에서 확인). 합쳐진 전체 원문은 `elias_letters_playthrough_log.md` #4 참고.

---

## 2. 세계관 속 지명 (Glimmith의 장소들)

퍼즐 지역(레벨) 이름 중 지명으로 보이는 것들입니다 (퍼즐 규칙 이름인 Boxy/Bricky/Loopy/Compass/Palisade 등과는 구분됨).

| EN | KO |
|---|---|
| Glimmith Bridge | 글리미스 다리 |
| Glimmith Overlook | 글리미스 전망대 |
| Forest Trailhead | 숲길 입구 |
| Hedge Maze | 생울타리 미로 |
| Secluded Garden | 한적한 정원 |
| Spiral Island | 나선형 섬 |
| Castle Gates | 성문 |

---

## 3. 정리 — Elias Vidimus에 대해 파일에서 드러나는 것

- Elias Vidimus는 **글리미스(Glimmith)의 스테인드글라스/유리공예 작품 복원을 플레이어("장인/Artisan")에게 의뢰한 인물**입니다.
- 그는 편지를 통해서만 등장하며, 직접적인 대사(음성/컷씬 대화)는 게임 텍스트 데이터 안에 존재하지 않습니다. 즉 이 게임의 서사는 **서명편지 6통 분량**으로 매우 절제되어 있습니다 (로케레스상 "독립 인용구"로 보였던 3개는 전부 이 6통의 도입부였음이 실제 플레이로 확인됨 — 순수 신규 편지가 아님).
- 어조는 시종일관 격식 있고 정중하며("Esteemed/Respected/Dearest Artisan"), 플레이어의 실력을 존중하고 칭찬하는 멘토/의뢰인의 태도를 보입니다.
- 규칙(퍼즐 제약)에 대해 스스로 "제가 지나친 제한을 두었다"며 사과하는 자의식적 유머가 있고, 색상 선택 등 창의적 자유는 플레이어에게 맡긴다고 밝힙니다.
- 한국어판 번역(편지 E)에서 "글리미스의 옛 영광을 되찾아 달라"는 문구가 추가되어, 글리미스가 한때 영광을 누렸으나 현재는 복원이 필요한 쇠퇴한/훼손된 곳이라는 배경 설정이 암시됩니다.

---

## 부록 — 원본 전체 en/ko 대조 데이터

작업 중 생성된 전체 393개 항목의 원문(en/ko key-value 전체)은 아래에 CSV로 함께 저장되어 있습니다.
- `elias_vidimus_lore_en.csv`
- `elias_vidimus_lore_ko.csv`
