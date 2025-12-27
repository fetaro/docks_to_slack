# Google Docsの箇条書きをSlackにコピーするツール

## 問題

Google Docsの箇条書きをMacのクリップボードにコピーしてSlackにペーストすると、以下のように箇条書きが崩れてしまう。

例えば、このようなGoogle Docsの箇条書き

![good_slack](docs/docs.png)

これをSlackにコピーすると

![bad_slack](docs/bad_slack.png)

とフラットな箇条書きでコピーされてしまう

### このツールを使うと

インデントの構造を保持してコピーできます！

![good_slack](docs/good_slack.png)


### インストール

```bash
git clone https://@github.com/fetaro/docks_to_slack.git
cd docks_to_slack
uv sync
```

### 使い方

1. Google Docsの箇条書きをコピーします

2. クリップボードにGoogle Docsの箇条書きがある状態で以下のコマンドを実行します

```bash
python main.py
```

これでSlackに貼り付け可能なデータがクリップボードに書き込まれました

3. Slackにてペーストします

#### (オプション)テキストとしてペーストする場合

`-t` オプションでmarkdown形式のテキストとしてペーストすることも可能です

```bash
python main.py -t
```

以下のようなテキストがクリップボードに保存されます

```
- インデントレベル１
    - インデントレベル２のA
    - インデントレベル２のB
    - インデントレベル２のC
```

#### デバッグ

`-d` オプションを付けるとデバッグモードになります