
from .client import DefiLlamaClient

llama=DefiLlamaClient()

TOOLS={

"dl_protocols":
lambda a: llama.get("/protocols"),

"dl_protocol":
lambda a: llama.get(
f"/protocol/{a['slug']}"
),

"dl_chains":
lambda a: llama.get("/v2/chains"),

"dl_tvl":
lambda a: llama.get("/v2/historicalChainTvl"),

"dl_yields":
lambda a: llama.get("/pools"),

"dl_stablecoins":
lambda a: llama.get("/stablecoins"),

}
