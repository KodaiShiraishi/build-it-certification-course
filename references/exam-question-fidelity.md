# 公式問題形式と実務Artifactの再現基準

この基準は、IT資格の問題集を「用語を覚えたか」だけでなく、試験が測る実務判断へ近づけるために使う。コード量を全資格で固定せず、現行の公式試験ガイド、公式サンプル／模擬問題、公式製品資料から資格ごとに校正する。

## 1. 問題作成前のEvidence gate

通常問題または模擬問題を新規作成・大幅拡張する前に、次を順に確認する。

1. 現行の公式試験ページと試験ガイドを開き、対象Version、確認日、Objective、比率、問題形式、想定経験を記録する。
2. 現行試験向けの公式Sample questions、Practice test、Practice assessmentを探す。
3. 公開Sampleが旧版・retiredであれば、現行試験の直接的な出題比率の根拠にせず、旧版であることを記録する。
4. Academy、Webassessor、Learning portalなどへのLoginが必要なら、何がLogin後にあるか不明なまま推測しない。ユーザーへアクセス制約を伝え、本人が確認できる場合は抽象化した観察結果を依頼する。
5. 公式問題が見つからない場合も、検索場所、確認日、`not_found` を記録する。「公式問題と同等」とは表現しない。

ユーザーへ依頼する観察結果は、コードや表の有無、長さ、選択肢間の差、診断か暗記か、領域別の印象などである。実問題の本文、選択肢、正答を転載・復元させない。非公式Dumpや記憶再現問題をEvidenceにしない。

現行の公式問題形式が不明で、Login後の確認が必要な場合は、その確認前に大量生成や最終的な問題構成を確定しない。先に公式ガイドから仮のCoverage mapと不足情報だけを作る。

## 2. 実務Artifactの分類

60%ポリシーへ算入する問題は、選択肢そのものに提示して正しい実装・設定・出力等を選ばせる候補を `artifact_types` で分類し、学習者が独立して受ける問題面を `assessment_surface` で識別する。一問が複数Typeへ該当してよい。各宣言Typeについて全 `option:<key>` に一件ずつ `artifact_evidence` を持ち、候補内に実在する文字列をExact sliceとして保持する。StemだけのArtifactは補助Scenarioとして使用できるが、60%の件数Evidenceにはしない。

| 値 | 対象 |
|---|---|
| `code` | SQL、Python、Java、C#、API呼び出しなどの実行可能CodeまたはFragment |
| `command` | CLI、Shell、管理Command、引数、実行順 |
| `configuration` | YAML、Manifest、Policy、IaC、Pipeline／Bundle定義などの設定 |
| `structured_data` | JSON、YAML、XML、Nested object、Request／Response、Schema |
| `table_io` | 入力表、期待出力表、Schema、行数、NULL、Cardinalityの変化 |
| `logs_metrics` | Error、Log、Metric、Execution plan、Trace、Monitoring画面の値 |
| `diagram_ui` | Architecture図、Topology、Console／UIの状態 |

素材を本文に置いただけ、またはOptionの一部だけに置いただけでArtifact選択問題と数えない。全Optionが同じArtifact種別と技術粒度の実在可能な候補を持ち、具体的な行、Field、値、構造、呼出順、演算子、Identity境界、実行結果の差を読んで要件を満たす候補を決めることを条件にする。概念だけの問題、StemのCodeやLogを読んで自然文の原因名・Service名を答える問題は `artifact_types: []` と `artifact_evidence: []` にし、必要なら別の補助分類で追跡する。`format: code`、Family名、Filename、Stem中の「Codeを確認した」というProse、Generatorの分類関数は、選択肢内実物の代わりにならない。

各算入問題に `artifact_selection.task: select_correct_artifact`、要求Behavior／Result、全候補を覆う実物中の `decision_axes`、候補検証を保持する。候補検証は共通Fixture、Schema／Dry run、または入力からの導出結果を使い、検証Reference、候補別結果、検証済み正答集合を記録する。Code候補は正答・誤答を同じ実行可能またはStub化したFixtureへ通す。意味Reviewだけの自己申告を実行証拠にしない。

