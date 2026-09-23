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

### A-3. CurseForge 앱에 프로필 만들기

1. CurseForge 앱 → Minecraft → **Create Custom Profile**
2. 이름 **SY World**, Minecraft **26.2**, 로더 **NeoForge 26.2.0.88**
3. SY Dungeon · SY Village · SY Works · SY Magic을 추가 — **CurseForge에서 승인된 파일만** 넣을 수 있다
   (방금 올린 버전이 아직 심사 중이면 승인된 이전 버전을 넣는다)

---

## B. 새 버전 배포

```text
1. 앱에서 프로필을 고친다        모드 버전을 올리거나, 새 SY 모드를 추가한다
2. 새 SY 모드라면 pack.json      "family"에 한 줄 (이름 · 프로젝트 id · slug) — 빠지면 검사가 막는다
3. 앱에서 내보낸다               프로필 ⋯ → Export Profile. 이름 SY World, 버전 = 새 버전 → pack/ 에 저장
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
- [ ] **첫 업로드는 처음 쓰는 경로다.** 모드는 CurseForgeGradle로 올렸고, 모드팩은 `publish.py`가 업로드 API를
      직접 부른다. 게임 버전은 Minecraft `26.2` 하나만 보낸다. CurseForge가 다른 항목(로더 등)을 요구하면
      오류 본문이 그대로 찍히니 그걸 보고 `metadata`에 더한다.
