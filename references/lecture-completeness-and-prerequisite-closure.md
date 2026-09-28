# 講義の包括性と問題前提閉包

講義の新規制作、大幅更新、または問題集に登場するService、Artifact、連携Patternを講義で学べるか監査するときに使う。

必要知識を先に学べることは共通の品質要件とする。本書のサービスカテゴリ・固有Entry・全出現リンクに関する契約と厳格CLIは、[講座設定](course-settings.md) のサービス学習の導線を採用する場合に適用する。既存の個人用講座サイトではこの設定を継承する。別形式の教材には適した配置・検査を選ぶが、対象知識の説明と前提の充足を省略しない。

## 1. 講義の学習契約

資格Levelは到達点であり、入口の暗黙前提ではない。Professional、Expert、Advanced等の講座でも、下位資格の取得や製品経験を、名称だけを理由に前提としない。前提にできるのは、次のいずれかだけである。

- ユーザーが既知だと明示した知識
- 公式に必須とされ、一次情報を記録した要件
- 一般的なIT基礎として範囲を具体化したもの
- 講座内で、最初に使う前に教えるもの

公式の「推奨経験」は必須条件ではない。推奨経験に含まれる知識を省略する根拠にせず、経験者が飛ばせる基礎経路と、未経験者が追いつける経路を分ける。

包括的とは、製品の全機能を百科事典のように列挙することではない。対象資格の問題を解くために必要な概念、Service、操作、連携、Artifact読解、障害診断、比較、設計判断を、明示した入口から切れ目なく学べることである。

## 2. 問題集の全面再作成では問題から講義を作り直す

問題集の全面再作成では、新しい問題が要求する知識から講義を逆設計する。講義も依頼範囲に含まれる場合は同じ非流用境界で再制作する。問題内容の初期校正と、講義Link・表示を含む正式Reviewを分け、最終HashはLink確定後に固定する。

必須順序は次のとおりとする。

1. 公式試験範囲、一次情報、問題Source分析からAuthoring planを確定する。
2. 旧問題と旧講義を生成Seedにせず、新しい正規問題Corpusを作成する。代表例の読み比べ、正答性・曖昧さ・候補の初期校正を済ませ、問題内容を講義設計の入力として保存する。この段階はDraftであり、関連講義Linkの未確定を含む最終Gateや正式Review台帳のPASSを要求しない。
3. 全問題のStem、全候補、正答・誤答解説、Artifact契約からFoundation、Service、Artifact、IntegrationのRequirementを抽出する。正規問題の `learning_requirements` と抽出漏れの意味確認をもとに `assessment_requirement_inventory` を生成し、講義制作の入力SnapshotとそのHashを記録する。
4. Requirement集合を学習上の前提関係でClusterし、必要な講義数、章分割、導入順、Path、Service curriculum、Artifact grammar、Integration flowを決める。旧講義数や既存章立てを先に目標値へしない。
5. 新しいLecture IDまたは明示的な全面置換Manifestの下で講義本文を作り直す。問題で正答を決めるMechanism、Failure、Evidence、Decision boundaryを、問題より前に学べる本文として教える。
6. 新講義のInventoryから問題の関連Linkを割り当て、学習契約Manifestを生成する。正規問題・講義・生成表示をそろえて構造検査、全Requirementの閉包、講義の意味Review、生成再現性を検証する。
7. Linkを含む完成問題で全問の意味・独立Reviewを完了し、最終 `question_corpus_hash` と台帳を確定する。初期校正の記録は判断材料として再利用できるが、DraftのHashを最終版の証拠として転記しない。

旧講義のID、Path、本文、講義数はBaseline、非再利用監査、Link移行のためだけに参照できる。安定URLを保つためPathを再利用してもよいが、旧本文をSeed、Template、要約元、内容上限、または新問題の制約へ使わない。新問題を既存講義へ割り当てる、旧講義へ短い追記をする、Foundation／Service／Integrationの汎用補助ページだけを追加する、といった処理は講義全面再作成ではない。Domain／Task講義を含む再作成対象Corpusの本文そのものを、新問題Requirementから再設計する。

旧Lecture Pathを新問題の制約へ使わない。講義制作中に問題の正答性・曖昧さ・範囲逸脱を発見したら、DraftとRequirement Snapshotを更新して影響講義を直す。Link割当てだけでは必要知識を再設計しないが、最終HashにはそのLinkも含める。正式Review後の変更範囲と記録は [再レビュー基準](review-update-policy.md) に従う。講義へ収めるためだけにScenario、選択肢、正答を変えない。

`lecture_rebuild_manifest` または同等の機械可読な証拠へ、最低限次を保持する。

- 確定した正規問題ID集合と `question_corpus_hash`
- 講義設計に使ったDraft SnapshotのHash。最終Corpus Hashとは別Fieldで保持する
- 問題全件から生成した `assessment_requirement_inventory_hash`
- 旧講義Inventory、旧本文集合のBaseline Hash、再作成対象Path
- `old_lecture_seed_used=false` と、講義Generatorが読み込む正規Source一覧
- 新講義Inventory、各講義のID／Path／導入順／本文Hash
- 各Requirementから講義EvidenceへのTraceと、どの問題IDが各講義を必要としたか
- 問題修正後に下流のRequirement、講義、Reviewを無効化して再実行する規則