意味上の依存性はMetadataやCode fenceの存在だけでは証明できない。独立レビューでOption Artifactを一時的に隠し、Stem、Optionラベル、周辺Proseだけで正答を特定できないか確認する。本文が「違反行を除外して続行する」「devとprodでCatalogだけを変える」など、正答の動作をすでに言い換えている場合は削除テスト不合格とし、Artifact件数へ数えない。表に `correct`、`matches`、`expected answer`のような正答ラベルを置く問題も同様に扱う。全候補の観測結果が同じ、差が識別子・Comment・表示値だけ、または要求Contractと候補差が結び付かない場合も不合格にする。

既存Text問題をArtifact問題へ変換するときは、候補を差し替えるだけのOverlayにしない。Stem、全候補、正答集合、正答解説、全誤答解説、Evidence、選択契約を一つの原子的なAuthoring unitとして作り直す。Stemは、候補Artifactから判断できるContext、入力／状態、Hard constraint、期待する観測と、どの種類のArtifact候補を選ぶかを明示する。旧Stemの一般的な「最適な方法はどれか」を残して末尾だけArtifact選択へ変えたり、旧Optionが表したService／Architecture選択の理由を新しいCode／YAML候補の解説として流用したりしない。変換前の文はBaseline hash、Change log、監査用Sourceとしてだけ保持し、learner-visible出力へ連結しない。

各算入問題の `artifact_selection.stem_contract` に、Stem中のArtifact選択要求と、ScenarioのContext、入力／状態、Hard constraint、期待する観測のExact sliceを保持する。候補を隠すと正答できないことを確認したReview／Fixtureも `deletion_test.review_reference` へ残す。一意性判定ではHard constraint、期待する観測、Decision axis、候補別結果を正規化したContractをBank全体で比較し、Actor名、ID、数値Literal、Option順、背景文だけを変えたStemを別問題として数えない。問題形式だけをTextからArtifactへ変更した場合も、問題Hashと意味Review／独立Reviewを更新する。

## 3. 資格ごとのArtifact policy

試験Objectiveごとに、次を対応表へ記録する。

| Objective | 公式Evidence | 問われる判断 | Artifact type | 最低問数 | 根拠 |
|---|---|---|---|---:|---|

通常問題集、Practice Exam A、Practice Exam B、各Mockなど、学習者が別々に開始・採点できる単位を独立したAssessment surfaceとする。各SurfaceのArtifact問題総数は、全Optionの検証済み `artifact_evidence` と有効な `artifact_selection` を持つ一意な正しいArtifact候補選択問題で、そのSurface全体の60%以上を共通下限とする。500問なら300問以上、1,000問なら600問以上、65問のExam formなら39問以上であり、`ceil(surface total × 0.60)` で端数を切り上げる。全Surface合算で60%を満たしても一つでも下限未満なら失敗とする。Stem-only Artifact問題は分子へ入れない。複数Typeを持つ一問は種類別集計では各Typeへ一回ずつ数えるが、60%の分子では一問と数える。公式Sampleで実際に素材が提示される頻度、試験ガイドの動詞、想定実務経験、ユーザーの受験後Feedbackを根拠に、資格・Objective・Surface別のType配分と60%を超える最低数を設計する。

公式Sampleの母数が少ない場合は、見かけの割合をそのまま全問題へ外挿しない。60%は公式出題率の推定ではなく、実務読解を十分に練習する教材品質の下限として扱い、その区別とEvidenceの不確実性を `calibration_note` に書く。ユーザーの領域別Scoreと教材習得状況が得られたら、単なる苦手分野ではなく、Coverage、Artifact密度、問題形式、受験言語の差を分けて再評価する。

## 4. Artifactを使う問題Pattern

- **Code correctness**: API名、引数、呼出順、Return、Scope、Execution semanticsのいずれかが異なる、実在可能な近接Code片を比較させる。正解の完成Codeを本文へ先に表示し、その言い換えをOptionから選ばせない。
- **Input → output**: Stemに小さな入力を示し、各Optionへ異なる出力表または変換Codeを提示して、Filter、Join、Aggregate、Window、NULL、重複、Schema変化を正しく反映する候補を選ばせる。
- **Configuration／structured data**: 全Optionへ実在可能な設定候補を置き、階層、必須Field、型、参照関係、権限境界の差から正しい候補を選ばせる。
- **Troubleshooting**: ErrorやLogをStemの説明だけにせず、全Optionへ診断Command、修正Configuration、または期待する検証結果をArtifact候補として提示し、観測、原因切り分け、修正、再検証の契約に合う候補を選ばせる。
- **Command／operation**: 全OptionへCommand列を置き、実行場所、Credential、Context、Option、副作用、Rollback、fail-fastの差から正しい列を選ばせる。
- **Architecture／access boundary**: 全OptionへDiagram／Policy／構成候補を置き、利用主体、Account有無、Read／Write、Cloud／Region、Protocol、管理責任の差から正しい候補を選ばせる。

