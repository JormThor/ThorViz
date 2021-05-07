import json
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict

# Core
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import ftx

########################################################################################
# Config
########################################################################################

COINS = ["RUNE","BNB","BTC","ETH",]

########################################################################################
# Data
########################################################################################

def get_market_price() -> float:

    """
    Grabs Rune/USD market price from FTX.
    """
    ftx_client = ftx.FtxClient()
    
    result = ftx_client.get_market('RUNE/USD')
    
    market_price = result['price']
    
    return market_price

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_rune_stats() -> Dict[str, float]:
    # TODO - docstring 
    """
    Gathers ThorChain Network data from MCCN and SCCN,
    """ 

    market_price = get_market_price()
    
    # MCCN
    mccn = requests.get('https://midgard.thorchain.info/v2/network')
    mccn_dict = mccn.json()
    
    mccn_total_pooled_rune = float(mccn_dict['totalPooledRune']) / 1e8
    mccn_total_active_bond = float(mccn_dict['bondMetrics']['totalActiveBond']) / 1e8 
    
    # ---
    
    # SCCN
    sccn = requests.get('http://thorb.sccn.nexain.com:8080/v1/network')
    sccn_dict = sccn.json()
    
    sccn_total_staked_rune = float(sccn_dict['totalStaked']) / 1e8
    sccn_total_active_bond = float(sccn_dict['bondMetrics']['totalActiveBond']) / 1e8 
    
    # calculations
    
    rune_in_lp_count = mccn_total_pooled_rune + sccn_total_staked_rune
    rune_bonded_count = mccn_total_active_bond + sccn_total_active_bond
    
    total_in_network_count = rune_in_lp_count + rune_bonded_count
    
    deterministic_value = rune_in_lp_count * market_price * 3 # In USD
    
    determined_price = deterministic_value / total_in_network_count # In USD
    
    speculation = market_price - determined_price # USD
    
    speculation_pct = speculation / market_price
    
    # Collect Results
    result_dict = {
        'Rune_in_LP_count': rune_in_lp_count,
        'Rune_bonded_count': rune_bonded_count,
        'total_in_network_count': total_in_network_count,
        'deterministic_value_usd': deterministic_value,
        'determined_price': determined_price,
        'market_price_usd': market_price,
        'speculation_premium_usd': speculation,
        'speculation_pct_of_market': speculation_pct,
    }
    
    return result_dict 


########################################################################################
# Helpers
########################################################################################



########################################################################################
# App
########################################################################################


# ------------------------------ Config ------------------------------

st.set_page_config(
    page_title="ThorViz", page_icon="⚡", layout="wide",
    #initial_sidebar_state="expanded"
)


# ------------------------------ Sidebar ------------------------------

#st.sidebar.title("Config")

#days = st.sidebar.slider("Days:", value=60, min_value=0, max_value=60)
primary = "RUNE"#st.sidebar.selectbox("Primary:", COINS)
#compare = st.sidebar.multiselect("Compare: ", COINS)


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
  </div>
