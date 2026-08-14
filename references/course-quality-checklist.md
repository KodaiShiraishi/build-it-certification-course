# IT資格講座の最終品質チェックリスト

新規制作、大幅更新、問題増量、公開前に使う。対象外の項目は除外してよいが、ユーザーの依頼範囲を勝手に狭めない。

## 目次

- [1. 要件と範囲](#1-要件と範囲)
- [2. 公式情報と試験対応](#2-公式情報と試験対応)
- [3. 講義の理解しやすさ](#3-講義の理解しやすさ)
  - [3.1 包括性と問題前提閉包](#31-包括性と問題前提閉包)
- [4. 用語集と導線](#4-用語集と導線)
- [5. ハンズオン](#5-ハンズオン)
- [6. 通常問題と模擬試験](#6-通常問題と模擬試験)
- [7. 問題品質レビュー](#7-問題品質レビュー)
- [8. ソースと回帰防止](#8-ソースと回帰防止)
- [9. Web表示](#9-Web表示)
- [10. 外部サービスと公開](#10-外部サービスと公開)
- [11. 最終報告](#11-最終報告)

## 1. 要件と範囲

- [ ] 相談、レビュー、制作、公開のどの依頼かを取り違えていない
- [ ] 新規講座では教材言語を明示的に確定し、指定がなければ制作前にユーザーへ質問して回答を待っている
- [ ] 確定した教材言語をサイト名、ナビゲーション、講義、用語集、演習、問題、解答・解説、生成元へ一貫して適用し、正式名称、試験コード、API名、コード、識別子、URLは必要に応じて原表記を保っている
- [ ] 対象資格、対象読者、既知の基礎、苦手領域、期限、利用環境が反映されている
- [ ] ユーザーが止めた領域を変更していない
- [ ] 通常問題と模擬試験など、指定された対象を別の成果物で代用していない
- [ ] 既存の未コミット変更と保護対象を維持している
- [ ] ユーザーがリポジトリ自体の公開を明示していない場合、資格講座のソースリポジトリをPrivateで作成・維持する要件になっている

## 2. 公式情報と試験対応

- [ ] 最新の公式試験ガイド、試験コード、対象バージョン、確認日を記録している
- [ ] 現行公式Sample／Practiceを調査し、問題形式、Artifact、判断粒度、確認日、現行／旧版状態を記録している
- [ ] 公式問題がLogin必須でCodexから確認できない場合、アクセス制約をユーザーへ伝え、実問題の転載ではなく抽象化した観察結果を依頼している
- [ ] 資格を Associate 相当／Professional 相当／対象外のいずれかへ、ベンダーの公式資格体系、想定経験、試験対象から判断し、根拠と確認日を記録している
- [ ] 講義、演習、通常問題、模擬問題を試験目標へ対応付けている
- [ ] 変更されやすい製品仕様を公式一次情報で確認している
- [ ] 試験ガイドと製品仕様書を区別し、仕様依存の主張・問題へ公式Sourceと確認日を追跡できる形で残している
- [ ] 公式ページ同士で名称、提供日、Preview／GA、利用条件が食い違う場合、不一致を記録し、断定や日付暗記へ誘導していない
- [ ] 非公式な試験ダンプや無断転載を含まない
- [ ] 公式範囲外の補足を、試験範囲と誤認させていない

## 3. 講義の理解しやすさ

- [ ] 初学者向けの基礎導線と、経験者が飛ばせる主導線がある
- [ ] 章が前提関係と処理順に沿っている
- [ ] 各主要ページに一文要約、具体例、必要な理由、誤解時の症状がある
- [ ] 本文が未定義の専門用語から始まっていない
- [ ] 専門用語を別の未説明用語だけで定義していない
- [ ] 目的、内部動作、因果関係、トレードオフ、障害時の観察を説明している
- [ ] 初心者向け囲みだけでなく、本文と説明順も改善している
- [ ] 箇条書きの断片や機能一覧だけで講義を済ませていない
- [ ] 生成講義では正規Sourceが、概念固有の定義、前提、仕組み、Scenario、処理順、障害Evidence、比較条件を保持し、名前・推奨Control・誤答候補だけの薄いSchemaを共通Templateで水増ししていない
- [ ] 各主要概念に固有のMechanism、Evidence、Decision boundaryがあり、見出し・最低語数・共通説明だけを深さとして合格させていない
- [ ] 正規化した完全一致の文・段落と共通語数を講義群で集計し、見出し・Navigation・共通Safety注意を教育本文と分離した分子・分母・プロジェクト固有上限を記録している。共通接頭辞・末尾・Paddingを固有説明へ数えていない
- [ ] 講義Scenario、用語集の具体例、障害診断が名称・Task IDだけを差し替えた同一文でなく、Generic本文だけのNegative fixtureが講義深さGateで失敗する
- [ ] 特定領域だけが不自然に厚く、他領域が簡潔すぎる状態になっていない
- [ ] 講義で完成例として示すCodeとConfigurationをParser、Compiler、Linter、または製品固有の検証Commandで検査し、全候補が少なくとも構文上有効である
- [ ] 講義でMethod chainや設定の一部だけを示す場合、FragmentであることとReceiver、代入先、前後の実行Contextを明示し、完成例と誤認させていない
- [ ] 講義内QuizとLabのDecision questionも主問題集と同じ近接誤答基準でReviewし、全誤答へ候補固有の失敗理由があり、無関係な機能名・冗談の値・明白な破壊操作で水増ししていない
- [ ] 講義・Labの全Question/Answer blockを形式別に列挙し、Open responseをMC/MRの候補品質件数へ混ぜていない。Open responseには期待判断・必須Evidence・採点または自己確認基準がある
- [ ] Open responseのEvidence/RubricがYes/No・正答文・Expected judgmentの再掲ではなく、問題固有のField・実行結果・失敗条件・設計境界を要求し、Evidence同士も実質的に異なる
- [ ] 講義・LabのInline questionを独立した母集団として正答位置・語彙・長さを集計し、A/Bだけに偏る、C/Dが0件、または旧候補の説明がLabelだけ変わって残る状態を検出している

### 3.1 包括性と問題前提閉包

- [ ] Entry contractに、入口で仮定する知識、根拠、講座内で教える知識を記録し、資格Levelの名称や公式の推奨経験だけを理由に下位資格取得・製品経験・Service知識を仮定していない
- [ ] 講座上部Navigationに確定した教材言語の独立したServiceカテゴリが一つあり、親カテゴリの下へ隠れず、Domain／Task講義、通常問題、模擬問題より前にある
- [ ] ServiceカテゴリにLanding pageと正規Service curriculum Inventoryがあり、問題に登場する全Serviceを目的、構成要素、Mechanism、設定、Security、Reliability／Failure、Observability、Cost／Performance、代替、Integration、Worked exampleで体系的に教えている
- [ ] 公式範囲と正規AssessmentのStem・全候補に現れる固有Service／主要機能を正規Service-entry Inventoryへ出力し、正答候補だけを抽出してDistractor Serviceを未講義にしていない
- [ ] 各固有Service Entryが正式名称の独立見出し、固定Anchor、Landingからの直接Linkを持ち、「何か」の平易な定義から、仕組み、設定・Security、障害・観測、Cost／Performance、代替、Integration、Worked exampleまで用語集より厚く教えている
- [ ] Family総論と子ServiceのEvidenceを分離し、名前一覧、Family共通本文、一文定義、正式名称だけを差し替えたTemplateを個別Service講義として合格させていない
- [ ] 正規Navigation InventoryのCategory ID、Kind、Label、Sequence、Landing path、Page path、ParentがManifestと完全一致している
- [ ] 下位資格取得を前提にする場合、ユーザーの明示的承認と参照を記録している
- [ ] 正規問題Sourceの全Question IDを学習契約Manifestへ出力し、ManifestのAssessment ID集合・件数と完全一致している
- [ ] 各問題が要求するFoundation、Service、Artifact Type、Integration Pattern、関連講義を列挙し、問題より前のLearning unitへ100%閉じている。問題で正答に必要な基礎知識を初出させていない
- [ ] 問題に登場する各Serviceについて、目的、構成要素、Mechanism、設定、Security、Reliability／Failure、Observability、Cost／Performance、代替、Integration、Worked exampleをService固有のLearner-visible本文で教えている
- [ ] 正規講義Inventoryを使用する場合、全Lecture ID／PathがManifestと一致している
- [ ] Domain／Task講義では、現在のScenarioに必要なServiceの責務、Mechanism、設定、Failure、観測、Integrationを該当本文で説明し、名前やLinkだけにしていない
- [ ] 通常講義末尾の `AWS services in this lecture`、`Services used in this lecture` 等の一覧・11 Dimension定型再掲を標準配置せず、既存の重複記述を内容を失わない範囲で削除している。見出し名を一律禁止するGateは作らず、Generatorの再生成が確認できた場合だけ回帰検査を追加している
- [ ] 各Assessmentが必要な包括的Service unitを `service_curriculum_links` で参照している
- [ ] Manifestの `service_entries` が独立Service-entry Inventoryと完全一致し、全Entryの11 Dimension Evidence、Family所属、固定Anchor、Landing index evidence、導入順を検査している。各Assessmentの `named_services` と `service_entry_links` が一致する
- [ ] 各Service Entryに正式名称を含む一意な `aliases` があり、正規InventoryとManifestが一致する。同一aliasが複数Entryへ解決せず、重なるaliasは最長一致で処理される
- [ ] 全正規講義と全learner-visible Assessment PageのStem、全Option、正答・誤答解説に現れるService正式名・正規aliasが、表記そのものから対応Entryの宣言Pathと固定Anchorへ直接Linkされ、裸alias、Landing／Family先頭／外部Documentation／別Entryへの誤Linkが0件である
- [ ] 問題に登場する各Artifact Typeについて、構造、Field／行／矢印／Operatorの意味、正常例、失敗例、判断Evidenceを同じGrammarのLearner-visible実物で先に教えている
- [ ] 複数Serviceを組み合わせる問題について、各Serviceの責務、Request／Event、Identity／Policy、Data／State、Failure／Recovery、ObservabilityのFlowをIntegration講義で追える
- [ ] 各必須DimensionのEvidenceが問題前に読めるMarkdownまたは生成HTMLのExact sliceであり、Filename、見出し、Metadata、Tag、汎用文の自己申告だけで合格させていない
- [ ] `scripts/validate_learning_contract.py --require-assessment-inventory --require-service-curriculum --navigation-jsonl <navigation-inventory> --require-named-service-entries --service-entry-jsonl <service-entry-inventory> --require-service-mention-links` または同等以上のGateが成功し、Assessment／Navigation／Service-entry inventory、alias、上部Serviceカテゴリ順、包括的Curriculum、固有Service Entry、Service表記Link、Artifact／Integration coverage、Exact learner-visible evidenceをBlockerとして検査している。`--require-service-sections` は明示的なプロジェクト要件がある場合だけ追加している
- [ ] Service説明不足、固有Entry欠落、名前一覧、一文定義、Family Evidence流用、名前差し替えTemplate、Anchor／Landing Link欠落、Assessment候補Service未Binding、alias欠落・衝突、講義／Stem／Option／解説の裸alias、誤Entry／Landing／外部DocumentationへのLink、最長一致違反、Code／URLの誤検出、上部Serviceカテゴリ欠落・下位化・後置、包括的CurriculumのDimension欠落・カテゴリ外配置・Assessment未Binding、Artifact読解不足、Integration flow不足、Evidence非表示、Question ID除外、未承認の下位資格仮定のNegative fixtureが失敗する
- [ ] 機械Gateとは別に、Requirement列挙の完全性、説明の技術的妥当性、前提の飛躍、Service名だけの説明、飾りのArtifactがないことを意味Reviewしている

## 4. 用語集と導線

- [ ] 確定した教材言語の平易な表現から説明する用語集がある
- [ ] 固定アンカーが一意で、講義からクリックして移動できる
- [ ] 同名異義語と似た概念を明確に区別している
- [ ] 初学者向け導入で、説明に必要な基礎IT用語を扱っている
- [ ] 生成HTMLで用語リンク切れと重複IDが0件
- [ ] 生成HTMLで全講義・問題のService alias Linkが正しいEntry Anchorへ解決し、裸alias、誤Link、Anchor欠落が0件
- [ ] ホーム、導入、用語集、学習ガイド、講義の順に移動できる

## 5. ハンズオン

- [ ] 目的、前提、開始方法、成果物、成功条件、観察点がある
- [ ] 初回利用者が始められるだけの手順がある
- [ ] 不要なクリック列挙へ偏っていない
- [ ] 失敗時の確認方法と利用不能時の代替がある
- [ ] 無料Edition、使用量Free Tier、期限付きTrial、Credit、有料環境を区別し、公式確認日を記録している
- [ ] 期限、Quotaと更新周期、Region、機能制限、支払方法、超過・失効後の停止または課金を説明している
- [ ] Budget／Alertを課金上限と誤説明せず、最小構成、自動停止、後片付け、残存Resourceを示している
- [ ] Data保持・削除・Model学習・Service改善・人手Review・Region条件を確認し、非機密の合成または架空Dataを使っている
- [ ] Credentialを教材・Git・Logへ残さず、最小権限・短期Credentialと終了時の失効を扱っている
- [ ] 利用不能または利用拒否時に、同じ学習目標を測れる無料の代替演習と未検証範囲がある
- [ ] ハンズオンを任意にした場合、Code、設定、入力、Log、Error、出力の全選択肢候補から正しいArtifactを選ぶ問題で観測と判断を補い、完全には代替できない実環境固有の操作を明示している

## 6. 通常問題と模擬試験

- [ ] 指定された問題種別と目標数を満たしている
- [ ] ユーザーが完成総数を指定していない新規講座または大幅増量・全面整備では、通常問題集が Associate 相当は正確に500問、Professional 相当は正確に1,000問になっている
- [ ] 限定修正、レビュー、公開だけの依頼を問題集全体の増量へ広げていない
- [ ] 限定修正、レビュー、公開だけの既存問題集では `scope-exempt-existing` で着手前件数を維持している
- [ ] 通常問題集は新規／既存のWork Modeを記録し、既存では正の `baseline_total` と `--require-baseline-protection` を使っている。模擬試験はWork Mode対象外だが、既存ならBaseline保護を使っている
- [ ] 完成総数の指定と「N問追加」を区別し、追加時は着手前件数と追加数から完成総数を算出している
- [ ] 模擬試験を通常問題集と別に数え、500問または1,000問の達成へ加算していない
- [ ] 通常問題を一意な正規問題IDで数え、章末など複数箇所の同一問題を重複計上していない
- [ ] 一つのBase問題からVariantを生成する場合、接頭辞・接尾辞、ID、Option順、正答位置、Cognitive labelだけで別問題化せず、Scenario条件、Artifact値、Failure、Required action、Candidate behaviorの少なくとも一つが判断を変える形で実質的に異なる
- [ ] 既存問題のID、内容Hash、件数を着手前に記録し、変更後と比較している。変更・削除した既存IDにはActionと理由があり、削除にはユーザー承認の参照があり、未記録の削除がない
- [ ] 既存の有効問題が既定数を超える場合、明示的な依頼なく削除せず、超過維持として基準件数、着手前件数、完成件数を記録している
- [ ] 各問のQuestion Setと目標ファイルが一致し、通常問題と模擬問題が混在していない
- [ ] `--require-course-count-policy` でQuestion Set、Levelと根拠、Count Mode、標準件数またはユーザー指定と実数の一致を検査している
- [ ] 公式ガイドの問題形式と、Single Choice／Multiple Response／Ordering／Matchingなどの形式別件数・Response表現が一致している
- [ ] 試験領域、難易度、思考タイプの分布を設計している
- [ ] 全問に `assessment_surface` があり、通常問題集、Practice Exam A／B、各Mockなど学習者が独立して受ける全SurfaceをTargetsへ列挙している
- [ ] 全OptionにArtifact候補があり、要件を満たす正しい候補を選ばせる検証済み問題を各Assessment surfaceの60%以上にし、現行公式EvidenceからSurface／種類別最低数を設計している。全Surface合算やStem-only Artifact問題を60%へ数えていない
- [ ] 算入問題の全宣言Typeについて全 `option:<key>` のExact `artifact_evidence`、候補固有Binding、有効な `artifact_selection`、共通Fixture／Schema／Dry run／導出検査の候補別結果と検証済み正答集合を `--require-artifact-policy` で検査している
- [ ] Text問題からArtifact問題へ変換した問は、候補だけを旧問題へ被せず、Stem、全候補、正答集合、正答解説、全誤答解説、Evidence、選択契約を原子的に再作成している。旧本文はBaseline／監査用の非表示Sourceにだけ残し、learner-visible Stem／解説へ連結していない
- [ ] 全算入問題の `artifact_selection.stem_contract` がArtifact選択要求、Context、入力／状態、Hard constraint、期待する観測のExact learner-visible sliceとDeletion test Referenceを保持する。一般的な旧Stem、末尾だけをArtifact選択へ変えたStem、同じ正規化Scenario contractの再利用が0件である
- [ ] 全算入問題の `artifact_selection.explanation_bindings` が全Optionを覆い、各候補の決定差分、共通検証の候補別結果、それらを含む正答または誤答解説をExact sliceで結んでいる。候補変更後の旧解説、候補に存在しないService／Architecture判断、全候補共通の汎用理由が0件である
- [ ] Artifact候補、候補別結果、Stem、正答または誤答解説のいずれかを変更した問は、問題Hash、意味Review、独立Reviewを同じ変更単位で更新している
- [ ] Artifact件数を `format`、Family、Filename、説明文、自己申告Label、Stem Artifact、Code fenceの見た目から数えず、全候補Coverageと選択契約に合格したEvidenceだけを集計し、生成Markdown／HTMLにも全OptionのExact Evidenceが残ることを照合している
- [ ] 構築、開発、Data変換、診断、運用を測る資格では、Code、Command、Configuration、Structured data、入力・出力表、Log／Metric等が正答判断に必要な問題を十分に含めている
- [ ] 全ObjectiveとGenerator familyを横断してOption Artifact削除テストを行い、候補Artifactを隠してもStem、Option label、周辺Proseの手掛かりだけで解ける問をArtifact件数から除外または修正している
- [ ] 削除テスト合格だけで完了せず、ArtifactとOptionが公式Objectiveに対応する製品固有のAPI、設定、Data変化、実行結果、診断、設計境界を測り、汎用的な値Copyや文字列一致を製品Artifact件数へ数えていない
- [ ] Artifactを平文へ戻しても判断が変わらない問をText問題へ戻し、架空の `apiVersion: course.*`、`*Candidate`、`services`／`operations`／`controls`／`flow` Wrapper、正答条件をComment／String Listへ直列化したCode／YAML／JSONを算入していない
- [ ] 60%へ算入する全問で全Optionが同じArtifact種別・粒度の実在可能な候補を持ち、API、引数、Field、構造、呼出順、演算子、Identity境界、出力の差が要求Contractに結び付いている。似た見た目だけ、識別子／Comment／表示値だけの差、全候補が同じ結果、正答だけが完成形の問題を算入していない
- [ ] Code／設定の形を問う問題では、正解実装を本文へ先に表示せず、全Option自体のAPI、引数、Field、構造、呼出順、演算子が異なる実在可能な近接候補を比較させ、検証済み正答集合が正規 `correct` と一致している
- [ ] 完成Codeとして提示する全OptionをParser、Compiler、Linter、または製品固有の検証Commandで検査し、FragmentならReceiver、代入先、前後の実行Contextを明示している
- [ ] 完成Configuration／Workflow候補の変数、Task key、Job parameter、依存Edge、出力参照が候補内または明示したContextで閉じ、製品Schema／Dry runが利用できる場合は全候補へ適用している
- [ ] 実行可能な全Code候補を同じ最小Fixtureで実行し、Keyed candidateだけが要求Contractを満たし、各誤答の観測結果が互いに異なり、その結果と候補別解説が一致している。空DataFrame、欠落key、未定義名、暗黙Global、同じ出力になる別候補をNegative fixtureで拒否している
- [ ] 同一ObjectiveのVariantを、識別子・Literal・Option順・定型文を除いた正規化AST、Control flow、Dataflow、Predicate、外部Call sequence、期待出力Schemaでも比較し、業種名やField名だけを変えたReskinを別問題として数えていない
- [ ] Rate、Cost、Latency、Count、Probabilityの型・単位・値域が現実的で、負の料金や範囲外の率を目印にしておらず、境界値では丸めと包含関係がStem、実装、解説で一致している
- [ ] 製品API、Model、Endpoint、Region、Deployment mode、Client、権限の前提をStemとSource claimへ明示し、Course独自Schema／Adapterを製品APIと区別している。要求出力が複数Fieldなら全候補のReturn型とField集合を厳密にBindingしている
- [ ] Command列がfail-fastを要件にする場合、native commandの非0終了が後続処理を確実に停止し、PowerShell等で終了Codeを無視してDeployへ進む形になっていない
- [ ] JSON／YAMLはField、Commandは引数、Codeは処理、LogはEvent／Attribute、表は判断列で意味的に改行し、算入ArtifactのSource行が100文字以下である。CSSの強制折返しだけで長い一行を隠していない
- [ ] Mermaid候補を `mermaid` Fenceで生成し、実Service／ResourceとEvent／Request／Data／Failure edgeを描いている。Raw MermaidのCode表示やMetadata box列をDiagram問題として算入していない
- [ ] Code問題で入力から中間結果・期待出力を追え、診断問題で観測から原因・修正・再検証の順を追える
- [ ] 暗記、比較、適用、診断、ログ読解、設計判断を組み合わせている
- [ ] 正答が一意で、問題文に判断条件が足りている
- [ ] 誤答が実際の誤解から作られ、消去法の手掛かりが少ない
- [ ] 正答位置、選択肢長、語彙、極端語、詳しさがCorrect／Incorrectと相関していない
- [ ] Code fenceを除いたOption proseで、十分な出現数を持つ語句のCorrect／Incorrect率とwrong-only問をBank・形式・領域別に検査し、率合わせの機械挿入ではなく該当候補を意味修正している
- [ ] 問題文なしのOption proseだけで正答役割を当てる交差検証Classifierまたは同等の複合手掛かり検査を行い、Baselineを実質的に超える場合は誤答だけに集中する破壊操作・未検証の即時本番反映・証跡削除・極端値を人手で洗い出し、同じ目的の現実的な近接誤認に書き換えている
- [ ] Classifierを合格するFeatureへ狭めず、Word n-gramとCharacter n-gramまたは同等に独立した表現を別々に評価し、平均値だけでなく各表現のBaseline差を記録している。いずれかが実質的に高い場合、そのFeatureが拾った候補を人手Reviewしている
- [ ] 語彙・文体の手掛かり修正がSQL Command、API名、Configuration key、JSON Field、Enum値を同義語置換しておらず、Code fence外のCommand-like proseも含めて一次情報の現行構文または利用可能なParserで再検証している
- [ ] 改行・Tab・HTML breakのEscape復元をraw全置換で行わず、inline/fenced code、Identifier、Path内のbacktick／backslashを保護している。実Escapeを変換するfixtureと、Escapeに似たIdentifierをbyte-identicalに保つfixtureが最終表示で通る
- [ ] ValidatorのParser・Token extractor・Normalizerを単体fixtureで直接呼び、非空の期待型を返すことと、決定Tokenを1つ削除した候補・解説がBinding gateで失敗することを確認し、到達不能return・常時None・空Setで検査が無効化されていない
- [ ] 選択肢長は、1文字差の順位を25%ずつへ機械的に揃えるのではなく、正答が誤答の中央値・最大値より実質的に長い／短い問を個別検査し、全体と問題形式別でも利用可能な長さ差の比率に上限を設けている。順位均等化のための定型句、不要条件、意味を変えないPaddingを追加していない
- [ ] 正答長・語彙偏り・重複率などの集計Gateは、上限を含むか未満かを明記し、丸め前の分子・分母で判定している。閾値の直前・境界値・直後のfixtureがあり、契約上不合格の境界分布を比較演算子の抜けで通さない
- [ ] Option順を変更するGeneratorではLabel参照だけを文脈限定で置換し、不定冠詞や`Project A`などを壊さない回帰テストがある
- [ ] 正解理由と、すべての誤答が不適切な固有理由がある
- [ ] Stem、全候補、正答・誤答解説に現れるService正式名・正規aliasが、正答役割に関係なく同じ規則で固有Service Entryへ直接Linkされている
- [ ] Artifact正答解説が正答だけを分けるField・Operator・値・Identity境界・実行順を示し、誤答にも共通するContainer名やAPI名、`X == Y`の比較、汎用Tokenだけを決定Evidenceとしていない
- [ ] Artifact誤答解説が各候補固有のMutationとFixture／Dry run／導出で観測した失敗結果を説明し、Text問題時代の選択肢理由や別候補の挙動を説明していない
- [ ] 解説の正規化済み文・句・完全一致をBank／Family／Correct role別に集計し、候補固有文の後へ同じ汎用接頭辞・末尾を大量反復して説明固有性を水増ししていない。機械可読な差分Labelは技術解説件数へ数えていない
- [ ] Stem、補足条件、Key decision factor、Hintと解説をField横断で比較し、正答理由や複数誤答の失敗理由を解答前に逐語・ほぼ同文で列挙していない。判断軸と、解答後に示す候補別診断を分離している
- [ ] 本文の丸写し、言い換え問題、定型解説で水増ししていない
- [ ] Generator固有の接頭辞・接尾辞とIDを除去したSemantic signatureでも、Variant同士が同一のStem、Artifact、Option coreになっていない
- [ ] Variantの独立したDecision axis、Failure mode、Candidate behavior、必要EvidenceをManifestまたはReview台帳へ記録し、正規化Signatureで検出したClusterを全件意味レビューしている
- [ ] 問題直後の解答表示または指定形式が正しく機能する
- [ ] 通常問題と模擬試験の題意重複を検査している

## 7. 問題品質レビュー

- [ ] 全問に一意なIDと学習目標がある
- [ ] 共通検査スクリプトまたは同等以上の記録済み閾値で、全問の欠落、対応ずれ、重複、説明固有性を自動検査している
- [ ] 全問を分割して正答性、曖昧さ、誤答、解説を意味レビューしている
- [ ] 領域横断のカバレッジと分布を確認している
- [ ] 独立した第二レビューを実施している
- [ ] 意味Reviewと独立Reviewを別台帳で管理し、Reviewerが異なり、全問題IDが一度ずつ存在する
- [ ] Review stampは実Reviewer identityと確認Scopeを明示入力として記録し、一つの確認操作からHard-codeした複数Reviewer名を合成していない。Validatorは名前の文字列差だけで独立性を認定していない
- [ ] Review台帳の問題Hashが現在の問題内容と一致し、修正後に古いReviewを流用していない
- [ ] Review用Content manifestはAcceptance ADR・Review台帳・Stamp出力を含む循環参照になっておらず、ADRをProposedからAcceptedへ変えてもReview hashがstaleにならない。必要なRelease hashは別manifestとして扱っている
- [ ] Review用Content manifestはReviewerが確認した固定Surfaceのみを含み、問題Reviewに無関係な講義、Lab、Validator、Dependencyなどを含めていない。対象外の変更でHash不変、対象内の変更でHash変化となるFixtureがある
- [ ] BlockerとMajorを修正し、再検査している
- [ ] 残るMinorは問題ID、理由、影響とともに記録している
- [ ] 件数だけを根拠に品質完了としていない

## 8. ソースと回帰防止

- [ ] 生成物がある場合、手修正だけでなく生成元を直している
- [ ] 再生成しても改善が維持される
- [ ] 多段生成は各ID／保護Fieldの正確なPreimageと最終Postimageを区別し、一部だけ最終化された混在Corpusを全体Skipしない。旧状態・最終状態・混在・部分完了・未知DriftのFixtureで、変換／Skip／Fail closedを検証している
- [ ] 全体翻訳・言語移行を多段修復と併用する場合、翻訳前に修復を正規Sourceへ実体化するか、翻訳後Sourceの正確なPreimage／Postimageを修復段へ登録している。旧言語Hashだけを受理する修復を残したまま正規Sourceを翻訳せず、移行後の通常生成経路と未知DriftがFail closedになるFixtureを通している
- [ ] 生成前後の対象ファイル集合と正規化本文が一致し、UTF-8 BOM、CRLF／LF、Locale依存SortによるWindows／Linux差を検査している
- [ ] 公開CIがLinuxの場合、生成再現性、問題検査、厳格BuildをCI上でも通している
- [ ] 依頼範囲とプロジェクト構造に適合する場合、プロジェクト固有の品質検査を追加または更新している。適合しない場合は既存検査または一時的な読み取り検査を記録している
- [ ] 学習契約Gateを導入した場合、正規問題SourceからManifestとAssessment inventoryを再現可能に生成し、手作業の事後申告だけをSource of truthにしていない
- [ ] 意図していない講義、問題、コード、解答、外部URLの変更がない
- [ ] 全体翻訳では、翻訳対象外の正式名称・コード・識別子を除き、旧言語がソースと生成物へ残っていないことを機械的に検査している
- [ ] `git diff --check`相当の差分検査が通る

## 9. Web表示

- [ ] 厳格ビルドが通る
- [ ] 各講座の生成HTMLで上部Serviceカテゴリが第一級カテゴリとして表示され、Domain／Task、通常問題、模擬問題より前にあり、包括的Curriculum landingへLinkし、Serviceページで正しくactiveになる
- [ ] Service landingの全正式名称Linkが生成HTMLの宣言Pageと固定Anchorへ解決し、個別見出しと用語集より厚い本文を表示する
- [ ] 全講義・問題HTMLのlearner-visible Service aliasが一つの`a`要素内にあり、`href`が宣言Entry Pageと固定Anchorへ解決する。Code、URL、HTML属性を対象外にし、Landing止まり、外部Documentation、別Entry、裸aliasが0件である
- [ ] 内部リンク、用語アンカー、画像、図、コード、数式、折りたたみが機能する
- [ ] 生成HTMLでMermaid Sourceが通常の `pre > code` として露出せず、Mermaid containerへ入り、JavaScript実行後DOMで各候補がSVG等へ描画されている
- [ ] 390px相当とPC幅の実DOMで、各Option Artifact containerの `scrollWidth <= clientWidth` を確認し、横スクロールなしで判断に必要な全内容を読める
- [ ] 複数講座サイトでは、講座切替、講座内カテゴリ、現在カテゴリ内のページ一覧を別の階層として表示している
- [ ] 複数講座サイトのCIが、全講座の生成元、講義、問題、Review台帳、静的HTML検査を対象にしている
- [ ] ローカルで必須のValidator、警告失敗Option、候補Artifact検査、Variant実質差検査を公開CIでも同じFailure policyで実行し、新規Gate追加後にCIとの集合差が残っていない
- [ ] 学習契約Gateが対象範囲なら、正規Assessment inventoryとの完全一致と100%の問題前提閉包を公開CIでも同じFailure policyで実行している
- [ ] ナビゲーション変更時は、代表ページだけでなく全生成ページで現在講座、現在カテゴリ、切替先、サイドバー範囲を検査している
- [ ] サブパスで公開するサイトでは、404ページ、アセット、絶対内部リンクが公開ベースパスを維持している
- [ ] 実画面でPCとスマートフォンの本文と表を確認した。またはブラウザ禁止時は静的検査だけを行い、見た目を未検証と記録した
- [ ] 目次、検索、前後移動、ナビゲーションを実操作で確認した。またはブラウザ禁止時はリンクとHTML構造だけを確認し、操作を未検証と記録した
- [ ] 検索抑制を非公開化や認証と誤説明していない
- [ ] 公開サイトとソースリポジトリのVisibilityを別々に扱い、サイト公開をリポジトリ公開の許可と解釈していない

## 10. 外部サービスと公開

- [ ] 新しい外部サービス、自動化、料金、権限、データ、代替案を事前説明している
- [ ] プッシュで既存CIが動く場合、トリガーと利用量を必要に応じて説明している
- [ ] 公開を依頼された場合、ローカル変更だけで止めていない
- [ ] 新規リポジトリを意図したVisibility（明示指定がなければPrivate）で作成し、既存リポジトリでは公開前に実際のVisibilityを確認している
- [ ] Privateリポジトリでは利用できない公開経路の場合、無断でPublicへ変更せず、制約、料金、公開範囲、代替経路を説明している
- [ ] CIまたはデプロイの完了を確認している
- [ ] 公開URLを直接確認し、新しい本文、リンク、問題、解説が反映されている
- [ ] 公開後もソースリポジトリが意図したVisibility（明示指定がなければPrivate）であることを再確認している
- [ ] 複数講座を公開した場合、各講座から少なくとも一つの新しい本文Markerを直接確認している
- [ ] ブラウザを避ける必要がある場合、生成HTMLとHTTPで内容・構造を確認し、レイアウトと操作は未検証と報告している

## 11. 最終報告

- [ ] 変更範囲、対象バージョン、件数、レビュー結果、ビルド結果を報告している
- [ ] 上部Serviceカテゴリの表示位置、Navigation category数、包括的Service curriculum Unit数、Assessment Binding数、生成HTML navigation Gateの結果を報告している
- [ ] 固有Service-entry数、公式／Assessment Inventory差分、固定Anchor／Landing直接Link数、全11 Dimension合格Entry数、Assessment named-service Binding数を報告している
- [ ] 正規Service alias数、講義・Stem・Option・解説別の直接Link数、裸／曖昧／誤Link数、Service mention Link Gateと生成HTML Gateの結果を報告している
- [ ] 公式Sample／Practiceの確認状態とAccess制約、各Assessment surfaceの総数・最低数・60%へ算入したArtifact-native Option Artifact問題数と種類別件数、Stem-only／架空Wrapper非算入数、候補検証・行長・Mermaid描画・横Overflow不合格数を報告している
- [ ] Artifact固有Stem契約、Scenario contract重複、全Option解説Binding、候補と不一致の旧解説の検査件数・不合格数を報告している
- [ ] 変更しなかった保護対象を報告している
- [ ] 公開URL、ソース、生成元、再検証方法を示している
- [ ] ソースリポジトリのVisibilityを示している
- [ ] 自動化、料金、サイトとリポジトリそれぞれの公開範囲、既知の制約を示している
- [ ] 「ビルド成功」と「学習内容の品質」を別々に評価している
