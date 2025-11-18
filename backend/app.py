from flask import Flask, jsonify, request
from flask_cors import CORS
from earnings_scraper import get_earnings_materials, get_company_name
import os
import json
import yfinance as yf
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# Supabase設定
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://lvlqrnrsnuxqmxqvfyjd.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2bHFybnJzbnV4cW14cXZmeWpkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4MjY5MjYsImV4cCI6MjA3ODQwMjkyNn0.S1krcgZVM0qiovk6ZxRSHaY3KLRWBfVw71h-qYwHnMw')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_stock_master():
    """
    株式マスターデータを読み込む

    Supabaseから全件取得（ページネーション対応）
    Supabase接続エラー時はローカルファイルにフォールバック
    """
    print("DEBUG: load_stock_master() called")
    
    # まずSupabaseから取得を試みる
    try:
        # PostgRESTの制限(1000件/リクエスト)を回避するため、複数回に分けて取得
        all_stocks = []
        page_size = 1000
        offset = 0

        print("Loading stocks from Supabase...")
        while True:
            response = supabase.table('stock_master').select('code, name').range(offset, offset + page_size - 1).execute()
            if not response.data:
                break
            all_stocks.extend(response.data)
            print(f"  Loaded {len(all_stocks)} stocks so far...")
            if len(response.data) < page_size:
                break
            offset += page_size

        if all_stocks:
            print(f"✅ Loaded {len(all_stocks)} stocks from Supabase")
            return all_stocks
        else:
            print("⚠️  Supabaseからデータが取得できませんでした。ローカルファイルにフォールバックします。")
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Supabase読み込みエラー: {error_msg}")
        # テーブルが存在しない場合や接続エラーの場合
        if 'table' in error_msg.lower() or 'PGRST205' in error_msg or 'connection' in error_msg.lower():
            print("⚠️  Supabase接続エラーまたはテーブルが見つかりません。ローカルファイルにフォールバックします。")

    # フォールバック: ローカルJSONファイルから読み込む
    try:
        print("Falling back to local file...")
        # バックエンドディレクトリから相対パスで読み込む
        stock_master_path = os.path.join(os.path.dirname(__file__), 'stock_master.json')
        with open(stock_master_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Loaded {len(data)} stocks from local file")
            return data
    except FileNotFoundError:
        print(f"❌ ローカルファイルが見つかりません: {stock_master_path}")
        return []
    except Exception as e:
        print(f"❌ ローカルファイル読み込みエラー: {e}")
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
    # デバッグ情報を追加
    debug_info = {
        "status": "ok",
        "supabase_url": SUPABASE_URL,
        "supabase_key_set": bool(SUPABASE_KEY),
        "supabase_key_length": len(SUPABASE_KEY) if SUPABASE_KEY else 0
    }
    return jsonify(debug_info)

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
    print(f"DEBUG: /api/search called with query='{query}'")

    if not query:
        return jsonify({"error": "検索キーワードを入力してください"}), 400

    stock_master = load_stock_master()
    print(f"DEBUG: Loaded {len(stock_master)} stocks")
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
        # テーブルが存在しない場合などは空配列を返す
        if 'table' in str(e).lower() or 'PGRST205' in str(e):
            print("⚠️  favoritesテーブルが見つかりません。空の配列を返します。")
            return jsonify({"favorites": []})
        return jsonify({"favorites": []})  # エラー時も空配列を返す

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
            # テーブルが存在しない場合
            if 'table' in str(insert_error).lower() or 'PGRST205' in str(insert_error):
                print("⚠️  favoritesテーブルが見つかりません。お気に入り機能は使用できません。")
                return jsonify({"error": "お気に入り機能は現在使用できません"}), 503
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
        # テーブルが存在しない場合
        if 'table' in str(e).lower() or 'PGRST205' in str(e):
            print("⚠️  favoritesテーブルが見つかりません。")
            return jsonify({"error": "お気に入り機能は現在使用できません"}), 503
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
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
