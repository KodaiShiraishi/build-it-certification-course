---
name: build-it-certification-course
description: "Design, create, expand, audit, and publish exam-aligned IT certification courses and study sites for Databricks, AWS, Azure, Google Cloud, Kubernetes, security, networking, databases, and similar IT certification exams. Use when Codex is asked to plan a named IT certification curriculum, deepen its lectures, explain prerequisite terminology in plain language, add a clickable glossary, create or substantially expand high-quality practice questions or mock exams, review question quality, add hands-on labs, repair generated certification content, organize multiple certification courses in one study site, maintain an existing certification study site, or verify and publish it. Require an identifiable certification or exam objective in the request or existing project. Do not use for general programming tutorials, product onboarding, internal training, academic computer-science courses, language learning, hobbies, or courses without a certification target."
---

# Build IT Certification Course

Databricks、AWS、Azure、Google Cloud、Kubernetes、セキュリティ、ネットワーク、データベースなど、IT資格の合格と実務理解を両立する講座を設計・改善・検証・公開する。

## 基本契約

- ユーザーの明示的な指示を、このSkillの既定値より優先する。
- 新規講座を作る前に、教材で使う言語を確定する。ユーザーが依頼内で言語を明示していれば再質問せず、その言語を使う。明示していなければ、構成案や教材本文を作り始める前に「講座は何語で作成しますか？」と一度だけ簡潔に質問し、回答を待つ。会話や依頼文の言語から教材言語を推測しない。
- 確定した教材言語を設計上の要件として記録し、サイト名、ナビゲーション、講義、用語集、ハンズオン、通常問題、模擬問題、解答・解説、生成テンプレートに一貫して適用する。製品名、資格名、試験コード、API名、コード、コマンド、識別子、URLなど、翻訳すると不正確になる要素は正式表記のまま保つ。
- 新規講座で「まず話し合う」「構成案だけ」と指定された場合、対象読者、範囲、深度、演習、問題、公開方法を提示し、制作開始の合図を待つ。完成する設計書やカリキュラム自体を明示的に依頼された場合は、その設計成果物を作る。
- 「作って」「増やして」「更新して」と依頼された場合、調査だけで止まらず、実装、品質レビュー、検証まで進める。公開も依頼範囲なら公開後確認まで完了する。
- 「レビューして」「改善点を挙げて」だけの依頼では、許可なく編集しない。
- 一度狭められた範囲を守る。特定領域の拡充を止める指示があれば、別領域を直す際もそこへ変更を混ぜない。
- ユーザーとの会話では依頼の言語に合わせる。教材本文では確定した教材言語を使い、専門用語を必要以上に別言語のまま並べず、その教材言語で自然に説明してから正式名称を結び付ける。
- 既存教材では、実際のリポジトリ、設定、生成元、公開経路、未コミット変更を確認してから編集する。
- 資格講座のソースリポジトリはPrivateを既定とする。ユーザーがリポジトリ自体の公開を明示的に指定しない限り、新規作成時もサイト公開時も非公開で作成・維持し、Publicへ変更しない。
- ブラウザ操作で環境が不安定になるとユーザーが伝えた場合、ブラウザを使わない。厳格ビルド、生成HTML検査、直接HTTP確認で内容と構造を検証し、見た目や実操作を証明できない項目は未検証として報告する。
- モデル、Effort、サブエージェント構成はユーザーが作業ごとに選択する。このSkillでは特定のモデル、Effort、ワーカー、フォールバックを推奨または固定しない。
- 資格Levelは講座の到達点であり、入口の暗黙前提ではない。Professional、Expert、Advanced等の名称だけを理由に、下位資格取得、製品経験、Service知識を前提にしない。ユーザーが明示的に既知とした知識、公式に必須の要件、具体化した一般IT基礎以外は、問題より前に講座内で教える。
- 新規講座、講義の大幅更新、全面品質改修では、**講座上部Navigationの独立したServiceカテゴリと包括的Service講義を必須のBlocker契約**にする。ServiceカテゴリをDomain／Task講義、通常問題、模擬問題より前へ置き、問題に登場する全Serviceを体系的に学べる正規Inventoryと全11 Dimension Evidenceを機械検査する。
- 同じ範囲では、Serviceカテゴリ内の責務Familyや製品カテゴリを比較・Navigation単位として使えても、それを個々のService講義の代替にしない。公式範囲およびAssessmentのStemと全候補に現れる各固有Service／主要機能について、正式名称の独立Entry、固定Anchor、Landingからの直接Link、全11 DimensionのService固有Evidenceを持つ正規 `service_entries` Inventoryを必須にする。名前一覧、一文定義、Family共通本文、Service名だけを差し替えたTemplateを拒否する。
- 同じ範囲では、全Service Entryに正式名称と一意な略称を含む正規 `aliases` を持たせ、全正規講義と全learner-visible AssessmentのStem、全候補、正答・誤答解説に現れる各alias表記そのものを、対応EntryのPageと固定Anchorへ直接Linkする。裸文字、Landing／Family先頭／外部DocumentationだけへのLink、曖昧alias、CodeやURLを壊すraw置換を拒否する。
- 同じ範囲では、**全正規講義ページの本文内Serviceセクションも必須のBlocker契約**にする。上部の包括的Service講義と本文内のScenario固有Service説明は相互に代替せず、各Assessmentを両方へBindingする。別冊Service handbookや用語集だけでは合格させない。
- 二層Service契約では、包括的Curriculumへの `curriculum_unit_id`／`service_curriculum_links` とページ内Service requirementを正規Manifestへ保持し、共通Gateの `--require-service-curriculum --navigation-jsonl ...` と `--require-service-sections --lecture-jsonl ...` を同じReleaseで両方実行する。プロジェクト固有Navigation検査は追加できるが、どちらかの共通Gateを省略する代替にしない。
- このSkillを使う作業では、作業モードにかかわらず、プロジェクト内に意思決定をADRとして作成または更新する。着手時と完了前に [references/adr-and-skill-evolution.md](references/adr-and-skill-evolution.md) を読み、配置、内容、状態を揃える。監査・レビューだけの依頼でもADRの記録は例外として許可された編集とし、教材やコードは変更しない。
- 作業で得た知見を完了前に評価し、複数の資格・ベンダー・リポジトリへ汎用的に適用でき、今回の作業または検証で裏付けられた改善は、このSkillの `SKILL.md`、`references/`、`scripts/` の適切な生成元へ最小範囲で反映する。プロジェクト固有の事情、未検証の推測、短期的な製品仕様はADRまたはプロジェクト側の資料に留める。