</div>
""",
    height=80,
)

# ------------------------------ Header  ------------------------------

# This is a hack to align center :-(

col1, col2, col3 = st.beta_columns([1,6,1])


with col1:
    st.write("")

with col2:
    st.title("ThorViz - Thorchain Tokenomics Dashboard")
    st.title('⚡⚡⚡ #RAISETHECAPS ⚡⚡⚡')

with col3:
    st.markdown("[![](coin_icons/btc_logo.png)](https://streamlit.io)")
    st.markdown("[Github](https://github.com/Cattleman/thor-viz)")
    st.markdown("[Twitter](https://twitter.com/JormungandrThor)")

# ------------------------------ Sections ------------------------------

st.error("This dashboard is in beta, there may be bugs. 🐞")
if st.button("➡️  I understand there could be bugs, let me in!"):

    with st.beta_expander("Rune Baseline Price ⚖️"):
    
        st.write('RUNE TO MOON!')
        
        rune_dict = get_rune_stats()

        # Note:  `:,` formats values with comma for easier reading.
        # TODO can format all of these with a helper function later 

        # Total Pooled Rune
        st.markdown(f'**Total Pooled Rune (MCCN + SCCN):** **ᚱ**{np.round(rune_dict["Rune_in_LP_count"], 2):,}')
        # DUPLICATE
        st.button(f' TEST - Total Pooled Rune (MCCN + SCCN): ᚱ{np.round(rune_dict["Rune_in_LP_count"], 2):,}', help='tooltip_test')
        # Total Active Bonded Rune
        st.markdown(f'**Total Active Bonded Rune:** **ᚱ**{np.round(rune_dict.get("Rune_bonded_count"), 2):,}')
        # In-Network Rune
        st.markdown(f'**Total In-Network Rune:** **ᚱ**{np.round(rune_dict.get("total_in_network_count"), 2):,}')
        # Deterministic Value
        st.markdown(f'**Total Deterministic Value:** **$**{np.round(rune_dict.get("deterministic_value_usd"), 2):,}')
        # Market Price 
        st.markdown(f'**Market Price (USD):** **$**{np.round(rune_dict.get("market_price_usd"), 2):,} (source: FTX)')
        # Calculate Baseline Price
        st.markdown(f'**Baseline Price (USD):** **$**{np.round(rune_dict.get("determined_price"), 2):,}')
        st.markdown(f'**Speculation Premium (USD):** **$**{np.round(rune_dict.get("speculation_premium_usd"), 2) :,}')
        st.markdown(f'**Speculation percentage of Market Price:** {np.round(rune_dict.get("speculation_pct_of_market") * 100 ,2)}%')


    with st.beta_expander("Baseline Price - Show me the math! 📐🤔"):

        st.markdown(""" y=mx+b

                """
                )

        st.latex("TotalRuneInNetwork = TotalPooledRune + TotalActiveBondedRune")

        st.latex("DeterministicValue \, (USD) = TotalPooledRune * MarketPrice * 3")

        st.latex(r"BaselinePrice \, (USD) = \frac{DeterministicValue}{TotalRuneInNetwork}")
        st.latex("SpeculationPremium \, (USD) = MarketPrice - BaselinePrice")

        st.latex(r"SpeculationPercentOfMarket \, (\%) = \frac{SpeculationPremium}{MarketPrice} * 100")
    
    with st.beta_expander("Deterministic Price Simulator"):

        st.write("Note: The calculations here are slightly different than the `Baseline price`. Here we are considering the Deterministic Price with TOTAL Rune, not just the in-network Rune.")
        
        st.markdown("# Instructions")
        st.markdown("**1.** Adjust the Prices of each coin.")
        st.markdown("**2.** Select a percentage of the total coins that will be LP'ed in ThorChain.")
        st.markdown("**3.** 🤯🤯🤯 ")

        st.markdown(" NOTE - this functionality doesnt work currently :-( ")
        st.markdown("")

        # NOTE to future ThorChads
        # Streamlit app will rerun computation when slider values change,
        # this isnt the ideal action...
        # see: https://discuss.streamlit.io/t/entire-app-refreshes-when-i-move-slider/8458/3

        col1, mid, col2 = st.beta_columns([1,1,20])
        with col1:
            st.image("coin_icons/btc_logo.png", width=40)
        with col2:
            st.markdown("**BTC**")
        # TODO - fetch market price from FTX
        st.slider(label="BTC Price - Adjust me!", min_value=30_000, max_value=100_000,value=50_000, step=1000)
        st.slider("% BTC in LP", min_value=0.0, max_value=100.0,value=0.05, step=0.01)

        col1, mid, col2 = st.beta_columns([1,1,20])
        with col1:
            st.image("coin_icons/eth_logo.png", width=40)
        with col2:
            st.markdown("**ETH**")
        
        eth_price = st.slider(label="ETH Price - Adjust me!", min_value=2000, max_value=10_000,value=3_500, step=100)
        
        eth_pct = st.slider("% ETH in LP", min_value=0.0, max_value=100.0,value=0.05, step=0.01)
        

        col1, mid, col2 = st.beta_columns([1,1,20])
        with col1:
            st.image("coin_icons/bnb_logo.png", width=40)
        with col2:
            st.markdown("**BNB**")

        bnb_price = st.slider(label="BNB Price - Adjust me!", min_value=200, max_value=1000,value=650, step=50)

        bnb_pct = st.slider("% BNB in LP", min_value=0.0, max_value=100.0, step=0.01)



# ------------------------------ Trading View Chart ------------------------------

    with st.beta_expander("Market (Binance) 📈📊"):

        components.html(
            f"""
        <div class="tradingview-widget-container">
          <div id="tradingview_49e5b"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget(
          {{
          "symbol": "BINANCE:{primary}USDT",
          "interval": "4H",
          "timezone": "Etc/UTC",
          "style": "1",
          "locale": "en",
          "toolbar_bg": "#f1f3f6",
          "enable_publishing": false,
          "allow_symbol_change": true,
          "container_id": "tradingview_49e5b"
          }}
          );
          </script>
        </div>
        """,
            height=550,
            width=900,
        )


    with st.beta_expander("ThorChain Data Resources 💾🗄️"):

        st.write(f'Data Source for MCCN: {"https://midgard.thorchain.info/v2/network"}')
        st.write(f'Data Source for SCCN: {"http://thorb.sccn.nexain.com:8080/v1/network"}')

    # TODO add additional tools
    with st.beta_expander("Support Development 🛠️ 🙏"):
        
        st.write('If this dashboard is helpful consider supporting development.')
        st.write("Were a distributed team of TradFi -> ThorFi Data Folks")
        st.write('Project Roadmap will come soon.')
        st.markdown('**BNB Address:** `bnb1t6nwpm5scau65gkm9ys8wceutz5p2a3mjhmjuc`')