Artifactは、その製品が実際に受理または生成するSchema、実在する言語、実行可能なCommand、実際のLog／Metric、入力・出力、またはArchitectureそのものを使う。自然文Optionを架空の `apiVersion: course.*`、`ArchitectureCandidate`、`services`／`operations`／`controls`／`flow`へ詰めただけのYAML／JSON、正答条件をCommentやString Listへ直列化したCodeを禁止する。Artifactを通常文へ戻しても同じ語句だけで解け、構文、Field、Operator、Control flow、Dataflow、Identity、実行結果を読む必要がない問はText問題へ戻し、Artifact件数へ算入しない。

Code候補を完成した実装として提示する場合は、正解だけでなく全候補を対象言語のParser、Compiler、Linter、または製品固有の検証Commandへ通し、少なくとも構文として完全であることを確認する。先頭がMethod chainだけのFragment、Receiverや必須引数が省略された式、URLだけの文字列などを使う場合は、FragmentであることとReceiver、代入先、前後の実行Contextを問題内に明示する。誤答は偶発的な構文欠落ではなく、実在可能なAPI、引数、Field、Operator、型、実行Semanticsの差で作る。

全候補を読みやすいSourceとして整形する。JSON／YAMLはField単位、Commandは引数単位、Codeは処理単位、LogはEvent／Attribute単位、表は判断に必要な列単位で改行し、一行100文字を共通上限とする。長いARN、URL、Token、Payloadは要件を失わないNamed placeholderや前提変数へ分ける。CSSの強制折返しだけをSource整形の代わりにせず、狭い画面では安全網として併用し、390px相当の実DOMで各Option Artifactの横Overflowが0であることを確認する。

Mermaid候補は `mermaid` Fenceで記述し、生成HTMLではMermaid container、JavaScript実行後DOMではSVG等へ変換されることを確認する。`flowchart LR`等を通常のCode blockへ表示しない。図はAmazon S3、Amazon EventBridge、Queue、Workflow等の実ResourceをNodeに、Event、Request、Data、Failure pathをEdgeにし、`services → operations → controls → flow`のようなMetadata box列をArchitecture図として数えない。Mermaid Source自体の正誤を問うと明示した問題だけRaw Source表示を許可し、その場合は `diagram_ui` ではなくCode問題として分類する。

Parser合格だけを完成Artifactの証拠にしない。設定やWorkflowは、参照する変数、Task key、Job parameter、依存Edge、出力が同じ候補内または明示した前提Contextで解決するかをReference closure検査する。Command列は、前段の失敗が後段を停止する契約まで確認する。たとえばPowerShellでnative commandの非0終了を前提にするなら、`$LASTEXITCODE`、`$?`、または明示的な例外化がなく次のDeployへ進む候補をfail-fast実装として扱わない。製品CLIのSchema検証やDry runが利用できる場合は、構文Parserだけでなく全完成候補へ適用する。

実行可能なCode候補では、問題文の最小入力と明示した前提をFixture化し、正答を含む全候補を同じHarnessで実行する。単にExceptionが出ないことではなく、要求Contractを満たす候補がKeyed candidateだけであること、誤答が説明どおりの固有な失敗結果を返すこと、候補間の観測結果が実質的に異なることを検査する。空DataFrame、欠落JSON key、未定義名、暗黙のGlobal、`None`、同じRowを返す別候補など、説明と実行結果がずれるFixtureを含める。外部呼出しは記録可能なStubまたはFakeへ置き換え、Endpoint、Method、Path、Payload、Identity、Poll対象まで比較する。

同一Objective内のVariantは、識別子、表示値、Option順、定型文を除去した正規化AST、Control flow、Dataflow、Predicate、外部Call sequence、期待出力SchemaのSignatureでも比較する。Stemの業種名やField名だけを変え、同じ分岐・同じ失敗・同じ処理を問うものは別問として数えない。各Variantには、少なくともDecision axis、Failure mode、Candidate behavior、必要なEvidenceのいずれかについて独立した学習判断を割り当て、その差をManifestまたはReview台帳へ記録する。

