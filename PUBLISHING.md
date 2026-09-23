# SY World 배포 가이드 (CurseForge 모드팩)

**한 번만 준비(A)** 해두면 이후에는 **앱에서 내보내고 태그를 밀면(B)** 됩니다.

---

## A. 최초 1회 준비

### A-1. CurseForge 프로젝트 생성

폼에 넣을 내용은 [`docs/curseforge/등록정보.md`](docs/curseforge/등록정보.md), 로고는 [`docs/curseforge/logo.png`](docs/curseforge/logo.png).

1. https://authors.curseforge.com → **Create A Project**
2. **Game**: Minecraft / **Class**: **Modpacks** / **Name**: SY World
3. Summary · Description · 카테고리 · 라이선스는 등록정보 문서에서
4. 생성 후 프로젝트 페이지의 **숫자 Project ID**를 [`pack.json`](pack.json)의 `curseforge_project_id`에 넣는다

### A-2. GitHub 저장소와 토큰

- 저장소를 만들고 push (`syang0531/syworld`)
- **시크릿은 저장소마다 따로다.** 모드 저장소에 넣은 `CURSEFORGE_TOKEN`은 여기서 안 보인다. 같은 토큰을 다시 등록한다:

```bash
gh secret set CURSEFORGE_TOKEN --repo syang0531/syworld
```

### A-3. CurseForge 앱에 dev 프로필 만들기