## 1. 作業モードを判定する

依頼を次のいずれかとして扱い、権限を取り違えない。

1. **相談・構成案のみ**: ユーザーが相談または案だけを求めた場合、方向性を提示し、教材ファイルの制作開始を待つ。
2. **監査・レビュー**: 根拠付きで問題を報告し、編集しない。
3. **設計成果物・新規制作・改善**: 依頼された設計書、カリキュラム、ソースを作成し、検証と品質レビューまで行う。
4. **公開**: 既存の公開方式と自動実行を説明し、ビルド、反映、公開URL確認まで行う。

既存サイトの変更では、まず次を調べる。

- 原稿、ナビゲーション、テーマ、スタイル、ビルド設定
- 問題や講義を生成するスクリプト、構造化データ、テンプレート
- 試験範囲と各講義・演習・問題の対応
- 現在の問題数、説明量、リンク、公開状態
- Git差分とユーザーの既存変更

生成物に問題がある場合、生成後のMarkdownだけでなく、再生成しても直るように生成元を修正する。

既存講座へ別言語のページや問題を追加する依頼では、ユーザーが追加分の言語を明示していなければ、既存言語へ合わせてよいかを制作前に確認する。既存講座全体の翻訳を依頼された場合は、指定言語をサイト全体と生成元へ適用し、翻訳対象外の正式名称・コード・識別子を除いて旧言語が残っていないことを機械的に検査する。

## 2. 公式試験範囲を確定する

変更されやすい資格情報は、制作時点の公式一次情報で確認する。非公式なまとめや試験ダンプを試験範囲の根拠にしない。

試験ガイドは「何が出題されるか」、製品ドキュメントは「機能が実際にどう動くか」の根拠として分けて扱う。講義や正答を左右する主張には、公式URLと確認日を生成元または追跡可能な対応表へ残す。公式ページ同士で名称、提供日、Preview／GA状態、利用条件が一致しない場合、都合のよい一方を採用して断定しない。不一致を記録し、専用機能ページ、Release Notes、実際のAccount画面など、学習者が受験・演習時点で再確認できる場所を示す。

問題を新規作成または大幅拡張する場合は、現行の公式Sample questions、Practice test、Practice assessmentも先に調べ、問題の長さ、Artifact、判断粒度、形式を確認する。旧版・retiredのSampleは現行試験の直接根拠にしない。Login後にしか確認できない場合はアクセス制約をユーザーへ伝え、本人が確認できるなら実問題の転載ではなく抽象化した観察結果を依頼する。公式問題形式が不明なまま大量生成や最終的な問題構成を確定しない。詳細は [references/exam-question-fidelity.md](references/exam-question-fidelity.md) に従う。

最低限、次を記録する。

- 資格名、試験コード、対象バージョン、公式ガイドの更新日または確認日
- 試験領域、出題比率、問われる操作・判断
- 問題形式、試験時間、受験条件など教材設計に関係する事実
- 製品仕様のうち、講義や正答を左右する公式ドキュメント
- 名称変更、Preview／GA、Maintenance Mode、Region差など変更されやすい状態と確認日

次の対応表を作り、空白と偏りを可視化する。

| 試験領域・目標 | 重み | 講義 | ハンズオン | 通常問題 | 模擬問題 |
|---|---:|---|---|---:|---:|

試験比率だけで深さを決めず、後続理解の前提になる概念、誤解しやすい概念、実務で診断が必要な概念には十分な説明量を割り当てる。

領域対応表とは別に、問題が要求するFoundation、Service、Artifact Type、Integration Patternを正規問題Sourceから抽出し、それぞれを先行講義へ対応付ける。領域名だけが一致していても、問題で使うServiceの仕組み、Artifactの読み方、Service間Flowを講義していなければカバレッジありとみなさない。

