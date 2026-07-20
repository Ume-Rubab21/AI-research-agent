# Diff: Simple Research Agent vs MCP + Multi-Agent Version

Ye document batata hai ke aapka pehla wala simple research agent (jo
sirf `main.py` + `agent/builder.py` chalata tha) aur ye naya MCP wala
version, dono mein farq kya hai — aur kyun ye farq matter karta hai.

## 1. Pehle: Ek hi Agent, Sab Kuch Khud Karta Tha

Purane version mein sirf **ek** agent tha:

```
main.py -> agent/builder.py (LLM + 3 tools) -> seedha jawab
```

`build_agent()` ek LangChain agent banata tha jisme 3 tools attach thay:
`serp_search`, `read_txt_file`, `read_pdf_file`. Jab user koi sawal
karta tha, wahi ek agent decide karta tha ke kaunsa tool chalana hai,
tool call karta tha, aur khud hi final jawab bhi bana deta tha.

Ye theek tha jab tak sirf 2-3 tools thay aur sab kuch ek hi jagah
handle ho sakta tha. Lekin isme kuch limitations thin:

- Agar kal ko 5-6 aur tools/agents add karne parte (jaise ek "email
  agent", ek "calendar agent"), to sab ka logic isi ek agent/prompt
  mein thoons dena parta — prompt bohat bara aur confusing ho jata.
- Ye agent sirf **isi Python process ke andar** kaam karta tha. Koi
  bahar wala tool (jaise Claude Code, Cursor, ya koi aur app) isse
  seedha connect nahi kar sakta tha — kyunke ye kisi standard protocol
  ke through expose hi nahi tha.
- Debugging mushkil thi — ek hi bara trace tha, ye pata lagana mushkil
  ke exactly kis step par cheez fail hui.

## 2. Ab: MCP Server + Supervisor + Do Workers

Naye version mein kaam **teen layers** mein split ho gaya hai:

```
Client (client/client.py, ya Claude Code/Cursor)
      |  MCP protocol (stdio transport)
      v
MCP Server (mcp_server/server.py)
      |  exposes: 1 resource + 1 tool + 2 prompts
      v
Supervisor (agent/supervisor.py)
      |  route karta hai based on query
      v
   ------------------------
   |                        |
FileWorker              SearchWorker
(file padhta hai)        (web search + LLM reasoning)
```

### a) MCP Server — ek "standard darwaza"

Pehle agent sirf Python code ke andar hi call ho sakta tha. Ab
`mcp_server/server.py` ne isko **MCP protocol** ke through expose kar
diya hai — matlab koi bhi MCP-compatible client (aapka apna
`client/client.py`, ya Claude Code, ya Cursor) isse connect ho sakta
hai bina ye jaane ke andar Python/LangChain use ho raha hai. Ye same
farq hai jaisay ek function ko direct call karna vs usko ek REST API
banake expose karna — dusri app ab isse independently use kar sakti
hai.

MCP server 3 cheezein expose karta hai (jo purane version mein
tha hi nahi):
- **Resource** (`research://about`) — read-only info jaisay ek static
  file/endpoint.
- **Tool** (`research`) — actual kaam karne wala function jo client
  call kar sakta hai.
- **Prompts** (`research_query`, `summarize_file`) — ready-made
  templates jo client fill kar ke use kar sakta hai, taake user ko
  har baar wording khud sochni na pare.

### b) Supervisor + Workers — kaam bant gaya

Pehle ek hi agent decide bhi karta tha aur execute bhi. Ab
**Supervisor** (`agent/supervisor.py`) sirf ek kaam karta hai: query
dekh kar decide karna ke ye **FileWorker** ke paas jaye, **SearchWorker**
ke paas jaye, ya dono ke paas (jab file + web dono chahiye ho, jaisay
"file mein jo language likhi hai uska latest version internet se batao").

- **FileWorker** = sirf file padhta hai (.pdf/.txt), koi LLM call nahi
  karta — fast aur free.
- **SearchWorker** = jahan asal LLM reasoning hoti hai (web search +
  jawab banana).

Farq ye hai ke ab har agent ka kaam **narrow aur clear** hai, jaisay
ek chota team ho jisme har banda apna specific kaam karta hai, ek
banda sab kuch nahi karta. Kal ko agar teesra worker (jaisay
EmailWorker) add karna ho, to Supervisor mein ek routing rule aur
add karo — purane agent ka pura prompt dobara likhne ki zarurat nahi.

### c) Tracing + Logging — har step record hota hai

Purane version mein koi structured logging nahi thi (bas terminal pe
print). Ab:
- `logs/agent_trace.log` — Supervisor aur Workers ke har decision ka
  timestamped record.
- `logs/tool_calls.log` — har individual tool call (search, PDF read,
  TXT read) ka record, success/fail status ke sath.
- `debug/replay.py` — dono logs ko mila kar ek timeline bana deta hai,
  taake baad mein pata chal sake exactly kahan cheez fail hui, bina
  dobara agent chalaye.

### d) Output Guardrail — ab jawab validate hota hai

Purane version mein jo bhi LLM/tool return karta, seedha user tak chala
jata tha. Ab `agent/schemas.py` mein ek Pydantic check hai jo Supervisor
ke har jawab ko validate karta hai — empty na ho, bohat lamba na ho,
aur raw tool data (jaisay unformatted search JSON) leak na ho. Agar
validation fail ho, to ek safe fallback message jata hai, crash nahi
hota.

## 3. Side-by-Side Summary

| Cheez | Purana (Simple Agent) | Naya (MCP + Multi-Agent) |
|---|---|---|
| Kitne agents | 1 (sab kuch khud karta) | 3 (Supervisor + FileWorker + SearchWorker) |
| Bahar se access | Sirf isi Python script ke andar | MCP protocol ke through, koi bhi MCP client (Claude Code, Cursor, custom) connect ho sakta hai |
| Tools kahan expose hote | Kahin nahi (bas internal LangChain tools) | MCP server ke through resource + tool + prompts ke roop mein |
| Routing logic | LLM khud prompt padh kar decide karta | Supervisor ek separate, dedicated routing layer hai |
| File reading vs Web search | Same agent, same LLM call mein mix | Alag workers, file reading LLM call bhi nahi karta (fast/free) |
| Debugging | Sirf terminal print, dobara run kar ke dekhna parta | Do log files + `debug/replay.py` se pura trace replay ho sakta hai |
| Output safety | Kuch nahi, raw output seedha user tak | Pydantic guardrail har jawab validate karta hai |
| Cost/latency soch | Koi documented strategy nahi thi | `COST_STRATEGY.md` mein likha hai kahan LLM call hoti hai aur kyun |

## 4. Ek line mein

Purana agent ek "sab kuch karne wala akela banda" tha jo sirf apne hi
ghar (Python script) ke andar kaam karta tha. Naya version usi kaam ko
ek **team** (Supervisor + 2 Workers) mein bant deta hai aur pure system
ko ek **standard protocol (MCP)** ke through duniya (koi bhi MCP client)
ke liye expose kar deta hai — jisse ye reusable, debuggable, aur scale
karne layak ban jata hai.
