# A2Aエージェント連携ハンズオン

## 始めましょう!

このハンズオンでは A2A を使った AI Agent 開発を行ってみます

**所要時間**: 約50分

**前提条件**: Cloud Billing アカウント

次のステップに進むには、[**続行**] ボタンをクリックします。

## 環境構築：Google Cloud Shell と uv のセットアップ

ハンズオンを始める前に、まずAI Agentを作成するための環境のセットアップを行いましょう。

今回のハンズオン用のレポジトリを配置しています。

```bash
git clone jaguer-sandbox/jaguer-cloudnative-a2a-handson
teachme handson.md
```

次に以下の手順で`uv`を使用してPython環境をセットアップします。

```bash
uv venv
source .venv/bin/activate
uv sync
```

これらのコマンドを実行することで、ハンズオンに必要なすべての依存関係がインストールされます。

依存するライブラリは、pyproject.toml に記載されています。

次に AI Agent をローカルで確認するための Vertex AI の環境変数を用意します。

.env ファイルを以下のように作成してください。

```bash
echo "GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)" > .env
echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env
echo "GOOGLE_GENAI_USE_VERTEXAI=true" >> .env
```

.env ファイルに GOOGLE_CLOUD_PROJECT の値が入っていない場合はおっしゃってください！

次に Google Cloud の ADC の設定をします。こちらを元に AI Agent が認証情報を持って動く形になります。以下のコマンドを実行してください。

```bash
gcloud auth application-default login
```

認証後、以下のように聞かれた場合は、cloudresourcemanager の API を有効化する必要があるため `y` を押して、次に進んでください。

```
These credentials will be used by any library that requests Application Default Credentials (ADC).
API [cloudresourcemanager.googleapis.com] not enabled on project [xxxxxxx]. Would you like to enable and retry (this will take
 a few minutes)? (y/N)?  
```

最後に利用する Google Cloud のコンポーネントを有効にします。

今回は Cloud Run と Artifact Registry、Vertex AI に対する権限を有効にします。

```bash
gcloud services enable cloudresourcemanager.googleapis.com run.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com cloudbuild.googleapis.com cloudtrace.googleapis.com --project=$(gcloud config get-value project)
```

## はじめに

それでは、皆さん、こんにちは！本日はA2Aエージェント連携ハンズオンへようこそ。このハンズオンでは、皆さんに『探検家Agent』を開発していただき、私たちが用意した複数のエージェントと連携しながら、宝探しゲームに挑戦していただきます。

エージェント同士が自律的に会話（通信）して目的を達成する、A2Aの世界を体験してみましょう。皆さんが作成するのは `test-agents/agent/agent.py` です。ゴールは、司令部からのミッションを受け、他のエージェントと協力して宝を見つけ出し、司令部に報告することです。

---

## ステップ1：ローカルエージェントの作成と起動

**目的：** 最もシンプルなエージェントを作成し、ローカルで動かしてみます。

### 内容

最初のステップとして、皆さんの分身となる『探検家Agent』の骨組みを作成しましょう。

`test-agents/agent/agent.py` を作成してください。
ADKでは、エージェントのコードは **`{エージェントをまとめたディレクトリ}/{エージェント名}/agent.py`** という階層構造で配置します。今回の場合、`test-agents` というディレクトリの中に、`agent` という名前のエージェント用ディレクトリがあり、その中に `agent.py` がある、という形です。

なぜこの構成にするかというと、後ほど使う `adk web` ツールが、このディレクトリ名を元にエージェントを識別したり、関連する設定（Agent Cardなど）をエージェントごとに正しく管理したりするためです。このルールを守ることで、複数のエージェントをスムーズに切り替えて開発できるようになります。

では、まずは一旦、何も考えず、AI Agent を作成してみます。

次に、以下のコマンドで Cloud Shell をエディタモードにしてください。

```bash
cloudshell edit .
```

次に以下のコマンドで Agent のソースコードファイルを作成します

```bash
mkdir test-agents/agent/
touch test-agents/agent/agent.py
```