## 3. 学習者の前提を二層で扱う

- 実務経験や既知の基礎を確認し、知っているSQLやPythonの初歩を主講義で繰り返さない。
- Entry contractとして、仮定する知識、根拠、講座内で教える知識を記録する。未確認の技術知識や下位資格取得を暗黙の前提にしない。公式の推奨経験は必須条件と区別し、省略の根拠にしない。
- 主講義の対象レベルとは別に、任意で読める「専門用語の前に読むページ」と用語集を用意する。ただし、問題の正答に必要な知識を任意の外部リンクだけへ追い出さず、講座内の先行経路で学べるようにする。
- 難しい領域を重点化しても、他の試験領域を短い箇条書きだけで済ませない。領域別のページ数、説明量、問題数を比較して偏りを検査する。
- 既知の人は基礎ページを飛ばせ、初学者はそこから追いつける導線にする。

## 4. 講義を前提順に設計する

講義の新規制作または大幅拡張では、先に [references/lecture-readability-standard.md](references/lecture-readability-standard.md) と [references/lecture-completeness-and-prerequisite-closure.md](references/lecture-completeness-and-prerequisite-closure.md) を読む。既存問題に対して講義カバレッジを監査または修復する場合も後者を読む。

章を「全体像 → 前提 → 内部の仕組み → 実装 → 運用・障害対応 → 設計判断 → 演習 → 問題」の順で接続する。製品機能の一覧を講義の代わりにしない。

講義をServiceの名前を知っている前提の設計判断集にしない。対象問題で使う各Serviceについて目的、構成要素、処理、設定、Security、障害、Observability、Cost／Performance、代替、Integration、Worked exampleを扱い、Artifact Typeには構造、Fieldの意味、正常例、失敗例、判断Evidenceを扱う。複数Serviceを使う問題には、Service別講義に加えてRequest／Event、Identity／Policy、Data／State、Failure／Recovery、Observabilityの接続を追うIntegration講義を置く。

### 上部Navigationの包括的Service講義をBlockerにする

各講座に、確定した教材言語で学習者に見える独立したServiceカテゴリを置く。講座Header、カテゴリTab、または同等の上部Course navigationで第一級カテゴリとして表示し、Domain／Task別の設計講義、通常問題、模擬問題より前へ配置する。IntroductionやFoundationをServiceカテゴリより前へ置くことはできるが、Service知識を使う講義や問題より後ろへ置かない。

ServiceカテゴリにはLanding pageと正規Service curriculum Inventoryを持たせる。問題に登場する各Serviceまたは主要機能について、目的、構成要素、Mechanism、設定、Security、Reliability／Failure、Observability、Cost／Performance、代替、Integration、Worked exampleをService固有の包括的講義として教える。一枚の長いhandbook、Service名の一覧、Documentation Link、比較表だけを包括的Service講義とみなさない。

責務Familyまたは製品カテゴリで複数Serviceを一ページへまとめる場合も、各固有Service／主要機能を用語集のように直接引ける独立見出しと固定Anchorにする。各Entryは「何か」の平易な定義だけで終わらず、解決する問題、構成要素と処理、設定とSecurity、障害と観測、Cost／Performance、代替、Integration、Worked exampleまで読める、用語集より厚い小講義にする。Family総論は比較の補助であり、子ServiceのEvidenceへ流用しない。

正規Inventoryは、公式のin-scope Service／Feature一覧と、正規AssessmentのStemおよび正誤を問わず全候補に現れる固有Service名の和集合から作る。正答候補だけを抽出してDistractor Serviceを未講義にしない。各 `service_entry` にID、正式名称、Kind、所属Curriculum unit、Path、見出し、Anchor、Landing index evidence、導入順、全11 DimensionのExact learner-visible Evidenceを保持し、独立したService-entry Inventoryと完全一致させる。

学習契約Manifestに `service_curriculum_policy`、`navigation_categories`、`service_curriculum` を保持し、正規Navigation Inventoryと一致させる。各ページ内Service unitは対応する包括的Service unitを `curriculum_unit_id` で参照し、各Assessmentは `service_curriculum_links` とページ内Service requirementの両方を持つ。上部カテゴリの完全な講義と、現在のScenarioでMechanismを再構成する本文内Serviceセクションの二層を維持する。

プロジェクト固有のNavigation validatorや静的HTML validatorを追加しても、下記の共通学習契約Commandから `--require-service-curriculum`、`--navigation-jsonl`、`--require-service-sections`、`--lecture-jsonl` のいずれも外さない。前二つは上部Curriculum、後二つはページ内適用講義を検査するため、別々のFailure surfaceである。

### 全講義ページのServiceセクションをBlockerにする

各正規講義ページに、確定した教材言語で学習者に見えるServiceセクションを必ず置く。その講義で使う製品Serviceまたは主要機能ごとに、目的、構成要素、Mechanism、設定、Security、Reliability／Failure、Observability、Cost／Performance、代替、Integration、Worked exampleをService固有の本文としてセクション内で体系的に教える。

別冊のService handbook、用語集、外部Documentation、Service名の列挙、比較表、設計判断だけで代用しない。正規講義Inventoryと各Service unitの講義・セクション所属を生成元で保持し、次のGateまたは同等以上を必ず実行する。

