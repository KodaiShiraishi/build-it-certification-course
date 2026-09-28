# Service表記から包括的Service講義への直接Link

講義または問題に現れるService名、略称、主要機能名を、上部Servicesカテゴリの固有Entryへ一Clickで戻せるようにするときに使う。Linkを補助一覧だけへ集約せず、学習者が読んでいる文中のService表記そのものをLinkにする。

この導線の採用範囲は [講座設定](course-settings.md) に従う。採用時のリンク対象・例外・表示検査は本書が正規定義であり、他の文書へ同じ条件一覧を複製しない。

## 1. 正規aliasを持つ

各 `service_entry` に `aliases` を持たせる。正式名称を必ず含め、教材本文、問題Stem、全Option、解説で実際に使う短縮名も列挙する。

```json
{
  "id": "service-entry.amazon-eks",
  "name": "Amazon Elastic Kubernetes Service (Amazon EKS)",
  "aliases": [
    "Amazon Elastic Kubernetes Service (Amazon EKS)",
    "Amazon EKS",
    "EKS"
  ],
  "path": "services/compute-containers.md",
  "anchor": "service-amazon-elastic-kubernetes-service-amazon-eks"
}
```

- aliasは正規Service-entry InventoryとManifestの両方へ同じ集合を出力する。
- 正式名称の括弧内にある略称表記と、その中のService固有Acronymを自動的に必須aliasへ導出する。たとえば `Amazon Elastic Kubernetes Service (Amazon EKS)` なら `Amazon EKS` と `EKS`を省略できない。末尾が3文字以上の大文字Acronymまたは数字を含む製品Tokenの場合も短縮alias候補として検査する。
- 空文字、前後空白、改行、Markdown Link記号を含むaliasを許可しない。
- 同一Course内で大文字小文字を畳んだaliasが複数Entryへ解決する状態を許可しない。
- `Amazon EKS`と`EKS`のように重なるaliasは長いものから照合する。長い表記の内部を短いaliasとして二重Linkしない。
- `Quick`、`Jobs`、`Functions`のように通常語と衝突する裸語は無理にalias登録しない。正式名または文脈を含む一意な表記へ本文を直す。
- 名称変更や旧称をaliasに残す場合、現在も講義またはAssessmentで使用する表記だけを登録する。時系列の説明はEntry本文で行う。

## 2. Link対象を完全に列挙する

全正規講義ページと全learner-visible Assessmentページを対象にする。Assessmentでは次をすべて含める。

- Stemと補足条件
- Single Choice、Multiple Response、Ordering、Matchingを含む全候補
- 正答解説
- 全誤答の候補別解説
- Hint、Key decision factor、関連ScenarioのProse

正答候補だけをLinkしない。Distractorとして出るServiceも、その語をClickすれば同じService Entryで比較条件を学べるようにする。

Service Entryの見出しと、そのEntry section内で自分自身を指すService名は、既に到達先にいるため自己Linkを必須にしない。同じService Pageで別Entryのaliasに言及する場合は、その別EntryへLinkする。Code、Command、Configuration、JSON／YAML、識別子、Path、URLは自動Link対象外にする。Artifactの構文をLink挿入で変えてはいけない。Artifactの前後にある説明ProseでService名を使う場合はLinkする。

## 3. 表記そのものを直接Linkする

対象語を、対応するEntryの宣言Pathと固定Anchorへ直接Linkする。

```markdown
The cluster runs on [EKS](../services/compute-containers.md#service-amazon-elastic-kubernetes-service-amazon-eks).
```

- Services Landing、責務Family pageの先頭、検索結果、外部DocumentationだけへLinkして完了にしない。
- `Related services: EKS`のような別一覧だけで本文中の裸の`EKS`を代替しない。
- Link textはService表記部分を含める。文全体を不必要にLinkしない。
- 同じページで同じServiceが複数回現れる場合も、講義・問題の各独立Blockで最初の一回だけに制限しない。学習者がそのBlockから一Clickで戻れるよう、対象となる各出現をLinkする。
- 既存Link内のService表記が外部Documentationや別Entryを指す場合、入れ子Linkにせず、Service表記のLink先を内部Entryへ変更する。一次情報はSource欄など別の明示Linkに残す。
- 相対Linkは現在Pageから正規化して宣言されたEntry pathと一致し、fragmentは固定Anchorと完全一致させる。

## 4. 構文を保護して生成する

raw文字列の全置換を禁止する。Markdownまたは使用中のMarkupをToken化し、次の領域を保護する。

- fenced codeとinline code
- Markdown Link destinationと画像
- raw URL、HTML tagとattribute
- 既に正しいEntryへ向くLink

Prose領域だけをaliasの長い順に、Unicodeの単語境界を考慮してLink化する。再生成時は既に正しいLinkをbyte-equivalentに保持し、二重角括弧、入れ子Link、fragmentの重複を作らない。初回生成と二回目生成が同一になる再入可能性Fixtureを持つ。

## 5. Sourceと生成HTMLを別々に検証する

共通学習契約Gateでは、少なくとも次をBlockerにする。

- `service_entry.aliases`がない、正式名称を含まない、重複・曖昧aliasがある
- 講義またはAssessment pageのProseにaliasが裸文字で残る
- Service表記が外部Documentation、Services Landing、Family先頭、別Entry、存在しないAnchorへLinkされる
- StemはLink済みだがOptionまたは解説の同じaliasが未Linkである
- 長いalias内部を短いaliasとして二重に数える
- inline／fenced code、URL、HTML属性を未Linkとして誤検出する、またはLink挿入で変更する

共通Commandには次を追加する。

```bash
--require-service-mention-links
```

Strict build後のHTML Gateでは、全講義・問題Pageについて次を検査する。

- learner-visibleな各alias出現が一つの`a`要素内にある
- `href`をPage基準で解決すると宣言されたService Entry pathとAnchorになる
- Link先HTMLに固定Anchorが一つだけ存在する
- Link textが空でなく、対象aliasを含む
- 壊れた内部Link、入れ子Anchor、重複IDがない

代表ServiceだけのClick確認を全件静的検査の代替にしない。公開が範囲なら、DesktopとMobileで講義から一件、問題Stemから一件、Optionまたは解説から一件を実際にClickし、該当Entry見出しへ移動することを確認する。

## 6. Negative fixture

最低限、次を保持する。

- `EKS`が講義Proseに裸で残る
- 問題Stemの`EKS`だけLinkし、Optionの`EKS`を裸で残す
- 誤答解説の`EKS`だけ裸で残す
- `[EKS](../services/index.md)`のようにLandingだけへLinkする
- `[EKS](https://docs.example/eks)`のように外部DocumentationだけへLinkする
- `Amazon EKS`を`Amazon [EKS](...)`として短いaliasだけ処理し、正規の最長一致を満たさない
- 二つのEntryへ同じ`EKS` aliasを登録する
- fenced code、inline code、URL内の`EKS`をLink対象として失敗させる
- 正しいLinkへ生成処理を二回適用するとMarkdownが変わる

成功Fixtureでは、正式名称、短縮名、Stem、全Option、正答・誤答解説、講義、Code保護、相対Path解決を一つの小Courseで通す。
