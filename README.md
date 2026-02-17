# A2A トレジャーハント

## 概要

このプロジェクトは、AIエージェント間の連携を体験するための「A2A（Agent-to-Agent）トレジャーハント」ワークショップのリポジトリです。
参加者は「探検家Agent」を開発し、運営側が提供する複数のAgent（司令部、鍵守、宝箱）とA2Aプロトコルで通信しながら、宝探しに挑戦します。

このワークショップでは、Google の Agent Development Kit (ADK) と Gemini を使用して、自律的に対話し連携する AI エージェント群を構築します。

**所要時間**: 約50分

**前提条件**: Cloud Billing アカウント

> ハンズオンの詳細な手順は [handson.md](handson.md) を参照してください。

## セットアップ

### 1. リポジトリのクローンとPython環境の構築

本プロジェクトでは、Pythonのパッケージ管理ツールとして `uv` を使用します。

```bash
git clone jaguer-sandbox/jaguer-cloudnative-a2a-handson
```

```bash
# 仮想環境の作成
uv venv

# 仮想環境のアクティベート
source .venv/bin/activate

# 依存関係のインストール
uv sync
```

### 2. 環境変数の設定

Vertex AI を利用するための `.env` ファイルを作成します。

```bash
echo "GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)" > .env
echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env
echo "GOOGLE_GENAI_USE_VERTEXAI=true" >> .env
```

運営から提供される各 Agent の Agent Card URL も `.env` に追加してください。

```bash
echo "COMMAND_AGENT_AGENT_CARD=xxxxxx" >> .env
echo "KEY_MASTER_AGENT_AGENT_CARD=xxxxxx" >> .env
echo "TREASURE_CHEST_AGENT_AGENT_CARD=xxxxxx" >> .env
```

### 3. 認証と API の有効化

Google Cloud の Application Default Credentials (ADC) を設定します。

```bash
gcloud auth application-default login
```

必要な Google Cloud API を有効化します。

```bash
gcloud services enable \
  cloudresourcemanager.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  cloudtrace.googleapis.com \
  --project=$(gcloud config get-value project)
```

## プロジェクト構成

```
.
├── agents/                  # 運営側が提供するエージェント群
│   ├── command_center/      # 司令部Agent（ミッションを出す）
│   ├── key_master/          # 鍵守Agent（クイズを出す）
│   └── treasure_chest/      # 宝箱Agent（宝を渡す）
├── test-agents/
│   └── agent/
│       └── agent.py         # 参加者が開発する探検家Agent
├── handson.md               # ハンズオン手順書
├── Dockerfile               # Cloud Run デプロイ用
├── pyproject.toml           # Python依存関係の定義
└── .env                     # 環境変数（要作成）
```

## 使用方法

### ローカルでの開発

`test-agents/agent/agent.py` に探検家エージェントを実装し、以下のコマンドで Web UI を起動します。

```bash
adk web test-agents
```

開発中はホットリロードを有効にすると便利です。

```bash
adk web --reload_agents --reload test-agents
```

ブラウザでチャット画面が開くので、`start` と入力すると宝探しが始まります。

## デプロイ

開発した探検家エージェントは、Google Cloud Run にデプロイして公開できます。

### adk deploy を使う方法

```bash
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=asia-northeast1 \
  --service_name=explorer-agent \
  --app_name=explorer_agent \
  --port=8080 \
  --with_ui \
  test-agents/agent \
  -- --allow-unauthenticated --env-vars-file .env
```

Cloud Trace を有効にする場合は `--trace_to_cloud` オプションを追加してください。

### gcloud を使う方法

```bash
gcloud run deploy explorer-agent \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --command="adk" \
  --args="web,test-agents,--host,0.0.0.0,--port,8080" \
  --env-vars-file .env
```

デプロイが完了すると、公開 URL が発行されます。

## お片付け

ハンズオン終了後は、以下のコマンドでリソースを削除してください。

```bash
gcloud run services delete explorer-agent --region asia-northeast1

gcloud artifacts docker images delete \
  asia-northeast1-docker.pkg.dev/$(gcloud config get-value project)/cloud-run-source-deploy/explorer-agent \
  --delete-tags
```

