<a name="readme-top"></a>

[JP](README.md) | [EN](README_en.md)

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]

# Ollama for ROS

<!-- 目次 -->
<details>
  <summary>目次</summary>
  <ol>
    <li>
      <a href="#概要">概要</a>
    </li>
    <li>
      <a href="#セットアップ">セットアップ</a>
      <ul>
        <li><a href="#環境条件">環境条件</a></li>
        <li><a href="#インストール方法">インストール方法</a></li>
      </ul>
    </li>
    <li><a href="#モデルのダウンロード方法">モデルのダウンロード方法</a></li>
    <li><a href="#実行・操作方法">実行・操作方法</a></li>
    <li><a href="#サーバーへのリクエストの送信">サーバーへのリクエストの送信</a></li>
    <li><a href="#使用可能なモデル">使用可能なモデル</a></li>
    <li><a href="#関数呼び出し機能">関数呼び出し機能</a></li>
    <li><a href="#マイルストーン">マイルストーン</a></li>
    <li><a href="#参考文献">参考文献</a></li>
  </ol>
</details>



<!-- レポジトリの概要 -->
## 概要

本レポジトリは，オフラインのローカルのみで大規模言語モデル(LLM:Large Language Models)を動かすことができるパッケージです．\
処理速度はCPU/GPUで変わりますが，モデルによってはCPUでも問題なく動きます．\
特に，大規模言語モデルは1単語ずつ返答が構築されていく仕組みのため，呼び出しから返答までの間に途中経過が存在することから，ROS2のAction通信を用います．

<p align="right">(<a href="#readme-top">上に戻る</a>)</p>


## セットアップ

ここで，本レポジトリのセットアップ方法について説明します．

<p align="right">(<a href="#readme-top">上に戻る</a>)</p>


### 環境条件

まず，以下の環境を整えてから，次のインストール段階に進んでください．

| System | Version |
| --- | --- |
| Ubuntu | 22.04 (Jammy Jellyfish) |
| ROS    | Humble Hawksbill    |
| Python | >=3.10              |

<p align="right">(<a href="#readme-top">上に戻る</a>)</p>


### インストール方法

1. ROS2の`src`フォルダに移動します．
    ```sh
    cd ~/colcon_ws/src/
    ```
2. 本レポジトリをcloneします．
    ```sh
    git clone -b humble-devel https://github.com/TeamSOBITS/ollama_ros
    ```
3. レポジトリの中へ移動します．
    ```sh
    cd ollama_ros/
    ```
4. 依存パッケージをインストールします．
    ```sh
    bash install.sh
    ```
5. パッケージをコンパイルします．
    ```sh
    cd ~/colcon_ws/
    ```
    ```sh
    colcon build --symlink-install
    ```
    ```sh
    source ~/colcon_ws/install/setup.sh
    ```

<p align="right">(<a href="#readme-top">上に戻る</a>)</p>


## モデルのダウンロード方法

1. [model_download.launch.py](launch/model_download.launch.py)を起動する
    ```sh
    ros2 launch ollama_ros model_download.launch.py
    ```
2. GUIのから使いたいモデルをダウンロードする\
  モデルのダウンロードは[download]をクリックしてください．

