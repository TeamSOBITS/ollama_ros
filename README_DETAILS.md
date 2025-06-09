<sub>[READMEへ戻る](README.md)</sub>

## 詳細

### メッセージ型について

Action通信にて呼び出すメッセージの構成は以下のようになっています．
```sh
# ChatLlmRecognition.action
# Goal
string room_name            # 部屋名指定
string request              # リクエストメッセージ
sensor_msgs/Image[] image   # 入力画像のリスト
string[] sound_file_path    # 入力音声ファイルのパスのリスト
string model_name           # modelの名前
bool is_stack               # このやり取りをroom_nameにメモリーするか
---
# Result
string result               # 返答メッセージ
float64 elapsed_time        # 返答まで何秒かかったか
---
# Feedback
string wip_result           # 途中経過のメッセージ
bool end_flag               # 途中経過の送信がが終了したかどうか
```


### `room_name`とは

`room_name`とは会話のストックを割り当てるラベルです．
例えばChat GPTでは各会話ごとに部屋を切り替えられると思います．

例としては以下のような状態です．

```yaml
# 部屋A
USER : SOBITSについて教えてください
GPT : 私は大規模言語モデルであるため，特定のワードについての知識はありません．
USER : そうでしたか．SOBITSとは創価大学の崔研究室と萩原研究室の学生で構成されたチームです
GPT : そうなのですね！2つの研究室の合同チームとは素晴らしいですね！

# 部屋B
USER : 数学についての質問に答えてください
GPT : もちろんです。どのような数学の質問がありますか？
USER : 0で割ることはなぜいけないのですか？
GPT : 0で割るという操作は数学的に定義されていないため、意味がありません．
```

このような2つの部屋A,Bがあったとします．\
この2部屋でユーザから「SOBITSとはどのようなものですか？」と質問すれば当然部屋AではGPTが答えることができます．\
以下回答例です．

```yaml
# 部屋A
USER : SOBITSとはどのようなものですか？
GPT : SOBITSは先程あなたに教えてもらいました．崔研究室と萩原研究室の合同チームでしたね．なにか間違いがありましたか？

# 部屋B
USER : SOBITSとはどのようなものですか？
GPT : SOBITSについて私は知識を持ち合わせていません．数学の質問でしたらお答えすることができるかもしれません．
```

このパッケージでの`room_name`はこの部屋Aや部屋Bに当てはまります．\
`room_name`はいくつでも作ることができ，Serverのlaunchを切らない限りは過去に指定したことのある部屋名を指定すればその部屋での会話の続きができます．


### 事前プロンプトを定義

上で`room_name`を指定したように，事前に会話をしたように，履歴を定義しておくことができます．
基本的に，[base_prompt.yaml](prompt/base_prompt.yaml)に定義できます．

中は一例ですが，以下のように定義しました．

```yaml
# 事前に会話を定義しておくことができるyamlファイル
sobit_mini:                                         # sobit_miniという部屋では．．．
- {user     : "My name is SOBIT MINI."}             # 「私の名前はSOBIT MINIです」とUser側から言ったら，，，  
- {assistant: "Nice to meet you SOBIT MINI!"}       # 「よろしくね，SOBIT MINIさん」と言っている会話を予め定義しているので
                                                    # sobit_miniという部屋を指定すればこの続きから会話できます

team_introduce:                                     # team_introduceという別の部屋も準備している
- {user     : "Our team name is SOBITS."}
- {assistant: "I love it! SOBITS sounds like a unique and fun team name."}
- {user     : "SOBITS consists of about 30 people."}
- {assistant: "A team of 30 people! That's impressive!"}
```

sobit_miniという`room_name`ではUserの名前がSOBIT MINIとしてシステムが認識した状態で会話を進めることができます．
また別の部屋として，team_introduceという`room_name`では，チームSOBITSについての説明をしており，チーム名とチームの人数をシステムは知っている状態になっています．

これらを踏まえて，部屋や事前プロンプトを用いた簡単な操作方法について説明します．

1. ActionServerを立ち上げる
    ```console
    ros2 launch ollama_ros ollama.launch.py
    ```

2. アクションクライアントを実行します

そこで`room_name`を`default`にして，`request`に「Do you know my name?」と打ってみてください．

<div align="left">
<img src="img/default_result.png" height="420">
</div>

`default`という部屋は事前プロンプトにもなく今定義した部屋なので，返答は「わかりません」になったと思います．

ここでもう一度クライアントを実行してください．
今度は`room_name`をsobit_miniにして，同様に`request`を「Do you know my name?」としてみてください．

<div align="left">
<img src="img/sobit_mini_result.png" height="420">
</div>

すると「あなたの名前はSOBIT MINIですね」という趣旨の返答が得られたと思います．
これは会話履歴が部屋ごとに蓄積させているので，Serverのlaunchを切らない限り部屋名の指定さえすれば，何度でも事前プロンプトや会話の続きから，使うことができます．

> [!IMPORTANT]
> 使用するモデルによっては文章だけでなく，画像や音声も送ることができます．
