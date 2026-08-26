# 問題集の再現可能な検証手順

大量問題の品質検査を担当者ごとの感覚にしないため、共通JSONL、既定閾値、意味・独立Review記録、生成再現性検査を使う。既存プロジェクトに同等以上の検査がある場合は、対応表と実行結果を残して代用できる。

## 目次

- [1. 共通JSONLへ書き出す](#1-共通jsonlへ書き出す)
- [2. 件数目標をJSONで保存する](#2-件数目標をjsonで保存する)
- [3. 二段階ReviewをHash付きで記録する](#3-二段階reviewをhash付きで記録する)
- [4. 一次情報を追跡する](#4-一次情報を追跡する)
- [5. 正答の手掛かりを検査する](#5-正答の手掛かりを検査する)
- [6. 類似判定の既定値](#6-類似判定の既定値)
- [7. 共通検査を実行する](#7-共通検査を実行する)
- [8. 生成再現性を検査する](#8-生成再現性を検査する)
- [9. プロジェクト固有形式へ接続する](#9-プロジェクト固有形式へ接続する)

## 1. 共通JSONLへ書き出す

問題生成元を直接置き換えず、検証用に一問一行のUTF-8 JSONLを書き出す。

見やすさのため次は整形している。実際のJSONLでは一問を一行へSerializeする。

```json
{
  "id": "IAM-001",
  "question_set": "practice",
  "assessment_surface": "practice-bank",
  "objective": "IAM.1",
  "difficulty": "medium",
  "cognitive_type": "application",
  "question_type": "single_choice",
  "stem_artifact_types": [],
  "stem_artifact_evidence": [],
  "artifact_types": ["configuration"],
  "stem": "An operator must deny object deletion. Which JSON policy candidate produces an explicit deny for s3:DeleteObject?",
  "options": {
    "A": "{\n  \"Effect\": \"Deny\",\n  \"Action\": \"s3:DeleteObject\"\n}",
    "B": "{\n  \"Effect\": \"Allow\",\n  \"Action\": \"s3:DeleteObject\"\n}"
  },
  "correct": "A",
  "rendered_correct": "A",
  "correct_explanation": "With `\"Effect\": \"Deny\"`, the simulator returns explicitDeny, so A enforces the required deletion boundary.",
  "wrong_explanations": {
    "B": "With `\"Effect\": \"Allow\"`, the simulator returns allowed, so B grants the action instead of denying it."
  },
  "artifact_evidence": [
    {
      "type": "configuration",
      "location": "option:A",
      "content": "{\n  \"Effect\": \"Deny\",\n  \"Action\": \"s3:DeleteObject\"\n}",
      "decision_binding": "Effect Deny implements the required denial."
    },
    {
      "type": "configuration",
      "location": "option:B",
      "content": "{\n  \"Effect\": \"Allow\",\n  \"Action\": \"s3:DeleteObject\"\n}",
      "decision_binding": "Effect Allow grants the operation."
    }
  ],
  "artifact_selection": {
    "task": "select_correct_artifact",
    "requirement": "Deny s3:DeleteObject without granting it.",
    "stem_contract": {
      "artifact_request": "Which JSON policy candidate",
      "scenario": {
        "context": "An operator must deny object deletion",
        "input_or_state": "object deletion",
        "hard_constraints": ["explicit deny"],
        "expected_observation": "produces an explicit deny for s3:DeleteObject"
      },
      "deletion_test": {
        "artifact_candidates_required": true,
        "review_reference": "reviews/artifact-deletion.csv#IAM-001"
      }
    },
    "decision_axes": [
      {
        "name": "policy effect",
        "option_values": {
          "A": "\"Effect\": \"Deny\"",
          "B": "\"Effect\": \"Allow\""
        }
      }
    ],
    "validation": {
      "method": "schema_or_dry_run",
      "reference": "tests/iam_policy_candidates.py::test_delete_effect",
      "validated_correct": ["A"],
      "candidate_results": {
        "A": "simulator returns explicitDeny",
        "B": "simulator returns allowed"
      }
    },
    "explanation_bindings": {
      "A": {
        "artifact_excerpt": "\"Effect\": \"Deny\"",
        "result_excerpt": "returns explicitDeny",
        "explanation_excerpt": "With `\"Effect\": \"Deny\"`, the simulator returns explicitDeny"
      },
      "B": {
        "artifact_excerpt": "\"Effect\": \"Allow\"",
        "result_excerpt": "returns allowed",
        "explanation_excerpt": "With `\"Effect\": \"Allow\"`, the simulator returns allowed"
      }
    }
  },
  "links": ["../iam/#policy-evaluation"],
  "sources": ["https://docs.example.com/iam/policy-evaluation"],
  "source_reviewed_at": "2026-07-18"
}
```

基本必須項目は `id`、`objective`、`difficulty`、`cognitive_type`、`stem`、`options`、`correct`、`correct_explanation`、`wrong_explanations`、`links` とする。`question_set`、`assessment_surface`、`question_type`、`sources`、`source_reviewed_at`、Stem用の `stem_artifact_types`／`stem_artifact_evidence`、Option用の `artifact_types`／`artifact_evidence` は最終検査で必須化する。`question_set`は通常問題を `practice`、模擬問題を `mock` として一問ごとに保持し、`assessment_surface`は `practice-bank`、`practice-exam-a`、`practice-exam-b`等、学習者が独立して開始・採点できる表示単位を保持する。`links`は関連講義または用語、`sources`は正答を支える公式一次情報として分ける。

`stem_artifact_types` はStem内でLearner-visibleな実体Artifactを判断に使うType、`stem_artifact_evidence` は `location: "stem"`、Stem内のExact `content`、その内容が正答判断へ必要な理由を保持する。JSON等の形式名・製品名・作業名だけのProseは空Listにする。`artifact_types` はOption Artifactを [exam-question-fidelity.md](exam-question-fidelity.md) の共通分類で保持する。Option算入問題の `artifact_evidence` は各宣言Typeと全Optionの組合せにつき一件を持ち、`type`、`location`（`option:<key>`のみ）、その候補にExact substringとして存在する `content`、判断に必要な行・Field・Operator・値・関係を示す候補固有の `decision_binding` を保持する。さらに `artifact_selection` に `task: select_correct_artifact`、要求、全Optionを覆うDecision axis、共通Fixture／Schema／Dry run／導出検査のReference、候補別結果、検証済み正答集合、Artifact固有の `stem_contract`、全Optionの `explanation_bindings` を持たせる。Stem Artifactだけの問題はOption側を `artifact_types: []`、`artifact_evidence: []` にし、概念問題は両Locationを空Listにする。

`stem_contract` は、learner-visible StemにExact substringとして存在する `artifact_request` と、`scenario.context`、`scenario.input_or_state`、一件以上の `scenario.hard_constraints`、`scenario.expected_observation` を保持する。`deletion_test.artifact_candidates_required` を `true` にし、候補を隠すと解けないことを確認したReview／Fixtureを `review_reference` へ記録する。ValidatorはHard constraint、期待する観測、Decision axis、候補別結果を数値正規化したSignatureとしてBank全体で比較する。Actor、ID、数値Literal、背景文だけを変えて同じ判断を再利用したArtifact問題を拒否する。

`explanation_bindings` は全Option Keyを一度ずつ持つ。各Optionの `artifact_excerpt` はその候補内に存在しDecision axisの値と一致し、`result_excerpt` は共通検証の当該 `candidate_results` に存在し、`explanation_excerpt` はKeyedされた正答または誤答解説に存在して両Excerptを含む。これにより、候補Artifactだけを更新して旧Text問題の解説を残す変更、正答解説だけ更新して誤答解説を放置する変更、全候補へ同じ汎用結果を付ける変更を失敗させる。Text問題から変換するときは旧本文をBaseline hashまたは監査用非表示Sourceとしてだけ保持し、learner-visible Stem／解説へ連結しない。

`correct`は問題形式に合わせる。

- `single_choice`: Option KeyのString
- `multiple_response`: 正答KeyのList。順序は意味を持たない。`select_count`に正答数を入れるか、選択数を固定しない形式では`selection_instruction`に表示する選択条件を入れる
- `ordering`: 全Keyを一度ずつ並べたList。順序が意味を持つ
- `matching`: 左側Keyから右側ValueへのObject。少なくとも二つの異なる対応先を持たせ、一対一対応が必要な試験ではProject固有検査で全対応先の一意性も確認する

生成済みMarkdown／HTMLから正答を読み取れる場合、`rendered_correct`も書き出し、生成元の`correct`と照合する。既存ProjectでField名が異なる場合は、読み取り専用Adapterで共通形式へ変換する。

## 2. 件数目標をJSONで保存する

新規講座、または通常問題集の大幅増量・全面整備で、ユーザーが完成総数を明示していない場合、`total` は次の標準完成件数と一致させる。限定修正、レビュー、公開だけの依頼ではこのPolicyを新たな増量の根拠にしない。

| `credential_level` | `total` |
|---|---:|
| `associate-equivalent` | 500 |
| `professional-equivalent` | 1000 |

`credential_level` は `associate-equivalent`、`professional-equivalent`、`not-applicable` のいずれかとし、ベンダーの公式資格体系、想定経験、試験対象から判断した根拠を別の追跡可能な記録へ残す。`not-applicable` でユーザー指定もない場合は、問題作成前に完成総数を確認する。

通常問題集の `work_mode` は新規を `new`、一問以上ある既存通常問題集の変更を `existing` とする。`existing` では正の `baseline_total` とBaseline Hash比較を必須にし、`new` ではBaselineを省略する。ユーザーが全面再作成を明示した場合もCount policy上は `existing` としてBaselineを保持するが、旧Corpusの非流用、Authoring前のSource profile、新ID namespaceまたは全面置換Manifestを別Gateで証明する。これにより、既存通常問題集の全面再作成やユーザー指定件数でも、着手前問題の全置換を検査なしで通さない。模擬試験も全面再作成の対象なら同じ非流用・Source-profile Gateを適用する。

`count_mode` は次のいずれかとする。

| `count_mode` | 用途 | 必須値 |
|---|---|---|
| `standard` | ユーザー指定がない Associate／Professional 相当 | レベル別の `total` |
| `user-specified-total` | ユーザーが完成総数を指定 | `requested_total` |
| `user-specified-increment` | ユーザーが追加数を指定 | `baseline_total`、`requested_increment` |
| `retained-overage` | 既存有効問題が標準件数を超え、削除しない | 標準超過の `baseline_total` |
| `scope-exempt-existing` | 限定修正、Review、公開だけで既存件数を維持 | 変更前と同じ `baseline_total` |

`credential_level_source` にレベル判定を支える公式HTTPS URL、`credential_level_reviewed_at` に確認日を保存する。通常問題集の最終検査では、根拠URLのHostを `--official-source-host` で一件以上許可する。`question_set` は通常問題集を `practice`、模擬試験を `mock` とする。章末など複数箇所へ同じ通常問題を表示する場合も、一意な正規問題IDを一度だけJSONLへ出力する。Validatorは各問の `question_set` と目標ファイルを照合するため、通常問題と模擬問題を同じJSONLへ混ぜない。模擬試験は別の目標ファイルで管理し、通常問題集の `total` へ加算しない。

既存問題を変更する前に、同梱Validatorの `--hash-report baseline-hashes.csv` で問題ID、内容Hash、着手前件数を保存する。変更後は `--baseline-hash-report baseline-hashes.csv` で比較する。既存IDの変更または削除がある場合だけ、次のCSVを `--baseline-change-log` へ渡す。理由のない変更、未記録の削除、現在の差分と一致しない古い記録はエラーにする。削除理由にはユーザーの明示的な削除依頼を記録する。

```csv
id,action,reason,approval_ref
IAM-002,changed,曖昧な条件を修正して意味Reviewを再実施,
IAM-009,removed,ユーザーが重複問題の削除を明示,user-message-2026-07-24
```

次は Professional 相当の標準件数を検査する自己完結した例である。

```json
{
  "question_set": "practice",
  "work_mode": "new",
  "credential_level": "professional-equivalent",
  "credential_level_source": "https://docs.example.com/credentials/levels",
  "credential_level_reviewed_at": "2026-07-24",
  "count_mode": "standard",
  "total": 1000,
  "objectives": {
    "OBJ.1": 250,
    "OBJ.2": 250,
    "OBJ.3": 250,
    "OBJ.4": 250
  },
  "allowed_question_types": ["single_choice", "multiple_response", "ordering", "matching"],
  "question_types": {
    "single_choice": 720,
    "multiple_response": 200,
    "ordering": 40,
    "matching": 40
  },
  "difficulties": {
    "knowledge_recall": 250,
    "single_concept_application": 500,
    "multi_concept_integration": 250
  },
  "cognitive_types": {
    "comparison": 250,
    "application": 300,
    "diagnosis": 250,
    "design_decision": 200
  },
  "question_source_profile": {
    "analyzed_before_authoring": true,
    "sample_size": 20,
    "observed_question_type_counts": {
      "single_choice": 16,
      "multiple_response": 4
    },
    "observed_primary_decision_pattern_counts": {
      "service_or_feature_selection": 8,
      "configuration_or_permission_change": 5,
      "failure_diagnosis": 4,
      "cost_performance_tradeoff": 3
    },
    "scope_analysis": {
      "official_weight_status": "published",
      "official_domain_weights": {
        "D1": 0.34,
        "D2": 0.26,
        "D3": 0.22,
        "D4": 0.18
      },
      "official_objectives": ["D1", "D2", "D3", "D4"],
      "observed_primary_objective_counts": {
        "D1": 7,
        "D2": 5,
        "D3": 4,
        "D4": 0,
        "unmapped": 4
      },
      "observed_primary_content_family_counts": {
        "ingestion_and_transformation": 7,
        "data_store_management": 5,
        "operations_and_monitoring": 4,
        "security_and_governance": 4
      },
      "observed_service_feature_counts": {
        "object storage": 6,
        "managed ETL": 5,
        "stream processing": 4
      },
      "observed_integration_pattern_counts": {
        "source_to_ingestion_to_lake": 5,
        "event_to_stream_processor": 3
      },
      "observed_lifecycle_stage_counts": {
        "ingest": 7,
        "transform": 5,
        "operate": 4,
        "secure": 4
      },
      "observed_constraint_counts": {
        "least_operational_overhead": 6,
        "cost_optimization": 4,
        "least_privilege": 3
      },
      "scope_gaps": [
        "The small source does not cover every official objective."
      ],
      "authoring_scope_decisions": [
        "Use official domain weights for final coverage and source observations for scenario depth."
      ],
      "scope_selection_patterns": [
        {
          "id": "constraint_to_managed_boundary",
          "description": "The source turns an operational constraint into a managed-service boundary decision.",
          "observed_count": 6,
          "question_transformation": "Compare supported service behavior under the stated operational constraint."
        }
      ],
      "official_scope_extrapolations": [
        {
          "objective": "D4",
          "primary_source_topics": ["least-privilege access and data protection"],
          "primary_source_urls": ["https://vendor.example/security-guide"],
          "inferred_question_patterns": [
            "Select the least-privilege control that preserves the required data flow."
          ],
          "basis_pattern_ids": ["constraint_to_managed_boundary"],
          "confidence": "medium",
          "reasoning": "The official objective contains the same constraint-to-boundary decision shape.",
          "authoring_status": "adopted"
        }
      ]
    },
    "artifact_location_counts": {
      "stem_artifact_questions": 4,
      "option_artifact_questions": 6,
      "both_stem_and_option_artifact_questions": 2,
      "neither_artifact_questions": 12
    },
    "artifact_location_rates": {
      "stem_artifact_rate": 0.2,
      "option_artifact_rate": 0.3,
      "both_stem_and_option_artifact_rate": 0.1,
      "neither_artifact_rate": 0.6
    },
    "stem_artifact_by_type": {
      "logs_metrics": 3,
      "configuration": 1
    },
    "option_artifact_by_type": {
      "configuration": 4,
      "command": 2
    },
    "classification_rule": {
      "mention_only_is_artifact": false,
      "requires_learner_visible_material_and_decision_dependency": true
    },
    "authoring_targets": {
      "practice-bank": {
        "total": 1000,
        "minimum_questions_with_stem_artifacts": 200,
        "minimum_questions_with_option_artifacts": 300,
        "minimum_questions_with_both_artifacts": 100
      }
    }
  },
  "artifact_policy": {
    "calibration_evidence": [
      {
        "kind": "exam_guide",
        "status": "current",
        "url": "https://docs.example.com/credentials/exam-guide",
        "reviewed_at": "2026-07-24"
      },
      {
        "kind": "official_sample",
        "status": "current",
        "url": "https://docs.example.com/credentials/sample-questions",
        "reviewed_at": "2026-07-24"
      }
    ],
    "calibration_note": "Official objectives and samples require configuration, command, and diagnostic artifact reasoning.",
    "minimum_questions_with_artifacts": 300,
    "assessment_surfaces": {
      "practice-bank": {
        "total": 1000,
        "minimum_questions_with_artifacts": 300,
        "minimum_by_type": {
          "configuration": 120,
          "command": 80
        }
      }
    },
    "minimum_by_type": {
      "command": 80,
      "configuration": 120
    }
  }
}
```

実際には公式試験目標をすべて列挙する。`total` と実数の不一致に加え、目標数、許可されない問題形式、形式別件数、難易度、思考タイプと実数の不一致はエラーにする。公式ガイドが形式別比率を公開していない場合も、`allowed_question_types`には公式に許可された形式を、`question_types`には教材として設計した件数を入れ、その配分理由を別途記録する。問題本文を作る前に `question_source_profile` へSource母数、問題形式、主判断Pattern、公式Weight／Objective、観察した主Objective・主内容Family、Service／Feature・Integration・Lifecycle・制約、Scope gap、Authoring scope decision、`scope_selection_patterns`、`official_scope_extrapolations`、Stem Artifact、Option Artifact、両方、どちらでもない問題の件数・割合、位置別Type件数、分類規則、Authoring targetを保存する。`--require-question-source-profile` でPrimary分布とSource母数、公式Weight、観察Objectiveと公式範囲、Scope Inventory、出題化Pattern、Source未観察Objectiveの一次情報ベースExtrapolation、2×2と割合の整合を検査する。形式名への言及だけをArtifactへ数えない。

`artifact_policy.calibration_evidence` には現行公式ガイドと公式Sample／Practiceの調査結果を含め、Login必須、未発見、旧版もStatusとして残す。全講座共通の `artifact_target_ratio` 既定値は置かない。公式またはユーザーがOption比率を明示した場合だけ保持し、未指定ならSource profileから決めた `minimum_questions_with_artifacts` を直接使う。`artifact_policy.assessment_surfaces`へ公開Navigation上の全独立問題面と各総数・Option Artifact最低数を宣言し、各問の `assessment_surface` と完全一致させる。Stem側の最低数・割合・種類、両方、どちらでもない件数は `question_source_profile.authoring_targets` とプロジェクト固有のLocation別Gateで検査する。最終検査では `--require-course-count-policy`、`--require-metadata-targets`、`--require-artifact-policy` を使い、Question Set、Assessment Surface、Level、根拠、Count Mode、標準件数またはユーザー指定、問題形式、難易度、思考タイプ、公式Calibration Evidence、各宣言Typeの全Option `artifact_evidence`、有効な `artifact_selection`、`stem_contract`、全Optionの `explanation_bindings`、検証済み正答集合、Surface別明示最低数、明示時だけ比率下限、種類別最低数の省略・不一致を失敗にする。Option側では候補不足、同一候補、結果差なし、再利用Scenario契約、候補と一致しない旧解説、架空Wrapper、100文字超の行、Raw Mermaidを件数へ数えない。

模擬試験の目標ファイルには `question_set: "mock"` と模擬問題だけの `total`、各分布、各Practice／Mock formの `assessment_surfaces`を入れ、各問にも `question_set: "mock"` と対応する `assessment_surface` を持たせる。同じ `--require-course-count-policy --require-artifact-policy` とLocation別Gateで集合分離、件数、各FormのStem／Option別明示最低数、明示時だけ各比率Floorを検査するが、`credential_level`、`count_mode`、500／1,000問の標準は適用しない。別JSONLへ分ける場合も各Formへ個別に全Gateを実行し、一つの模擬試験だけの成功を全Formの成功とみなさない。

## 3. 二段階ReviewをHash付きで記録する

```csv
id,status,reviewer,notes,question_hash
IAM-001,PASS,reviewer-a,,sha256:qbank-v1:9f7c...
IAM-002,FIXED,reviewer-a,曖昧な条件を追加して再確認,sha256:qbank-v1:17a2...
```

意味Reviewと独立Reviewは別CSVにする。`status`は`PASS`または`FIXED`のみ完了とし、全問題IDが各台帳へ一度ずつ存在し、Reviewerが空でなく、`FIXED`には修正内容を必須とする。同じ問題の意味Reviewerと独立Reviewerは異なる値にする。

Review stamp用CLIは、実際に確認したReviewer identityと範囲（全件、Domain、ID list、または固定Manifest）を明示入力として受け、台帳へそのまま記録する。一つのBoolean確認や一回の実行から、Domain別の複数Reviewer名をHard-codeして合成してはならない。一人が複数Domainを確認した場合は一つの正直なIdentityで記録し、二人によるReviewを主張するなら各Reviewerが自分の範囲を別々に確定した証拠を残す。Validatorは文字列が異なるだけで独立性を認定せず、Identity、Scope、現在Manifest hash、stamp操作の対応を検査する。

Reviewを固定するContent manifestには、Review後も変化しない教材、Generator、Validator、Source mapを含める。そこへReview台帳、Stamp出力、またはContent hashとStatusを追記するAcceptance ADR自身を含めて循環参照を作らない。ADRを`Proposed`から`Accepted`へ変えただけでReview hashがstaleになる設計は禁止する。ADRやRelease metadataも含めた全体Hashが必要なら、Review用Content manifestとは別のRelease manifestとしてAcceptance後に計算し、二つの用途と境界を明記する。

`question_hash`は、検証用内部Fieldを除く一問分のJSONをKey順でCanonical化し、UTF-8へEncodeしたVersion付きSHA-256（`sha256:qbank-v1:...`）とする。CRLF／LFとUnicode NFCを正規化し、Multiple Responseの正答集合は順不同として扱うが、数値、比較Operator、Orderingの順序は保持する。同梱Validatorの`--hash-report`で現在Hashを出力できる。問題を変更したら旧HashのReviewを完了扱いにせず、再Reviewして台帳を更新する。

## 4. 一次情報を追跡する

仕様依存問題では、`sources`へ正答を直接支える公式URLを一つ以上、`source_reviewed_at`へISO形式の確認日を入れる。試験ガイドだけでは製品挙動を裏付けられない場合、製品ドキュメントも入れる。

- `--require-sources`でSourceと確認日を必須化する。
- `--official-source-host`を繰り返して公式Hostを許可する。
- `--max-source-age-days`で確認日の古さを警告できる。
- 公式ページ同士が矛盾する場合、問題の正答を無理に一意化せず、Source記録と講義側の注記を先に直す。

## 5. 正答の手掛かりを検査する

`--check-answer-cues`で、Single Choice、True／False、Multiple Response全体における正答Optionの長さと、極端語・限定語の出現がCorrect／Incorrectへ偏っていないか警告する。Multiple Responseでは各正答Optionを正答集合のMemberとして数え、誤答Option群との長さ差も比較する。既定語は日本語と英語の「必ず」「絶対」「常に」「のみ」「always」「never」「must」「only」などとし、Project固有語は`--cue-term`で追加する。

警告は機械的にOptionを書き換える合図ではなく、内容を理解せず推測できるかを意味Reviewする起点にする。用語自体が仕様上必要なら、理由を記録したProject固有検査で代用する。

大規模なSingle Choice銀行では、単語ごとの警告がゼロでも検査を終えない。問題文を隠したOption proseのみから正答Option集合を予測する交差検証Classifierまたは同等のBackstopを実行し、ランダムLabel Baselineと比較する。異常に高い場合は、学習器を通す言い換えでなく、予測に貢献したOptionを全件読み、同じObjectiveの近接誤認か、破壊操作や非現実的な値だけで消去できる候補かを記録して修正する。実装した場合は、予測ロジックが実問題に依存せず、LabelをシャッフルしたBaselineで性能が下がることをfixtureで確認する。

手掛かり修正の差分について、Code fenceの内外を問わずCommand-likeなOptionを再列挙する。編集前後でKeyword、API、Field、Enumが変わったら、その変更が意図した技術Mutationである記録を必須にし、記録のない同義語置換をエラーにする。正答の現行構文と正答解説に記録した構文が一致しないfixtureも必須にする。

Validatorの自己検査では、実問題全体のPASS／FAILとは別に、各中間helperの最小正常例と最小失敗例を直接呼ぶ。例えばOption token extractorは、実在するTokenが一つ以上入るSetを返すことを先に断言し、正答の決定Tokenを解説から削ったfixtureがそのBinding errorで失敗することを確認する。関数の返却値が `None`または空Collectionなら、後続検査がたまたま緑でも自己検査を失敗させる。

## 6. 類似判定の既定値

同梱スクリプトは、完全一致判定では比較Operatorと数値を保持し、類似判定ではURLと数値差を吸収した文字5-gramのJaccard係数を使う。これにより、`<`と`>`、`!=`と`==`、Version 1.2と1.3を完全一致と誤判定しない。

- 問題文の高類似: `0.82`以上
- 解説の高類似: `0.90`以上
- 正解解説の短文警告: 空白とMarkdownを除き80文字未満
- 各誤答解説の短文警告: 同50文字未満
- 完全一致の問題文、重複ID、不足フィールド、関連リンク欠落、目標数不一致、未完了レビュー: エラー
- 同一問題内または問題間の同一解説、正答位置の偏り: 警告。最終検査の `--fail-on-warnings` で未解決なら失敗

Option順を変更するGeneratorでは、表示後の正答・解説対応に加え、Label参照の置換境界を回帰テストする。少なくとも `Option A` や `A and C` のような明示的Labelは新しいLabelへ追従し、英語の `A sample` と区分名の `Project A` は変更されないことを確認する。

閾値は言語や問題形式に合わせて変更できるが、変更値と理由をリポジトリへ記録する。高類似でも正当な別問題なら、allowlist CSVへ比較対象のLabelと理由を記録する。

```csv
kind,id1,label1,id2,label2,reason
stem,IAM-041,stem,IAM-042,stem,同じ構成で権限境界の有無だけを比較する対問題
explanation,IAM-051,correct,IAM-052,wrong-B,公式定義を対比するため同じ一文を引用せず要約して共有
```

`stem`行は旧`kind,id1,id2,reason`形式も受理し、空Labelを`stem`として扱う。`explanation`行は`correct`または`wrong-<Option Key>`の`label1`と`label2`を必須とする。設問IDだけの広い例外で、その二問間の別の重複説明まで隠してはならない。

未置換の`TODO`、`TBD`、`FIXME`、`PLACEHOLDER`などは、問題文、選択肢、解説、選択指示、Matching対応先、Rendered Answerを含む学習者表示文字列で既定エラーにする。Project固有のMarkerは`--placeholder-pattern`を繰り返して追加する。「要件を満たさない」「リスクが増える」などの禁止句だけを接続語で連結・反復した説明も既定でエラーにし、追加の禁止句は`--forbidden-explanation`で指定する。具体的な原因、挙動、制約を続けた説明は、禁止句の部分一致だけでは失敗にしない。

## 7. 共通検査を実行する

```text
python <skill-dir>/scripts/validate_question_bank.py questions.jsonl \
  --targets targets.json \
  --require-course-count-policy \
  --require-metadata-targets \
  --require-question-source-profile \
  --require-artifact-policy \
  --review-ledger semantic-review.csv \
  --independent-review-ledger independent-review.csv \
  --require-independent-review \
  --require-review-hashes \
  --require-sources \
  --official-source-host docs.example.com \
  --check-answer-cues \
  --allowlist similarity-allowlist.csv \
  --fail-on-warnings
```

Windows PowerShellでは継続記号を使わず、一行で実行してよい。最終検査では`--fail-on-warnings`を付ける。警告をAllowlistへ移す前に意味Reviewを行い、理由のない抑制を禁止する。複数Providerを扱う場合は`--official-source-host`を繰り返す。

既存通常問題集では `work_mode: "existing"` と正の `baseline_total` を保存し、上記コマンドへ `--require-baseline-protection --baseline-hash-report baseline-hashes.csv` を加える。変更・削除した既存問題がある場合は、さらに `--baseline-change-log baseline-changes.csv` を加える。限定修正、Review、公開だけなら `count_mode: "scope-exempt-existing"` として着手前件数を維持する。新規通常問題集では `work_mode: "new"` とし、Baseline引数を使わない。既存模擬試験では目標ファイルに `work_mode` を入れず、CLIの `--require-baseline-protection` とBaseline引数だけで既存問題を保護する。

## 8. 生成再現性を検査する

生成済み問題やIndexがある場合、生成前の対象File集合と正規化本文をSnapshotし、Generator実行後と比較する。

```text
python <skill-dir>/scripts/check_generated_reproducibility.py --root . --include "docs/questions/**/*.md" --include "docs/questions/index.md" -- python scripts/generate_questions.py
```

同梱ScriptはUTF-8 BOMとCRLF／LFを正規化し、PathをLocale非依存順で比較する。追加・削除・本文変更を失敗にする。BOMや改行だけの差は同一とみなすが、末尾空白や本文順序の差は隠さない。

Windowsで成功しても、公開CIがLinuxならCI上でも同じ検査を実行する。Generator内のSortはCulture依存の既定順へ任せず、期待順または明示的Keyを使う。

## 9. プロジェクト固有形式へ接続する

既存のYAML、CSV、PowerShellデータ、Markdownなどから共通JSONLへ変換する小さな読み取り専用アダプターを作る。生成元が既に同等の項目を持つなら二重管理せず、検査時だけ書き出す。Navigationまたは公開Page単位から `assessment_surface` を導出し、通常問題と各Practice／Mock formを別々に集計できるようにする。`format` やFamilyから位置別Artifact Type／Evidenceを合成してはならない。Learner-visibleなStemと全Optionを別々に読み、実体Artifactと判断依存をExact evidenceへ変換する。Option Artifactへ算入する問では全Optionから実物断片と決定差分を抽出し、生成Markdown／HTMLにも同じ断片が残り、候補検証ReferenceがCIで実行されることを照合する。Stemにしか実物がない問題はStem Artifactへだけ算入する。全Optionを覆えない、共通検証がない、または自然文を架空Schemaへ包んだだけの場合はOption側を空Listにするか、問題Sourceを正しいArtifact-native候補選択問題へ修正する。形式名への言及だけならStem側も空Listにする。

既存検査で代用する場合、少なくとも次の対応を記録する。

- 必須項目と選択肢別解説の完全性
- Question Setと通常問題／模擬問題の分離
- 資格Levelと公式根拠、Count Mode、標準件数またはユーザー指定、実数の一致
- 問題形式、正答集合・順序・対応関係、Rendered Answerの一致
- 公式Source、確認日、許可Host
- Authoring前の公式ガイドと公式Sample／Practiceの調査状態、Source母数、Stem Artifact、Option Artifact、両方、どちらでもない問題の件数・割合、位置別Type件数、言及だけの非算入、および各Surfaceの軸別最低数。明示したTarget ratioだけFloorとして適用し、Option側は全候補Evidence・決定差分・候補検証に合格したArtifact-native選択問題だけを数える
- Artifact固有のStem契約、Scenario contractの一意性、全Optionの候補差分／検証結果／正誤解説Binding、候補変更後の旧解説が0件であること
- Artifact Sourceの100文字行長、生成HTMLのMermaid container、実DOMのSVG描画と390px横Overflow
- 重複ID、問題文、解説
- 高類似閾値と判定方法
- 目標別件数
- 正答位置・長さ・語彙による手掛かり
- 全問意味Reviewと問題Hashの一致
- 既存問題のBaseline Hashと、変更・削除理由の完全性
- 別台帳・別Reviewerによる独立Review後の指摘状況
- Windows／Linuxでの生成再現性

検査出力、使用した閾値、対象件数、エラー・警告数を最終報告に含める。
