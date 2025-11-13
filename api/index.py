from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import yfinance as yf
from supabase import create_client, Client

# Import local modules from api directory
from earnings_scraper import get_earnings_materials, get_company_name

app = Flask(__name__)
CORS(app)

# Supabase設定
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://lvlqrnrsnuxqmxqvfyjd.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2bHFybnJzbnV4cW14cXZmeWpkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4MjY5MjYsImV4cCI6MjA3ODQwMjkyNn0.S1krcgZVM0qiovk6ZxRSHaY3KLRWBfVw71h-qYwHnMw')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_stock_master():
    """
    株式マスターデータを読み込む

    優先順位:
    1. Supabaseから取得（本番環境推奨）
    2. ローカルJSONファイル（フォールバック）
    """
    try:
        # Supabaseから取得を試みる（全件取得するため limit を大きくする）
        # PostgRESTのデフォルトは1000件なので、limitを10000に設定
        response = supabase.table('stock_master').select('code, name').limit(10000).execute()
        if response.data and len(response.data) > 0:
            print(f"Loaded {len(response.data)} stocks from Supabase")
            return response.data
    except Exception as e:
        print(f"Supabaseからの読み込みに失敗、ローカルファイルを使用: {e}")

    # フォールバック: ローカルJSONファイルから読み込む
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        stock_master_path = os.path.join(current_dir, 'stock_master.json')
        with open(stock_master_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Loaded {len(data)} stocks from local file")
            return data
    except Exception as e:
        print(f"株式マスターの読み込みエラー: {e}")
        return []

def get_market_cap(stock_code):
    """
    証券コードから時価総額を取得

    Parameters:
        stock_code (str): 4桁の証券コード

    Returns:
        dict: 時価総額情報（円建て）または None
    """
    try:
        # 日本株はティッカーシンボルに.Tを付ける
        ticker = yf.Ticker(f"{stock_code}.T")
        info = ticker.info

        # 時価総額を取得（デフォルトはUSDなので円に変換）
        market_cap = info.get('marketCap')

        if market_cap:
            # 億円単位に変換（小数点以下切り捨て）
            market_cap_oku = int(market_cap / 100000000)
            return {
                "market_cap": market_cap,
                "market_cap_oku": market_cap_oku,
                "currency": "JPY"
            }
        return None
    except Exception as e:
        print(f"時価総額取得エラー: {e}")
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    return jsonify({"status": "ok"})

@app.route('/api/search', methods=['GET'])
def search_companies():
    """
    企業名または証券コードで検索

    Parameters:
        query (str): 検索クエリ（企業名の一部または証券コード）

    Returns:
        JSON形式の検索結果リスト
    """
    query = request.args.get('query', '').strip()

    if not query:
        return jsonify({"error": "検索キーワードを入力してください"}), 400

    stock_master = load_stock_master()
    results = []

    # 証券コードで検索（完全一致）
    if query.isdigit():
        for stock in stock_master:
            if stock['code'] == query:
                results.append(stock)

    # 企業名で検索（部分一致）
    if not results:
        for stock in stock_master:
            if query in stock['name']:
                results.append(stock)

    return jsonify({"results": results[:20]})  # 最大20件まで

@app.route('/api/earnings/<stock_code>', methods=['GET'])
def get_earnings(stock_code):
    """
    証券コードから決算説明会資料を取得するエンドポイント

    Parameters:
        stock_code (str): 4桁の証券コード（例: 7203）

    Returns:
        JSON形式の決算資料リスト（過去5年分）
    """
    try:
        # 証券コードのバリデーション
        if not stock_code or len(stock_code) != 4 or not stock_code.isdigit():
            return jsonify({
                "error": "無効な証券コードです。4桁の数字を入力してください。"
            }), 400

        # 決算資料を取得
        materials = get_earnings_materials(stock_code)

        if not materials:
            return jsonify({
                "error": "決算資料が見つかりませんでした。",
                "stock_code": stock_code
            }), 404

        return jsonify({
            "stock_code": stock_code,
            "materials": materials
        })

    except Exception as e:
        print(f"決算資料取得エラー: {e}")
        return jsonify({
            "error": f"エラーが発生しました: {str(e)}"
        }), 500

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """お気に入り一覧を取得"""
    try:
        response = supabase.table('favorites').select('*').order('created_at', desc=True).execute()
        favorites = [
            {
                "stock_code": fav['stock_code'],
                "company_name": fav['company_name']
            }
            for fav in response.data
        ]
        return jsonify({"favorites": favorites})
    except Exception as e:
        print(f"お気に入り取得エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """お気に入りに追加"""
    try:
        data = request.get_json()
        stock_code = data.get('stock_code')

        if not stock_code or len(stock_code) != 4 or not stock_code.isdigit():
            return jsonify({"error": "無効な証券コードです"}), 400

        # 企業名を取得
        company_name = get_company_name(stock_code)

        # Supabaseに追加（既に存在する場合はUNIQUE制約でエラーになるが、それは無視）
        try:
            supabase.table('favorites').insert({
                "stock_code": stock_code,
                "company_name": company_name
            }).execute()
            return jsonify({"message": "お気に入りに追加しました", "company_name": company_name}), 201
        except Exception as insert_error:
            # UNIQUE制約違反の場合は既に登録済み
            if "duplicate" in str(insert_error).lower() or "unique" in str(insert_error).lower():
                return jsonify({"message": "既にお気に入りに登録されています"}), 200
            raise insert_error

    except Exception as e:
        print(f"お気に入り追加エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/favorites/<stock_code>', methods=['DELETE'])
def remove_favorite(stock_code):
    """お気に入りから削除"""
    try:
        response = supabase.table('favorites').delete().eq('stock_code', stock_code).execute()

        if not response.data:
            return jsonify({"error": "お気に入りに登録されていません"}), 404

        return jsonify({"message": "お気に入りから削除しました"}), 200

    except Exception as e:
        print(f"お気に入り削除エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/market-cap/<stock_code>', methods=['GET'])
def get_market_cap_endpoint(stock_code):
    """
    証券コードから時価総額を取得するエンドポイント

    Parameters:
        stock_code (str): 4桁の証券コード

    Returns:
        JSON形式の時価総額情報
    """
    try:
        if not stock_code or len(stock_code) != 4 or not stock_code.isdigit():
            return jsonify({"error": "無効な証券コードです"}), 400

        market_cap_info = get_market_cap(stock_code)

        if not market_cap_info:
            return jsonify({"error": "時価総額情報を取得できませんでした"}), 404

        return jsonify(market_cap_info)

    except Exception as e:
        print(f"時価総額取得エラー: {e}")
        return jsonify({"error": str(e)}), 500

# Vercel用のハンドラー
# Vercelはこのappオブジェクトを使用してリクエストを処理する
