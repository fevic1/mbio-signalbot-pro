
from .client import CoinGeckoClient

cg=CoinGeckoClient()

TOOLS={

"cg_ping":
lambda a: cg.get("/ping"),

"cg_trending":
lambda a: cg.get("/search/trending"),

"cg_search":
lambda a: cg.get(
"/search",
{"query":a["query"]},
),

"cg_coin":
lambda a: cg.get(
f"/coins/{a['id']}",
),

"cg_markets":
lambda a: cg.get(
"/coins/markets",
{
"vs_currency":a.get("vs_currency","usd"),
"ids":a.get("ids",""),
},
),

"cg_global":
lambda a: cg.get("/global"),

}
