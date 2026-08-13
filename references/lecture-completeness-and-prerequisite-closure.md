# 講義の包括性と問題前提閉包

講義の新規制作、大幅更新、または問題集に登場するService、Artifact、連携Patternを講義で学べるか監査するときに使う。

## 1. 講義の学習契約

資格Levelは到達点であり、入口の暗黙前提ではない。Professional、Expert、Advanced等の講座でも、下位資格の取得や製品経験を、名称だけを理由に前提としない。前提にできるのは、次のいずれかだけである。

- ユーザーが既知だと明示した知識
- 公式に必須とされ、一次情報を記録した要件
- 一般的なIT基礎として範囲を具体化したもの
- 講座内で、最初に使う前に教えるもの

公式の「推奨経験」は必須条件ではない。推奨経験に含まれる知識を省略する根拠にせず、経験者が飛ばせる基礎経路と、未経験者が追いつける経路を分ける。

包括的とは、製品の全機能を百科事典のように列挙することではない。対象資格の問題を解くために必要な概念、Service、操作、連携、Artifact読解、障害診断、比較、設計判断を、明示した入口から切れ目なく学べることである。

## 2. カバレッジを四つの単位で持つ

試験領域だけでなく、問題が要求する知識を次の単位へ分解する。

1. **Foundation**: 基礎概念、用語、一般原理
2. **Service**: 製品Serviceまたは主要機能
3. **Artifact**: Code、Command、Configuration、Policy、Structured data、Diagram、Table、Log、Metric、Trace、UI等の読み方
4. **Integration**: 複数Service、Component、System間の接続とFlow

問題ごとに必要なUnitを列挙し、各Unitが問題より前に講義されていることを確認する。問題は新しいScenarioを提示してよいが、正答に必要な新しい基礎知識を初出させてはいけない。

## 3. Unit別の必須説明Dimension

### Foundation

- `plain_language_definition`: 平易な定義
- `mechanism`: 仕組みまたは因果関係
- `worked_example`: 小さな具体例
- `failure_or_misconception`: 誤解、失敗、または不適切な適用

### Service

- `purpose`: 何の問題を解くか
- `components`: 構成要素と責務境界
- `mechanism`: Request、Event、Data、Controlがどう処理されるか
- `configuration`: 代表的な設定または操作
- `security`: Identity、Policy、暗号化、Network境界
- `reliability_and_failure`: 可用性、Scaling、障害時の挙動
- `observability`: Log、Metric、Trace、Event、診断箇所
- `cost_and_performance`: 課金要因、Quota、性能特性
- `alternatives`: 類似Service、適用条件、Trade-off
- `integrations`: 他Serviceとの接続と役割
- `worked_example`: 要件から動作まで追える例

設計判断ページにService名が現れるだけではService講義とみなさない。上記Dimensionを、学習者向け本文のService固有の説明で満たす。

#### 上部Service curriculum契約

新規講座、講義の大幅更新、全面品質改修では、各講座の上部Navigationに独立したServiceカテゴリを置き、Domain／Task講義、通常問題、模擬問題より前へ配置する。Introduction、Foundation、用語集は必要に応じて先行できるが、Service知識を使う教材より後ろへ隠さない。

- 正規Navigation SourceからCategory ID、Kind、Label、Sequence、Landing path、Page pathのInventoryを生成し、Manifestと完全一致させる。
- Serviceカテゴリは親カテゴリを持たない第一級カテゴリとし、学習者がHeader、Category tab、または同等の上部Course navigationから直接開けるようにする。
- Serviceカテゴリ内に、公式範囲と正規AssessmentのStem・全候補で使う全Serviceまたは主要機能の正規Entryを置く。正答候補だけを抽出せず、学習者が比較して退けるDistractor Serviceも含める。各Entryは上記11 DimensionをService固有の包括的講義で満たす。
- 一枚のhandbook、名前一覧、比較表、外部LinkだけをCurriculum unitにしない。複数Serviceを一ページへまとめる場合もUnit別Evidenceと固定Anchorを保持する。
- 各Assessmentは必要な包括的Curriculum unitを参照する。Domain／Task講義は現在のScenarioに必要なServiceの責務とMechanismを該当本文で説明するが、ページ末尾へ包括的Curriculumを複製しない。
- Strict build後は全生成HTMLで上部Serviceカテゴリ、順序、Landing link、Active stateを検査する。Source ManifestだけでHeader表示を証明しない。