> [!NOTE]
> モデルはこれが全てではなく，[こちら](https://ollama.com/library)にあるものから抜選しています．(全て書くとGUIが膨大になってしまうのと，公式からの更新に対応できないため)

- もしGUIにないものをdownloadしたい場合は，[/models/model_list.yaml](models/model_list.yaml)に追加してください．
  - 例：deepseek-r1というモデルのパラメータ数14bのモデルをダウンロードしたい場合
    ```yaml
    models:
      - "deepseek-r1:14b"
    ```
- 既にモデルがダウンロードされている場合は削除([delete])，コピー([copy])，push([push])することができます．

> [!WARNING]
> モデルのダウンロードにはしばらく時間がかかります．GUIが更新されるまで待っていてください

<div align="center">
  <img src="img/download_demo.png" height="420">
</div>

> [!NOTE]
> 詳細や細かい操作方法などについては[元ollama-python](https://github.com/ollama/ollama-python)や[ollama](https://github.com/ollama/ollama)などを参照してください．

<p align="right">(<a href="#readme-top">上に戻る</a>)</p>


## 実行・操作方法
1. [prompt/base_prompt.yaml](prompt/base_prompt.yaml)上でモデルの設定を用途に応じて更新してください．
    ```yaml
    /**:
      ros__parameters:
        ollama:
          num_ctx: 4096          # コンテキストウィンドウ（記憶容量）。過去の会話や画像の情報をどれくらい保持するか（トークン単位）
          num_predict: 4096      # 最大出力トークン数。1回のリクエストでAIが生成できるテキストの最大長
          repeat_last_n: 64      # 繰り返し抑制の対象範囲。直近何トークンまで遡って「同じ言葉の繰り返し」をチェックするか
          repeat_penalty: 1.1    # 繰り返し抑制の強さ。1.0以上で抑制がかかり、同じフレーズのループを防ぐ（例: 1.1〜1.5）
          temperature: 0.7       # 生成の多様性（温度）。0に近いほど正確・固定的、1に近いほどクリエイティブ・ランダムになる
          top_k: 40              # 語彙の絞り込み数。次の言葉を選ぶ際、確率が高い上位40個に候補を制限して無意味な単語を省く
          top_p: 0.9             # 累積確率による絞り込み。累積確率が90%に達するまでの単語群から選択し、自然な文章にする
          seed: 42               # 乱数シード。同じ値を指定すると、同じ入力に対して常に同じ回答（再現性）が得られる（-1でランダム）
          json_mode: false       # JSON強制モード。trueにするとAIの回答を常に有効なJSON形式にする（システムプロンプトの調整も必要）
          tool_choice: "none"    # ツール（関数）呼び出し設定。"none"は使わない、"required"は必ずツールを使う、"auto"はAIが判断
    ```
    - 各パラメータは[ollama.launch.py](launch/ollama.launch.py)起動後でも変更できます．
      - 例： `tool_choice`を`auto`に変更する場合
        ```sh
        ros2 param set /ollama_action_server ollama.tool_choice auto
        ```

2. [任意][prompt/base_prompt.yaml](prompt/base_prompt.yaml)上で，文脈エンジニアリングのためのルームを記述してください．
    ```yaml
    example_room: # 部屋名
    # system: LLMのキャラクターや制約（役割，口調，ルール）を定義
    - {system: "あなたは案内ロボットの'SOBIT'です．丁寧な日本語で答えてください．"}

    # user: 人間（ユーザー）からの問いかけ（filesで画像添付が可能）
    - {user: "こんにちは！あなたは何ができますか？", files: ["sobit_mini.png"]}

    # model: LLMの回答（会話の流れを維持するために使用）
    - {model: "こんにちは！私はSOBITです．施設の案内や画像認識が可能です．"}
    ```

    ```yaml
    # 例：自チームに関する紹介のチャットボット
    team_introduce:               # team_introduceという別の部屋も準備している
      - {user : "私達のチームはSOBITSという学生チームを組んでいます！"}  # imageを入れない場合
      - {model: "SOBITSという学生チームを組んでいるのですね！素晴らしいですね！どういったチームなのですか？"}
      - {user : "学部生・修士・博士と幅広く在籍し，40人います！"}
      - {model: "40人ものメンバーがいる大規模な学生チームなのですね！\n幅広い層の方が在籍されているとのこと，多様な視点や知識が集まって素晴らしいチームになりそうですね．"}
    ```

3. [ollama.launch.py](launch/ollama.launch.py)を起動することでAction Serverを起動します．
   ```sh
   ros2 launch ollama_ros ollama.launch.py
   ```

> [!WARNING]
> CPUでは処理が遅くなってしまうため，Action通信で途中経過を見ながら待機していたほうがいいかもしれません．

> [!NOTE]
> 事前プロンプトの設定や`room_name`についての詳細は[こちら](README_DETAILS.md)を確認してください．

<p align="right">(<a href="#readme-top">上に戻る</a>)</p>

### サーバーへのリクエストの送信

`sobits_interfaces/action/ChatLlmRecognition`というアクションを用いて，Ollamaサーバにリクエストを送信します．

| 項目              | フィールド名          | 型                     | 説明                                                |
| :---------------- | :-------------------- | :--------------------- | :-------------------------------------------------- |
| **アクション名**  |                       |                        | `ollama_action`                                     |
| **Goal**          | `room_name`           | string                 | 会話履歴を管理するための任意のルームの名前          |
|                   | `request`             | string                 | ユーザーからのテキストメッセージ                    |
|                   | `image`               | sensor_msgs/Image[]    | 送信する画像メッセージのリスト                      |
|                   | `sound_file_path`     | string[]               | 送信するファイルのパスのリスト                  |
|                   | `model_name`          | string                 | 使用するモデルの名前 (例: "deepseek-r1:14b") |
|                   | `is_stack`            | bool                   | 現在の会話を会話履歴にスタックするかどうか          |
| **Result**        | `result`              | string                 | Ollamaからの応答テキスト                            |


<p align="right">(<a href="#readme-top">上に戻る</a>)</p>

## 関数呼び出し機能

LLMがユーザーの指示を解析し，状況に応じて事前に定義した関数を呼び出す機能です．LLMは実行すべき関数名と引数 をJSON形式で出力します．

1. 事前に使用する関数を [ollama_tools.yaml](./prompt/ollama_tools.yaml) に定義します．
    - `description` は明確かつ簡潔にしてください
    - 各パラメータが何を期待するかを記述することで，モデルが正しい引数を提供するのを助けます

    ```yaml
    tools: # LLMが使用可能なツールのリスト定義
      - type: "function" # ツールの種類（現在はfunction固定）
        function:
          name: "navigation" # 関数名：プログラム側で呼び出す際の一意の識別子
          description: "ロボットを指定された部屋や場所に移動させます．" # LLMへの指示：どのような時にこの関数を使うべきかの説明
          parameters: # 関数に渡す引数の定義
            type: "object" # 引数のデータ構造（通常はobject）
            properties: # 具体的な引数の内容
              location: # 引数名
                type: "string" # 引数の型（文字列）
                description: "目的地の名称（例：キッチン，リビングルーム）．" # 引数に何をいれるべきかのLLM向け説明
            required: ["location"] # 実行に必須となる引数のリスト

      - type: "function"
        function:
          name: "object_detect"
          description: "現在ロボットのカメラに映っているすべての物体を検出し，そのリストを返します．"
          parameters:
            type: "object"
            properties: {} # 引数が必要ない場合は空のオブジェクトを指定
            required: [] # 必須項目なし

    ```

2. [ollama_config.yaml](prompt/ollama_config.yaml) の `tool_choice` パラメータを以下のどちらかに変更します．
    * `required`: LLMに必ず何らかの関数（ツール）を呼び出させます．
    * `auto`: LLMが文脈に応じて，関数を呼ぶかテキストで答えるかを自動判断します．

3. Ollama ROSのアクションサーバを起動します．
    ```sh
    ros2 launch ollama_ros ollama.launch.py
    ```
4. クライアントからリクエストを送信します．

    - 例：リクエストをPlease go to the kitchen.とした場合，出力として以下の形式のJSON文字列が返されます．クライアント側でこの文字列をパースして使用してください．

      ```text
        TOOL_CALL:[{"name": "navigation", "args": {"location": "kitchen"}}]
      ```

<p align="right">(<a href="#readme-top">上に戻る</a>)</p>

<!-- マイルストーン -->
## マイルストーン

現時点のバッグや新規機能の依頼を確認するために[Issueページ][issues-url] をご覧ください．

<p align="right">(<a href="#readme-top">上に戻る</a>)</p>


<!-- 参考文献 -->
## 参考文献

* [ollama](https://ollama.com/)
* [ollama-python.git](https://github.com/ollama/ollama-python)
* [ollama.git](https://github.com/ollama/ollama)
* [Models](https://ollama.com/library)

<p align="right">(<a href="#readme-top">上に戻る</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/TeamSOBITS/ollama_python.svg?style=for-the-badge
[contributors-url]: https://github.com/TeamSOBITS/ollama_python/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/TeamSOBITS/ollama_python.svg?style=for-the-badge
[forks-url]: https://github.com/TeamSOBITS/ollama_python/network/members
[stars-shield]: https://img.shields.io/github/stars/TeamSOBITS/ollama_python.svg?style=for-the-badge
[stars-url]: https://github.com/TeamSOBITS/ollama_python/stargazers
[issues-shield]: https://img.shields.io/github/issues/TeamSOBITS/ollama_python.svg?style=for-the-badge
[issues-url]: https://github.com/TeamSOBITS/ollama_python/issues
[license-shield]: https://img.shields.io/github/license/TeamSOBITS/ollama_python.svg?style=for-the-badge
[license-url]: LICENSE