```bash
python scripts/validate_learning_contract.py \
  --manifest data/learning-contract.json \
  --content-root docs \
  --question-jsonl data/questions.jsonl \
  --require-assessment-inventory \
  --lecture-jsonl data/lectures.jsonl \
  --require-service-sections \
  --navigation-jsonl data/navigation.jsonl \
  --require-service-curriculum \
  --service-entry-jsonl data/service-entries.jsonl \
  --require-named-service-entries \
  --require-service-mention-links
```

全Navigation category、包括的Service unit、固有Service entry、Lecture ID／Path、全Serviceセクション、全11 Dimension Evidenceが一致しなければBlockerにする。Serviceカテゴリが存在しない、下位階層に隠れている、Domain／Questionカテゴリより後ろにある、名前とLinkだけである、Family本文しかない、包括的講義とページ内講義の片方しかない状態を合格させない。

問題は講義で学んだ知識を新しいScenarioへ適用させる。正答に必要なService知識、Artifact grammar、連携Mechanism、Failure特性を問題で初出させない。

主要な講義ページでは、次を一続きの説明として含める。

1. 一言でいうと何か
2. 何の問題を解くものか
3. 身近な例または小さな具体例
4. 用語と構成要素
5. 実際に何がどの順で起きるか
6. なぜその設計や操作が必要か
7. しない場合に何が起き、どう観測されるか
8. 代替案、比較、適用条件、トレードオフ
9. よくある誤解と試験での見分け方
10. 理解確認または関連問題への導線

初心者向けの短い囲みを追加しただけで完了にしない。本文自体が未定義語から始まる場合、説明順、見出し、例、因果関係まで書き直す。

## 5. 用語を理解できる形にする

講義または問題にService／主要機能が現れる場合は、先に [references/service-mention-linking.md](references/service-mention-linking.md) を読み、正式名称だけでなく `EKS` のような正規aliasも、文中の表記そのものから包括的Service Entryへ一Clickで移動できるようにする。問題はStemだけでなく全Option、正答解説、全誤答解説を対象にする。Code、Command、Configuration、URL、Link destinationはLink挿入で変更しない。

- 専門用語を別の未説明な専門用語だけで定義しない。まず確定した教材言語の平易な表現で意味を伝え、その後に正式名称を結び付ける。
- 用語集に安定した固定アンカーを付け、講義中の初出または重要箇所からクリックで移動できるようにする。
- 用語集の各項目に「一言でいうと」「具体例」「関連講義」を含める。
- 同じ語が製品や文脈で異なる意味を持つ場合、横並びで違いを示す。例: Spark JobとLakeflow Job、Spark TaskとワークフローTask、Spark PartitionとWindow Partition。
- 初学者向け導入では、データ、ファイル、表、行、列、キー、スキーマ、メタデータ、ストレージ、コンピュート、SQL、API、ログ、メトリクスなど、説明に使う基礎語から扱う。
- リンク先を読まないと本文が成立しない書き方は避け、用語集は補助線として使う。

## 6. ハンズオンを学習へ接続する

無料枠、Trial、Credit、Sandboxまたは無償の開発環境を使う場合、先に [references/free-environment-safety.md](references/free-environment-safety.md) を読む。

- 利用可能な無料枠や検証環境を優先し、使用不能な機能には設計演習、ログ読解、設定比較などの代替を用意する。
- 各演習に、目的、前提、開始方法、手順、成果物、成功条件、観察点、失敗時の確認、振り返りを含める。
- 初回利用者が開始できないほど手順を省かない。一方、UIそのものが学習対象でない場合は、意味のないクリック列挙を避ける。
- 「動いた」で終わらせず、ログ、実行計画、メトリクス、データ変化など、仕組みを理解したと判断できる観察対象を示す。
- 無料枠と期限付きTrial／Creditを区別し、期限、対象機能、Region、Quota、停止条件、超過時の課金、後片付けを演習前に明示する。
- Providerが入力DataをModel学習やService改善へ利用できる場合、または利用条件が不明確な場合、合成Data・架空Dataだけを使う。実顧客Data、個人情報、社内文書、秘密情報、Credentialを入力しない。
- ユーザーが時間効率を優先してハンズオンを任意にしたい場合、実行で得る観測と判断を、Code、Command、Configuration、入力表、Log、Error、出力を読む問題へ変換する。実環境固有の操作感が試験対象なら完全な代替とは扱わず、任意の補助経路として残す。

## 7. 問題集を量と質の両方で拡張する

問題の新規作成または拡張では、先に [references/exam-question-fidelity.md](references/exam-question-fidelity.md)、[references/question-bank-quality-standard.md](references/question-bank-quality-standard.md)、[references/question-bank-validation-procedure.md](references/question-bank-validation-procedure.md) を読む。