Rate、Cost、Latency、Count、Probabilityなどの値は、Scenarioで別途定義しない限り現実的な型と値域へ制約する。負の料金や`[0,1]`外の率など、正答位置を目立たせる不自然値を誤答へ置かない。境界値を問う場合は、値域、単位、丸め、上限を含むかをStemと実装で一致させる。

製品固有API、Model、Endpoint、Region、Deployment mode、Client library、権限に条件がある場合、その条件をStemへ明示し、Source claimもそのScopeへ限定する。一般機能の説明と、特定のServing方式・Region・Endpoint typeだけで成立する説明を混同しない。問題が複数FieldやRecordを要求するなら、候補のReturn型とField集合をその要求へ厳密にBindingし、一つのScalarや欠落Fieldを「意味は同じ」として正答扱いしない。Course独自SchemaやAdapterは製品APIと誤認されないよう明示し、型、必須Field、Receiver、提供Contextを問題内で完結させる。

難易度は長文、珍しい言い回し、翻訳しにくい否定表現で上げない。現実的なArtifact、似た実装、実行結果の推論、適用条件の比較で上げる。正答解説は、判断に使う行やFieldと中間結果を順に示す。誤答解説は、どの条件、構文、実行結果が違うかを個別に説明する。

Artifact問題の正答解説は、全候補に共通するContainer名やAPI名ではなく、正答だけを分けるField、Operator、値、Identity境界、実行順、または複数行の組合せを指す。引用した決定Evidenceが一つの誤答候補にも同じ形で存在するなら、その引用だけでは正答理由にならない。Generatorでは `XではなくY` の `X == Y`、`.merge(`、`bundle:`、`if (`のような共通Tokenだけを差分として出力する状態をNegative fixtureで拒否する。正答の決定差分と、各誤答のMutation差分を候補本文から再計算し、解説を固定Slotから組み立てない。

全Optionを覆う `artifact_selection.explanation_bindings` を持ち、各Optionについて、候補内の決定的なExact `artifact_excerpt`、共通検証の候補別結果に含まれるExact `result_excerpt`、両方を含む正答または誤答解説のExact `explanation_excerpt` を結ぶ。正答候補では、どのField／Call／値／Edgeが要求を満たし、Fixture／Dry run／導出で何が観測されたかを示す。誤答候補では、その候補固有のMutationがどの結果、Failure、欠落、余分な副作用を生むかを示す。Artifact候補または候補別結果を変更してBindingと解説を更新しなければGateを失敗させる。旧Text問題の解説、候補に存在しないService判断、全Optionへ共通の「要件を満たさない」を残した問題を60%へ数えない。

候補固有の原因を一文だけ示した後へ、同じ「このField、Operator、値、Callが契約を変える」のような汎用接頭辞・末尾を数百問へ付けても、説明固有性を高めたことにはしない。解説の文単位・正規化済み句単位・完全一致で、Bank／Family／Correct role別の重複数と超過件数を集計し、大量反復する汎用文は削除するか、その候補で実際に変わる製品挙動、出力、失敗条件へ置き換える。差分を機械可読に示す短い定型Labelは許容できるが、それ自体を候補固有の技術解説件数へ数えない。

解答を開く前に見えるStem、補足条件、`Key decision factor`、Hintへ、正答理由や各誤答の失敗理由を逐語またはほぼ同じ文で列挙しない。判断軸は「どのFieldと要件を比較するか」までに留め、各候補の診断結果は解答欄で初めて示す。学習者表示の解答前Fieldと、正答・誤答解説の正規化文、長いn-gram、決定Token列を相互比較し、複数候補の理由が先に公開されるfixtureを失敗させる。問題文に正当な要件語が重なるだけのSafe fixtureも持ち、短い共通用語の一致を答え漏洩と誤判定しない。

語彙手掛かりは単語の禁止Listだけでなく、Code fenceを除いたOption proseについてCorrect／Incorrectの出現率とwrong-only question数をBank、形式、領域ごとに比較する。十分な出現数がある語や句が誤答へ排他的または著しく偏る場合、全該当問を役割単位でReviewする。正答側へ同じ語を機械挿入して率だけを均すことは禁止し、近接候補を平行な文法と同じ技術粒度で書き直す。正当な条件表現を含むSafe fixtureと、複数誤答だけが譲歩・欠落・無条件動作の語で識別できるUnsafe fixtureの両方を持つ。

