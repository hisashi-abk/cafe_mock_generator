#!/usr/bin/env python3
"""
カフェ売上モックデータ生成器 (RDB対応版)
Python学習者向け機械学習チュートリアル - 第1章用

機能:
- 正規化されたテーブル構造でのデータ生成
- CSV/JSON/XLSX/DB形式での出力対応
- リアルなビジネスパターンの実装
- 機械学習用特徴量の自動生成
"""

import yaml
import pandas as pd
import numpy as np
import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import random
from dataclasses import dataclass
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()

@dataclass
class GeneratedData:
    """生成されたデータを格納するデータクラス"""
    customers: pd.DataFrame
    menu_items: pd.DataFrame
    categories: pd.DataFrame
    orders: pd.DataFrame
    order_items: pd.DataFrame
    daily_summary: pd.DataFrame

class CafeDataGenerator:
    """カフェ売上データ生成クラス"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """初期化"""
        self.config = self._load_config(config_path)
        self.data: Optional[GeneratedData] = None
        self.engine = None
        
        # データ生成用の設定を解析
        self._parse_config()
        
        # 出力ディレクトリの作成
        self._create_output_directories()
        
    def _load_config(self, config_path: str) -> Dict:
        """設定ファイルの読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"設定ファイルが見つかりません: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"YAML解析エラー: {e}")
            raise
    
    def _parse_config(self):
        """設定の解析と変数への格納"""
        gen_config = self.config['data_generation']
        self.start_date = datetime.strptime(gen_config['start_date'], '%Y-%m-%d')
        self.end_date = datetime.strptime(gen_config['end_date'], '%Y-%m-%d')
        self.business_hours = gen_config['business_hours']
        self.base_customers_per_hour = gen_config['base_customers_per_hour']
        
    def _create_output_directories(self):
        """出力ディレクトリの作成"""
        paths = self.config['output']['file_paths']
        for dir_path in paths.values():
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            
    def _setup_database(self):
        """データベース接続の設定"""
        db_config = self.config['database']
        engine_type = db_config['default_engine']
        
        if engine_type == 'sqlite':
            db_path = db_config['connections']['sqlite']['path']
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            self.engine = create_engine(f'sqlite:///{db_path}')
        elif engine_type == 'postgresql':
            # 環境変数から接続情報を取得（実装例）
            conn_str = "postgresql://user:password@localhost:5432/cafe_mock_sales"
            self.engine = create_engine(conn_str)
        else:
            logger.warning(f"未対応のDB: {engine_type}, SQLiteを使用します")
            self.engine = create_engine('sqlite:///data/cafe_mock_sales.db')
            
    def generate_categories(self) -> pd.DataFrame:
        """カテゴリマスターの生成"""
        categories = []
        for category in self.config['menu']['categories']:
            categories.append({
                'category_id': category['id'],
                'category_name': category['name'],
                'description': category['description'],
                'created_at': datetime.now()
            })
        return pd.DataFrame(categories)
        
    def generate_menu_items(self) -> pd.DataFrame:
        """メニューマスターの生成"""
        menu_items = []
        for item in self.config['menu']['items']:
            menu_items.append({
                'menu_id': item['id'],
                'category_id': item['category_id'],
                'item_name': item['name'],
                'price': item['price'],
                'cost': item['cost'],
                'profit_margin': (item['price'] - item['cost']) / item['price'],
                'available_hours': json.dumps(item['available_hours']),
                'popularity_weight': item['popularity_weight'],
                'is_seasonal': item.get('is_seasonal', False),
                'seasonal_preference': item.get('seasonal_preference', ''),
                'seasonal_multiplier': item.get('seasonal_multiplier', 1.0),
                'created_at': datetime.now()
            })
        return pd.DataFrame(menu_items)
        
    def generate_customers(self, num_customers: int = 500) -> pd.DataFrame:
        """顧客マスターの生成"""
        customers = []
        customer_config = self.config['customers']
        
        start_id = self.config['data_generation']['id_generation']['customer_id_start']
        
        for i in range(num_customers):
            # 年齢層の決定
            age_group = np.random.choice(
                [ag['name'] for ag in customer_config['age_groups']],
                p=[ag['base_ratio'] for ag in customer_config['age_groups']]
            )
            age_group_info = next(ag for ag in customer_config['age_groups'] if ag['name'] == age_group)
            age = np.random.randint(age_group_info['min_age'], age_group_info['max_age'] + 1)
            
            # 性別の決定
            gender = np.random.choice(['male', 'female'], 
                                   p=[customer_config['gender_distribution']['male'],
                                      customer_config['gender_distribution']['female']])
            
            # 顧客属性の決定
            visit_frequency = np.random.choice(['regular', 'occasional', 'rare'], p=[0.3, 0.5, 0.2])
            avg_order_value = np.random.normal(800, 200)  # 平均800円、標準偏差200円
            
            customers.append({
                'customer_id': start_id + i,
                'age': age,
                'age_group': age_group,
                'gender': gender,
                'visit_frequency': visit_frequency,
                'average_order_value': max(300, avg_order_value),  # 最低300円
                'registration_date': self.start_date + timedelta(days=np.random.randint(0, 365)),
                'is_active': True,
                'created_at': datetime.now()
            })
            
        return pd.DataFrame(customers)
        
    def _get_weather_for_date(self, date: datetime) -> Tuple[str, float]:
        """日付に基づく天気の生成（簡易版）"""
        # 季節に応じた天気パターン
        month = date.month
        if month in [12, 1, 2]:  # 冬
            weather_probs = {'sunny': 0.4, 'cloudy': 0.3, 'rainy': 0.2, 'snowy': 0.1}
            temp_base = 5
        elif month in [3, 4, 5]:  # 春
            weather_probs = {'sunny': 0.5, 'cloudy': 0.3, 'rainy': 0.2, 'snowy': 0.0}
            temp_base = 15
        elif month in [6, 7, 8]:  # 夏
            weather_probs = {'sunny': 0.6, 'cloudy': 0.2, 'rainy': 0.2, 'snowy': 0.0}
            temp_base = 25
        else:  # 秋
            weather_probs = {'sunny': 0.5, 'cloudy': 0.3, 'rainy': 0.2, 'snowy': 0.0}
            temp_base = 15
            
        weather = np.random.choice(list(weather_probs.keys()), p=list(weather_probs.values()))
        temperature = temp_base + np.random.normal(0, 5)
        
        return weather, temperature
        
    def _calculate_demand_multiplier(self, date: datetime, hour: int, weather: str) -> float:
        """需要の乗数を計算"""
        multiplier = 1.0
        
        # 曜日係数
        weekday = date.weekday()
        if weekday in self.config['data_generation']:
            multiplier *= self.config['data_generation'][weekday]
            
        # 時間帯係数
        hour_multipliers = self.config['data_generation']['hour_multiplier']
        if hour in hour_multipliers:
            multiplier *= hour_multipliers[hour]
            
        # 天気係数
        weather_multipliers = self.config['data_generation']['weather_multiplier']
        if weather in weather_multipliers:
            multiplier *= weather_multipliers[weather]
            
        # 季節係数
        seasonal_multipliers = self.config['data_generation']['seasonal_multiplier']
        if date.month in seasonal_multipliers:
            multiplier *= seasonal_multipliers[date.month]
            
        # 特別イベント
        date_str = date.strftime('%Y-%m-%d')
        for event in self.config['data_generation']['special_events']:
            if event['date'] == date_str:
                multiplier *= event['multiplier']
                break
                
        return multiplier
        
    def generate_orders_and_items(self, customers_df: pd.DataFrame, menu_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """注文と注文詳細の生成"""
        orders = []
        order_items = []
        
        order_id_start = self.config['data_generation']['id_generation']['order_id_start']
        order_id = order_id_start
        
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # 定休日チェック
            if current_date.weekday() in self.config['data_generation']['business_hours']['closed_days']:
                current_date += timedelta(days=1)
                continue
                
            # その日の天気を取得
            weather, temperature = self._get_weather_for_date(current_date)
            
            # 営業時間内でのループ
            for hour in range(self.business_hours['open'], self.business_hours['close']):
                current_datetime = current_date.replace(hour=hour)
                
                # その時間の需要乗数を計算
                demand_multiplier = self._calculate_demand_multiplier(current_date, hour, weather)
                expected_customers = int(self.base_customers_per_hour * demand_multiplier)
                
                # 実際の来客数（ポアソン分布でばらつきを追加）
                actual_customers = max(0, np.random.poisson(expected_customers))
                
                # 各来客に対して注文を生成
                for _ in range(actual_customers):
                    # 顧客を選択
                    customer = customers_df.sample(1).iloc[0]
                    
                    # 注文を作成
                    order = {
                        'order_id': order_id,
                        'customer_id': customer['customer_id'],
                        'order_datetime': current_datetime + timedelta(minutes=np.random.randint(0, 60)),
                        'weather_condition': weather,
                        'temperature': temperature,
                        'is_weekend': current_date.weekday() >= 5,
                        'created_at': datetime.now()
                    }
                    
                    # その時間帯に利用可能なメニューをフィルタ
                    available_menu = menu_df[menu_df['available_hours'].str.contains(str(hour))]
                    
                    # 顧客の嗜好に基づいてメニューを選択
                    selected_items = self._select_menu_items(customer, available_menu, current_date)
                    
                    # 注文詳細を作成
                    total_amount = 0
                    for item_id, quantity in selected_items.items():
                        item_info = menu_df[menu_df['menu_id'] == item_id].iloc[0]
                        subtotal = item_info['price'] * quantity
                        total_amount += subtotal
                        
                        order_items.append({
                            'order_id': order_id,
                            'menu_id': item_id,
                            'quantity': quantity,
                            'unit_price': item_info['price'],
                            'subtotal': subtotal,
                            'created_at': datetime.now()
                        })
                    
                    order['total_amount'] = total_amount
                    orders.append(order)
                    order_id += 1
                    
            current_date += timedelta(days=1)
            
            # 進捗表示
            if current_date.day == 1:
                logger.info(f"データ生成中: {current_date.strftime('%Y-%m')}")
                
        return pd.DataFrame(orders), pd.DataFrame(order_items)
        
    def _select_menu_items(self, customer: pd.Series, available_menu: pd.DataFrame, order_date: datetime) -> Dict[int, int]:
        """顧客属性に基づいてメニューアイテムを選択"""
        selected_items = {}
        
        # 顧客の嗜好を取得
        preferences = self.config['customers']['preferences'][customer['gender']][customer['age_group']]
        
        # カテゴリ別の重みを計算
        category_weights = []
        categories = self.config['menu']['categories']
        
        for category in categories:
            category_name = category['name']
            weight = preferences.get(category_name, 1.0)
            category_weights.append(weight)
            
        # メイン商品を選択（必ず1つ）
        if len(available_menu) > 0:
            # 人気度と顧客嗜好を組み合わせた重み
            weights = []
            for _, item in available_menu.iterrows():
                base_weight = item['popularity_weight']
                
                # 季節商品の調整
                if item['is_seasonal']:
                    season_mult = self._get_seasonal_multiplier(order_date, item['seasonal_preference'])
                    base_weight *= season_mult
                    
                weights.append(base_weight)
            
            # 正規化
            if sum(weights) > 0:
                weights = np.array(weights) / sum(weights)
                selected_item = np.random.choice(available_menu.index, p=weights)
                item_id = available_menu.loc[selected_item, 'menu_id']
                selected_items[item_id] = 1
                
                # 追加注文の可能性（20%の確率）
                if np.random.random() < 0.2:
                    additional_item = np.random.choice(available_menu.index, p=weights)
                    additional_id = available_menu.loc[additional_item, 'menu_id']
                    if additional_id in selected_items:
                        selected_items[additional_id] += 1
                    else:
                        selected_items[additional_id] = 1
                        
        return selected_items
        
    def _get_seasonal_multiplier(self, date: datetime, seasonal_preference: str) -> float:
        """季節による乗数を取得"""
        month = date.month
        
        if seasonal_preference == 'summer' and month in [6, 7, 8]:
            return 1.5
        elif seasonal_preference == 'winter' and month in [12, 1, 2]:
            return 1.3
        elif seasonal_preference == 'spring' and month in [3, 4, 5]:
            return 1.2
        elif seasonal_preference == 'autumn' and month in [9, 10, 11]:
            return 1.2
        else:
            return 1.0
            
    def generate_daily_summary(self, orders_df: pd.DataFrame, order_items_df: pd.DataFrame) -> pd.DataFrame:
        """日次集計データの生成"""
        # 注文データと注文詳細データを結合
        order_summary = orders_df.merge(
            order_items_df.groupby('order_id').agg({
                'subtotal': 'sum',
                'quantity': 'sum'
            }).reset_index(),
            on='order_id'
        )
        
        # 日次でグループ化
        daily_summary = order_summary.groupby(order_summary['order_datetime'].dt.date).agg({
            'order_id': 'count',  # 注文数
            'customer_id': 'nunique',  # ユニーク顧客数
            'subtotal': 'sum',  # 売上合計
            'quantity': 'sum',  # 販売個数
            'temperature': 'mean',  # 平均気温
            'weather_condition': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'unknown',  # 最頻天気
            'is_weekend': lambda x: x.iloc[0]  # 週末フラグ
        }).reset_index()
        
        # カラム名を変更
        daily_summary.columns = [
            'date', 'total_orders', 'unique_customers', 'total_sales', 
            'total_items_sold', 'avg_temperature', 'weather_condition', 'is_weekend'
        ]
        
        # 追加の集計指標
        daily_summary['avg_order_value'] = daily_summary['total_sales'] / daily_summary['total_orders']
        daily_summary['avg_items_per_order'] = daily_summary['total_items_sold'] / daily_summary['total_orders']
        daily_summary['created_at'] = datetime.now()
        
        return daily_summary
        
    def generate_all_data(self) -> GeneratedData:
        """全データの生成"""
        logger.info("データ生成を開始します...")
        
        # 1. マスターデータの生成
        logger.info("カテゴリマスターを生成中...")
        categories_df = self.generate_categories()
        
        logger.info("メニューマスターを生成中...")
        menu_df = self.generate_menu_items()
        
        logger.info("顧客マスターを生成中...")
        customers_df = self.generate_customers()
        
        # 2. トランザクションデータの生成
        logger.info("注文データを生成中...")
        orders_df, order_items_df = self.generate_orders_and_items(customers_df, menu_df)
        
        # 3. 集計データの生成
        logger.info("日次集計データを生成中...")
        daily_summary_df = self.generate_daily_summary(orders_df, order_items_df)
        
        # データ品質の調整（ノイズ注入）
        if self.config['data_quality']['noise_injection']['missing_data_rate'] > 0:
            logger.info("データ品質調整中（学習用ノイズ注入）...")
            orders_df, order_items_df = self._inject_noise(orders_df, order_items_df)
        
        self.data = GeneratedData(
            customers=customers_df,
            menu_items=menu_df,
            categories=categories_df,
            orders=orders_df,
            order_items=order_items_df,
            daily_summary=daily_summary_df
        )
        
        logger.info(f"データ生成完了!")
        logger.info(f"  - 顧客数: {len(customers_df)}")
        logger.info(f"  - 注文数: {len(orders_df)}")
        logger.info(f"  - 注文詳細数: {len(order_items_df)}")
        logger.info(f"  - 集計データ日数: {len(daily_summary_df)}")
        
        return self.data
        
    def _inject_noise(self, orders_df: pd.DataFrame, order_items_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """学習用のノイズ注入"""
        noise_config = self.config['data_quality']['noise_injection']
        
        # 欠損値の注入
        missing_rate = noise_config['missing_data_rate']
        if missing_rate > 0:
            # 注文データの一部を欠損にする
            missing_indices = np.random.choice(
                orders_df.index, 
                size=int(len(orders_df) * missing_rate), 
                replace=False
            )
            orders_df.loc[missing_indices, 'temperature'] = np.nan
            
        # 異常値の注入
        outlier_rate = noise_config['outlier_rate']
        if outlier_rate > 0:
            outlier_indices = np.random.choice(
                order_items_df.index,
                size=int(len(order_items_df) * outlier_rate),
                replace=False
            )
            # 価格を10倍にして異常値とする
            order_items_df.loc[outlier_indices, 'unit_price'] *= 10
            order_items_df.loc[outlier_indices, 'subtotal'] *= 10
            
        return orders_df, order_items_df
        
    def export_data(self):
        """データのエクスポート"""
        if self.data is None:
            logger.error("データが生成されていません。generate_all_data()を先に実行してください。")
            return
            
        output_formats = self.config['output']['formats']
        
        for format_type in output_formats:
            if format_type == 'csv':
                self._export_csv()
            elif format_type == 'json':
                self._export_json()
            elif format_type == 'xlsx':
                self._export_xlsx()
            elif format_type == 'db':
                self._export_database()
            else:
                logger.warning(f"未対応の出力形式: {format_type}")
                
    def _export_csv(self):
        """CSV形式でのエクスポート"""
        csv_dir = self.config['output']['file_paths']['csv_dir']
        encoding = self.config['output']['encoding']
        
        tables = {
            'customers': self.data.customers,
            'categories': self.data.categories,
            'menu_items': self.data.menu_items,
            'orders': self.data.orders,
            'order_items': self.data.order_items,
            'daily_summary': self.data.daily_summary
        }
        
        for table_name, df in tables.items():
            file_path = os.path.join(csv_dir, f"{table_name}.csv")
            df.to_csv(file_path, index=False, encoding=encoding)
            logger.info(f"CSV出力完了: {file_path}")
            
    def _export_json(self):
        """JSON形式でのエクスポート"""
        json_dir = self.config['output']['file_paths']['json_dir']
        
        tables = {
            'customers': self.data.customers,
            'categories': self.data.categories,
            'menu_items': self.data.menu_items,
            'orders': self.data.orders,
            'order_items': self.data.order_items,
            'daily_summary': self.data.daily_summary
        }
        
        for table_name, df in tables.items():
            file_path = os.path.join(json_dir, f"{table_name}.json")
            # datetimeをstrに変換
            df_json = df.copy()
            for col in df_json.columns:
                if df_json[col].dtype == 'datetime64[ns]':
                    df_json[col] = df_json[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            df_json.to_json(file_path, orient='records', force_ascii=False, indent=2)
            logger.info(f"JSON出力完了: {file_path}")
            
    def _export_xlsx(self):
        """Excel形式でのエクスポート"""
        xlsx_dir = self.config['output']['file_paths']['xlsx_dir']
        file_path = os.path.join(xlsx_dir, "cafe_mock_data.xlsx")
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            self.data.customers.to_excel(writer, sheet_name='customers', index=False)
            self.data.categories.to_excel(writer, sheet_name='categories', index=False)
            self.data.menu_items.to_excel(writer, sheet_name='menu_items', index=False)
            self.data.orders.to_excel(writer, sheet_name='orders', index=False)
            self.data.order_items.to_excel(writer, sheet_name='order_items', index=False)
            self.data.daily_summary.to_excel(writer, sheet_name='daily_summary', index=False)
            
        logger.info(f"Excel出力完了: {file_path}")
        
    def _export_database(self):
        """データベースへのエクスポート"""
        self._setup_database()
        
        if self.engine is None:
            logger.error("データベース接続に失敗しました")
            return
            
        try:
            # テーブルの作成とデータ投入
            self.data.categories.to_sql('categories', self.engine, if_exists='replace', index=False)
            self.data.menu_items.to_sql('menu_items', self.engine, if_exists='replace', index=False)
            self.data.customers.to_sql('customers', self.engine, if_exists='replace', index=False)
            self.data.orders.to_sql('orders', self.engine, if_exists='replace', index=False)
            self.data.order_items.to_sql('order_items', self.engine, if_exists='replace', index=False)
            self.data.daily_summary.to_sql('daily_summary', self.engine, if_exists='replace', index=False)
            
            logger.info("データベース出力完了")
            
        except Exception as e:
            logger.error(f"データベース出力エラー: {e}")

def main():
    """メイン処理"""
    try:
        # データ生成器の初期化
        generator = CafeDataGenerator("config.yaml")
        
        # データ生成
        data = generator.generate_all_data()
        
        # データのエクスポート
        generator.export_data()
        
        print("\n=== データ生成が完了しました！ ===")
        print("次のステップ:")
        print("1. data/csv/ フォルダの中身を確認してみましょう")
        print("2. pandas を使ってデータを読み込んでみましょう:")
        print("   import pandas as pd")
        print("   df = pd.read_csv('data/csv/daily_summary.csv')")
        print("   print(df.head())")
        print("3. matplotlib でグラフを作成してみましょう！")
        
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        raise

if __name__ == "__main__":
    main()