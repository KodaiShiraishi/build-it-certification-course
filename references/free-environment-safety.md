# 無料・Trial環境の安全確認基準

資格講座のハンズオンでFree Tier、Free Edition、Trial、Credit、Sandbox、Community環境を案内するときに使う。料金が0円であることだけで安全・無制限・機密利用可能と判断しない。

## 1. 環境の種類を区別する

- 継続的な無料枠、期限付きTrial、金額Credit、教育用Sandbox、機能限定Editionを区別する。
- 開始条件、終了日、Credit失効日、本人確認、支払方法登録の要否を公式情報で確認する。
- 「無料」とだけ書かず、何が、どのRegionで、どの期間、どの上限まで無料かを書く。

## 2. 料金と停止条件を確認する

- 対象Service、Instance／Compute、Storage、Network転送、Request、Model Tokenなど課金単位を確認する。
- 日次・月次Quota、Fair Usage、同時実行数、停止時間、再開条件を確認する。
- 上限超過時に停止するのか、自動的に従量課金へ移るのかを区別する。
- Budget、Alert、Spend Limit、Quota設定が利用できる場合、Lab開始前の手順へ入れる。
- BudgetやAlertは通知であり、課金を必ず停止する上限ではない場合がある。Hard Limitか通知だけかを確認し、残るRiskを説明する。
- Lab終了時に削除・停止すべきResourceと、削除後も残り得るStorage、Snapshot、Log、IP、Endpointを示す。

## 3. 機能差と利用可能性を確認する

- 有料版との機能差、Region差、Preview制限、Model／Runtime一覧、権限、同時実行制限を確認する。
- 公式比較表だけでなく、必要に応じて専用Limitページと実際のAccount画面を確認する。
- UI、Quota、Preview状態は変わり得るため、教材の確認日とLab開始時の再確認場所を示す。
- 利用不能な機能には、設計表、設定比較、Log読解、生成済みOutputなど、同じ学習目標を測れる代替を用意する。

## 4. Data利用条件を確認する

公式の利用規約、Privacy、Data Governance、Product固有FAQで次を確認する。

- 入力、Prompt、Document、Upload、Output、Telemetryが保存されるか
- 保存期間、削除方法、BackupやLogへ残る可能性
- ProviderがModel学習、Service改善、品質評価へ利用できるか
- Opt-outの有無と、Plan・Region・契約による違い
- 人手Review、Subprocessor、第三者Model Providerへの送信があり得るか
- 保存Region、越境移転、Tenant分離、Encryptionの扱い
- 機密保持、Compliance、Data Processing Agreementの適用範囲

Model学習・Service改善へ利用できる場合、または条件を確認できない場合、教材付属の合成Dataまたは完全な架空Dataだけを使う。匿名化だけを根拠に、実顧客Data、個人情報、社内文書、秘密情報、Source Code、Access Key、Token、Passwordを入力しない。

## 5. AccountとCredentialを安全に扱う

- 個人Accountと組織Accountのどちらを使うか、組織Policyに反しないかを確認する。
- 最小権限、短期Credential、MFA、秘密情報の環境変数・Secret Manager利用を優先する。
- 教材、Screenshot、Notebook、Git履歴、LogへCredentialや個人情報を残さない。
- 共有Accountを前提にせず、削除・権限変更が他の利用者へ与える影響を説明する。
- Lab終了時に短期Credential、API Key、Tokenを失効・削除したことを確認する。

## 6. Labを安全に設計する

- 目的、必要Resource、想定時間、想定消費量、成功条件、観察点、停止・削除手順を先に示す。
- 小さいFixture、最小構成、短い実行時間を既定にする。
- 公開Dataを使う場合も、License、個人情報、再配布条件を確認する。
- CostやData条件へ同意できない学習者向けに、実行しない代替演習を用意する。
- 「無料だから実行してよい」とせず、新しい外部Serviceや課金可能Resourceを有効化する前に説明して了承を得る。

## 7. 完了チェック

- [ ] 環境種別、期限、対象機能、Region、Quota、停止・課金条件を確認した
- [ ] 料金、Budget／Alert、後片付け、残存Resourceを説明した
- [ ] Data保存、Model学習・Service改善、人手Review、Region、削除条件を確認した
- [ ] 実Data・機密Data・Credentialを使わず、合成または架空Dataを用意した
- [ ] 公開Dataを使う場合、License、個人情報、再配布条件を確認した
- [ ] 終了後に課金対象が残っていないことと、短期Credentialの失効を確認できる
- [ ] 利用不能・利用拒否時の代替演習がある
- [ ] 公式Sourceと確認日、Lab開始時の再確認場所を記録した
