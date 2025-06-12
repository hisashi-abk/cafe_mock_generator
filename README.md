# 🏪 カフェ売上モックデータ生成器 & 機械学習チュートリアル

Python初学者が機械学習とWeb開発の実践的なスキルを身につけるための包括的なチュートリアルプロジェクトです。

## 📋 プロジェクト概要

カフェの売上データを使って、データ分析から機械学習、Webアプリ開発、デプロイまでを段階的に学習し、最終的にGitHubで公開できるポートフォリオを作成します。

## 🎯 対象読者

- Python初学者（プログラミング基礎知識があると良い）
- 機械学習に興味がある学習者
- 就職活動でポートフォリオを作成したい学生・転職者
- 実践的なWeb開発スキルを身につけたい人

## 🚀 クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-username/cafe-ml-tutorial.git
cd cafe-ml-tutorial
```

### 2. 仮想環境の作成と有効化

```bash
# Python 3.8以上が必要です
python -m venv cafe_env

# Windows
cafe_env\Scripts\activate

# macOS/Linux  
source cafe_env/bin/activate
```

### 3. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. サンプルデータの生成

```bash
python cafe_generator.py
```

### 5. 生成されたデータの確認

```bash
# 生成されたCSVファイルを確認
ls data/csv/

# Pythonでデータを読み込み
python -c "
import pandas as pd
df = pd.read_csv('data/csv/daily_summary.csv')
print(df.head())
print(f'データ期間: {df.date.min()} - {df.date.max()}')
print(f'総売上: {df.total_sales.sum():,.0f}円')
"
```

## 📖 チュートリアル構成

### 🔹 第1章: Pythonの基礎 & データ操作 ✅
**📌 現在の章**
- [x] モックデータ生成器の作成
- [x] Pandasでのデータ操作
- [ ] 基本的なグラフ作成

**📈 達成目標:**
- Pythonを使ってデータを読み込んだり整理できる
- 可視化を通じてデータの特徴を掴める

### 🔹 第2章: 売上データ分析 📋
- [ ] データの前処理・クリーニング
- [ ] 統計的分析とビジネス洞察
- [ ] インタラクティブダッシュボード作成

### 🔹 第3章: 売上予測モデルの作成 🤖
- [ ] 機械学習モデルの構築
- [ ] モデル評価と改善
- [ ] 予測結果の可視化

### 🔹 第4章: Webアプリ & API開発 🌐
- [ ] Streamlitでのアプリ開発
- [ ] FastAPIでのAPI作成
- [ ] フロントエンド連携

### 🔹 第5章: データベース管理 🗄️
- [ ] PostgreSQL設計と運用
- [ ] データ管理画面の作成

### 🔹 第6章: Dockerによる環境構築 🐳
- [ ] コンテナ化
- [ ] 開発環境の標準化

### 🔹 第7章: GitHubでの公開 & デプロイ 🚀
- [ ] CI/CDパイプライン
- [ ] クラウドデプロイメント

### 🔹 第8章: 就職活動向けの活用 💼
- [ ] ポートフォリオ作成
- [ ] 技術ブログ執筆

## 📁 プロジェクト構成

```
cafe-ml-tutorial/
├── README.md                 # このファイル
├── requirements.txt          # 必要なパッケージ一覧
├── config.yaml              # データ生成設定
├── cafe_generator.py         # メインのデータ生成器
├── data/                    # 生成されたデータ
│   ├── csv/                 # CSV形式
│   ├── json/                # JSON形式
│   ├── xlsx/                # Excel形式
│   └── cafe_mock_sales.db   # SQLiteデータベース
├── notebooks/               # Jupyter Notebook（分析用）
│   └── chapter1_basic_analysis.ipynb
├── src/                     # ソースコード
│   ├── data_analysis/       # データ分析モジュール
│   ├── ml_models/           # 機械学習モデル
│   └── web_app/             # Webアプリケーション
├── tests/                   # テストコード
└── docs/                    # ドキュメント
    ├── chapter1/            # 各章の詳細ガイド
    ├── chapter2/
    └── ...