単語・n-gramごとの偏りが閾値内でも、複数の文体特徴を合わせると正答役割が漏れることがある。十分な問題数があるSingle Choiceでは、問題文・Option Label・Code fence・URLを見せずOption proseだけを入力する単純な交差検証Classifierまたは同等の数理的Backstopを実行し、ランダムLabelのBaselineより実質的に高い正答集合再現率が出た場合は全該当候補を人手Reviewする。この検査は学習器の精度を盲目的なRelease閾値にせず、誤答にだけ破壊操作、未検証の即時本番反映、証跡削除、極端な値、実在しない製品挙動が集中していないかを特定する起点にする。修正は、同じ目的・同じ運用境界で起こる一つの現実的な誤認へ置き換える。Classifierを通すための同義語挿入、文長Padding、Labelの機械的並べ替えは修正と数えない。

ClassifierのFeature表現を、結果が通る単語単位だけへ事後的に狭めない。十分な母数では少なくともWord n-gramとCharacter n-gram、または語形・句読点・接続表現の役割漏れを同等に捕捉できる独立した表現を用い、表現ごとの交差検証結果とBaseline差を記録する。複数表現の平均だけをGateにせず、いずれか一つが実質的にBaselineを上回れば、そのFeatureが拾った候補群を人手Reviewする。Feature、n-gram範囲、正規化、閾値を候補結果を見た後に削って合格へ寄せることは禁止し、Safe／Unsafe fixtureで検出力を固定する。

語彙・文体の手掛かり修正で、SQL Command、API名、Configuration key、JSON Field、Enum値、Identifierを一般語の同義語置換対象にしない。例えば人間の文章で `set`が正答役割に偏っていても、`ALTER TABLE ... SET MANAGED`の `SET`を `CONFIGURE`に置き換えてはいけない。修正後は一次情報の現行構文と実行可能なParser・Schema・Command helpのうち利用できるもので、正答とすべての近接誤答Artifactを再検証する。正答の必須Keywordを別語に変えたfixtureと、Code fence外のCommand-like proseだけを壊したfixtureの両方を失敗させる。

Generatorで改行・Tab・HTML breakなどのEscapeを復元するとき、Raw substringの全置換を学習者文字列全体へ適用しない。PowerShellのbacktick、Python／JSONのbackslash、Markdown inline codeを構文Contextなしに置換すると、`` `normalize` ``や`new_stats_client`のような正当なIdentifierまで壊れる。実際のEscape tokenだけを生成段階で型付きに保持するか、Code fence／inline code／正式Tokenを退避してからContext-awareに復元する。実改行を変換するUnsafe fixtureと、Escape markerに似た先頭文字を持つIdentifier、Command、Pathをbyte-identicalに保つSafe fixtureを持ち、最終learner-visible outputでも検査する。

ValidatorのNegative fixtureは、最終エラー数だけでなく、検査が依存するParser・Token extractor・Normalizerの中間結果を直接検証する。非空の候補から期待するSet・List・Recordが返ること、決定Tokenを候補本文または解説から一つ削ると対応するBinding gateだけが失敗することを確認する。到達不能な `return`、常時 `None`、空Set、Exceptionの握りつぶしによって検査がサイレントに無効化されていないか、小さな正常入力と失敗入力の両方で検証する。

正答長、語彙偏り、重複率などの集計Gateでは、閾値を「最大値を含む」か「最大値未満」かまで文章で定義し、実装の比較演算子と一致させる。0.35、35%、`7 / 20`のように同じ境界を別表現で比較する場合は丸め前の分子・分母で判定する。上限の直前、境界値そのもの、直後を作るNegative／Safe fixtureを持ち、たとえば「35%未満」が契約なら7/20を合格させない。全問の実分布が十分低いことだけをGateの有効性の証拠にせず、意図した悪い分布を必ず落とすDeletion test相当の自己検査を行う。

講義内Quiz、LabのDecision question、章末確認問題も、主問題集と同じOption品質基準でReviewする。製品概念と無関係な語、明らかな破壊操作、冗談に近い値を誤答に置かず、同じ障害や設計境界で実務上起こり得る近接誤判断を使う。正答だけを説明せず、各誤答についてその候補固有の失敗条件を一つずつ示す。