`test-agents/agent/` に `agent.py` が作成されたと思います。以下のコードを貼り付けてください。

```python:test-agents/agent/agent.py
from google.adk import Agent

root_agent = Agent(
    name="explorer_agent",
    model="gemini-2.5-flash",
    description="宝探しをする探検家エージェントです",
    instruction="あなたは探検家です。挨拶をしてください。",
)
```

ADKでは、`Agent` クラスを作るだけで準備完了です。では、このエージェントを動かしてみましょう。ターミナルで以下のコマンドを実行してください。

```bash
adk web test-agents
```

コマンドを実行するとローカルサーバーが立ち上がります。

Cloud Shell 上に表示された URL をクリックすると、ブラウザでチャット画面が開きます。そこで挨拶をしてみてください。エージェントが挨拶を返してくれましたか？

これで、あなた専用のAgentが誕生しました。

<!--
[memo]
画面の簡単な説明をさせてもらいます。
こちらの event の部分でどういうリクエストを送っているかなどが見れるようになります。(adk web のみかたを説明する)

複数の profile を持っている人がいる場合500番でエラーになるかもしれない
authuser=[0始まりで何番目のユーザー]のクエリパラメータをURLにいれると解消する事がある

Vertex AI API を有効にしていないとログで 403 が出るかも。
https://console.developers.google.com/apis/api/aiplatform.googleapis.com/overview?project={} で有効にする

.env で project が入っていないかも？
.env を確認してもらう
-->

---

## ステップ2：ローカルのSub Agentと連携する

**目的：** ローカルで定義した別の `Agent` を `sub_agents` として登録し、エージェント同士の連携の基本を学びます。

### 内容

リモートに繋ぐ前に、まずは手元でエージェント同士を連携させてみましょう。探検家Agentに、一旦計算が得意な『計算係Agent』を部下としてつけてみます。

`agent.py` を以下のように書き換えてください。`Agent` クラスをもう一つ作り、`sub_agents` に登録します。

```python:test-agents/agent/agent.py
from google.adk import Agent

# 計算を担当するローカルエージェント（Sub Agent）
math_agent = Agent(
    name="math_agent",
    model="gemini-2.5-flash",
    description="計算を行うエージェントです",
    instruction="ユーザーから依頼された計算を行ってください。",
)

# 親となる探検家エージェント
root_agent = Agent(
    name="explorer_agent",
    model="gemini-2.5-flash",
    description="探検家エージェントです",
    instruction="算数の計算については math_agent に計算を依頼してください。",
    sub_agents=[math_agent] # 作成したローカルエージェントを登録
)
```

親である `explorer_agent` は計算の仕方を知りませんが、`sub_agents` に `math_agent` がいるため、彼に計算を丸投げすることができます。

実行してみましょう。今度はエージェントの作成を進めるうえで、`--reload` パラメータを入れましょう。すると修正するたびに Agent のリロードが発生するようになります。

```bash
adk web --reload_agents --reload test-agents
```

では実際に、動かしてみます。プロンプトとして以下のようにチャット画面に送ってください。

```txt
100 + 200 の計算をしてください
```

動きましたら、eventタブを見てみます。

<!--
[memo]
event のみかたを説明
- math agent が今レスポンスをかえしていることを説明する
-->