- ユーザーが完成総数を明示していない新規講座、または通常問題集の大幅増量・全面整備では、完成件数を Associate 相当は正確に500問、Professional 相当は正確に1,000問とする。これらは最低数ではなく既定の総数である。新規か既存かをWork Modeとして記録し、問題の限定修正、レビュー、公開だけの依頼を問題集全体の増量依頼へ広げず、既存件数を維持する `scope-exempt-existing` として扱う。
- ユーザーが完成総数を指定した場合はその件数を優先する。「N問追加」は完成総数N問ではなく、着手前の有効問題数にN問を加えた件数として扱う。
- レベルは資格名の単語だけで推測せず、ベンダーの公式資格体系、想定経験、試験対象を根拠に Associate 相当、Professional 相当、または対象外へ分類し、根拠と確認日を記録する。Fundamentals、Expert、Specialtyなどを信頼できる根拠なく二段階へ押し込まない。対象外で完成総数の指定もない場合は、問題作成前にユーザーへ確認する。
- 上記件数は通常問題集の一意な問題IDを数える。各問に通常問題または模擬問題のQuestion Setを持たせ、章末問題を同じ通常問題集の正規データから表示する場合は一度だけ数え、模擬試験の設問は加算しない。「通常問題を増やす」という依頼を模擬試験の追加で代用しない。
- 既存問題を変更する前に問題ID、内容Hash、件数を記録し、変更後と比較する。変更・削除した既存IDにはActionと理由を残し、削除にはユーザー承認の参照も残す。品質上の理由がない良問を件数調整だけで削除・置換しない。既存の有効問題が500問または1,000問を超える場合は、明示的な削除依頼なく維持し、超過維持として基準件数、着手前件数、完成件数を記録する。
- 大幅増量では、先に試験領域、学習目標、難易度、思考タイプ別の目標数を決める。数合わせの言い換え問題を作らない。
- 新規講座、講義または問題集の大幅更新、全面品質改修では、各問題に正答前提となるLearning unit、Service、Artifact Type、Integration Pattern、関連講義を正規Sourceで保持する。問題IDの全件を学習契約Manifestへ出力し、問題より前のLearner-visible講義へ100%閉じる。60% Artifact問題下限を、講義側でArtifactの読み方を教える割合へ流用しない。
- 新規制作、大幅増量、または問題集全体の改修では、Code、Command、Configuration、JSON／YAML等のStructured data、入力・期待出力表、Log／Metric、図／UIのいずれかを正答判断に必要とするArtifact問題を、通常問題集全体の60%以上にする。500問なら300問以上、1,000問なら600問以上とし、複数Typeを持つ一問も分母に対しては一問と数える。この60%は教材品質の共通下限であり、現行公式Evidenceと受験後Feedbackから資格・Objective別のType配分と、必要なら60%を超える最低数を決める。限定修正、レビュー、公開だけの依頼へ無断で全面改修を広げない。
- Code問題では構文の一語だけでなく、入力、期待結果、Schema／行数／値の変化、中間結果、適用条件を追わせる。Troubleshooting問題ではError直後の修正暗記ではなく、観測、原因切り分け、修正、再検証の順を扱う。
- 公式ガイドにSingle Choice、Multiple Response、Ordering、Matchingなどの形式がある場合、形式、正答集合・順序・対応関係、形式別件数を生成元へ保持し、許可形式と分布を検査する。
- 暗記だけでなく、比較、適用、原因診断、ログ読解、構成選択、コスト・性能・セキュリティの設計判断を混ぜる。
- 各問に一意に判定できる正答、正答集合、順序または対応関係を持たせる。正解理由と、該当するすべての誤答が不適切な理由を持たせ、誤答解説を同じ定型文で埋めない。候補固有の一文へ同じ汎用接頭辞・末尾を全問で足しても説明固有性を満たしたことにしない。
- 正答だけが長い、詳細、丁寧、極端語を避けているなど、内容を理解せず推測できる語彙・長さの手掛かりを全問横断で検査する。
- 仕様依存の問題には公式Sourceと確認日を保持し、関連講義へのLinkと一次情報Sourceを混同しない。
- 問題直後に折りたたみ式の解答を置くことを既定とし、別形式の希望があれば従う。
- Stem、全候補、正答解説、全誤答解説に現れるService正式名・正規aliasを、対応する包括的Service Entryの固定Anchorへ直接Linkする。正答候補だけをLinkせず、Distractor Serviceも同じ規則でLinkする。一次情報SourceへのLinkは別Field／別表示として保持する。
- 非公式な流出問題、記憶再現ダンプ、無断転載を使わない。公式目標と製品仕様から独自のシナリオを作る。

大量生成後は、問題数だけを報告せず、必ず品質レビューを行う。

1. 全問に対する構造・対応・重複・説明固有性の自動検査
2. 全問を分割した意味レビュー: 正答、曖昧さ、誤答の妥当性、解説の正確さ
3. 領域横断のカバレッジと難易度分布の検査
4. 独立した第二レビューによる境界事例、紛らわしい問題、代表問題の再確認
5. 指摘修正後の再検査

意味レビューと独立レビューは別の台帳で記録する。現在の問題ID集合との完全一致、Reviewer、`FIXED`の修正内容、問題本文のHashを検査し、同じReviewerまたは古いHashを独立レビュー完了の証拠にしない。