#### 固有Service encyclopedia entry契約

責務Familyや製品カテゴリはNavigationと比較の単位として使えるが、各固有Service／主要機能を教えた証拠にはしない。各Entryは用語集のように正式名称の独立見出しと「一言でいうと何か」から始め、用語集より厚い小講義として同じEntry内で11 Dimensionを満たす。

- 正規 `service_entries` Inventoryに、Entry ID、正式名称、Kind、所属Curriculum unit、Path、見出し、固定Anchor、Landing index evidence、導入順、全11 DimensionのExact learner-visible Evidenceを保持する。
- Landing pageは全Entryを正式名称で一覧または検索でき、宣言されたPageの固定Anchorへ直接Linkする。Family pageだけへLinkして学習者に手動探索を強制しない。
- Family unitは所属する `service_entry_ids` を持ち、Entry側の所属と完全一致させる。Family総論のEvidenceを子Entryへ流用しない。
- Entry Evidenceは宣言された見出しのMarkdown section内に限定する。別Entry、Family総論、Metadata、Anchor、見出し、外部DocumentationをEvidenceにしない。
- 全11 Dimensionを一文ずつ機械的に分断する必要はない。因果関係が読みやすい段落で複数Dimensionを扱えるが、少なくとも定義と目的、構成要素とMechanism、設定とSecurity、ReliabilityとObservability、Cost／Performanceと代替、IntegrationとWorked exampleを区別できるExact sliceで覆う。
- 最低語数は短い用語定義を除外する補助Gateにだけ使う。Service名を除去した本文が別Entryと同一、またはFamily共通Templateだけで固有Mechanism、Evidence、Decision boundaryがない状態は、語数にかかわらず失敗させる。
- 各Assessmentは learner-visible Stemと全候補から抽出した `named_services` と、対応する `service_entry_links` を持つ。両集合を完全一致させ、Entryを問題より前に置く。

#### Service表記の直接Link契約

各 `service_entry` は正式名称を含む `aliases` を持つ。講義およびAssessmentのlearner-visible Proseに正式名称またはaliasが現れたら、その表記自体を対応Entryの宣言Pathと固定Anchorへ直接Linkする。詳細は [service-mention-linking.md](service-mention-linking.md) に従う。

- 正規講義Inventoryの全Pageと、正規AssessmentのSourceが指す全learner-visible Pageを走査する。AssessmentはStem、全候補、正答解説、全誤答解説を含む。
- aliasはCourse内で一意に解決し、正式名称を必ず含む。`Amazon EKS`と`EKS`のような重なりは最長一致にし、短いaliasを長い表記の内部へ二重適用しない。
- LinkはServices LandingやFamily Page先頭ではなく、固有EntryのAnchorへ直接向ける。外部Documentation Linkは一次情報として別に保持する。
- fenced／inline code、Command、Configuration、URL、HTML属性、Markdown Link destinationは対象外にし、raw文字列置換で壊さない。
- Manifestの自己申告だけで完了せず、Source Markdownとstrict build後の全生成HTMLで、裸alias、誤Link、Anchor欠落、重複IDを検査する。

#### 通常講義でのService説明契約

通常のDomain／Task講義では、現在のScenarioを理解するために必要なServiceまたは主要機能の役割、Mechanism、設定、Failure、観測、Integrationを、それが必要な本文位置で説明する。Cloud以外の資格では、試験で独立した動作・設定・障害境界を問う主要製品機能またはComponentをService相当として扱う。

- 正規Sourceから全Lecture IDとPathのInventoryを生成し、Manifestの講義集合と完全一致させる。
- 上部Service curriculumの固有Entryが11 Dimensionを包括的に教え、各Assessmentが必要EntryへBindingされることを必須にする。
- 通常講義の末尾へ `AWS services in this lecture`、`Services used in this lecture` 等のService一覧や11 Dimensionの定型再掲を標準配置しない。既存の重複記述は内容を失わない範囲で削除する。
- 同じServiceを複数講義で使う場合も、現在のScenarioで必要な仕組みと責務境界を該当本文へ組み込み、名前とLinkだけで済ませない。一方、Service自体の包括的プロフィールは上部Curriculumへ一元化する。
- 見出し名を一律禁止する機械Gateは設けない。Generatorが末尾の重複Serviceセクションを再生成すると実証できた場合だけ、生成元を修正し回帰検査を追加する。

