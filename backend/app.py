from flask import Flask, jsonify, request
from flask_cors import CORS
from earnings_scraper import get_earnings_materials, get_company_name
import os
import json
import yfinance as yf

app = Flask(__name__)
CORS(app)

# お気に入りデータを保存するファイルパス
FAVORITES_FILE = 'favorites.json'

def load_favorites():
    """お気に入りをJSONファイルから読み込む"""
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_favorites(favorites):
    """お気に入りをJSONファイルに保存する"""
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

def load_stock_master():
    """株式マスターデータを読み込む"""
    try:
        with open('stock_master.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
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
        return jsonify({
            "error": f"エラーが発生しました: {str(e)}"
        }), 500

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """お気に入り一覧を取得"""
    try:
        favorites = load_favorites()
        return jsonify({"favorites": favorites})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """お気に入りに追加"""
    try:
        data = request.get_json()
        stock_code = data.get('stock_code')

        if not stock_code or len(stock_code) != 4 or not stock_code.isdigit():
            return jsonify({"error": "無効な証券コードです"}), 400

        favorites = load_favorites()

        # 既に登録されているかチェック
        if any(f['stock_code'] == stock_code for f in favorites):
            return jsonify({"message": "既にお気に入りに登録されています"}), 200

        # 企業名を取得
        company_name = get_company_name(stock_code)

        # 追加
        favorites.append({
            "stock_code": stock_code,
            "company_name": company_name,
            "added_at": None  # フロントエンドで設定
        })

        save_favorites(favorites)
        return jsonify({"message": "お気に入りに追加しました", "company_name": company_name}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/favorites/<stock_code>', methods=['DELETE'])
def remove_favorite(stock_code):
    """お気に入りから削除"""
    try:
        favorites = load_favorites()

        # 削除
        new_favorites = [f for f in favorites if f['stock_code'] != stock_code]

        if len(new_favorites) == len(favorites):
            return jsonify({"error": "お気に入りに登録されていません"}), 404

        save_favorites(new_favorites)
        return jsonify({"message": "お気に入りから削除しました"}), 200

    except Exception as e:
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
