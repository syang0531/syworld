# SY World

**SY 모드를 한 팩으로.** 던전, 마을, 기계, 마법 — 전부 바닐라 재료로, 바닐라가 하던 일은 그대로 둔 채.

Minecraft **26.2** / **NeoForge 26.2.0.88** CurseForge 모드팩 — [curseforge.com/minecraft/modpacks/syworld](https://www.curseforge.com/minecraft/modpacks/syworld). 새 SY 모드가 나오면 이 팩에 더해진다.

| 모드 | 무엇을 하나 | CurseForge |
|---|---|---|
| SY Dungeon | 손으로 지은 조각을 매번 다르게 이어 붙이는 던전 스물일곱 | [sydungeon](https://www.curseforge.com/minecraft/mc-mods/sydungeon) |
| SY Village | 마을을 키우는 연장 — 건물 도면, 떠나지 않는 골렘, 이주하는 가족 | [syvillage](https://www.curseforge.com/minecraft/mc-mods/syvillage) |
| SY Works | 이미 캔 잡템을 바닐라 재료와 경험치로 되돌리는 기계 셋 | [syworks](https://www.curseforge.com/minecraft/mc-mods/syworks) |
| SY Magic | 지팡이 한 자루, 마법책 세 권. 귀환 마법책으로 자석석에 돌아간다 | [symagic](https://www.curseforge.com/minecraft/mc-mods/symagic) |

## 이 저장소에 있는 것

```
syworld/
├── pack.json                  팩 설정 — CurseForge 프로젝트 id, Minecraft 버전, 들어가야 할 SY 모드 목록
├── pack/                      CurseForge 앱에서 내보낸 모드팩 zip (버전마다 하나)
├── CHANGELOG.md               "## <버전>" 구간이 CurseForge 변경 내역이 된다
├── PUBLISHING.md              배포 절차
├── tools/
│   └── publish.py             내보낸 zip을 검사하고 CurseForge에 올린다 (표준 라이브러리만)
├── docs/
│   ├── 진행상황.md            다음 세션 인계
│   └── curseforge/            등록 문구 · 로고
└── .github/workflows/release.yml   태그를 밀면 검사 → CurseForge 업로드 → GitHub Release
```

**모드팩 자체는 CurseForge 앱이 만든다.** CurseForge 규정이 앱으로 만든 형식을 요구하고, 앱이 쓴 manifest를
손으로 고치는 것을 금한다. 그래서 이 저장소는 팩을 만들지 않는다 — 앱에서 내보낸 zip을 검사하고, 그대로 올린다.
절차는 [PUBLISHING.md](PUBLISHING.md).

```powershell
python tools\publish.py 1.0.0 --dry-run   # 내보낸 zip 검사 (토큰 불필요)
```

## 라이선스

MIT — [LICENSE](LICENSE).