Artifact問題は、独立レビューでArtifact部分を隠す削除テストを行う。本文の言い換え、Optionのラベル、`expected`／`correct`列などからArtifactなしでも正答を特定できる場合、その問をArtifact件数へ数えない。公式EvidenceがCodeや設定の正しい形の選択を要求する場合、正解実装を本文へ先に表示せず、API名、引数、Field、構造、呼出順、演算子が異なる実在可能な近接候補を比較させる。`format: code`、Filename、Family名、Generator内のLabel、Stem中の「Codeを確認した」というProse、`artifact_types` の自己申告をArtifactの存在証拠にしない。宣言した各Typeには、学習者が解答前に実際に見るStemまたはOption内の構造化断片と、その行・Field・Operator・値・関係が判断をどう拘束するかを `artifact_evidence` で対応付ける。Metadataと構文検査の合格だけを意味上のArtifact依存性の証拠にしない。

実行可能なCode候補は全Optionを同一Fixtureで動かし、要求を満たす候補が一意で、各誤答の実行結果と解説が一致することを確認する。同一Objectiveの大量Variantは、識別子やLiteralを正規化したAST、Control flow、Dataflow、Predicate、Call sequenceでも比較し、見た目だけを変えたReskinを別問題として数えない。値域、Region、Endpoint、Client、権限など製品挙動の前提と、要求するReturn型・Field集合を問題文と候補へ明示的にBindingする。詳細は [references/exam-question-fidelity.md](references/exam-question-fidelity.md) に従う。

構造化データまたは生成問題は、プロジェクト形式から共通JSONLへ書き出し、同梱の `scripts/validate_question_bank.py` で全問を検査する。通常問題集の最終検査では `--require-course-count-policy` と `--require-artifact-policy` を使い、Level、Count Mode、目標数、実数、公式Evidence、全問のArtifact分類、各Typeに対応する学習者表示内の `artifact_evidence`、Artifact問題が全体の60%以上であること、種類別最低数の一致を必須にする。Artifact件数はEvidence検証に合格したTypeだけから数え、Labelだけの宣言は0件として失敗させる。`artifact_policy.minimum_questions_with_artifacts` 自体も `ceil(total × 0.60)` 未満なら失敗させ、低い目標値でGateを迂回させない。生成後はEvidenceの `content` がLearner-visible Markdown／HTMLにも残ることを照合し、宣言件数が1件以上なのに表示上の実物が0件ならBlockerとする。プロジェクト固有の検査で代用する場合も、60%下限、Labelからの推定禁止、Exact learner-visible slice、構造検査、宣言との一致、生成後照合を同じFailure policyで実装した対応表を残す。

レビュー前に「高品質」「完成」と宣言しない。BlockerとMajorは0件にし、Minorは修正するか、残す理由と学習者への影響を最終報告へ記録する。

## 8. Web教材として整える

複数の資格講座を同じサイトで扱う場合、またはヘッダー、タブ、サイドバーを変更する場合は、先に [references/multi-course-site-navigation.md](references/multi-course-site-navigation.md) を読む。

- ホームから「専門用語の前に読むページ → 用語集 → 学習ガイド → 講義」へ迷わず移動できる導線を作る。
- 各講座の上部カテゴリに確定した教材言語のServiceカテゴリを第一級項目として表示し、Serviceカテゴリから包括的Service講義へ、包括的講義から適用先のDomain／Task講義へ移動できるようにする。ServiceカテゴリはDomain／Task、通常問題、模擬問題より前へ置く。
- PCとスマートフォンで、本文、表、コード、数式、図、折りたたみ解答が読めるようにする。実画面を確認できない場合、レスポンシブCSSとHTML構造の静的検査は行うが、見た目とタップ操作を合格扱いにしない。
- 検索、目次、前後移動、用語アンカー、講義間リンクを機能させる。
- 全講義・問題のService表記Linkを生成HTMLで検査し、各 `href` が宣言EntryのPageと固定Anchorへ解決すること、Link先Anchorが一意に存在すること、裸alias・Landing止まり・誤Entry・外部DocumentationだけへのLinkが0件であることを確認する。
- 長いページを増やすだけでなく、前提単位と試験目標単位で分割し、学習順を示す。
- ソース非公開、検索抑制、認証付き非公開を混同しない。`noindex`や`robots.txt`はアクセス制御ではないと説明する。
- 公開サイトとソースリポジトリのVisibilityを分けて扱う。サイトを一般公開する依頼は、ソースリポジトリをPublicにする許可ではない。
- 複数講座サイトのCIでは、全講座の生成元、講義、問題、レビュー台帳、静的HTML検査を明示的に列挙する。一つの講座だけの成功をサイト全体の成功として扱わない。
- 新しいValidatorを追加したり警告を致命化したりした場合、ローカルの必須検査集合と公開CIの検査集合を比較し、同じFailure policyで実行する。公開Workflowに旧Commandが残り、候補Artifact、Variant実質差、警告失敗などの新しいGateを迂回できる状態を許可しない。Linux CIへWindows用Orchestratorをそのまま渡せない場合は、同等の個別Stepを明示して可搬性を検証する。

## 9. 外部サービスと公開を扱う

新しい外部サービス、自動化、従量制機能、アカウント権限を使う前に、目的、トリガー、頻度、無料枠、超過時の挙動、データ、公開範囲、代替案を説明して了承を得る。

