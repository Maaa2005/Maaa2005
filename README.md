# 中村 奨志 — Masashi Nakamura

**AI × プロダクト開発エンジニア（2028年新卒予定）**

オンデバイスML・LLM／RAG・AIエージェントと、iOSネイティブ開発を、
企画から App Store リリース・運用まで通しで手がけます。
「機密を守りながら自動化する」「ユーザーの負を技術で消す」ことに関心があります。

---

## Featured Projects

### Stellise — AIエージェント型アラームアプリ（iOS / SwiftUI）
App Store で公開中。「起きられない」だけでなく「起きた後に何をすべきか迷う」朝の認知的負荷そのものを下げる AI アラーム。
コアメンバー2名のチーム開発（リーダー兼エンジニア）として、企画・設計・iOS 実装・バックエンド・App Store リリース・運用まで完遂しました。

- **オンデバイスAI** — Google YAMNet を TensorFlow Lite で端末内に組み込み、いびき等の音イベントをオフライン推論で検知。CoreMotion の体動と組み合わせ、睡眠の浅さ・妨げを示す独自スコアを端末内で算出（健康データを外に出さないプライバシー設計）。
- **iOSの制約突破** — バックグラウンド制限（最大30秒）を UNUserNotificationCenter の連続通知ロジックで突破し、「絶対に起こす UX」と「止めた後の快適さ」を両立。
- **LLMの暴走防止** — 天気・経路・予定を関数（API）で取得して LLM（Gemini）に渡し、構造化出力＋ガードレールで毎朝のルーティンを生成。プロンプト構造化と重み付けの見直しでハルシネーションを約30%低減。
- 技術: Swift / SwiftUI / TensorFlow Lite / Python(Flask) / Gemini API
- → **[リポジトリ: Stellise](https://github.com/Maaa2005/Stellise)** ・ [App Store](https://apps.apple.com/jp/app/id6760934295)

### 社内完結型AIエージェント（業務DX・開発中 / 非公開）
外部 API に依存せず機密を守る「社内完結型」AI エージェント。OSS LLM（Qwen 等）をローカル稼働させ、
自身は **RAG アーキテクチャの設計・構築を主担当**（検索精度・誤検索を防ぐガードレール）。
「機密保持」と「自動化」のトレードオフを技術で壊すことを狙っています。
- → **[設計ドキュメント: local-rag-architecture](https://github.com/Maaa2005/local-rag-architecture)**（コードは非公開のため、設計判断を公開）

### ENISHI — 本人代理AIエージェントの通信基盤（macOS / 開発中）
「自分の代理AIエージェント同士が、人間の代わりに日程調整などを構造化データで交渉する」ためのプラットフォーム。
名前は縁（人と人のつながり）と阿吽（言葉なしに呼吸を合わせる二者）から。エージェント間プロトコルは **AUN Protocol** と呼んでいます。
Tauri 2 + React のデスクトップアプリと、127.0.0.1限定・Bearer認証必須の Local Core（FastAPI）で構成。
選択的開示（相手に見せる情報を最小化）と人間承認ゲートを核に、プロトコルの設計から実装まで個人開発しています。
- 技術: TypeScript / React / Tauri 2 / Python(FastAPI)
- → **[リポジトリ: ENISHI](https://github.com/Maaa2005/ENISHI)**

### 服選び支援Webアプリ（学内チーム開発中・仕様検討段階）
複数人の学内チームで開発中の Web アプリ。Next.js / Supabase。**フロントエンド設計とポイント管理を担当**。
ブランチ運用・PR / コードレビュー・フィードバック反映の反復開発を実践しています。

---

## Tech Stack

| 領域 | 使うもの |
|---|---|
| 言語 | Swift / Python / JavaScript / TypeScript / C |
| フロントエンド | SwiftUI / React / Next.js |
| バックエンド | Node.js / Flask / Firebase / Supabase |
| AI・ML | TensorFlow / TensorFlow Lite / RAG / LLM（function calling・構造化出力・ガードレール）/ NumPy / Pandas |
| インフラ・その他 | Google Cloud / Git・GitHub |

---

## いま掘っていること

- **AIエージェントの制御・オーケストレーション** — 複数エージェントを、トークン効率（コスト・レイテンシ）と出力品質のトレードオフを設計して両立させる。モデルルーティング（安価なワーカー＋上位のオーケストレータ）／プロンプトキャッシュ／evals・LLM-as-judge・ガードレール／observability。
- **コンテキスト圧縮と外部メモリ** — トークン効率と回答精度の両立、RAG／外部メモリ設計。
- **自作のAI開発環境** — 会話・作業ログを自動で要約・蒸留して恒久メモリに蓄積し、起動時に必要な記憶だけ読み込むパイプライン（複数 PC で Git 同期・hook で保存／読込を自動化）。

---

## 資格・受賞

- **Google AI Professional Certificate**（2026）
- **JDLA Deep Learning for GENERAL（G検定）**（2026）
- **Tongali ビジネスプランコンテスト 準優秀賞**（東海地区大学コンソーシアム主催, 2025）

---

## Contact

- Email: mtk.zin5ri@gmail.com