```

## 💾 生成されるデータ

### テーブル構成
- **customers**: 顧客マスター（年齢、性別、来店頻度など）
- **categories**: 商品カテゴリマスター
- **menu_items**: メニューマスター（価格、原価、人気度など）
- **orders**: 注文データ（日時、天気、顧客情報など）
- **order_items**: 注文詳細データ（商品、数量、小計など）
- **daily_summary**: 日次集計データ（売上、来客数、平均客単価など）

### データ特徴
- **期間**: 2023年1月1日 - 2024年12月31日（2年間）
- **営業時間**: 9:00-18:00（木曜定休）
- **リアルなパターン**: 
  - 時間帯・曜日・季節による売上変動
  - 天気による影響
  - 顧客属性別の購買傾向
  - 特別イベント（クリスマス、バレンタインなど）

## 🔧 カスタマイズ

### 設定ファイル（config.yaml）の主要項目

```yaml
# データ生成期間の変更
data_generation:
  start_date: "2023-01-01"
  end_date: "2024-12-31"

# 営業時間の調整
business_hours:
  open: 9
  close: 18
  closed_days: [3]  # 木曜定休

# 出力形式の選択
output:
  formats: ["csv", "json", "xlsx", "db"]
```

## 🧪 第1章: 基本的な分析例

### データ読み込みと基本統計

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 日次集計データの読み込み
daily_df = pd.read_csv('data/csv/daily_summary.csv')
daily_df['date'] = pd.to_datetime(daily_df['date'])

# 基本統計
print("=== 基本統計 ===")
print(f"営業日数: {len(daily_df)}日")
print(f"総売上: {daily_df['total_sales'].sum():,.0f}円")
print(f"平均日商: {daily_df['total_sales'].mean():,.0f}円")
print(f"平均客数: {daily_df['unique_customers'].mean():.1f}人")
print(f"平均客単価: {daily_df['avg_order_value'].mean():.0f}円")
```

### 簡単な可視化

```python
# 売上推移グラフ
plt.figure(figsize=(12, 6))
plt.plot(daily_df['date'], daily_df['total_sales'])
plt.title('日別売上推移')
plt.xlabel('日付')
plt.ylabel('売上（円）')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 曜日別売上
daily_df['weekday'] = daily_df['date'].dt.day_name()
weekday_sales = daily_df.groupby('weekday')['total_sales'].mean()
plt.figure(figsize=(10, 6))
weekday_sales.plot(kind='bar')
plt.title('曜日別平均売上')
plt.ylabel('売上（円）')
plt.xticks(rotation=45)
plt.show()
```

## 📚 学習リソース

### 推奨教材
- **Python基礎**: [Python.org Tutorial](https://docs.python.org/3/tutorial/)
- **Pandas**: [10 Minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
- **機械学習**: [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- **可視化**: [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html)

### 各章の詳細ガイド
- [第1章: データ操作の基礎](docs/chapter1/README.md)
- [第2章: データ分析](docs/chapter2/README.md)
- [第3章: 機械学習](docs/chapter3/README.md)

## 🐛 トラブルシューティング

### よくある問題

**Q: `ModuleNotFoundError`が発生する**
```bash
# 仮想環境が有効化されているか確認
pip list

# パッケージを再インストール
pip install -r requirements.txt --upgrade
```

**Q: データ生成でエラーが発生する**
```bash
# 設定ファイルの文法チェック
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# ログレベルを上げて詳細を確認
python cafe_generator.py --verbose
```

**Q: 文字化けが発生する**
- Windowsの場合、`config.yaml`の`encoding: "utf-8"`を`"cp932"`に変更

## 🤝 コントリビューション

バグ報告、機能要望、改善提案など、どんな形でもコントリビューションを歓迎します！

1. Issueを作成して問題を報告
2. フォークして機能を実装
3. プルリクエストを送信

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照

## 🌟 就活での活用

このプロジェクトを完了すると、以下のスキルを証明できます：

- **データサイエンス**: Python、pandas、機械学習
- **Web開発**: API設計、フロントエンド開発
- **インフラ**: Docker、データベース、クラウド
- **プロジェクト管理**: Git、CI/CD、ドキュメント作成

## 📞 サポート

質問や困ったことがあれば、以下の方法でサポートを受けられます：

- [GitHub Discussions](https://github.com/your-username/cafe-ml-tutorial/discussions) - 一般的な質問
- [GitHub Issues](https://github.com/your-username/cafe-ml-tutorial/issues) - バグ報告・機能要望
- [Wiki](https://github.com/your-username/cafe-ml-tutorial/wiki) - 詳細ドキュメント

---

**Happy Learning! 🎓** 

機械学習とWeb開発の旅を一緒に楽しみましょう！