完了Gateでは、Manifestの自己申告だけでなく、講義Generatorが旧講義本文を入力にしていないこと、再作成対象の各本文が新Hashになっていること、旧講義の完全な段落が正式名称・一次情報の短い引用・Code・URL等の正当な共通部分を除いて残っていないことを検査する。さらに、講義数と章立てがRequirement clusteringの結果であり、着手前の講義数へ合わせた数合わせではないことを意味Reviewする。

## 3. カバレッジを四つの単位で持つ

試験領域だけでなく、問題が要求する知識を次の単位へ分解する。

1. **Foundation**: 基礎概念、用語、一般原理
2. **Service**: 製品Serviceまたは主要機能
3. **Artifact**: Code、Command、Configuration、Policy、Structured data、Diagram、Table、Log、Metric、Trace、UI等の読み方
4. **Integration**: 複数Service、Component、System間の接続とFlow

問題ごとに必要なUnitを列挙し、各Unitが問題より前に講義されていることを確認する。問題は新しいScenarioを提示してよいが、正答に必要な新しい基礎知識を初出させてはいけない。

## 4. Unit別の必須説明Dimension

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
- 各Assessmentは learner-visible Stem・全候補・全解説から抽出した `named_services` と、対応する `service_entry_links` を持つ。両集合を完全一致させ、Entryを問題より前に置く。

#### Service表記の直接Link契約

aliasの定義・最長一致・保護対象・正しいLink先・表示検証は [service-mention-linking.md](service-mention-linking.md) を正規基準にする。全講義とAssessmentのStem・全候補・全解説に適用する。必要知識一覧からの漏れの検査は、本書第5節の正規問題JSONL照合で補う。

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

## 5. 問題前提閉包Manifest

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

厳格検査の正規問題JSONLは、IDだけでなく `stem`、`options`、`correct_explanation`、`wrong_explanations` と次の `learning_requirements` を含める。プロジェクトのFieldが違う場合は読み取りAdapterで書き出す。

```json
{
  "learning_requirements": {
    "requirements": ["foundation.identity", "service.object-storage", "artifact.policy"],
    "services": ["Object Storage"],
    "artifact_types": ["policy-json"],
    "integration_patterns": [],
    "named_services": ["Object Storage Service"]
  }
}
```

これはField形の例であり、実問題の本文から抽出した値を使う。`requirements` は学習Unitまたは承認済みEntry assumptionのID、`services`・`artifact_types`・`integration_patterns` は学習契約側の語彙である。Option Artifactの粗い分類を無変換でコピーしない。

`--require-assessment-inventory` は正規JSONLとManifestの全IDおよび上記集合の一致を検査する。固有Serviceの厳格検査時には `named_services` も照合し、Stem・全候補・全解説で観測した登録aliasが正規必要知識から抜けた場合に失敗する。Code・URLはalias検出から除く。IDだけの既存Exportは本文と必要知識を追加して移行し、検査を無効化して通さない。

この照合だけで抽出の完全性は証明できない。未登録Service、暗黙の前提、Artifactの読解知識、Integrationの抽出漏れは、問題本文と必要知識一覧を突き合わせて意味Reviewする。Manifestを後から埋めた自己申告だけで100%閉包と報告しない。

## 6. 必須Gate

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

このCommandは個人用講座サイト設定の厳格な検査例であり、採用時にはサービス関連の引数も必須とする。別設定では `--require-assessment-inventory` による全問題の必要知識照合を保ち、採用した導線に対応する検査を使う。`--require-service-sections`／`--lecture-jsonl` は、講義内Serviceセクションを明示的に要求する場合だけ追加する。適用する以下の項目を検査計画へ対応づけ、設定の違いを理由に既存Gateを無断で弱めない。

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

合格率は100%とする。`artifact_target_ratio` は「全選択肢のArtifact候補から正しい候補を選ばせる問題の割合」であり、StemへArtifactを置く割合でも、講義側の前提閉包を同じ比率でよいとする規則でもない。問題で実際に要求するService、Artifact、Integrationはすべて先に教える。

## 7. Negative fixtureと意味Review

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
- 問題集を全面再作成したのに、旧講義数と旧Pathを先に固定し、新問題をそこへ割り当てただけである
- 旧Domain／Task講義本文を残したまま、汎用Foundation／Service／Integrationページの追加だけを講義再作成と申告する
- `lecture_rebuild_manifest` の問題Corpus HashまたはRequirement Inventory Hashが現行問題と一致しない
- 講義Generatorが旧講義本文をSeedまたはTemplateとして読み込む、あるいは旧講義の完全な段落が正当な共通部分を除いて残る
- 講義制作後に問題を修正したが、Requirement Inventory、影響講義、Review Hashを更新していない

機械Gateは、正規問題との必要知識の一致、登録済みServiceの抽出漏れ、宣言された関係とExact Evidenceの存在を検査する。説明が技術的に正しく、Dimensionを本当に教えているか、問題のRequirement列挙が完全かは意味Reviewで確認する。独立ReviewにはManifestだけでなく、正規問題、Learner-visible講義、Artifact実物を渡す。

## 8. 完了条件

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
- 問題集全面再作成では、新Draftの必要知識から講義を作り直し、Link割当て後の正式Reviewで最終Corpus Hashを固定した。旧講義への割当てや追記だけで代用していない
- `lecture_rebuild_manifest` が現行問題・Requirement・講義Hashと一致し、旧講義本文をSeedにしていないことと、問題修正時の下流再生成を証明する
