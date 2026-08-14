# IT資格問題集の品質基準

通常問題、章末問題、模擬試験を新規作成または大幅拡張するときに使う。量を増やしても、正答の一意性、解説の具体性、範囲の網羅性を落とさない。問題作成前に [exam-question-fidelity.md](exam-question-fidelity.md) を使い、現行公式問題の調査状態と実務Artifact量を資格ごとに校正する。

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
- 通常問題集は新規か既存かをWork Modeとして記録する。既存問題のID、内容Hash、件数を着手前に記録し、品質上の理由がない良問を件数調整だけで削除・置換しない。削除にはユーザー承認の参照を残す。既存の有効問題が標準完成件数を超えている場合は明示的な削除依頼なく維持し、超過維持として基準件数、着手前件数、完成件数を記録する。模擬試験はPractice用Work Modeの対象外だが、既存なら同じBaseline Hash保護を行う。

作成前に、次の軸で件数表を作る。

| 試験領域・目標 | 基礎確認 | 比較・適用 | 診断 | 設計判断 | 合計 |
|---|---:|---:|---:|---:|---:|

- 公式試験目標を一つも空欄にしない。
- 公式ガイドが許可する問題形式を列挙し、Single Choice、Multiple Response、Ordering、Matchingなどの形式別件数を通常問題と模擬試験で設計する。
- 通常問題は一意な正規問題IDで数える。章末ページなど複数箇所へ同じ問題を表示しても重複計上しない。
- 模擬試験と通常問題を別々に管理し、上表の500問または1,000問へ模擬試験の設問を加算しない。
- 「10倍」などの量的目標は、同じ題意の言い換えで埋めず、目標、状況、制約、失敗モード、判断軸を変える。
- 難易度を知識再生、単一概念適用、複数概念統合に分ける。
- 現行の公式Sample／Practiceを確認し、全選択肢にArtifact候補があり要件を満たす正しい候補を選ばせる検証済みOption Artifact問題を、通常問題集、Practice Exam A／B、各Mockなど独立Assessment surfaceのそれぞれで60%以上にする。そのうえでCode、Command、Configuration、Structured data、入力・出力表、Log／Metric、図／UIの種類別最低数を設計する。全Surface合算での達成やStem-only Artifact問題を60%へ数えない。公開されていない、Loginが必要、旧版である場合もその状態を記録する。60%は公式出題率の主張ではなく教材品質の下限として記録する。

## 2. 問題文を作る

- 問いたい判断を一つに定める。
- 正答に必要な情報を問題文へ入れ、不要な物語や意地悪な欠落を避ける。
- 「最適」「最小コスト」「最も安全」などは、評価軸を状況から判定できるようにする。
- 否定形を乱用せず、使う場合は見落としにくくする。
- 製品仕様に依存する正答は、公式ドキュメントと対象バージョンを確認する。
- 本文の一文をそのまま探すだけで解ける問題に偏らせない。
- 60%へ数えるCodeや設定の問題では、Stemに要件と必要な前提だけを置き、全選択肢へ同じArtifact種別・粒度の実在可能な候補を提示する。各宣言Typeを全 `option:<key>` 内のExact learner-visible sliceと候補固有の `decision_binding` を持つ `artifact_evidence` へ対応付ける。StemだけのCode block、Optionの一部だけのArtifact、`format`、Family、Filename、説明文、`artifact_types` の自己申告を件数へ数えない。
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
- 60%へ算入する問題は、全Optionに同じArtifact種別の候補を置き、API名、引数、Field、構造、呼出順、演算子、Identity境界、出力の決定差分を候補内Exact sliceとして記録する。候補が似て見えるだけ、正答だけが完成形、差が識別子・Comment・表示値だけ、または全候補の観測結果が同じ問題を算入しない。
- `artifact_selection` に `select_correct_artifact`、要求Behavior／Result、全Optionを覆うDecision axis、共通Fixture／Schema／Dry run／導出検査のReference、候補別結果、検証済み正答集合を持たせる。Code候補は同じ実行可能またはStub化したFixtureへ通し、検証済み正答集合を正規 `correct` と一致させる。
- JSON／YAMLはField、Commandは引数、Codeは処理、LogはEvent／Attribute、表は判断列の単位で改行し、Artifact Sourceの一行を100文字以下にする。CSS折返しだけでSource整形を代用しない。
- Diagram候補は実Service／Resource、Event／Request／Data／Failure edgeを描く。Mermaidは `mermaid` Fenceで出力し、Raw記法を通常のCode blockへ表示せず、Metadata box列をArchitecture図として算入しない。