### Artifact

- `structure`: 全体の形式と目的
- `field_meaning`: Field、行、矢印、Operator、値の意味
- `normal_example`: 正常な実物例と読み順
- `failure_example`: 壊れた例、Error、異常値、誤設定
- `decision_use`: どのEvidenceが原因、修正、設計判断を拘束するか

問題に出すArtifact Typeは、講義で同じGrammarと判断方法を先に練習させる。単にCode fence、画像、表を置くことをArtifact教育とみなさない。

### Integration

- `service_roles`: 各ServiceまたはComponentの責務
- `request_or_event_flow`: Request、Event、Messageの順序
- `identity_and_policy`: Caller、Role、Policy、Trust、Network境界
- `data_or_state_flow`: Data、State、整合性、永続化の移動
- `failure_and_recovery`: 障害伝播、Retry、Failover、復旧境界
- `observability`: どこで何を観測して切り分けるか

Architecture Diagramだけで完了にせず、Data planeとControl plane、同期と非同期、正常時と異常時を必要に応じて分けて説明する。

## 4. 問題前提閉包Manifest

新規講座、講義または問題集の大幅更新、全面品質改修では、正規Sourceから機械可読な学習契約Manifestを生成する。手作業の事後申告だけをSource of truthにしない。

Manifestには最低限、次を保持する。

- `entry_contract`: 入口で仮定する知識、根拠、下位資格仮定の明示的承認
- `learning_units`: Unit ID、Kind、導入順、Subject、必須DimensionごとのLearner-visible Evidence
- `lectures`: 必要な場合の正規講義数、Lecture ID、Path、導入順
- `service_curriculum_policy`、`navigation_categories`、`service_curriculum`: 上部Serviceカテゴリ、Category順、Landing／Page path、比較・Navigation用Curriculum unit、全11 Dimension Evidence
- `service_entries`: 公式範囲とAssessment候補の固有Service Inventory、正式名称、Kind、所属Curriculum unit、Path、見出し、Anchor、Landing index evidence、導入順、Entry内の全11 Dimension Evidence
- `assessments`: 全問題ID、出現順、必要Unit、Service、Artifact Type、Integration Pattern、関連講義
- `assessment_policy.expected_count`: 正規問題数

各Evidenceは、学習者が問題を解く前に読めるMarkdownまたは生成HTMLのPathとExact contentを持つ。Filename、見出し、Metadata、Tag、Unit名だけをEvidenceにしない。一つの汎用文を複数Dimensionへ自己申告して合格させず、Dimensionごとに固有のExact sliceを対応付ける。

Manifestの形は次のようにする。これはSchemaの抜粋であり、実ファイルではKindごとの全必須Dimensionと全Assessmentを列挙する。