팩을 **내보내는 데만** 쓰는 프로필이다. 플레이는 여기서 하지 않는다 — [C](#c-프로필-둘--플레이용과-dev).

1. CurseForge 앱 → Minecraft → **Create Custom Profile**
2. 이름 **SY World (dev)**, Minecraft **26.2**, 로더 **NeoForge 26.2.0.88**
3. SY Dungeon · SY Village · SY Works · SY Magic을 추가 — **CurseForge에서 승인된 파일만** 넣을 수 있다
   (방금 올린 버전이 아직 심사 중이면 승인된 이전 버전을 넣는다)

> 1.0.0은 오래 플레이하던 `NeoForge 26.2` 프로필에서 내보냈다. 그 프로필이 이제 dev 프로필이다 —
> 앱에서 이름만 **SY World (dev)** 로 바꾸면 된다.

---

## B. 새 버전 배포

```text
1. dev 프로필을 고친다           모드 버전을 올리거나(승인된 파일만), 새 SY 모드를 추가한다
                                 테스트 월드로 한 번 켜 본다 — 가족 월드의 사본이면 더 좋다
2. 새 SY 모드라면 pack.json      "family"에 한 줄 (이름 · 프로젝트 id · slug) — 빠지면 검사가 막는다
3. 앱에서 내보낸다               dev 프로필 ⋯ → Export Profile. 이름 SY World, 버전 = 새 버전, config 체크 해제 → pack/ 에 저장
4. CHANGELOG.md                  맨 위에 "## <새 버전>" 구간
5. 검사                          python tools/publish.py <새 버전> --dry-run
6. 커밋 · 태그                   git add -A && git commit -m "Release <새 버전>" && git push
                                 git tag v<새 버전> && git push origin v<새 버전>
```

태그가 올라가면 [`.github/workflows/release.yml`](.github/workflows/release.yml)이

1. `pack/`에서 manifest 버전이 태그와 같은 zip을 찾아 검사하고 (이름 · Minecraft 버전 · NeoForge · SY 모드 전부 들어 있는지)
2. `CHANGELOG.md`의 해당 구간을 변경 내역으로 붙여 CurseForge에 올리고
3. 같은 zip과 변경 내역으로 GitHub Release를 만든다

진행 상황은 저장소 **Actions** 탭에서. 태그 없이 검사만 해 보려면 Actions → Release → **Run workflow**(dry run 체크).

### 로컬에서 올리기 (워크플로 없이)

```powershell
$env:CURSEFORGE_TOKEN = "..."; python tools\publish.py 1.0.0
```

---

## C. 프로필 둘 — 플레이용과 dev

| 프로필 | 용도 | 어디서 오나 |
|---|---|---|
| **SY World** | 가족과 실제로 플레이. 가족 컴퓨터에도 같은 것 | CurseForge에서 설치한 팩 |
| **SY World (dev)** | 새 모드 버전을 먼저 넣어 보고, **팩을 내보낼 때만** 쓴다 | 손으로 관리 |

왜 나누나:

- **가족 월드가 실험을 타지 않는다.** 새 버전이 월드를 깨도(SY Works 0.4.0처럼 이전 월드와 호환되지 않는 업데이트) dev에서 끝난다.
- **팩이 깨끗하다.** 오래 플레이한 프로필에는 옛 설정 · `.bak`이 쌓인다 — 1.0.0 첫 내보내기에 `placitum-common.toml`이 딸려 들어갔었다.
- **남들이 받는 팩과 같은 것으로 논다.** 팩에 문제가 있으면 가족이 먼저 만난다.

dev에서도 테스트 월드는 만들어도 된다. 가족 월드만 거기서 돌리지 않는다.

### 월드 옮기기

월드는 프로필의 `saves\` 아래 폴더 하나다. 모드와 버전이 같으면 다른 프로필로 옮겨도 전부 남는다.

1. 앱에서 SY World를 설치하고 한 번 실행했다 끈다 — `saves\`가 생긴다
2. `C:\Users\syang\curseforge\minecraft\Instances\<옛 프로필>\saves\<월드>`를
   `...\Instances\SY World\saves\`로 **복사**한다 (이동하지 않는다 — 원본이 백업이다)
3. 가족 컴퓨터에도 같은 팩을 설치하면 LAN으로 그대로 같이 한다

### 팩이 올라간 뒤 플레이용 프로필 업데이트

1. CurseForge 심사가 끝나면 앱의 SY World 프로필에 업데이트가 뜬다
2. **누르기 전에 `saves\`를 백업한다**
3. 업데이트한다. 가족 컴퓨터도 같은 버전으로 — LAN은 버전이 다르면 들어가지 못한다

월드가 이어지는지는 모드마다 다르다. 각 모드 CHANGELOG에 "이전 월드와 호환되지 않는다"가 없으면 이어진다.
있으면 팩의 CHANGELOG에도 그 말을 옮겨 적는다.

---

## CurseForge 모드팩 규정 — 지킬 것

- **앱으로 만든 형식이어야 한다.** 손으로 만든 zip은 거절된다.
- **앱이 쓴 manifest를 고치지 않는다.** 모드를 바꾸려면 앱에서 프로필을 고쳐 다시 내보낸다.
  `publish.py`는 읽기만 하고 고치지 않는다.
- **팩 안의 모든 파일이 CurseForge에 있고 승인된 상태여야 한다.** SY 모드는 전부 CurseForge에 있다.
- **로더가 맞는 모드만.** 전부 NeoForge다.
- 서버 팩을 올릴 때는 본 파일의 **Additional File**로 올린다.

## 배포 전 점검

- [ ] `pack.json`의 `curseforge_project_id`가 실제 값인가 — `1708139` (slug `syworld`)
- [ ] `CURSEFORGE_TOKEN` 시크릿이 이 저장소에 있는가 — 모드 저장소와 따로다
- [ ] 팩에 넣은 SY 모드 버전이 전부 CurseForge에서 **승인**됐는가
- [ ] `python tools/publish.py <버전> --dry-run`이 통과하는가
- [ ] 새 모드 버전이 이전 월드와 호환되지 않으면 CHANGELOG에 적었는가 — [C](#c-프로필-둘--플레이용과-dev)
- 업로드 경로(`publish.py`가 업로드 API를 직접 부르고, 게임 버전은 Minecraft `26.2` 하나만 보낸다)는
  1.0.0에서 추가 항목 요구 없이 통과했다. CurseForge가 나중에 다른 항목을 요구하면 오류 본문이 그대로 찍히니
  그걸 보고 `metadata`에 더한다.