講義・Labの全Question blockとAnswer blockを列挙し、Single Choice、Multiple Response、Open response、手順確認などの形式へ明示分類する。Open responseを、A-D候補、Keyed answer、誤答別理由を検査した件数へ混ぜない。Open responseを残す場合は、期待する判断、必須Evidence、採点または自己確認基準を検査する。Validatorが単にAnswer block数を数え、実際には候補がないQuestionまでDistractor品質の合格証拠にしていないことをNegative fixtureで確認する。

Open responseの必須EvidenceとRubricは、`Yes`／`No`、`Not always`、正答文、Expected judgmentを別Labelで再掲しただけでは合格にしない。学習者が挙げるべきField、Operator、Data変化、実行結果、失敗条件、設計境界のうち問題固有の要素を要求し、Evidence同士も同じ内容の言い換えにしない。答えLabelをEvidenceへCopyした例、JudgmentをRubricへ繰り返した例、問題と無関係な講義導入をRubricにした例をNegative fixtureで拒否する。

主問題集の正答位置、Option長、語彙手掛かり検査が講義・LabのInline questionまで自動的に覆うと仮定しない。Inline questionの固定Inventoryを母集団として、形式別の正答位置、Correct／Incorrect語彙率、wrong-only item、実質的な長さ差を別に集計する。A/Bだけで全問を回す、C/Dが一度も正答にならない、または旧候補の説明がLabelだけ変わって残る状態を、候補本文とKeyed explanationのBinding検査で拒否する。

60%へ算入するすべての問題で、Option自体に複数のArtifact候補を提示する。全Optionへ同じ正解Codeを複製し、汎用的な`require_all`、`remediate`、`pass`のようなFlagだけを変えた問題はCode correctnessとして数えない。製品固有のAPI名、引数、JSON Field、Column、Operator、Identity境界、実行結果の差が正答を決めるようにする。

## 5. ハンズオンを省略したい学習者への代替

ユーザーが時間効率を優先してハンズオンを任意にしたい場合、演習成果を削除せず、全選択肢の実装候補から正しいArtifactを選ばせる問題へ変換する。

- 実行する代わりに、Code、Command、Configuration、入力、Log、出力を一つのScenarioとして読む。
- 正常系だけでなく、意図的なError、観測結果、原因、修正後の結果まで一続きにする。
- 解答後に、Code各行、Data各段階、診断順を追える解説を置く。
- 実環境固有のUI操作や感覚が試験対象なら、ハンズオンを完全な代替扱いにせず任意の補助経路として残す。

## 6. 共通JSONLと機械検査

各問に次を追加する。

````json
{
  "id": "Q-001",
  "assessment_surface": "practice-bank",
  "artifact_types": ["code"],
  "stem": "An application invokes AWS Glue and has the job name. Which Python implementation starts exactly one job run and returns the new JobRunId?",
  "options": {
    "A": "```python\nresponse = glue.start_job_run(JobName=job_name)\nreturn response['JobRunId']\n```",
    "B": "```python\nresponse = glue.get_job_run(JobName=job_name, RunId=job_name)\nreturn response['JobRun']['Id']\n```"
  },
  "correct": "A",
  "correct_explanation": "`start_job_run` records one start call and returns jr-123, so option A creates the requested run and exposes its JobRunId.",
  "wrong_explanations": {
    "B": "`get_job_run` records no start_job_run call and only reads an existing run, so option B cannot create the requested run."
  },
  "artifact_evidence": [
    {
      "type": "code",
      "location": "option:A",
      "content": "```python\nresponse = glue.start_job_run(JobName=job_name)\nreturn response['JobRunId']\n```",
      "decision_binding": "start_job_run creates a run and JobRunId is the required return value."
    },
    {
      "type": "code",
      "location": "option:B",
      "content": "```python\nresponse = glue.get_job_run(JobName=job_name, RunId=job_name)\nreturn response['JobRun']['Id']\n```",
      "decision_binding": "get_job_run reads an existing run and cannot create the required run."
    }
  ],
  "artifact_selection": {
    "task": "select_correct_artifact",
    "requirement": "Start the named job and return the newly created run identifier.",
    "stem_contract": {
      "artifact_request": "Which Python implementation",
      "scenario": {
        "context": "An application invokes AWS Glue",
        "input_or_state": "has the job name",
        "hard_constraints": ["starts exactly one job run"],
        "expected_observation": "returns the new JobRunId"
      },
      "deletion_test": {
        "artifact_candidates_required": true,
        "review_reference": "reviews/artifact-deletion.csv#Q-001"
      }
    },
    "decision_axes": [
      {
        "name": "AWS Glue operation",
        "option_values": {"A": "start_job_run", "B": "get_job_run"}
      }
    ],
    "validation": {
      "method": "shared_fixture",
      "reference": "tests/glue_start_job_candidates.py::test_candidates",
      "validated_correct": ["A"],
      "candidate_results": {
        "A": "Records one start_job_run call and returns jr-123.",
        "B": "Attempts to read a run and records no start_job_run call."
      }
    },
    "explanation_bindings": {
      "A": {
        "artifact_excerpt": "start_job_run",
        "result_excerpt": "returns jr-123",
        "explanation_excerpt": "`start_job_run` records one start call and returns jr-123, so option A creates the requested run and exposes its JobRunId."
      },
      "B": {
        "artifact_excerpt": "get_job_run",
        "result_excerpt": "records no start_job_run call",
        "explanation_excerpt": "`get_job_run` records no start_job_run call and only reads an existing run, so option B cannot create the requested run."
      }
    }
  }
}
````