```json
{
  "version": 1,
  "course": {"id": "advanced-cloud-architect"},
  "entry_contract": {
    "assumptions": [
      {
        "id": "entry.general-it",
        "description": "Can read ordinary technical prose.",
        "basis": "general_it",
        "rationale": "Product-specific knowledge is taught in this course."
      }
    ],
    "assumed_certifications": []
  },
  "service_curriculum_policy": {
    "require_top_level_category": true,
    "require_named_service_entries": true,
    "require_service_mention_links": true,
    "service_category_id": "category.services",
    "expected_navigation_category_count": 3,
    "expected_service_count": 1,
    "expected_named_service_count": 1,
    "minimum_named_service_profile_words": 80
  },
  "navigation_categories": [
    {
      "id": "category.services",
      "kind": "service",
      "label": "Services",
      "sequence": 10,
      "landing_path": "services/index.md",
      "page_paths": ["services/index.md", "services/object-storage.md"],
      "parent_id": null
    }
  ],
  "service_curriculum": [
    {
      "id": "curriculum.object-storage",
      "subject": "Object Storage",
      "path": "services/object-storage.md",
      "sequence": 11,
      "service_entry_ids": ["service-entry.object-storage"],
      "evidence": []
    }
  ],
  "service_entries": [
    {
      "id": "service-entry.object-storage",
      "name": "Object Storage Service",
      "aliases": ["Object Storage Service", "OSS"],
      "kind": "service",
      "curriculum_unit_id": "curriculum.object-storage",
      "path": "services/object-storage.md",
      "heading": "## Object Storage Service",
      "anchor": "service-object-storage",
      "sequence": 12,
      "index_evidence": {
        "path": "services/index.md",
        "content": "[Object Storage Service](object-storage.md#service-object-storage)"
      },
      "evidence": []
    }
  ],
  "learning_units": [
    {
      "id": "service.object-storage",
      "kind": "service",
      "subject": "Object Storage",
      "curriculum_unit_id": "curriculum.object-storage",
      "sequence": 12,
      "evidence": [
        {
          "path": "services/object-storage.md",
          "content": "Object storage solves ...",
          "dimensions": ["purpose"]
        }
      ]
    }
  ],
  "assessment_policy": {"expected_count": 1},
  "assessments": [
    {
      "id": "Q-001",
      "sequence": 1000,
      "source": {"path": "questions/domain-1.md", "content": "Q-001"},
      "requirements": ["service.object-storage"],
      "lecture_links": ["service.object-storage"],
      "services": ["Object Storage"],
      "service_curriculum_links": ["curriculum.object-storage"],
      "named_services": ["Object Storage Service"],
      "service_entry_links": ["service-entry.object-storage"],
      "artifact_types": [],
      "integration_patterns": []
    }
  ]
}
```

問題ID集合は正規問題Sourceから書き出したJSONLと完全一致させる。Manifestに存在する問題だけを検査して、未登録問題を見逃すことを許可しない。

## 5. 必須Gate

同梱の `scripts/validate_learning_contract.py` または同等以上のプロジェクト固有Validatorで、少なくとも次をBlockerとして検出する。

```bash
python scripts/validate_learning_contract.py \
  --manifest data/learning-contract.json \
  --content-root docs \
  --question-jsonl data/questions.jsonl \
  --require-assessment-inventory \
  --navigation-jsonl data/navigation.jsonl \
  --require-service-curriculum \
  --service-entry-jsonl data/service-entries.jsonl \
  --require-named-service-entries \
  --require-service-mention-links
```

この共通Commandでは `--require-service-curriculum`／`--navigation-jsonl`、固有Service Entry、Service表記Linkを必須にする。`--require-service-sections`／`--lecture-jsonl` は、ユーザーまたはプロジェクト仕様が講義内Serviceセクションを明示的に要求する場合だけ追加する。上部Navigation専用Validatorや生成HTML検査は追加Gateであり、包括的Curriculumの代替ではない。

- Entry contractにない知識を暗黙に仮定している
- 明示的なユーザー承認なしに下位資格取得を仮定している
- 正規問題ID集合とManifestのAssessment ID集合が一致しない
- 問題が必要とするUnit、Service、Artifact Type、Integration Patternに先行講義がない
- Service、Artifact、Integration Unitが必須Dimensionを欠く
- Unitの導入順が、それを使う問題より後である
- EvidenceのPathが範囲外、存在しない、またはExact contentがLearner-visible本文にない
- 問題から必要Unitへの講義Linkが欠ける
- 正規Navigation InventoryとManifestのCategory、順序、Landing path、Page集合が一致しない
- 上部Serviceカテゴリが存在しない、親カテゴリの下にある、またはDomain／Task／Question／Mockカテゴリより後ろにある
- 包括的Service curriculumが11 Dimensionを欠く、Serviceカテゴリ外にある、またはLearner-visible Evidenceがない
- 正規Service-entry InventoryとManifestのID、正式名称、Kind、所属、Path、Anchorが一致しない
- 固有Service Entryが欠ける、固定Anchor／独立見出し／Landing直接Linkがない、宣言されたEntry section外のEvidenceを使う、または全11 Dimensionを満たさない
- Service名一覧、一文定義、Family総論の流用、Service名だけを差し替えた同一本文をEntryとして使う
- AssessmentのStemまたは全候補に現れる `named_services` と `service_entry_links` が一致しない、またはEntryが問題より後にある
- Service Entryの `aliases` がない、正式名称を含まない、同一aliasが複数Entryへ解決する、または正規Service-entry Inventoryと一致しない
- 講義またはAssessmentのStem、全候補、正答・誤答解説にaliasが裸文字で残る、あるいはLink先が宣言EntryのPath／Anchorと一致しない
- Services Landing、Family先頭、外部Documentation、別EntryへのLinkで固有Entryへの直接Linkを代用する
- 長いaliasの内部を短いaliasとして二重処理する、またはCode、URL、Link destinationをProseとして誤Linkする
- Assessmentが対応する包括的Service curriculum unitへBindingされていない
- 正規講義Inventoryを使用する場合にManifestのLecture IDまたはPathが一致しない

