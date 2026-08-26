# IT資格問題集の品質基準

通常問題、章末問題、模擬試験を新規作成、大幅拡張、または全面再作成するときに使う。量を増やしても、正答の一意性、解説の具体性、範囲の網羅性を落とさない。問題作成前に [exam-question-fidelity.md](exam-question-fidelity.md) を使い、現行公式問題の調査状態、問題形式、判断Pattern、Stem／Option別の実務Artifact量を資格ごとに校正する。

## 目次

- [1. 問題数を設計する](#1-問題数を設計する)
- [2. 問題文を作る](#2-問題文を作る)
- [3. 選択肢を作る](#3-選択肢を作る)
- [4. 解説を書く](#4-解説を書く)
- [5. 生成元を設計する](#5-生成元を設計する)
- [6. 全問をレビューする](#6-全問をレビューする)
- [7. 完了条件](#7-完了条件)

## 1. 問題数を設計する

ユーザーが完成総数を明示していない新規講座、または通常問題集の大幅増量・全面整備では、標準完成件数を次のとおり正確に設定する。問題の限定修正、レビュー、公開だけの依頼では、自動的にこの件数まで増量しない。

| 講座レベル | 通常問題集の標準完成件数 |
|---|---:|
| Associate 相当 | 500問 |
| Professional 相当 | 1,000問 |

- 上表は最低数ではなく既定の総数とする。ユーザーが別の件数を指定した場合は、その件数を優先する。
- 「N問追加」は完成総数N問ではなく、着手前の有効問題数にN問を加えた件数とする。完成総数の指定と追加数の指定を生成元で区別する。
- 資格名だけで判定せず、ベンダーの公式資格体系、想定経験、試験対象を根拠に Associate 相当、Professional 相当、または対象外を決め、根拠と確認日を記録する。Fundamentals、Expert、Specialtyなどを信頼できる根拠なく二段階へ押し込まない。対象外で完成総数の指定もない場合は、問題作成前にユーザーへ確認する。
- 通常問題集は新規、保守、全面再作成のどれかをWork Modeとして記録する。保守では既存問題のID、内容Hash、件数を着手前に記録し、品質上の理由がない良問を件数調整だけで削除・置換しない。全面再作成では旧ID・Hash・件数を監査用Baselineと重複検査にだけ使い、旧Stem、Option、Scenario、解説、Artifact overlayをSeed、Template、言い換え元へ使わない。先に現行公式Sourceから `question_source_profile` とAuthoring planを確定し、その後に新ID namespaceまたは全面置換Manifestを持つ新規Corpusを生成する。削除にはユーザー承認の参照を残す。既存の有効問題が標準完成件数を超えている場合は明示的な削除依頼なく維持し、超過維持として基準件数、着手前件数、完成件数を記録する。模擬試験も依頼が全面再作成なら同じ非流用契約を適用する。

作成前に、次の軸で件数表を作る。

| 試験領域・目標 | 基礎確認 | 比較・適用 | 診断 | 設計判断 | 合計 |
|---|---:|---:|---:|---:|---:|

- 公式試験目標を一つも空欄にしない。
- 公式ガイドが許可する問題形式を列挙し、Single Choice、Multiple Response、Ordering、Matchingなどの形式別件数を通常問題と模擬試験で設計する。
- 通常問題は一意な正規問題IDで数える。章末ページなど複数箇所へ同じ問題を表示しても重複計上しない。
- 模擬試験と通常問題を別々に管理し、上表の500問または1,000問へ模擬試験の設問を加算しない。
- 「10倍」などの量的目標は、同じ題意の言い換えで埋めず、目標、状況、制約、失敗モード、判断軸を変える。
- 難易度を知識再生、単一概念適用、複数概念統合に分ける。
- 現行の公式Sample／Practiceを確認し、問題本文を作る前に、公式ガイドの全Domain／Task／ObjectiveとWeight、Sourceの問題形式、主判断Pattern、主Objective、主内容Family、Service／Feature、Integration、Lifecycle、制約、Coverage gap、Authoring scope decisionを `question_source_profile` へ記録する。Sourceから、一次情報上のどの境界・制約・Failure・Trade-offがどのScenarioとDistractor差になるかを `scope_selection_patterns` へ抽象化し、そのPatternを公式ガイド全体と一次情報へ適用した `official_scope_extrapolations` を作る。Source未観察の公式Objectiveにも採用候補を持たせ、作問範囲をSourceで見つかったTopicへ限定しない。最終Coverageは公式Weight／Objectiveを優先し、Sourceの観察は内容の深さ・Scenario・判断粒度へ反映する。Sourceで頻出でも公式範囲外の内容を水増しせず、Sourceで未観察でも公式範囲内のObjectiveを空白にしない。さらにSource母数に対するStem Artifact、Option Artifact、両方、どちらでもない問題の件数・割合と、位置別のCode、Command、Configuration、Structured data、入力・出力表、Log／Metric、図／UI件数を記録する。「JSONを使用する」等の形式名だけのProseはArtifactへ数えない。通常問題集、Practice Exam A／B、各Mockなど独立Assessment surfaceごとに、EvidenceからStem／Option別の最低数と重なりを設計する。全講座共通の既定比率は置かず、公式またはユーザーが明示した場合だけ対応するTarget ratioを使う。全Surface合算での達成、またはStem ArtifactをOption Artifactの分子へ入れることを許可しない。公開されていない、Loginが必要、旧版である場合もその状態を記録する。比率は公式出題率の主張ではなく教材設計値として記録する。

## 2. 問題文を作る

- 問いたい判断を一つに定める。
- 正答に必要な情報を問題文へ入れ、不要な物語や意地悪な欠落を避ける。
- 「最適」「最小コスト」「最も安全」などは、評価軸を状況から判定できるようにする。
- 否定形を乱用せず、使う場合は見落としにくくする。
- 製品仕様に依存する正答は、公式ドキュメントと対象バージョンを確認する。
- 本文の一文をそのまま探すだけで解ける問題に偏らせない。
- Option Artifactへ数えるCodeや設定の問題では、Stemに要件と必要な前提だけを置き、全選択肢へ同じArtifact種別・粒度の実在可能な候補を提示する。各宣言Typeを全 `option:<key>` 内のExact learner-visible sliceと候補固有の `decision_binding` を持つ `artifact_evidence` へ対応付ける。StemだけのCode blockはStem Artifactとして別集計し、Optionの一部だけのArtifact、`format`、Family、Filename、説明文、`artifact_types` の自己申告をOption件数へ数えない。
- Text問題をOption Artifact問題へ変換する場合は、旧問題へ候補だけを重ねず、Stem、全候補、正答集合、正答解説、全誤答解説、Evidence、選択契約を一つの原子的単位として再作成する。Stemを、候補Artifactから判断できるContext、入力／状態、Hard constraint、期待する観測とArtifact選択要求へ書き直し、一般的な旧StemやService選択時代の問いを残さない。
- `artifact_selection.stem_contract` にArtifact選択要求とScenario各要素のExact learner-visible slice、Artifact候補を隠すDeletion testのReferenceを保持する。Hard constraint、期待する観測、Decision axis、候補別結果を正規化したContractをBank全体で一意にし、Actor名、ID、数値Literal、Option順、背景文だけを変えたStemを別問題として数えない。
- Artifactを平文へ戻しても判断が変わらない場合はText問題にする。架空のCourse Schema、`*Candidate`、`services`／`operations`／`controls`／`flow`の汎用Wrapper、正答条件をCommentや配列へ直列化しただけのCode／YAML／JSONをArtifact問題へ分類しない。
- Data変換では入力と期待出力を示し、Schema、行数、値、NULL、重複、集計粒度のどれが変わるかを追わせる。診断ではError直後の修正暗記ではなく、観測、原因切り分け、修正、再検証の順を問う。
- Stemと補足条件にService正式名または正規aliasが現れる場合、表記そのものを包括的Service Entryの固定Anchorへ直接Linkする。関連Service一覧、Services Landing、外部DocumentationだけへのLinkで代用しない。

## 3. 選択肢を作る

- Single Choiceでは正答を一つにする。Multiple Responseでは選択数または選択条件を明示し、OrderingとMatchingでは一意な順序・対応関係を持たせる。複数のResponseが条件付きで正しくなる場合、条件を追加するか問題を分ける。
- 選択肢の文法、長さ、粒度、製品レベルを揃える。
- 誤答を無関係な語で作らず、実際の誤解、似た機能、誤った優先順位、適用条件違いから作る。
- 正答だけが詳細、丁寧、長文になる手掛かりを避ける。
- 「常に」「絶対」などの極端語を、安易な消去法の手掛かりにしない。
- 選択肢順や正答位置の偏りを検査する。
- 問題単体だけでなく全体で、正答の文字数、句読点、条件節、製品名、極端語、断定の強さがCorrect／Incorrectと相関していないか検査する。
- 正答・誤答を問わず、全Option内のService正式名・正規aliasを対応Entryへ直接Linkする。正答候補だけがLinkを持つこと自体を正答手掛かりにしない。
- Option Artifactへ算入する問題は、全Optionに同じArtifact種別の候補を置き、API名、引数、Field、構造、呼出順、演算子、Identity境界、出力の決定差分を候補内Exact sliceとして記録する。候補が似て見えるだけ、正答だけが完成形、差が識別子・Comment・表示値だけ、または全候補の観測結果が同じ問題を算入しない。
- `artifact_selection` に `select_correct_artifact`、要求Behavior／Result、全Optionを覆うDecision axis、共通Fixture／Schema／Dry run／導出検査のReference、候補別結果、検証済み正答集合を持たせる。Code候補は同じ実行可能またはStub化したFixtureへ通し、検証済み正答集合を正規 `correct` と一致させる。
- JSON／YAMLはField、Commandは引数、Codeは処理、LogはEvent／Attribute、表は判断列の単位で改行し、Artifact Sourceの一行を100文字以下にする。CSS折返しだけでSource整形を代用しない。
- Diagram候補は実Service／Resource、Event／Request／Data／Failure edgeを描く。Mermaidは `mermaid` Fenceで出力し、Raw記法を通常のCode blockへ表示せず、Metadata box列をArchitecture図として算入しない。

## 4. 解説を書く

解説Authoring前に [explanation-writing-standard.md](explanation-writing-standard.md) を読む。解説Sourceがない場合は、同文書の「候補のCapability／Action → Scenarioの決定条件 → 適合／不適合の境界 → 結果」を既定の説明順にする。ユーザーが解説Sourceを提供した場合は、構成、説明順、候補別の粒度、語調、用語導入、比較、結論、Multiple Responseの扱いをAuthoring前に分析し、複数の完全な例で反復して観察できるPatternを既定スタイルより優先する。Sourceの文章をCopyせず、一件だけの癖や不完全な境界断片を全問へ固定しない。Sourceの書き方と読みやすさ・技術的正確さが衝突する場合は後者を守り、変更理由を `explanation_source_profile` へ残す。

各問の解説に次を含める。

1. 正解
2. この状況で正解になる決定的な条件
3. 正答が問題をどう解決するか
4. 各誤答が魅力的に見える理由と、この状況では不適切な理由
5. Multiple Responseでは正答集合が必要十分である理由
6. 再利用できる判断ルール。ただし候補別説明の定型的な再掲になる場合は省略する
7. 関連講義または用語へのリンク

各候補の説明は、その候補が製品上で実際に行うこと、問題文のどの制約が決定的か、その制約へ適合するか外れるか、結果として何が起きるかを一続きにする。内部のFamily名、Case ID、`decision_rule`、正誤Label、Generatorの分類語を示すだけでは学習者向け解説にならない。正答解説だけを長くし、誤答を「要件を満たさない」で終わらせず、各誤答が魅力的に見える条件と今回外れる境界を区別する。構造化Sourceを使う場合は、候補ごとに `candidate_capability`、`decisive_constraint`、`fit_or_mismatch`、`consequence` と、必要な候補だけ `valid_elsewhere`、Multiple Responseでは `required_role` を保持するか、同等の意味要素を追跡可能にする。

Multiple Responseでは、各正答候補の個別理由だけでなく、その正答集合が必要十分である理由を示す。正答の一部だけを選ぶ、誤答を一つ追加する、選択数は合うが必要な役割が欠ける、といった集合としての失敗も解説する。

正答解説と全誤答解説に現れるService正式名・正規aliasも、対応Entryの固定Anchorへ直接Linkする。一次情報SourceへのLinkは根拠として別に表示し、Service表記の内部Entry Linkを置き換えない。

「要件を満たさない」「リスクが増える」だけの定型文を誤答解説にしない。何の要件に反し、どの挙動や制約が原因かを選択肢ごとに書く。同一文の使い回し、変数だけを置換した説明、正答文の言い換えを検出する。

Artifact問題では、全Optionについて候補内の決定的なExact slice、共通検証で得た候補別結果のExact slice、その両方を含む正答または誤答解説のExact sliceを `artifact_selection.explanation_bindings` で結ぶ。正答解説は正答候補のField／Call／値／Edgeと通過結果を、誤答解説は各候補固有のMutationと失敗結果を説明する。候補だけを変更して旧Text問題の解説を残す、候補に存在しないService／Architecture判断を説明する、全候補へ同じ理由を付ける状態を許可しない。Artifactまたは候補別結果を変更したら、Binding、解説、問題Hash、意味Review、独立Reviewを同じ変更単位で更新する。

## 5. 生成元を設計する

大量問題では、Markdownへ直接複製するより、構造化された正規データと生成処理を使う。既存方式がある場合はそれを尊重する。

一問ごとに、少なくとも次を保持する。

- 一意なID
- 通常問題または模擬問題を示すQuestion Set
- 通常問題集、Practice Exam A／B、各Mock等の独立表示単位を示すAssessment Surface
- 試験領域と学習目標
- 難易度と思考タイプ
- 問題文と選択肢
- 正答
- 正解理由
- 選択肢別の誤答理由
- 関連講義・用語
- 問題形式と、正答Key・正答集合・順序・対応関係
- 仕様確認元となる公式Sourceと確認日
- 生成済み表示から読んだ正答を照合する場合のRendered Answer
- StemとOptionを分離した実務Artifactの分類。概念問題も空Listとして明示する `stem_artifact_types` とOption用の `artifact_types`
- Stem Artifactの実体と判断依存を保持するLocation別Exact evidence、およびOption Artifact問題の全Option Exact slice、候補固有Binding、要求、Decision axis、候補検証Reference、候補別結果、検証済み正答集合を保持する `artifact_evidence` と `artifact_selection`
- Option Artifactへ算入する問題のArtifact固有Prompt／Scenario／Deletion testを保持する `artifact_selection.stem_contract` と、全候補の決定差分／検証結果／正誤解説を結ぶ `artifact_selection.explanation_bindings`
- Text問題から変換した場合の旧本文はBaseline hashまたは監査用の非表示Sourceとしてだけ保持し、learner-visible Stem／解説へ連結しない
- Stem、全Option、正答・誤答解説へ出力するService表記と、正式名称・略称をEntryへ解決する正規alias情報

関連講義へのLinkと、正答の根拠となる一次情報Sourceを別Fieldで保持する。生成時に、欠落、選択肢と解説の対応ずれ、Source不足、Rendered Answerとの不一致、正答位置、重複ID、短すぎる解説、同一解説を検出する。共通の書き出し形式、既定閾値、レビュー記録は [question-bank-validation-procedure.md](question-bank-validation-procedure.md) に従う。

選択肢を並べ替えるGeneratorで本文や解説中のOption Labelも更新する場合、`A`〜`H`の単独文字を全文置換しない。`Option A`、`A and C`、順序列など、Labelであることを構文またはFieldで判定できる箇所だけを置換する。教材言語が英語なら不定冠詞の `A sample`、固有の区分名である `Project A`、通常の英文中の文字を保持し、実際のLabel参照とこれらの非Label例を回帰テストへ含める。

## 6. 全問をレビューする

大量作成でもサンプリングだけで品質保証を終えない。

### 第1段階: 全問の自動検査

- ID、正答、選択肢、解説、リンクの完全性
- Stem、全Option、正答・誤答解説のService aliasが対応Entryの固定Anchorへ直接Linkされ、裸alias、曖昧alias、Landing／外部Documentation／別Entryへの誤Linkが0件であること
- 問題形式、正答集合・順序・対応関係、Rendered Answerの一致
- 公式Source、確認日、許可された公式Hostの完全性
- 正答と解説の対応
- 完全一致と高類似の問題・選択肢・解説
- 正答位置、問題形式、領域、難易度、思考タイプの分布
- 公式Evidence、Authoring前のSource profile、問題形式・主判断Pattern・公式Weight／Objective・観察Objective・主内容Family・Service／Feature・Integration・Lifecycle・制約・Coverage decision、全問のAssessment Surface、Stem／Option別Artifact分類、両方・どちらでもない件数、位置別種類数、各Surfaceで宣言した軸別最低数、および明示した場合だけ対応する比率Floor
- 正答の長さや語彙による手掛かり
- 禁止された定型文、短すぎる説明、未置換プレースホルダー

### 第2段階: 全問の意味レビュー

全問を扱える大きさに分割し、各問について次を判定する。

- 公式仕様上の正答性
- 正答の一意性と問題文の十分性
- 誤答のもっともらしさ
- 解説が選択肢固有か
- 既存問題との題意重複
- 対象レベルに対する難易度

### 第3段階: 横断レビュー

- 公式試験範囲の空白と過密
- 同じシナリオ、固有名詞、数値、文型の反復
- 正答位置や製品機能への偏り
- 通常問題と模擬試験の重複
- Text問題のStem・正誤解説を候補Artifactだけ差し替えて流用した変換問題と、正規化Scenario contractの再利用
- 講義で説明していない知識への依存
- 領域別のArtifact密度と、説明文だけの問題へ偏っていないか
- 通常問題集だけがArtifact豊富でPractice／Mock formが0件または宣言済み目標比率未満になっていないか
- 架空Wrapper、平文の直列化、長い単一行、Raw Mermaid、Metadata boxだけの図が残っていないか

### 第4段階: 独立レビュー

別のレビュー担当に、意図した正答や先入観を渡しすぎず、境界事例、難問、類似問題、修正済み問題を再判定させる。Blocker、Major、Minorに分け、修正後に再検査する。

意味レビューと独立レビューは別台帳にし、各行へ現在の問題内容から算出したHashを記録する。問題修正後は古いHashのReviewを無効とし、再Reviewする。同じReviewerによる二つの台帳、問題IDの不足・余分・重複、`FIXED`なのに修正内容がない行を完了扱いにしない。

BlockerとMajorは必ず0件にする。Minorは原則修正し、残す場合は問題ID、理由、学習者への影響をレビュー記録と最終報告に残す。「指摘なし」と「未確認」を混同しない。

## 7. 完了条件

- [ ] 目標問題数と実数が一致する
- [ ] Question Set、資格Levelと根拠、Count Mode、標準件数またはユーザー指定を記録し、機械検査が通る
- [ ] 公式試験目標の空白がない
- [ ] 現行公式ガイドと公式Sample／Practiceの調査状態、確認日、Access制約が記録され、問題本文作成前の `question_source_profile` がある
- [ ] 解説Sourceがない場合、全問が `explanation-writing-standard.md` の候補別因果順を既定としている。解説Sourceがある場合、Authoring前の `explanation_source_profile` が構成、順序、候補単位、説明量、語調、比較、結論、Multiple Response、観察母数と例外を記録し、複数の完全例で反復したPatternを既定スタイルより優先している。逐語転載や一例だけの一律模倣はしていない
- [ ] `question_source_profile` に公式Weight／全Objective、Sourceの問題形式・主判断Pattern・主Objective・主内容Family・Service／Feature・Integration・Lifecycle・制約、Scope gap、Authoring scope decisionがあり、各Primary分布の合計がSource母数と一致する
- [ ] Sourceの出題化Patternを抽象化した `scope_selection_patterns` と、それを公式範囲全体・一次情報へ適用した `official_scope_extrapolations` がある。Source未観察の各公式Objectiveに採用済み候補があり、一次情報URL・根拠Pattern・確度・推論・採否を追跡できる
- [ ] 最終BankのDomain／Objective件数が公式Coverageを満たし、Source観察を内容の深さ・Scenario・判断粒度へ反映しつつ、Source未観察の公式Objectiveを欠落させていない
- [ ] SourceのStem Artifact、Option Artifact、両方、どちらでもない問題の件数・割合と位置別Type件数が `--require-question-source-profile` に合格し、各Assessment surfaceの同じ実測値も2×2の整合式を満たす。形式名等の言及だけをArtifactへ数えていない
- [ ] 全問に `assessment_surface` と位置別Artifact分類・Evidenceがあり、Optionへ算入する問は全OptionのExact slice、候補固有Binding、有効な `artifact_selection`、共通検証済み正答集合を持つ。Stem／Optionそれぞれが通常問題集と各Practice／Mock formでSource profile由来の軸別最低数以上となり、対応するTarget ratioを明示した場合だけ比率Floorも満たす。架空Wrapperを含めず、位置別種類最低数が公式Evidenceに基づいて一致する
- [ ] 算入する全問にArtifact固有の `stem_contract` と全Optionの `explanation_bindings` があり、候補Artifact、候補別結果、正誤解説がExact sliceで一致する。旧Text問題のStem／解説、候補変更後のStale explanation、再利用Scenario contractが0件である
- [ ] 全問の構造検査が通る
- [ ] 公式試験の問題形式と形式別件数が一致する
- [ ] 公式Source、確認日、Rendered Answerの照合が通る
- [ ] 全問の意味レビュー記録がある
- [ ] 重複・高類似の指摘を解消している
- [ ] すべての誤答に選択肢固有の理由がある
- [ ] 各候補の解説が実際の候補挙動、決定的なScenario制約、適合／不適合、結果を結び、内部Case名や共通定型文を技術説明の代わりにしていない。Multiple Responseは正答集合の必要十分性と部分集合・余分な選択の失敗も説明している
- [ ] 正答位置・長さ・語彙による手掛かりを解消している
- [ ] 意味Reviewと独立Reviewの台帳が別で、現在の問題Hashと一致する
- [ ] 独立レビュー後のBlockerとMajorが0件で、残るMinorを明示している
- [ ] ビルド後の問題、解答、折りたたみ、リンクを確認している
- [ ] Mermaid候補が実DOMで図へ描画され、390px相当のOption Artifactに横Overflowがない
- [ ] Stem、全Option、正答・誤答解説のService正式名・正規aliasが固有Service Entryへ直接Linkされ、正答だけのLink、裸alias、誤Linkがない
- [ ] 公開した場合、公開ページの件数と新しい解説を確認している
