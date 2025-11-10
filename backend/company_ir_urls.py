"""
主要企業のIRページURLマッピング
"""

COMPANY_IR_URLS = {
    "7203": {  # トヨタ自動車
        "name": "トヨタ自動車",
        "ir_url": "https://global.toyota/jp/ir/library/",
        "direct_links": []
    },
    "9984": {  # ソフトバンクグループ
        "name": "ソフトバンクグループ",
        "ir_url": "https://www.softbank.jp/corp/ir/documents/",
        "direct_links": []
    },
    "6758": {  # ソニーグループ
        "name": "ソニーグループ",
        "ir_url": "https://www.sony.com/ja/SonyInfo/IR/library/presen.html",
        "direct_links": []
    },
    "8306": {  # 三菱UFJフィナンシャル・グループ
        "name": "三菱UFJフィナンシャル・グループ",
        "ir_url": "https://www.mufg.jp/ir/presentation/",
        "direct_links": []
    },
    "9433": {  # KDDI
        "name": "KDDI",
        "ir_url": "https://www.kddi.com/corporate/ir/library/",
        "direct_links": []
    },
}


def get_company_ir_url(stock_code: str) -> dict:
    """
    証券コードから企業のIR情報を取得

    Args:
        stock_code (str): 証券コード

    Returns:
        dict: 企業IR情報
    """
    return COMPANY_IR_URLS.get(stock_code, {
        "name": f"企業コード{stock_code}",
        "ir_url": None,
        "direct_links": []
    })