合格率は100%とする。60% Artifact問題ポリシーは「全選択肢のArtifact候補から正しい候補を選ばせる問題の割合」であり、StemへArtifactを置く割合でも、講義側の前提閉包を60%でよいとする規則でもない。問題で実際に要求するService、Artifact、Integrationはすべて先に教える。

## 6. Negative fixtureと意味Review

次を代表的な失敗Fixtureとして保持する。

- 設計判断だけがあり、Serviceの目的・仕組み・障害・観測を欠く
- 問題にService名を追加したが、Manifestと講義を更新していない
- Artifact問題はあるが、講義には形式名または完成例しかない
- Diagramはあるが、Identity、Data、Failure、ObservabilityのFlowがない
- EvidenceをMetadataへ宣言したが、学習者向け本文にExact sliceがない
- 問題IDをManifestから除外して、見かけ上100%にする
- Professional等の名称だけを理由に下位資格取得済みとする
- 上部NavigationにServiceカテゴリがない、またはQuestionカテゴリより後ろにある
- Serviceカテゴリ名はあるが、包括的Curriculum unitまたは11 Dimension Evidenceがない
- Family pageにService名一覧とFamily全体の11 Dimensionだけがあり、固有Service Entryがない
- 固有Service見出しはあるが、一文定義だけでMechanism、障害Evidence、Decision boundaryを欠く
- 二つのEntryからService名を除くと本文が同一で、名前だけを差し替えたTemplateになっている
- EntryのAnchorまたはLandingからの直接Linkがない
- 正答候補のServiceだけがEntryへBindingされ、Distractor Serviceが未講義である
- 講義の`EKS`が裸文字、問題StemだけLink済みでOptionまたは誤答解説の`EKS`が裸文字、または`EKS`がServices Landing／外部DocumentationへだけLinkされている
- 二つのEntryへ同じaliasを割り当てる、`Amazon EKS`内の`EKS`だけを処理する、またはCode fence内のaliasを未Linkとして誤検出する
- 包括的Service講義はあるが、AssessmentからBindingされていない
- 通常講義の末尾へ同じ `Services in this lecture` 一覧・定型プロフィールをGeneratorが全ページへ複製している

機械Gateは、宣言された関係とExact Evidenceの存在を検査する。説明が技術的に正しく、Dimensionを本当に教えているか、問題のRequirement列挙が完全かは意味Reviewで確認する。独立ReviewにはManifestだけでなく、正規問題、Learner-visible講義、Artifact実物を渡す。

## 7. 完了条件

次をすべて満たすまで「包括的」「問題を解ける講義」「完成」と宣言しない。

- 入口の前提が明示され、未確認の資格・経験を仮定していない
- 全Assessment IDが正規Sourceと一致する
- 全Assessment requirementが先行するLearning unitへ閉じている
- 全Service、Artifact、Integration Unitが必須DimensionをLearner-visible本文で満たす
- 上部Serviceカテゴリと包括的Service curriculumが正規Navigation、全Assessment、生成HTMLへ100%Bindingされている
- 全固有Service Entryが正規Inventory、所属Family、固定Anchor、Landing直接Link、全11 Dimension Evidence、全Assessment候補へ100%Bindingされている
- 全Service Entry aliasが一意で正規Inventoryと一致し、全講義・Assessment Proseの各出現が対応Entryの固定Anchorへ直接Linkされ、裸・曖昧・誤Linkが0件である
- Negative fixtureが意図どおり失敗する
- 意味Reviewで前提漏れ、説明の飛躍、名だけのService解説、飾りのArtifactが残っていない