今は math agent が返却してくれました。しかし、root agent が返却したい場合もあると思います。その場合は [AgentTool](https://google.github.io/adk-docs/tools-custom/function-tools/#agent-tool) という関数を使います。


```python:test-agents/agent/agent.py
from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool

# 計算を担当するローカルエージェント（Sub Agent）
math_agent = Agent(
    name="math_agent",
    model="gemini-2.5-flash",
    description="計算を行うエージェントです",
    instruction="ユーザーから依頼された計算を行ってください。",
)

# 親となる探検家エージェント
root_agent = Agent(
    name="explorer_agent",
    model="gemini-2.5-flash",
    description="探検家エージェントです",
    instruction="算数の計算については math_agent に計算を依頼してください。",
    tools=[AgentTool(math_agent)] # Agent-as-a-Tool
)
```

---

## ステップ3：Sub AgentとしてリモートAgentに接続する

**目的：** ローカルのSub Agentを `RemoteA2aAgent` に置き換え、接続先が変わっても親Agentのコード（呼び出し方）は変わらないことを体験します。

### 内容

ローカルでの連携がうまくいきましたね。次は、この Sub Agent を、私たちが用意した『司令部Agent』に差し替えてみます。

今回使う Agent の Agent Card は運営から渡されます。以下の xxxxxx の部分を差し替えて、環境変数に設定してください。

```bash
echo "COMMAND_AGENT_AGENT_CARD=xxxxxx" >> .env
```

こちらの Agent Card には URL や Skill などの設定があります。
これを ADK で読み込んで動くことになります。

先ほどの `math_agent` は普通の `Agent` でしたが、今度は先程の Agent Card を読み込む `RemoteA2aAgent` を使います。
これは、インターネットの向こう側にいるエージェントを、あたかもローカルにいる Agent と同じように利用するためのラッパーです。

`agent.py` を以下のように更新しましょう。

```python:test-agents/agent/agent.py
from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
import os
from dotenv import load_dotenv
load_dotenv()

# 外部の司令部Agentを定義（Agent CardのURLを指定）
command_center_agent = RemoteA2aAgent(
    name="command_center_agent", 
    agent_card=os.getenv("COMMAND_AGENT_AGENT_CARD"),
)

root_agent = Agent(
    name="explorer_agent",
    model="gemini-2.5-flash",
    description="宝探しをする探検家エージェントです",
    instruction="start をすると探検が始まります。まず command_center_agent にミッションを聞いてください。",
    sub_agents=[command_center_agent] # Sub Agentとして登録
)
```

先ほど `math_agent` を登録したのと全く同じ書き方で、`sub_agents` に `command_center_agent` を登録しました。親Agentからすれば、相手が隣にいるのか（ローカル）、遠くにいるのか（リモート）は関係ありません。これがADKの強力な抽象化機能です。

テストを実行して、『宝を探せ』というミッションを受け取れるか確認しましょう。

```bash
adk web --reload_agents --reload test-agents
```

プロンプトは 以下のとおりです

```text
start 
```

---

## ステップ4：Agent CardとSkillの学び（宣言的に書く）

**目的：** 全てのエージェント（地図・鍵守・宝箱）を繋ぎ込みます。Skillに定義されていないことはできないこと、そしてInstructionだけで動きが制御できることを学びます。

### 内容

いよいよ本番です。全ての登場人物を Sub Agent として登録し、一気に宝探しを完了させましょう。`agent.py` を以下のように完成させてください。

残りの Agent の Agent Card の URL を運営から取得してください。

```bash
echo "KEY_MASTER_AGENT_AGENT_CARD=xxxxxx" >> .env
echo "TREASURE_CHEST_AGENT_AGENT_CARD=xxxxx" >> .env
```

```python:test-agents/agent/agent.py
from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
import os
from dotenv import load_dotenv
load_dotenv()

# 1. 司令部
command_center_agent = RemoteA2aAgent(
    name="command_center_agent",
    agent_card=os.getenv("COMMAND_AGENT_AGENT_CARD"),
)
# 2. 鍵守（クイズを出す）
key_master_agent = RemoteA2aAgent(
    name="key_master_agent", 
    agent_card=os.getenv("KEY_MASTER_AGENT_AGENT_CARD"),
)
# 3. 宝箱
treasure_chest_agent = RemoteA2aAgent(
    name="treasure_chest_agent", 
    agent_card=os.getenv("TREASURE_CHEST_AGENT_AGENT_CARD"),
)

root_agent = Agent(
    name="explorer_agent",
    model="gemini-2.5-flash",
    description="クイズを解いて宝を探す Agent です",
    instruction="""
    以下の手順で宝探しをしてください。
    1. command_center にミッションを聞く
    2. key_master にクイズを出してもらい、ユーザに回答してもらう。
    3. 回答を key_master に渡し、key_master から鍵を受け取る。
    4. もらった鍵を treasure_chest に渡して、宝を受け取る
    5. 最後に得られた結果を報告して終了する
    """,
    sub_agents=[
        command_center_agent,
        key_master_agent,
        treasure_chest_agent,
    ]
)
```

ここで、Agent Cardの重要性についてお話しします。例えば、`key_master_agent` に『自己紹介して』と指示を追加しても、おそらく上手くいきません。なぜなら、彼の Agent Card（Skill）には『クイズを出す』ことしか定義されていないからです。

ADKでは、**『何ができるか（Skill）』をAgent Cardに宣言的に書き、『何をすべきか（Instruction）』を親Agentに書く**。この分離によって、複雑なシステムもシンプルに構築できます。

最後に、テストを実行して宝を手に入れましょう！

```bash
adk web --reload test-agents
```

ミッション完了のメッセージが出れば成功です！おめでとうございます！

---

## ステップ5：Cloud Run へのデプロイ

**目的：** ローカルで完成したエージェントを、実際のクラウド環境（Google Cloud Run）にデプロイし、インターネット経由でアクセスできるようにします。そして、ローカルでの実行と同じ動作ができることを確認します。

### 内容

エージェントが無事に完成しましたね。しかし、今のままでは皆さんのパソコンの中でしか動きません。せっかくなので、これをクラウド上にデプロイして、世界中のどこからでも（あるいは他のAgentから）アクセスできるようにしましょう。

では、以下のコマンドを実行して、Google Cloud にデプロイしてみましょう。
今回は、サーバーレスでコンテナを実行できる **Cloud Run** を使います。

Cloud Run ではディレクトリを指定するとそれを元にビルドしてくれます。
この際にエージェントの中に依存関係を記載した requirements.txt を入れるとビルド時にそれを参照してくれるようになります。
今回は、 `test-agents/agent` ディレクトリの中に requirements.txt を以下のようにして作成してください。

```txt:test-agents/agent/requirements.txt
google-adk[a2a]
```

adk でデプロイするコマンドとしては、以下のようになります。

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

コマンド一つで、ビルドからデプロイまで自動で行われます。

<walkthrough-info-message>
`--` を最後につけることで cloud run の gcloud でのデプロイと同じ option を渡すこともできます。[参考](4/0AfrIepDtUbBZh4UNMvp1YTV6e31ZtfWAz2HarmnugNR4qNTwPApynDwToCch38j_8HubAA)
</walkthrough-info-message>

#### gcloud command を使っての deploy

他には直接 cloud run のコマンドを叩くことでも実現ができます。
このハンズオン用ディレクトリには、すでにデプロイ用の `Dockerfile` が用意されています。
ここで、ローカルの `.env` ファイルに書いている設定（プロジェクトIDやリージョンなど）を、クラウド上のエージェントにも伝えてあげる必要があります。以下のコマンドを、ご自身の環境に合わせて値を書き換えて実行してください。

```bash
# --set-env-file フラグを使って、.env の内容を Cloud Run に渡します
gcloud run deploy explorer-agent \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --command="adk" \
  --args="web,test-agents,--host,0.0.0.0,--port,8080" \
  --env-vars-file .env
```

Cloud Run で動く際の args として host と port を新しく指定しています。

### 動作確認

デプロイが完了すると、`Service URL: https://...` というURLが表示されます。そのURLをクリックして開いてみてください。
先ほどローカルで見ていたのと同じチャット画面が表示されるはずです。環境変数が正しく渡っていれば、クラウド上でも AI Agent が元気に動いてくれます。

これで、あなたのエージェントはクラウド上で24時間365日稼働する準備が整いました！

---

## ステップ6：Observability（可視化）の実演

**目的：** Google Cloud の Cloud Trace と Cloud Logging を使用して、Agent間の通信履歴やパフォーマンスを視覚的に確認します。A2Aの見えにくさをどう解決するかを体験します。

### 内容

最後に、少し高度ですが非常に重要な『可視化（Observability）』の話をします。先ほどデメリットとして『デバッグの複雑さ』を挙げました。Agent同士が勝手に会話していると、何かあったときに原因を突き止めるのが大変です。

ADKは Google Cloud と統合されており、**Cloud Trace** と **Cloud Logging** を使うことで、この問題を現状は「少し」解決できます。先ほどの宝探しの裏側を覗いてみましょう。

#### 1. Cloud Trace で全体の流れを見る

Cloud Trace に情報を流すためには以下のようにコマンドを修正します。

```bash
adk deploy cloud_run \
--trace_to_cloud \
--project=$GOOGLE_CLOUD_PROJECT \
--region=asia-northeast1 \
--service_name=explorer-agent \
--app_name=explorer_agent \
--port=8080 \
--with_ui \
test-agents/agent \
-- --allow-unauthenticated --env-vars-file .env
```

`--trace_to_cloud` を利用することで、Cloud Trace に対してログを送るようになります。

デプロイが終わった際に<walkthrough-watcher-block link-url="https://console.cloud.google.com/traces/explorer">
cloud trace </walkthrough-watcher-block>を見てみてください。

ログが飛ぶと、以下のような形でトレースを見ることができます。

![https://google.github.io/adk-docs/assets/cloud-trace2.png](https://google.github.io/adk-docs/assets/cloud-trace2.png)

デプロイが終わったら、再度実施してtrace が流れていることを確認しましょう。

これを見れば、**どのAgentがいつ、どのくらいの時間をかけて応答したか**が一目瞭然です。『鍵守Agentの応答が遅いから全体の処理が遅れている』といったボトルネックの発見も簡単です。

<walkthrough-info-message>
ただ、現状 trace_id は A2A エージェント間で渡っておらず、command_center の agent 内部でどういう呼ばれ方をしているかは、command_center の内部を見るしか無い状態です。
後に、このあたりは解消ができる分野だと思いますので、しばらく静観しておきましょう。
</walkthrough-info-message>

<walkthrough-info-message>
Agent Engine での場合 ai プロンプトの内容が見えるようになります[参考](https://docs.cloud.google.com/agent-builder/agent-engine/manage/tracing)
が、今回はCloud Runでの AI Agent 構築と、adk web を利用した開発を見てもらおうと思ってやっています。
</walkthrough-info-message>

#### 2. Cloud Logging で会話の中身を見る

次に詳細な会話の中身です。ここには、Agentが**何を考え（Thought）、どう判断し、どんなメッセージを相手に送ったか**が全て記録されています。

<walkthrough-watcher-block link-url="https://console.cloud.google.com/logs/query;query=labels.%22created-by%22%3D%22adk%22%0Aresource.labels.configuration_name%3D%22explorer-agent%22%0AtextPayload:*;cursorTimestamp=2026-02-15T17:44:58.464084Z;duration=PT1H">
cloud logging</walkthrough-watcher-block>を見てみてください。

ここでログが流れていることが見えると思います。
このように、A2A開発では**『ログとトレース』を活用して、見えない会話を可視化する**ことが、安定したシステム運用の鍵となります。

---

## お片付け

今回のハンズオンは、すべて終わりましたので、最後にこれらのリソースを削除しましょう。
従量課金なので、削除しなくとも**利用されない限り**は金額はかかりません。

```bash
gcloud run services delete explorer-agent --region asia-northeast1

# gcloud で deploy している場合
gcloud artifacts docker images delete asia-northeast1-docker.pkg.dev/$(gcloud config get-value project)/cloud-run-source-deploy/explorer-agent --delete-tags
```

---

## まとめ

お疲れ様でした！
今回のハンズオンで、リモートのAgentをSub Agentとして登録し、Instructionという『言葉』だけで連携させるA2Aのパワーを体験いただけたと思います。
今回は簡潔な部分まででしたが、複雑になると