無料環境も外部サービスである。料金が0円でも、利用期限、Fair Usage、停止、Data保持、Model学習・Service改善への利用、人手Review、Region、機密性、利用規約を確認する。「無料」を「無制限」「機密Dataを置ける」「永続的に使える」と言い換えない。

既存ワークフローを発火させるプッシュでも、ユーザーが把握していない可能性があれば先に説明する。GitHub Actions、GitHub Pages、クラウド検証環境、有料API、定期ジョブを「無料だから」という理由だけで無断利用しない。

新規リポジトリは、ユーザーがPublicを明示指定した場合を除きPrivateで作成する。既存リポジトリでは公開前後に実際のVisibilityを確認する。現在の作業で誤ってPublicにした場合はPrivateへ修正し、以前から存在するPublicリポジトリでは外部利用への影響を説明して変更の了承を得る。Privateリポジトリから選択したホスティングへ公開できない場合も、無断でPublicへ変更しない。制約、料金、公開範囲、代替経路を説明し、方針の指示を受ける。

公開が依頼範囲なら、次まで行う。

1. ローカルの厳格ビルドと品質検査
2. 意図したファイルだけの差分確認
3. ソースリポジトリが意図したVisibility（明示指定がなければPrivate）であることの確認
4. コミットと公開経路への反映
5. CIまたはデプロイ完了の確認
6. 公開URLのHTTP状態と、新しい本文・リンク・問題の反映確認
7. 公開後もソースリポジトリが意図したVisibility（明示指定がなければPrivate）であることの再確認

ブラウザを使えない場合、直接HTTP取得と生成HTML検査で、HTTP状態、本文反映、リンク先、HTML構造を確認する。レイアウト、検索操作、折りたたみ操作、タップ領域は証明できないため、未検証項目として明示する。

## 10. 完了前に検証する

新規制作、大幅更新、公開前には [references/course-quality-checklist.md](references/course-quality-checklist.md) を読み、該当項目を確認する。

- 講義だけの変更では問題ファイルやコード例が変わっていないことを、問題だけの変更では講義や模擬試験が意図せず変わっていないことを差分で確認する。
- 可能なら、対象ページ数、用語アンカー数、内部リンク数、問題数、重複数、レビュー結果を機械的に数える。
- 新規講座、講義または問題集の大幅更新、全面品質改修では、正規問題IDと学習契約ManifestのAssessment IDを完全一致させ、同梱の `scripts/validate_learning_contract.py --require-assessment-inventory` または同等以上の検査を必須Gateとして実行する。全Assessment requirementが先行Learning unitへ閉じ、各Service、Artifact、Integrationの必須Dimensionに対応するExact learner-visible evidenceがあることを100%で検査する。Manifestから問題を除外する、MetadataだけをEvidenceにする、同じ汎用文を複数Dimensionへ自己申告する迂回を許可しない。
- 同じ範囲では、正規講義InventoryとManifestのLecture ID／Pathを完全一致させ、全講義ページのServiceセクション、そこに所属するService unit、全11 DimensionのExact Evidenceが実際のセクション内にあることを `--require-service-sections` で検査する。別ページ、別冊handbook、見出し外の本文、Metadata、Service名だけの記載を合格Evidenceにしない。
- 同じ範囲では、正規Navigation InventoryとManifestのCategory ID、Kind、順序、Landing path、Page集合を完全一致させ、上部Serviceカテゴリが一つだけ存在し、Domain／Task、通常問題、模擬問題より前にあることを `--require-service-curriculum` で検査する。包括的Service curriculumの全Unitと全11 Dimension Evidence、ページ内Service unitの `curriculum_unit_id`、Assessmentの `service_curriculum_links` を100%照合する。
- 同じ範囲では、公式範囲と全Assessment候補から作る正規Service-entry InventoryをManifestの `service_entries` と完全一致させ、各正式名称の独立見出し、固定Anchor、Landing直接Link、全11 DimensionのService固有Evidence、Family unitとの所属、Assessmentの `named_services`／`service_entry_links` を `--require-named-service-entries --service-entry-jsonl ...` で100%照合する。Family総論、短い用語定義、名前差し替えTemplateを合格させない。
- 同じ範囲では、各Service Entryの正式名称を含む `aliases` を正規Inventoryと完全一致させ、全正規講義と全learner-visible Assessment PageのProseに現れる各aliasが正しいEntry pathと固定Anchorへ直接Linkされることを `--require-service-mention-links` で100%照合する。長いaliasを優先し、同一aliasの複数Entry割当、裸文字、StemだけのLink、Option／解説の未Link、Code／URLの誤検出を失敗させる。
- 厳格Build後の全生成HTMLで、上部Header、Tab、または同等のCourse navigationにServiceカテゴリが表示され、正しいLanding pageへ移動できることを検査する。Source Manifestだけの自己申告を公開表示の証拠にしない。
- 学習契約Gateには、Service説明不足、固有Service Entry欠落、名前一覧だけ、一文用語定義だけ、Family Evidence流用、Service名差し替えTemplate、Anchor／Landing Link欠落、Assessment候補Service未Binding、alias欠落・衝突、講義／Stem／Option／解説の裸alias、誤Entry／Landing／外部DocumentationへのLink、最長一致違反、Code／URLの誤Link、Artifact読解不足、Integration flow不足、Learner-visible evidence欠落、問題ID欠落、未承認の下位資格仮定を拒否するNegative fixtureを含める。機械Gate合格後も、Requirement列挙の完全性と説明の技術的妥当性を意味Reviewする。
- 問題を新規作成、大幅拡張、または全面改修した場合、検証済み `artifact_evidence` からArtifactを含む一意な問題数と種類別件数を数え、通常問題集全体の60%以上かつ公式Evidenceから定めた種類別最低数を満たすことを確認する。`format`、Family、Filename、説明文、`artifact_types` の宣言数を実測数として報告しない。
- 大規模変更では、依頼範囲に含まれ、プロジェクト構造に適合する場合、プロジェクト固有の検証スクリプトを追加または更新する。保護対象を変える必要がある場合は追加せず、既存検査と一時的な読み取り検査で代替する。
- Review用Content manifestは、そのReviewerが実際に確認した固定Surfaceだけで構成する。問題ReviewならCanonical問題、Learner-visible生成問題、対応Objective表などに限定し、無関係な講義、Lab、Validator、Dependency、ADR、Review台帳を含めない。Review外の変更を含むRelease manifestは別に保持し、Review対象自体が同一なのにStampがStale化しないことを、対象内／対象外の変更Fixtureで確認する。
- 生成物がある場合、生成前後の対象ファイル集合と正規化本文を比較し、再生成で差分が出ないことを確認する。同梱の `scripts/check_generated_reproducibility.py` または同等検査を使い、UTF-8 BOMとCRLF／LFは同値として正規化し、Locale依存Sortを排除してWindowsとLinuxで同一結果にする。
- 複数段の修復を重ねる生成器は、正規Source読み込み時に各IDと各保護Fieldの正確な最終Postimageを保持する。「Corpusの一部が最終形なら全体をSkip」は禁止し、各ID／Fieldを正確なPreimage、正確なPostimage、それ以外のDriftに分類する。Preimageのみ変換、PostimageのみSkip、部分完了や未知DriftはFail closedとし、旧状態、最終状態、両者混在、一Fieldだけ最終状態のNegative fixtureで再入可能性を検証する。
- 公開CIがLinuxで動く場合、Windowsのローカル成功だけで完了にしない。少なくとも生成再現性、問題検査、厳格BuildをCI上でも通す。
- 厳格ビルド、リンク・アンカー、重複ID、コード、図、折りたたみ、ナビゲーションを検査する。
- 講義または問題を大幅に変えた場合、独立レビューを行い、Blocker、Major、Minorで指摘を整理する。