Targetsには、Evidenceと最低数を保持する。`calibration_evidence` には `exam_guide` と、`official_sample` または `official_practice` の調査結果を必ず含める。公開されていなくても `login_required`、`not_found`、旧版なら `outdated` と記録する。ユーザーの抽象化された受験観察は `user_observation` とADR等のReferenceで追加できる。

```json
{
  "artifact_policy": {
    "calibration_evidence": [
      {
        "kind": "exam_guide",
        "status": "current",
        "url": "https://vendor.example/exam-guide",
        "reviewed_at": "2026-08-01"
      },
      {
        "kind": "official_sample",
        "status": "login_required",
        "reviewed_at": "2026-08-01"
      },
      {
        "kind": "user_observation",
        "status": "reported",
        "reference": "docs/adr/20260801-exam-retrospective.md",
        "reviewed_at": "2026-08-01"
      }
    ],
    "calibration_note": "Official guide and abstract user observations indicate frequent code and input-output reasoning.",
    "minimum_questions_with_artifacts": 600,
    "assessment_surfaces": {
      "practice-bank": {
        "total": 1000,
        "minimum_questions_with_artifacts": 600,
        "minimum_by_type": {
          "code": 180,
          "configuration": 40
        }
      }
    },
    "minimum_by_type": {
      "code": 180,
      "table_io": 80,
      "configuration": 40,
      "logs_metrics": 40
    }
  }
}
```

最終検査では、通常の検査引数に次を加える。

```powershell
python scripts/validate_question_bank.py questions.jsonl `
  --targets targets.json `
  --require-artifact-policy `
  --official-source-host vendor.example
