#!/usr/bin/env python3
"""
カフェ売上モックデータ生成スクリプト（第1章用）
Python初学者向けの簡潔版

機能:
- config.yamlからの設定読み込み
- 基本的な売上データ生成
- CSV, JSON, XLSX形式での出力
- 一目で分かるデータ構造
- 詳細な顧客行動パターン
"""

import yaml
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import json
from typing import Dict, List, Any, Tuple, Optional, Union


class CafeDataGenerator:
    """カフェ売上データ生成クラス（第1章用）"""

    def __init__(self, config_path="config.yaml") -> None:
        """
        設定ファイルを読み込んで初期化

        Args:
            config_path (str, optional): 設定ファイルのパス. Defaults to "config.yaml".
        """
        self.config: Dict[str, Any] = self._load_config(config_path)
        self.menu_items: List[Dict[str, Any]] = self._prepare_menu_items()
        self.customer_patterns: List[Dict[str, Any]] = self._prepare_customer_patterns()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        YAML設定ファイルを読み込み

        Args:
            config_path (str): 設定ファイルのパス

        Returns:
            Dict[str, Any]: 設定データの辞書

        Raises:
            FileNotFoundError: 設定ファイルが見つからない場合
            yaml.YAMLError: YAML形式に問題がある場合
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"設定ファイル {config_path} が見つかりません")
            raise
        except yaml.YAMLError as e:
            print(f"YAML読み込みエラー: {e}")
            raise

    def _prepare_menu_items(self) -> List[Dict[str, Any]]:
        """
        メニューアイテムを扱いやすい形式に変換

        Returns:
            List[Dict[str, Any]]: メニューアイテムのリスト
        """
        items: List[Dict[str, Any]] = []
        categories: Dict[str, str] = {cat["id"]: cat["name"] for cat in self.config["menu"]["categories"]}

        for item in self.config["menu"]["items"]:
            items.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "category": categories[item["category_id"]],
                    "price": item["price"],
                    "cost": item["cost"],
                    "available_hours": item["available_hours"],
                    "popularity": item["popularity_weight"],
                    "is_seasonal": item.get("is_seasonal", False),
                    "seasonal_preference": item.get("seasonal_preference", None),
                    "seasonal_multiplier": item.get("seasonal_multiplier", 1.0),
                }
            )
        return items

    def _prepare_customer_patterns(self) -> List[Dict[str, Any]]:
        """
        顧客行動パターンを準備

        Returns:
            List[Dict[str, Any]]: 顧客行動パターンのリスト
        """
        return self.config["customers"]["behavioral_patterns"]

    def _get_customer_pattern(self, date: datetime, hour: int) -> Dict[str, Any]:
        """
        日時に基づいて顧客パターンを決定

        Args:
            date (datetime): 対象の日付
            hour (int): 対象の時間(0-23)

        Returns:
            Dict[str, Any]: 該当する顧客パターンの辞書
        """
        is_weekend: bool = date.weekday() >= 5
        day_type = "weekend" if is_weekend else "weekday"

        # 該当するパターンを検索
        for pattern in self.customer_patterns:
            conditions = pattern["conditions"]
            if day_type in conditions["day_types"] and hour in conditions["hours"]:
                return pattern

        # デフォルトパターン (平日全時間帯)
        return {
            "demographics": {
                "gender_ratio": {"male": 0.45, "female": 0.55},
                "age_distribution": {
                    "teens": 0.15,
                    "twenties": 0.35,
                    "thirties": 0.25,
                    "forties": 0.15,
                    "seniors": 0.10,
                },
            }
        }

    def _generate_customer_demographics(self, pattern: Dict[str, Any]) -> Dict[str, Union[str, int]]:
        """
        顧客の性別・年代を生成

        Args:
            pattern (Dict[str, Any]): 顧客パターンの辞書

        Returns:
            Dict[str, Union[str, int]]: 顧客の属性情報(性別, 年代, 年齢)
        """
        demographics: Dict[str, Any] = pattern["demographics"]

        # 性別決定
        gender = np.random.choice(
            ["male", "female"], p=[demographics["gender_ratio"]["male"], demographics["gender_ratio"]["female"]]
        )

        # 年代決定
        age_groups: List[str] = list(demographics["age_distribution"].keys())
        age_probabilities: List[float] = list(demographics["age_distribution"].values())
        age_group: str = np.random.choice(age_groups, p=age_probabilities)

        # 具体的な年齢を生成
        age_config: List[Dict[str, Any]] = self.config["customers"]["age_groups"]
        age_range: Dict[str, Any] = next(ag for ag in age_config if ag["name"] == age_group)
        age: int = np.random.randint(age_range["min_age"], age_range["max_age"] + 1)

        return {
            "gender": gender,
            "age_group": age_group,
            "age": age,
        }

    def _get_customer_preferences(self, gender: str, age_group: str) -> Dict[str, float]:
        """
        顧客の性別・年代に基づく商品嗜好を取得

        Args:
            gender (str): 性別("male"または"female")
            age_group (str): 年代グループ

        Returns:
            Dict[str, float]: カテゴリ別の嗜好度合い
        """
        try:
            preferences: Dict[str, float] = self.config["customers"]["preferences"][gender][age_group]
            return preferences
        except KeyError:
            # デフォルト設定
            return {
                "モーニング": 1.0,
                "ランチ": 1.0,
                "軽食": 1.0,
                "ドリンク": 1.0,
                "スイーツ": 1.0,
            }

    def _get_weather_for_date(self, date: datetime) -> str:
        """
        日付に基づいて天気を決定

        Args:
            date (datetime): 対象の日付

        Returns:
            str: 天気の文字列（"sunny", "cloudy", "rainy", "snowy"）
        """
        # 将来的には天気APIを使用
        weather_options: List[str] = ["sunny", "cloudy", "rainy", "snowy"]
        weights: List[float] = [0.4, 0.3, 0.2, 0.1]  # 晴れが多め

        # 季節による調整
        if date.month in [12, 1, 2]:
            weights = [0.25, 0.35, 0.2, 0.2]  # 冬
        elif date.month in [6, 7, 8]:
            weights = [0.6, 0.25, 0.15, 0.00]  # 夏

        return np.random.choice(weather_options, p=weights)

    def _apply_seasonal_adjustment(self, item: Dict[str, Any], date: datetime) -> float:
        """
        季節調整を適用

        Args:
            item (Dict[str, Any]): メニューアイテムの辞書
            date (datetime): 対象の日付

        Returns:
            float: 季節調整後の人気度
        """
        if not item["is_seasonal"]:
            return item["popularity"]

        season_map: Dict[str, List[int]] = {
            "spring": [3, 4, 5],
            "summer": [6, 7, 8],
            "autumn": [9, 10, 11],
            "winter": [12, 1, 2],
        }

        current_season: Optional[str] = None
        for season, months in season_map.items():
            if date.month in months:
                current_season = season
                break

        if current_season == item["seasonal_preference"]:
            return item["popularity"] * item["seasonal_multiplier"]

        return item["popularity"]

    def _calculate_hourly_customers(self, date: datetime, hour: int) -> int:
        """
        時間帯別の来客数を計算

        Args:
            date (datetime): 対象の日付
            hour (int): 対象の時間(0-23)

        Returns:
            int: 予想来客数
        """
        base_customers: int = self.config["data_generation"]["base_customers_per_hour"]

        # 曜日係数（月曜=0, 日曜=6）
        weekday: int = date.weekday()
        day_multiplier: float = self.config["data_generation"].get(str(weekday), 1.0)

        # 時間帯係数
        hour_multiplier: float = self.config["data_generation"]["hour_multiplier"].get(hour, 1.0)

        # 天気係数
        weather: str = self._get_weather_for_date(date)
        weather_multiplier: float = self.config["data_generation"]["weather_multiplier"].get(weather, 1.0)

        # 季節係数
        seasonal_multiplier: float = self.config["data_generation"]["seasonal_multiplier"].get(date.month, 1.0)

        # 最終来客数計算
        customers: float = base_customers * day_multiplier * hour_multiplier * weather_multiplier * seasonal_multiplier

        # ポアソン分布でランダム性を追加
        return max(0, np.random.poisson(customers))

    def _select_menu_items_with_preferences(
        self, hour: int, customer_demographics: Dict[str, Union[str, int]], date: datetime
    ) -> Tuple[List[Dict[str, Any]], List[float]]:
        """
        顧客の嗜好を考慮してメニューアイテムを選択

        Args:
            hour (int): 時間 (0-23)
            customer_demographics (Dict[str, Union[str, int]]): 顧客の属性情報
            date (datetime): 対象の日付

        Returns:
            Tuple[List[Dict[str, Any]], List[float]]: 利用可能なアイテムのリストと, それぞれの重み
        """
        available_items: List[Dict[str, Any]] = [item for item in self.menu_items if hour in item["available_hours"]]

        if not available_items:
            return [], []

        # 顧客の嗜好を取得
        preferences: Dict[str, float] = self._get_customer_preferences(
            customer_demographics["gender"],
            customer_demographics["age_group"],
        )

        # 人気度に基づいて重み付け選択
        weights: List[float] = []
        for item in available_items:
            base_weight = self._apply_seasonal_adjustment(item, date)
            category_preference = preferences.get(item["category"], 1.0)
            final_weight = base_weight * category_preference
            weights.append(final_weight)

        return available_items, weights

    def generate_sales_data(self) -> pd.DataFrame:
        """
        売上データを生成

        Returns:
            pd.DataFrame: 売上データを含むDataFrame
        """
        start_date: datetime = datetime.strptime(self.config["data_generation"]["start_date"], "%Y-%m-%d")
        end_date: datetime = datetime.strptime(self.config["data_generation"]["end_date"], "%Y-%m-%d")

        business_hours: Dict[str, Any] = self.config["data_generation"]["business_hours"]
        open_hour: int = business_hours["open"]
        close_hour: int = business_hours["close"]
        closed_days: List[int] = business_hours["closed_days"]

        sales_data: List[Dict[str, Any]] = []
        customer_id_counter: int = self.config["data_generation"]["id_generation"]["customer_id_start"]
        order_id_counter: int = self.config["data_generation"]["id_generation"]["order_id_start"]

        current_date: datetime = start_date
        while current_date <= end_date:
            # 定休日チェック
            if current_date.weekday() in closed_days:
                current_date += timedelta(days=1)
                continue

            # 営業時間内の売上生成
            for hour in range(open_hour, close_hour):
                customers = self._calculate_hourly_customers(current_date, hour)

                if customers == 0:
                    continue

                # 時間帯の顧客パターンを取得
                customer_pattern: Dict[str, Any] = self._get_customer_pattern(current_date, hour)

                # 各顧客の注文を生成
                for customer in range(customers):
                    # 顧客の属性を生成
                    customer_demographics: Dict[str, Union[str, int]] = self._generate_customer_demographics(
                        customer_pattern
                    )

                    available_items, weights = self._select_menu_items_with_preferences(
                        hour, customer_demographics, current_date
                    )

                    if not available_items:
                        continue

                    # 1人あたりの注文数（1-3個）
                    num_orders: int = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])

                    customer_orders: List[Dict[str, Any]] = []
                    for _ in range(num_orders):
                        # 人気度に基づいて商品選択
                        if weights and sum(weights) > 0:
                            normalized_weights: np.ndarray = np.array(weights) / np.sum(weights)
                            selected_item: Dict[str, Any] = np.random.choice(available_items, p=normalized_weights)
                            customer_orders.append(selected_item)

                    # 注文データを記録
                    order_timestamp: datetime = current_date.replace(
                        hour=hour,
                        minute=np.random.randint(0, 60),
                        second=np.random.randint(0, 60),
                    )

                    current_customer_id: int = customer_id_counter
                    current_order_id: int = order_id_counter

                    for item in customer_orders:
                        sales_data.append(
                            {
                                "注文ID": current_order_id,
                                "顧客ID": current_customer_id,
                                "日時": order_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                "日付": current_date.strftime("%Y-%m-%d"),
                                "時間": hour,
                                "曜日": ["月", "火", "水", "木", "金", "土", "日"][current_date.weekday()],
                                "商品ID": item["id"],
                                "商品名": item["name"],
                                "カテゴリ": item["category"],
                                "単価": item["price"],
                                "原価": item["cost"],
                                "利益": item["price"] - item["cost"],
                                "天気": self._get_weather_for_date(current_date),
                                "月": current_date.month,
                                "季節": self._get_season(current_date.month),
                                "性別": "男性" if customer_demographics["gender"] == "male" else "女性",
                                "年代": self._convert_age_group_japanese(customer_demographics["age_group"]),
                                "年齢": customer_demographics["age"],
                                "平日休日": "平日" if current_date.weekday() < 5 else "休日",
                            }
                        )

                    customer_id_counter += 1
                    order_id_counter += 1

            current_date += timedelta(days=1)

        return pd.DataFrame(sales_data)

    def _convert_age_group_japanese(self, age_group: str) -> str:
        """
        年代を日本語に変換

        Args:
            age_group (str): 英語の年代表記

        Returns:
            str: 日本語の年代表記
        """
        conversion: Dict[str, str] = {
            "teens": "10代",
            "twenties": "20代",
            "thirties": "30代",
            "forties": "40代",
            "seniors": "50代以上",
        }
        return conversion.get(age_group, "不明")

    def _get_season(self, month: int) -> str:
        """
        月から季節を判定

        Args:
            month (int): 月 (1-12)

        Returns:
            str: 季節の日本語表記
        """
        if month in [3, 4, 5]:
            return "春"
        elif month in [6, 7, 8]:
            return "夏"
        elif month in [9, 10, 11]:
            return "秋"
        else:
            return "冬"

    def save_data(self, df: pd.DataFrame, output_dir: str = "data") -> None:
        """
        複数形式でデータを保存

        Args:
            df (pd.DataFrame): 保存するDataFrame
            output_dir (str, optional): 出力ディレクトリ. Defaults to "data".
        """
        os.makedirs(output_dir, exist_ok=True)

        # CSV形式
        self._save_csv(df, output_dir)

        # JSON形式
        self._save_json(df, output_dir)

        # XLSX形式
        self._save_xlsx(df, output_dir)

        print(f"\n💾 データ保存完了:")
        print(f"  📁 保存先: {output_dir}")
        print(f"  📄 形式: CSV, JSON, XLSX")

    def _save_csv(self, df: pd.DataFrame, output_dir: str) -> None:
        """
        CSV形式で保存

        Args:
            df (pd.DataFrame): 保存するDataFrame
            output_dir (str): 出力ディレクトリ
        """
        csv_dir: str = os.path.join(output_dir, "csv")
        os.makedirs(csv_dir, exist_ok=True)

        # メイン売上データ
        main_file: str = os.path.join(csv_dir, "cafe_sales_data.csv")
        df.to_csv(main_file, index=False, encoding="utf-8")

        # 日別集計データ
        daily_summary: pd.DataFrame = self._create_daily_summary(df)
        daily_file: str = os.path.join(csv_dir, "daily_summary.csv")
        daily_summary.to_csv(daily_file, index=False, encoding="utf-8")

        # 商品別集計データ
        product_summary: pd.DataFrame = self._create_product_summary(df)
        product_file: str = os.path.join(csv_dir, "product_summary.csv")
        product_summary.to_csv(product_file, index=False, encoding="utf-8")

        # 顧客分析データ
        customer_summary: pd.DataFrame = self._create_customer_summary(df)
        customer_file: str = os.path.join(csv_dir, "customer_summary.csv")
        customer_summary.to_csv(customer_file, index=False, encoding="utf-8")

        print(f"  ✅ CSV保存完了: {csv_dir}")

    def _save_json(self, df: pd.DataFrame, output_dir: str) -> None:
        """
        JSON形式で保存

        Args:
            df (pd.DataFrame): 保存するDataFRame
            output_dir (str): 出力ディレクトリ
        """
        json_dir: str = os.path.join(output_dir, "json")
        os.makedirs(json_dir, exist_ok=True)

        # メインデータをJSONに変換
        main_data: Dict[str, Any] = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_records": len(df),
                "date_range": {"start": df["日付"].min(), "end": df["日付"].max()},
                "total_sales": int(df["単価"].sum()),
                "total_profit": int(df["利益"].sum()),
            },
            "sales_data": df.to_dict("records"),
        }

        main_file: str = os.path.join(json_dir, "cafe_sales_data.json")
        with open(main_file, "w", encoding="utf-8") as f:
            json.dump(main_data, f, ensure_ascii=False, indent=2)

        # 集計データをJSON形式で保存
        summaries: Dict[str, List[Dict[str, Any]]] = {
            "daily_summary": self._create_daily_summary(df).to_dict("records"),
            "product_summary": self._create_product_summary(df).to_dict("records"),
            "customer_summary": self._create_customer_summary(df).to_dict("records"),
        }

        summary_file: str = os.path.join(json_dir, "summaries.json")
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summaries, f, ensure_ascii=False, indent=2)

        print(f"  ✅ JSON保存完了: {json_dir}")

    def _save_xlsx(self, df: pd.DataFrame, output_dir: str) -> None:
        """
        Excel形式で保存

        Args:
            df (pd.DataFrame): 保存するDataFrame
            output_dir (str): 出力ディレクトリ
        """
        try:
            xlsx_dir: str = os.path.join(output_dir, "xlsx")
            os.makedirs(xlsx_dir, exist_ok=True)

            # 複数シートを持つExcelファイルを作成
            excel_file: str = os.path.join(xlsx_dir, "cafe_sales_analysis.xlsx")

            with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
                # メインデータ
                df.to_excel(writer, sheet_name="売上データ", index=False)

                # 各種集計データ
                daily_summary: pd.DataFrame = self._create_daily_summary(df)
                daily_summary.to_excel(writer, sheet_name="日別集計", index=False)

                product_summary: pd.DataFrame = self._create_product_summary(df)
                product_summary.to_excel(writer, sheet_name="商品別集計", index=False)

                customer_summary: pd.DataFrame = self._create_customer_summary(df)
                customer_summary.to_excel(writer, sheet_name="顧客分析", index=False)

                # 性別・年代別分析
                demographic_analysis: pd.DataFrame = self._create_demographic_analysis(df)
                demographic_analysis.to_excel(writer, sheet_name="性別年代分析", index=False)

            print(f"  ✅ XLSX保存完了: {xlsx_dir}")

        except ImportError:
            print("  ⚠️  XLSX保存にはopenpyxlが必要です。pip install openpyxlを実行してください。")
        except Exception as e:
            print(f"  ❌ XLSX保存エラー: {e}")

    def _create_daily_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        日別集計データを作成

        Args:
            df (pd.DataFrame): 元の売上データ

        Returns:
            pd.DataFrame: 日別に集計されたDataFrame
        """
        daily_summary = (
            df.groupby(["日付", "曜日", "天気", "季節", "平日休日"])
            .agg({"単価": ["count", "sum", "mean"], "利益": "sum", "顧客ID": "nunique"})
            .round(2)
        )

        # カラム名を整理
        daily_summary.columns = ["注文件数", "売上合計", "平均単価", "利益合計", "ユニーク顧客数"]

        return daily_summary.reset_index()

    def _create_product_summary(self, df: pd.DateOffset) -> pd.DataFrame:
        """
        商品別集計データを作成

        Args:
            df (pd.DateOffset): 元の売上データ

        Returns:
            pd.DataFrame: 商品別に集計されたDataFrame
        """
        product_summary = (
            df.groupby(["商品名", "カテゴリ"]).agg({"単価": ["count", "mean"], "利益": ["sum", "mean"]}).round(2)
        )

        # カラム名を整理
        product_summary.columns = ["販売回数", "平均単価", "利益合計", "平均利益"]
        product_summary = product_summary.reset_index()
        return product_summary.sort_values("販売回数", ascending=False)

    def _create_customer_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        顧客分析データを作成

        Args:
            df (pd.DataFrame): 元の売上データ

        Returns:
            pd.DataFrame: 顧客属性別に集計されたDataFrame
        """
        customer_summary = (
            df.groupby(["性別", "年代"])
            .agg({"単価": ["count", "sum", "mean"], "利益": "sum", "顧客ID": "nunique"})
            .round(2)
        )

        customer_summary.columns = ["注文回数", "売上合計", "平均単価", "利益合計", "ユニーク顧客数"]
        return customer_summary.reset_index()

    def _create_demographic_analysis(self, df: pd.DataFRame) -> pd.DataFrame:
        """
        性別・年代別詳細分析

        Args:
            df (pd.DataFRame): 元の売上データ

        Returns:
            pd.DataFrame: 性別・年代・カテゴリ別に分析されたDataFrame
        """
        analysis = (
            df.groupby(["性別", "年代", "カテゴリ"]).agg({"単価": ["count", "sum"], "顧客ID": "nunique"}).round(2)
        )

        analysis.columns = ["注文回数", "売上", "顧客数"]
        return analysis.reset_index()

    def display_data_info(self, df: pd.DataFrame) -> None:
        """
        生成されたデータの基本情報を表示

        Args:
            df (pd.DataFrame): 表示するDataFrame
        """
        print("\n" + "=" * 60)
        print("📊 カフェ売上データの概要")
        print("=" * 60)

        print(f"📅 データ期間: {df['日付'].min()} ～ {df['日付'].max()}")
        print(f"📈 総レコード数: {len(df):,}件")
        print(f"💰 総売上: ¥{df['単価'].sum():,}")
        print(f"💵 総利益: ¥{df['利益'].sum():,}")
        print(f"🏪 平均単価: ¥{df['単価'].mean():.0f}")
        print(f"👥 ユニーク顧客数: {df['顧客ID'].nunique():,}人")

        print(f"\n👫 性別分布:")
        gender_dist = df["性別"].value_counts()
        for gender, count in gender_dist.items():
            percentage = (count / len(df)) * 100
            print(f"  {gender}: {count:,}件 ({percentage:.1f}%)")

        print(f"\n🎂 年代分布:")
        age_dist = df["年代"].value_counts().sort_index()
        for age, count in age_dist.items():
            percentage = (count / len(df)) * 100
            print(f"  {age}: {count:,}件 ({percentage:.1f}%)")

        print(f"\n📊 カテゴリ別売上:")
        category_sales = df.groupby("カテゴリ")["単価"].sum().sort_values(ascending=False)
        for category, sales in category_sales.items():
            print(f"  {category}: ¥{sales:,}")

        print(f"\n🔍 データサンプル（最初の10行）:")
        print(df[["日時", "商品名", "性別", "年代", "単価"]].head(10))


def main() -> None:
    """
    メイン実行関数

    カフェ売上データの生成から保存、情報表示までを実行
    """
    print("🏪 カフェ売上データ生成ツール（第1章用）")
    print("=" * 60)

    try:
        # データ生成器を初期化
        generator = CafeDataGenerator()

        # データ生成
        print("📊 売上データを生成中...")
        sales_df = generator.generate_sales_data()

        # データ情報表示
        generator.display_data_info(sales_df)

        # データ保存
        print("\n💾 データを保存中...")
        generator.save_data(sales_df)

        print("\n🎉 データ生成が完了しました！")
        print("\n📋 次のステップ:")
        print("1. data/csv/ フォルダでCSVファイルを確認")
        print("2. data/json/ フォルダでJSON形式を確認")
        print("3. data/xlsx/ フォルダでExcelファイルを開いて分析")
        print("4. 顧客の性別・年代別の購買傾向を分析してみましょう")

        print("\n🔍 分析のヒント:")
        print("- 性別・年代によって好まれる商品カテゴリが異なるか確認")
        print("- 時間帯と顧客属性の関係を調べる")
        print("- 季節と年代の関係を分析する")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        print("config.yamlファイルとrequirements.txtの内容を確認してください")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