## 11. ADRとSkill改善を完了する

完了前に [references/adr-and-skill-evolution.md](references/adr-and-skill-evolution.md) に従い、ADRへ最終判断、影響、検証結果、残課題を反映する。再利用可能な改善の有無を必ず判定し、更新した場合はSkill構造と変更したスクリプトを検証する。更新しない場合も、判定理由をADRに一文で残す。

Skill更新が適用範囲の拡大、既存方針との衝突、外部サービスの追加、または大きな互換性変更を伴う場合は、独断で進めずユーザーへ方針を確認する。Skillの保存場所が読み取り専用などで更新できない場合は、ADRに具体的な更新案を残し、未反映として報告する。

## 12. 引き渡す

結果を先に伝え、次を簡潔に報告する。

- 何をどの範囲まで変更したか
- 公式試験範囲の確認日または対象バージョン
- 講義、用語、問題、演習の件数と主な改善
- 公式Sample／Practiceの確認状態、Access制約、Artifact問題総数と種類別件数
- Entry contract、問題前提閉包のAssessment総数、未対応Service／Artifact／Integration件数、学習契約Gateの結果
- 正規Lecture総数、本文内Serviceセクション合格数、欠落数、セクション外Service Evidence数、`--require-service-sections` Gateの結果
- 上部Serviceカテゴリの表示位置、正規Navigation category数、包括的Service curriculum Unit数、未対応Assessment数、`--require-service-curriculum` Gateと生成HTML navigation Gateの結果
- 正規Service-entry数、公式／Assessment由来のInventory差分、固定Anchor／Landing直接Link数、全11 Dimension合格Entry数、未講義または未Bindingの固有Service数、`--require-named-service-entries` Gateの結果
- 正規Service alias数、講義・Stem・Option・解説別のService表記Link数、裸／曖昧／誤Link数、`--require-service-mention-links` Gateと生成HTML Link Gateの結果
- 全ページ内Service unitの `curriculum_unit_id` Binding数、全Assessmentの `service_curriculum_links` Binding数、未Binding数、および二層共通Gateを実行した完全なCommand
- 自動検査、意味レビュー、独立レビュー、ビルド、公開確認の結果
- 変更していない保護対象
- 公開URL、ソース、生成元、再検証コマンド
- ソースリポジトリのVisibility
- 自動実行、料金、サイトとリポジトリそれぞれの公開範囲、既知の制約
- ADRのパスと状態、Skill更新の有無、更新した場合の検証結果

件数やビルド成功だけを品質の証拠にしない。学習者が前提から追え、問題が理解を測り、公開物へ実際に反映されたことまで示す。
