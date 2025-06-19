#!/usr/bin/env python3
"""
カフェ売上モックデータ生成スクリプト（第1章用）
Python初学者向けの簡潔版

機能:
- config.yamlからの設定読み込み
- 基本的な売上データ生成
- CSV形式での出力
- 一目で分かるデータ構造
"""

import yaml
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os


class CafeDataGenerator:
    """カフェ売上データ生成クラス（第1章用簡易版）"""
    
    def __init__(self, config_path="config.yaml"):
        """設定ファイルを読み込んで初期化"""
        self.config = self._load_config(config_path)
        self.menu_items = self._prepare_menu_items()
        
    def _load_config(self, config_path):
        """YAML設定ファイルを読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"設定ファイル {config_path} が見つかりません")
            raise
        except yaml.YAMLError as e:
            print(f"YAML読み込みエラー: {e}")
            raise
    
    def _prepare_menu_items(self):
        """メニューアイテムを扱いやすい形式に変換"""
        items = []
        categories = {cat['id']: cat['name'] for cat in self.config['menu']['categories']}
        
        for item in self.config['menu']['items']:
            items.append({
                'id': item['id'],
                'name': item['name'],
                'category': categories[item['category_id']],
                'price': item['price'],
                'cost': item['cost'],
                'available_hours': item['available_hours'],
                'popularity': item['popularity_weight']
            })
        return items
    
    def _get_weather_for_date(self, date):
        """日付に基づいて天気を決定（簡易版）"""
        # 実際のアプリでは天気APIを使用
        weather_options = ['sunny', 'cloudy', 'rainy', 'snowy']
        weights = [0.4, 0.3, 0.2, 0.1]  # 晴れが多め
        
        # 冬は雪の確率を上げる
        if date.month in [12, 1, 2]:
            weights = [0.3, 0.3, 0.2, 0.2]
        
        return np.random.choice(weather_options, p=weights)
    
    def _calculate_hourly_customers(self, date, hour):
        """時間帯別の来客数を計算"""
        base_customers = self.config['data_generation']['base_customers_per_hour']
        
        # 曜日係数（月曜=0, 日曜=6）
        weekday = date.weekday()
        day_multiplier = self.config['data_generation'].get(weekday, 1.0)
        
        # 時間帯係数
        hour_multiplier = self.config['data_generation']['hour_multiplier'].get(hour, 1.0)
        
        # 天気係数
        weather = self._get_weather_for_date(date)
        weather_multiplier = self.config['data_generation']['weather_multiplier'].get(weather, 1.0)
        
        # 季節係数
        seasonal_multiplier = self.config['data_generation']['seasonal_multiplier'].get(date.month, 1.0)
        
        # 最終来客数計算
        customers = base_customers * day_multiplier * hour_multiplier * weather_multiplier * seasonal_multiplier
        
        # ポアソン分布でランダム性を追加
        return max(0, np.random.poisson(customers))
    
    def _select_menu_items(self, hour):
        """時間帯に応じてメニューアイテムを選択"""
        available_items = [item for item in self.menu_items if hour in item['available_hours']]
        
        if not available_items:
            return []
        
        # 人気度に基づいて重み付け選択
        weights = [item['popularity'] for item in available_items]
        return available_items, weights
    
    def generate_sales_data(self):
        """売上データを生成"""
        start_date = datetime.strptime(self.config['data_generation']['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(self.config['data_generation']['end_date'], '%Y-%m-%d')
        
        business_hours = self.config['data_generation']['business_hours']
        open_hour = business_hours['open']
        close_hour = business_hours['close']
        closed_days = business_hours['closed_days']
        
        sales_data = []
        
        current_date = start_date
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
                
                available_items, weights = self._select_menu_items(hour)
                if not available_items:
                    continue
                
                # 各顧客の注文を生成
                for customer in range(customers):
                    # 1人あたりの注文数（1-3個）
                    num_orders = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
                    
                    customer_orders = []
                    for _ in range(num_orders):
                        # 人気度に基づいて商品選択
                        selected_item = np.random.choice(available_items, p=np.array(weights)/np.sum(weights))
                        customer_orders.append(selected_item)
                    
                    # 注文データを記録
                    for item in customer_orders:
                        timestamp = current_date.replace(
                            hour=hour, 
                            minute=np.random.randint(0, 60),
                            second=np.random.randint(0, 60)
                        )
                        
                        sales_data.append({
                            '日時': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            '日付': current_date.strftime('%Y-%m-%d'),
                            '時間': hour,
                            '曜日': ['月', '火', '水', '木', '金', '土', '日'][current_date.weekday()],
                            '商品ID': item['id'],
                            '商品名': item['name'],
                            'カテゴリ': item['category'],
                            '単価': item['price'],
                            '原価': item['cost'],
                            '利益': item['price'] - item['cost'],
                            '天気': self._get_weather_for_date(current_date),
                            '月': current_date.month,
                            '季節': self._get_season(current_date.month)
                        })
            
            current_date += timedelta(days=1)
        
        return pd.DataFrame(sales_data)
    
    def _get_season(self, month):
        """月から季節を判定"""
        if month in [3, 4, 5]:
            return '春'
        elif month in [6, 7, 8]:
            return '夏'
        elif month in [9, 10, 11]:
            return '秋'
        else:
            return '冬'
    
    def save_data(self, df, output_dir="data"):
        """データをCSV形式で保存"""
        os.makedirs(output_dir, exist_ok=True)
        
        # メインの売上データ
        main_file = os.path.join(output_dir, "cafe_sales_data.csv")
        df.to_csv(main_file, index=False, encoding='utf-8')
        print(f"売上データを保存しました: {main_file}")
        
        # 日別集計データ（分析しやすいように）
        daily_summary = self._create_daily_summary(df)
        daily_file = os.path.join(output_dir, "daily_summary.csv")
        daily_summary.to_csv(daily_file, index=False, encoding='utf-8')
        print(f"日別集計データを保存しました: {daily_file}")
        
        # 商品別集計データ
        product_summary = self._create_product_summary(df)
        product_file = os.path.join(output_dir, "product_summary.csv")
        product_summary.to_csv(product_file, index=False, encoding='utf-8')
        print(f"商品別集計データを保存しました: {product_file}")
    
    def _create_daily_summary(self, df):
        """日別集計データを作成"""
        daily_summary = df.groupby(['日付', '曜日', '天気', '季節']).agg({
            '単価': ['count', 'sum', 'mean'],
            '利益': 'sum'
        }).round(2)
        
        # カラム名を整理
        daily_summary.columns = ['注文件数', '売上合計', '平均単価', '利益合計']
        daily_summary = daily_summary.reset_index()
        
        return daily_summary
    
    def _create_product_summary(self, df):
        """商品別集計データを作成"""
        product_summary = df.groupby(['商品名', 'カテゴリ']).agg({
            '単価': ['count', 'mean'],
            '利益': ['sum', 'mean']
        }).round(2)
        
        # カラム名を整理
        product_summary.columns = ['販売回数', '平均単価', '利益合計', '平均利益']
        product_summary = product_summary.reset_index()
        product_summary = product_summary.sort_values('販売回数', ascending=False)
        
        return product_summary
    
    def display_data_info(self, df):
        """生成されたデータの基本情報を表示"""
        print("\n" + "="*50)
        print("📊 生成されたデータの概要")
        print("="*50)
        
        print(f"データ期間: {df['日付'].min()} ～ {df['日付'].max()}")
        print(f"総レコード数: {len(df):,}件")
        print(f"総売上: ¥{df['単価'].sum():,}")
        print(f"総利益: ¥{df['利益'].sum():,}")
        print(f"平均単価: ¥{df['単価'].mean():.0f}")
        
        print("\n📈 カテゴリ別売上:")
        category_sales = df.groupby('カテゴリ')['単価'].sum().sort_values(ascending=False)
        for category, sales in category_sales.items():
            print(f"  {category}: ¥{sales:,}")
        
        print("\n📅 曜日別平均売上:")
        weekday_sales = df.groupby('曜日')['単価'].sum()
        weekday_order = ['月', '火', '水', '木', '金', '土', '日']
        for day in weekday_order:
            if day in weekday_sales:
                print(f"  {day}曜日: ¥{weekday_sales[day]:,}")
        
        print(f"\nデータの最初の5行:")
        print(df.head())


def main():
    """メイン実行関数"""
    print("🏪 カフェ売上データ生成ツール（第1章用）")
    print("="*50)
    
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
        
        print("\n✅ データ生成が完了しました！")
        print("\n次のステップ:")
        print("1. data/cafe_sales_data.csv をExcelやPandasで開いてみましょう")
        print("2. data/daily_summary.csv で日別の傾向を確認しましょう")
        print("3. data/product_summary.csv で人気商品をチェックしましょう")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        print("config.yamlファイルが正しく配置されているか確認してください")


if __name__ == "__main__":
    main()
