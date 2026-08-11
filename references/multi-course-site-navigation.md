# 複数資格講座サイトのナビゲーション

2つ以上の資格講座を同じサイトで扱う場合、または既存サイトのヘッダー、タブ、サイドバーを変更する場合に使う。フレームワーク固有の実装より、情報階層、アクセシビリティ、生成物検証を優先する。

## 情報階層を分ける

1. 講座切替は、左上などの一貫した場所に置くコンパクトなプルダウンにする。
2. ヘッダーのタブは、現在の講座内カテゴリだけを表示する。
3. 左サイドバーは、現在カテゴリ内のページだけを表示する。
4. 講座一覧と404ページでは、講座内カテゴリを選択中として表示しない。

講座をURL接頭辞だけで判定しない。同じ講座のページが複数のパスへ分かれるサイトでは、ナビゲーションツリーまたはルーターのactive状態から現在講座とカテゴリを求める。

## Serviceカテゴリを上部の第一級学習経路にする

新規講座、講義の大幅更新、全面品質改修では、各講座のHeader tabまたは同等の上部Course navigationに、確定した教材言語の独立したServiceカテゴリを置く。ServiceカテゴリはDomain／Task講義、通常問題、模擬問題より前へ配置する。Introduction、Foundation、用語集は先行できるが、Service知識を使う教材より後ろへ置かない。

- ServiceカテゴリのLinkは包括的Service curriculumのLanding pageへ向ける。
- Landing pageから全固有Service／主要機能の正式名称を検索・一覧でき、各Entryの固定Anchorへ直接移動できるようにする。責務Family別Pageを中間の整理単位にしても、Landing → Family page → 手動探索を強制しない。各講義から関連Domain／Task講義へ戻れるようにする。
- 講義と問題の本文に現れる正式名称・正規aliasも、同じ固有Entryの固定Anchorへ直接Linkする。Stem、全Option、正答・誤答解説を含め、関連Service一覧やLanding Linkだけで本文中の裸aliasを代用しない。
- Serviceカテゴリを親カテゴリの下へ隠さず、他の第一級カテゴリと同じ視認性、操作領域、active表示を持たせる。
- 一枚のhandbookやService名一覧だけをカテゴリ内容にせず、問題で使う全Serviceを11 Dimensionで教える正規Page Inventoryと固有Service-entry Inventoryを持たせる。Family単位の11 Dimensionだけで子Serviceを教えたことにしない。
- 正規Navigation InventoryにCategory ID、Kind、Label、Sequence、Landing path、Page path、Parentを保持し、学習契約Manifestと完全一致させる。
- Source設定だけで完了せず、全生成HTMLでカテゴリ名、順序、Landing link、active状態、カテゴリ配下のSidebar範囲を検査する。

## 壊れにくく実装する

- 使用中のテーマと固定バージョンのテンプレートを確認してから、必要なpartialだけを上書きする。
- 講座切替は通常のリンクを含むnativeな`details`と`summary`などを基本にし、JavaScriptがなくても移動できるようにする。
- カテゴリリンクは、そのカテゴリの最初の意味あるページへ向ける。
- 狭い画面でもカテゴリタブを消さず、横スクロールできるようにする。直接URLを開いた場合もactiveタブを表示範囲へ移す。
- Escape、外側クリック、検索開始でプルダウンを閉じ、Escape時はsummaryへフォーカスを戻す。
- `aria-current`、具体的な`aria-label`、44〜48px相当の操作領域、明確なfocus表示、色以外のactive表示を用意する。
- forced colorsとreduced motionを考慮する。

## 全生成ページを検証する

期待値は生成HTMLから逆算せず、ナビゲーション設定や独立した対応表から用意する。代表ページだけの検査で完了にしない。

全ページで次を検査する。

- 講座切替が1つあり、講座名とリンク先の集合が期待値と一致する。
- 現在講座だけがcurrentになり、講座外ページと404では誤ったcurrentがない。
- 現在講座のカテゴリ名、順序、件数が一致し、activeカテゴリが1つだけある。
- Serviceカテゴリが上部の第一級カテゴリとして一つだけ存在し、Domain／Task、通常問題、模擬問題より前にあり、正しいCurriculum landing pageへLinkしている。
- Service landingの全正式名称Linkが宣言されたPageと固定Anchorへ解決し、生成HTMLに同じ見出しとEntry本文が存在する。
- 全講義・問題Pageのlearner-visible Service aliasが一つのLink内にあり、その`href`が宣言されたEntry Pageと固定Anchorへ解決する。Code、URL、HTML属性は対象外とし、Landing止まり、外部Documentation、別Entry、裸aliasを失敗させる。
- サイドバーの講座・カテゴリ文脈がactive状態と一致する。
- サイドバー内の各リンクが、独立して定義した現在カテゴリの許可範囲内にある。
- 講座一覧と404では講座内タブを出さず、サイドバーを講座一覧など必要最小限にする。
- CSSとJavaScriptが全ページから参照され、内部リンク、アンカー、重複IDに問題がない。

## 全講座をCIへ含める

複数講座を一つのSiteへ統合しても、CIが最初の講座だけを検査したままにならないようにする。期待する講座一覧はNavigation設定または独立したManifestから読み、CI設定と照合する。

- 各講座の原稿、問題生成元、生成再現性、問題Bank、意味Review、独立Reviewを検査する。
- 講座固有Validatorと共通Validatorのどちらを使ったか、同等性と閾値を記録する。
- 全講座を含む厳格Build後に、講座別の静的HTML検査を実行する。
- 新しい講座をManifestへ追加したのにCI Stepがない場合、失敗扱いにする。
- 一講座の成功をSite全体の成功とせず、講座別件数と検査結果を出力する。

## サブパス公開を検証する

GitHub Pagesのproject siteなど、ドメイン直下ではない場所へ公開する場合は次を行う。

- `site_url`などに実際の公開ベースパスを設定する。
- 404ページ、アセット、絶対内部リンクがベースパスを含むことを確認する。
- ローカル検証器は設定済みベースパスだけを取り除いて生成先へ解決し、ベースパスを欠く絶対内部リンクを失敗扱いにする。
- 公開後は、トップ、各講座の深いページ、404、CSS、JavaScriptを直接HTTP取得して反映を確認する。
- 内容変更を公開した場合、各講座から少なくとも一つ、今回追加・修正した固有の本文MarkerをCache回避付きURLで確認する。

## ブラウザを使えない場合

ブラウザを使わず、厳格ビルド、生成HTML・CSS・JavaScript検査、JavaScript構文検査、直接HTTP確認を行う。レスポンシブ配置、クリック、タップ、検索、プルダウンの実操作は未検証として報告する。

ナビゲーションだけを変更した場合も、講義や問題数、ID、生成再現性など既存の講座品質検査を回し、意図しない回帰がないことを確認する。
