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

通常問題の総数は [講座設定](course-settings.md#個人用の講座サイト設定) から決め、採用値と適用理由を制作計画へ記録する。個人用の標準件数は最低数ではなく既定総数であり、ユーザー指定・既存設定を優先する。限定修正、レビュー、公開だけの依頼では増量しない。

- 「N問追加」は完成総数N問ではなく、着手前の有効問題数にN問を加えた件数とする。完成総数の指定と追加数の指定を生成元で区別する。
- 資格名だけで判定せず、ベンダーの公式資格体系、想定経験、試験対象を根拠に Associate 相当、Professional 相当、または対象外を決め、根拠と確認日を記録する。Fundamentals、Expert、Specialtyなどを信頼できる根拠なく二段階へ押し込まない。対象外で完成総数の指定もない場合は、問題作成前にユーザーへ確認する。
- 通常問題集は新規、保守、全面再作成のどれかをWork Modeとして記録する。保守では既存問題のID、内容Hash、件数を着手前に記録し、品質上の理由がない良問を件数調整だけで削除・置換しない。全面再作成では旧ID・Hash・件数を監査用Baselineと重複検査にだけ使い、旧Stem、Option、Scenario、解説、Artifact overlayをSeed、Template、言い換え元へ使わない。先に現行公式Sourceから `question_source_profile` とAuthoring planを確定し、その後に新ID namespaceまたは全面置換Manifestを持つ新規Corpusを生成する。削除にはユーザー承認の参照を残す。既存の有効問題が標準完成件数を超えている場合は明示的な削除依頼なく維持し、超過維持として基準件数、着手前件数、完成件数を記録する。模擬試験も依頼が全面再作成なら同じ非流用契約を適用する。

作成前に [分析基準](source-analysis-method.md#2-一つの問題タイプへ混ぜず軸を分ける) の分類定義を配分計画へ引き継ぐ。正答決定の根拠、回答対象、解答形式、難易度を別軸で数える。例えば「構成を設計する」は回答対象、「成立案を費用で比較する」は正答決定の根拠であり、同じ排他分類表の別列にしない。

| 分析軸 | 分類 | Source観察数／母数 | 通常問題の目標数 | 各模試の目標数 | 採用・調整理由 |
|---|---|---:|---:|---|---|

一意の主分類は未分類を含めて総数と一致させ、複数タグの重複を合計へ混入しない。公式領域×正答決定の根拠など、偏りを見るための交差表を必要に応じて作る。数値は自己申告だけで終えず、完成本文から実件数を確認する。

- 公式試験目標を一つも空欄にしない。
- 公式ガイドが許可する問題形式を列挙し、Single Choice、Multiple Response、Ordering、Matchingなどの形式別件数を通常問題と模擬試験で設計する。
- 通常問題は一意な正規問題IDで数える。章末ページなど複数箇所へ同じ問題を表示しても重複計上しない。
- 模擬試験と通常問題を別々に管理し、通常問題の設定総数へ模擬試験の設問を加算しない。
- 「10倍」などの量的目標は、同じ題意の言い換えで埋めず、目標、状況、制約、失敗モード、判断軸を変える。
- 知識再生・単一概念適用・複数概念統合は必要な思考の特徴として扱う。難易度は前提知識、推論段階、候補の近さ等から別に見積もり、受験者の正答率を測った値とは区別する。既存の `cognitive_type` を主な正答決定の根拠へ無条件にコピーしない。
- Source分析、公式範囲への外挿、Artifactの位置別分類とSurface別目標は [exam-question-fidelity.md](exam-question-fidelity.md) に従う。観察頻度を公式配分とせず、Authoring前に計画する。

## 2. 問題文を作る

[source-calibrated-question-writing.md](source-calibrated-question-writing.md) を文体・情報順・形式・比較の正規基準にする。今回の該当Sourceを優先し、代表例の校正後に全体へ展開する。Artifactの妥当性は [exam-question-fidelity.md](exam-question-fidelity.md) に従う。

判断に必要な条件を問題内に置き、不要な物語・意地悪な欠落・本文検索だけの問題へ偏らせない。データ変換では入力と出力のどこが変わるか、診断では観測から原因・修正へどう進むかを判断させる。製品仕様は対象Versionの一次情報で裏付ける。

## 3. 選択肢を作る

[選択肢と最適化の基準](source-calibrated-question-writing.md) に従い、回答単位をそろえ、近い機能・操作・方式を比較させる。実現可能性と指定評価軸での最良性を分ける。形式ごとの正答表現は [共通JSONL](question-bank-validation-procedure.md#1-共通jsonlへ書き出す) に従う。

正答位置・長さ・語彙の偏りを問題単体とBank全体で調べる。比率をそろえるためのPaddingや、製品構文の同義語置換を行わない。全候補と解説のService表記は [Service Link基準](service-mention-linking.md) を同じように適用する。

## 4. 解説を書く

[explanation-writing-standard.md](explanation-writing-standard.md) を正規基準にする。各候補の採否を自然な文章で説明し、今回の解説Sourceの特徴を優先する。固定の文数・順序をここで重ねて定義しない。

候補の実物と結果を示すBindingは [検証手順](question-bank-validation-procedure.md#1-共通jsonlへ書き出す) に従う。同じ失敗結果を共有する候補も、原因が異なればそれぞれ説明する。実現可能だが評価軸で劣る候補を、実行不能と説明しない。

## 5. 生成元を設計する

正規Sourceが各問の完成した問題文・候補・正答・全解説を保持し、Rendererは番号・選択UI・Link・解答表示を担当する。少数の背景・制約・理由の直積で本文を量産しない。

共通Fieldと出力Schemaは [検証手順](question-bank-validation-procedure.md) を参照し、既存形式は読み取りAdapterで接続できる。必要知識の正規Exportは [学習契約](lecture-completeness-and-prerequisite-closure.md#5-問題前提閉包manifest) に従う。関連講義と技術根拠のURLは役割を分ける。

問題の変換・修正ではStem、候補、正答、全解説、Evidenceを一緒に更新する。旧本文は監査Baselineへ残せるが、新本文へ連結しない。確定前のLinkを仮の正式Review Hashへ押し込まず、再制作の段階に応じて確定する。

Optionの並べ替えで `A`〜`H` の単独文字を全文置換しない。`Option A` や順序列など、参照と分かるField・構文だけを更新する。不定冠詞の `A sample`、`Project A`、製品APIの通常文字を保つ正常例と、正答・解説の対応ずれを検出する失敗例を確認する。

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

初回は全対象の意味レビュー・独立レビューを完成版に対して行う。確認済み教材を変更した後の範囲と過去記録の利用は [再レビュー基準](review-update-policy.md)、台帳・現行Hash・実担当者の照合は [検証手順](question-bank-validation-procedure.md#3-二段階reviewをhash付きで記録する) に従う。古いHashのPASSを自動転記せず、名前の違いだけで独立性を認定しない。

BlockerとMajorは必ず0件にする。Minorは原則修正し、残す場合は問題ID、理由、学習者への影響をレビュー記録と最終報告に残す。「指摘なし」と「未確認」を混同しない。

## 7. 完了条件

- 設計した件数・範囲・形式と最終Bankが一致する。
- Sourceに沿う読みやすさ、候補の判断差、解説の具体性を完成出力で確認した。
- 全問の構造・意味・横断Reviewと必要な独立Reviewが完了し、完成Hashと実記録が対応する。
- 必要知識の抽出と先行講義との対応を確認し、正規Sourceから生成表示まで一致する。

詳細な確認項目は [course-quality-checklist.md](course-quality-checklist.md) の該当部分を使う。Schema、Source profile、Artifact Bindingの長い定義を完了条件へ複製しない。