## 4. 解説を書く

各問の解説に次を含める。

1. 正解
2. この状況で正解になる決定的な条件
3. 正答が問題をどう解決するか
4. 各誤答が魅力的に見える理由と、この状況では不適切な理由
5. 覚えるべき判断ルールまたはメンタルモデル
6. 関連講義または用語へのリンク

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
- 正答判断に必要な実務Artifactの分類。概念問題も空Listとして明示する `artifact_types`
- 60%へ算入する問題の全Option Exact slice、候補固有Binding、要求、Decision axis、候補検証Reference、候補別結果、検証済み正答集合を保持する `artifact_evidence` と `artifact_selection`
- 60%へ算入する問題のArtifact固有Prompt／Scenario／Deletion testを保持する `artifact_selection.stem_contract` と、全候補の決定差分／検証結果／正誤解説を結ぶ `artifact_selection.explanation_bindings`
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
- 公式Evidence、全問のAssessment SurfaceとOption Artifact分類、全候補Evidence・決定差分・候補検証に合格したArtifact-native選択問題が各Surfaceで60%以上であること、種類別最低数
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
- 通常問題集だけがArtifact豊富でPractice／Mock formが0件または60%未満になっていないか
- 架空Wrapper、平文の直列化、長い単一行、Raw Mermaid、Metadata boxだけの図が残っていないか

### 第4段階: 独立レビュー

別のレビュー担当に、意図した正答や先入観を渡しすぎず、境界事例、難問、類似問題、修正済み問題を再判定させる。Blocker、Major、Minorに分け、修正後に再検査する。

意味レビューと独立レビューは別台帳にし、各行へ現在の問題内容から算出したHashを記録する。問題修正後は古いHashのReviewを無効とし、再Reviewする。同じReviewerによる二つの台帳、問題IDの不足・余分・重複、`FIXED`なのに修正内容がない行を完了扱いにしない。

BlockerとMajorは必ず0件にする。Minorは原則修正し、残す場合は問題ID、理由、学習者への影響をレビュー記録と最終報告に残す。「指摘なし」と「未確認」を混同しない。

## 7. 完了条件

- [ ] 目標問題数と実数が一致する
- [ ] Question Set、資格Levelと根拠、Count Mode、標準件数またはユーザー指定を記録し、機械検査が通る
- [ ] 公式試験目標の空白がない
- [ ] 現行公式ガイドと公式Sample／Practiceの調査状態、確認日、Access制約が記録されている
- [ ] 全問に `assessment_surface`、`artifact_types`、`artifact_evidence` があり、60%へ算入する問は全OptionのExact slice、候補固有Binding、有効な `artifact_selection`、共通検証済み正答集合を持つ。これらに合格したArtifact-native候補選択問題が通常問題集と各Practice／Mock formのそれぞれで60%以上で、Stem-only／架空Wrapperを含めず、種類別最低数が公式Evidenceに基づいて一致する
- [ ] 算入する全問にArtifact固有の `stem_contract` と全Optionの `explanation_bindings` があり、候補Artifact、候補別結果、正誤解説がExact sliceで一致する。旧Text問題のStem／解説、候補変更後のStale explanation、再利用Scenario contractが0件である
- [ ] 全問の構造検査が通る
- [ ] 公式試験の問題形式と形式別件数が一致する
- [ ] 公式Source、確認日、Rendered Answerの照合が通る
- [ ] 全問の意味レビュー記録がある
- [ ] 重複・高類似の指摘を解消している
- [ ] すべての誤答に選択肢固有の理由がある
- [ ] 正答位置・長さ・語彙による手掛かりを解消している
- [ ] 意味Reviewと独立Reviewの台帳が別で、現在の問題Hashと一致する
- [ ] 独立レビュー後のBlockerとMajorが0件で、残るMinorを明示している
- [ ] ビルド後の問題、解答、折りたたみ、リンクを確認している
- [ ] Mermaid候補が実DOMで図へ描画され、390px相当のOption Artifactに横Overflowがない
- [ ] Stem、全Option、正答・誤答解説のService正式名・正規aliasが固有Service Entryへ直接Linkされ、正答だけのLink、裸alias、誤Linkがない
- [ ] 公開した場合、公開ページの件数と新しい解説を確認している
