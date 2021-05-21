'''
Components to add to app in the future
'''



# ------------------------------ Trading View Ticker ------------------------------

# format ticker coins for javascript input
tv_ticker_coins = list(
    map(lambda c: {"proName": f"BINANCE:{c}USDT", "title": f"{c}/USD"}, COINS)
)
components.html(
    f"""
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <div class="tradingview-widget-copyright">
    <a href="https://www.tradingview.com" rel="noopener" target="_blank">
    <script
        type="text/javascript"
        src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js"
        async
    >
      {{
        "symbols": {json.dumps(tv_ticker_coins)},
        "isTransparent": false,
        "locale": "en"
      }}
    </script>
#  </div>
#</div>
""",
    height=80,
)