```

この検査は、公式Calibration Evidenceの記録、全問の `assessment_surface`、全独立Surfaceの宣言総数と最低数、明示的な `artifact_types` と `artifact_evidence`、各宣言TypeのEvidenceが全Optionを覆いExact substringとして存在すること、Typeごとの最低限の構造、`artifact_selection` の要件・決定軸・候補検証・正答集合、Artifact固有の `stem_contract`、全Optionの決定差分・候補別結果・正誤解説を結ぶ `explanation_bindings`、Scenario contractの一意性、各SurfaceのOption Artifact選択問題総数が `ceil(surface total × 0.60)` 以上であること、種類別最低数を検証する。Stem location、候補不足、同一候補、候補結果差なし、再利用Scenario契約、候補と一致しない旧解説、架空Wrapper、100文字超のSource行、Raw Mermaid、検証済み正答と `correct` の不一致は0件扱いにする。複数Typeの一問は各Typeへ一回ずつ数えるため種類別合計は総問題数を超えてよいが、60%の分子では一問である。

機械検査は全Option Artifactの表示上の存在、構造、決定差分、候補検証記録を確認するGateであり、Reference先が実行された事実やObjective fidelityをMetadataだけで証明しない。生成後は各 `artifact_evidence.content` がLearner-visible Markdown／HTMLに残り、`artifact_selection.validation.reference` がローカル必須検査とCIで実行されることも照合する。Canonical JSONLだけが持つ非表示Metadataを表示Artifactや実行証拠と誤認しない。最終レビューでは全Objectiveを横断して削除テストを行い、さらにArtifact候補が公式Objectiveに対応する製品固有のAPI、設定、Data変化、実行結果、障害診断、または設計境界を実際に判断させるか確認する。汎用辞書の値Copy、YAML Slotの一対一転記、Trace文字列の完全一致だけで解ける問は、Artifactを消すと解けなくても製品Artifact件数へ数えない。正答条件を自然文で書いたCommentやCourse独自のAcceptance recordをCode、SQL、YAML、JSON Fenceへ包んだだけのものも、実装Artifactや実行結果として数えない。同じLog、Metric、Config、Codeの雛形をField名やAction文字列だけ変えて無関係なObjectiveへ回転させることも禁止する。ObjectiveとArtifact familyの組み合わせごとに、そのArtifactから導く判断がObjectiveの動詞と対象へ直接対応する根拠をReview台帳へ残す。確認した問題ID、Objective、判定、修正内容をReview台帳またはADRへ残す。テンプレート生成では、一つの失敗が大量複製されるため、Generatorの各問題Familyを少なくとも一度は確認する。

## 7. 完了条件

- 現行公式ガイドと公式Sample／Practiceの調査状態、確認日、Access制約が残っている。
- Loginが必要な公式問題をCodexが確認できない場合、ユーザーへ明示した記録がある。
- Objective別にArtifact typeと最低数の根拠がある。
- 全Option Evidenceと `artifact_selection` の検証に合格したArtifact-nativeな正しい候補選択問題の一意な件数が、通常問題集と各Practice／Mock formのそれぞれで60%以上である。
- 算入問題は各宣言Typeについて全Optionの `artifact_evidence` を持ち、Evidence内容が解答前に見えるOptionと生成Markdown／HTMLの両方に存在する。Stem-only Artifactは算入していない。
- 全候補のCode、Configuration、Data、Log等が同じ種別・粒度の実在可能な候補であり、要件を満たす正答を行・Field・Operator・値・関係・実行結果の差から選ばせる。
- Option Artifactを隠す削除テストで、Stemと周辺Proseだけから正答を特定できない。
- `artifact_selection` のDecision axisが候補内Exact sliceへ結び付き、共通Fixture／Schema／Dry run／導出検査の候補別結果と検証済み正答集合がある。Code候補は同じFixtureで実行されている。
- `artifact_selection.stem_contract` がArtifact選択要求とContext、入力／状態、Hard constraint、期待する観測のlearner-visible Exact sliceを保持し、Deletion testのReferenceがある。同じ正規化Scenario contractを別問題へ再利用していない。
- 全Optionの `explanation_bindings` が候補内の決定差分、候補別の検証結果、正答または誤答解説のExact sliceを結び、候補を変更して旧Text問題の解説を残すとGateが失敗する。
- ArtifactとOptionが公式Objectiveに対応する製品判断を測り、汎用的な値Copyや文字列一致だけの問題を製品Artifact件数へ数えていない。
- 架空のCourse Schema、Candidate Wrapper、自然文の直列化をArtifact件数へ数えていない。
- 正答条件を述べるCourse独自CommentやAcceptance proseをFenceへ包み、Codeや設定の件数へ算入していない。
- 一つの汎用Artifact familyを無関係なObjectiveへ回転させず、ObjectiveとFamilyの各組み合わせを意味レビューしている。
- Code／設定の形を問う問題では、正解を本文へ先に表示せず、実在可能な近接候補のAPI、引数、Field、構造、呼出順、演算子を比較している。
- 入力から出力、中間結果、Errorから診断順を追う問題が含まれる。
- Stem-only、Label-only、Option候補不足、同一候補、結果差なし、非表示Evidence、構造のないProseを拒否するNegative fixtureが成功する。
- Artifact候補と一致しない旧正答解説、旧誤答解説、一般的な旧Stem、候補だけを変更したStale explanation、再利用Scenario contractを拒否するNegative fixtureが成功する。
- Aggregateは60%以上でも一つのPractice／Mock surfaceが未達、100文字超の単一行、Raw Mermaid、Metadata boxだけの図を拒否するNegative fixtureが成功する。
- 生成HTMLと実DOMでMermaidが図へ描画され、390px相当のOption Artifactに横Overflowがない。
- `--require-artifact-policy` が成功し、検証済みEvidenceから数えた実測数が最低数を満たす。
- 公式問題と同一・再現と主張せず、一次資料から独自Scenarioを作っている。
