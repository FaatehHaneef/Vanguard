# Data cards (verified 2026-11-22)

Public datasets Vanguard may use. None is stored in this repository: each lives under the folder named by `VANGUARD_DATA_DIR` (default `D:\VanguardData`). Each was checked the same way: every file's size compared with the Hugging Face listing, and every JSON, JSONL and parquet file parsed. Pickle files and password-protected archives were deliberately not opened. Uses and limits follow `Vanguard.md`, Section 4.6a.

## osunlp/Mind2Web

| | |
|---|---|
| Licence | CC BY 4.0 |
| Source | https://huggingface.co/datasets/osunlp/Mind2Web (paper: arXiv 2306.06070) |
| Local copy | full: 15 files, 6.74 GB (`mind2web/`) |
| Verified | 15 of 15 files match the Hub listing in size; all 11 JSON shards parse |
| Content | 1,009 training tasks on real websites. Each task has `website`, `domain`, `subdomain`, `annotation_id`, `confirmed_task` (instruction), `action_reprs` (readable steps) and `actions`, each with `raw_html`, `cleaned_html`, `operation` (CLICK, TYPE or SELECT) and positive and negative candidate elements |
| Not opened | `test.zip` (password-protected by the authors to avoid contamination; it stays closed) and `scores_all_data.pkl` (a pickle; never unpickled) |
| Possible use | general web-navigation fine-tuning before our own traces (A4, option 5); statistics on the mix of action types |
| Limits | Pointer-centric (clicks), sighted users, no accessibility conditions; actions are on page snapshots, not live sites |

## berkeley-hci/Reduced-A11y-CUA

| | |
|---|---|
| Licence | CC BY 4.0 |
| Source | https://huggingface.co/datasets/berkeley-hci/Reduced-A11y-CUA (paper: arXiv 2602.09310); the full set, with video and audio, is berkeley-hci/A11y-CUA |
| Local copy | full: 13,881 files, 3.86 GB (`a11y-cua-reduced/`) |
| Verified | 13,881 of 13,881 files match the Hub listing; all 13,022 JSON files parse (229,261 records); the 857 HTML DOM snapshots were not opened |
| Content | Computer-use sessions by blind and low-vision users (`BLVU/`, 5,135 JSON files), sighted users (`SU/`, 5,026), and two agents, Claude Sonnet 4.5 (2,066) and Qwen3-VL-32B-Instruct (795), each under Default, Magnifier and Screen Reader conditions. Files: session metadata; interaction events (timestamp, event type and key, window, element under keyboard focus, element under the cursor with its box, cursor position); Windows UI Automation trees; and `web_logs` with browser-tab events, DOM snapshots and accessibility trees |
| Possible use | **reference statistics only, never training** (decided 2026-11-21): for example the share of keyboard vs pointer events for blind and low-vision users compared with sighted users, and how the two agents behave under screen-reader and magnifier conditions, as a point of comparison for Vanguard's personas |
| Care | The data comes from a user study. Use aggregate statistics only, never quote individual sessions, and never copy account or login details from the paper or its appendix into this repository |

## Qwen/WebWorldData (sample)

| | |
|---|---|
| Licence | Apache 2.0 |
| Source | https://huggingface.co/datasets/Qwen/WebWorldData |
| Local copy | sample only: the first 314.6 MB of `WebWorld_Training.jsonl` (52.2 GB in full), cut at the last complete record (`webworld/WebWorld_Training.head.jsonl`, with `PARTIAL.json` recording this) |
| Verified | 4,211 records, all parse |
| Content | Multi-turn conversations (`conversations`: list of `{from, value}`, human then gpt) for a web *world model*: given a page state as an accessibility tree and an action such as `click('604')`, predict the next page state. 2 to 20+ turns per record |
| Possible use | accessibility-tree page states for testing the screen-reader observation format, and a possible source of simulated pages; check fit before any bigger download |
| Limits | Synthetic, model-oriented trajectories, not human behaviour; the sample is the head of the file, not a random sample |

## webagentlab/webchain (card only)

| | |
|---|---|
| Licence | CC BY 4.0 |
| Source | https://huggingface.co/datasets/webagentlab/webchain (paper: arXiv 2603.05295) |
| Local copy | README card only (the dataset is about 386 GB) |
| Content (from the card) | Human-annotated trajectories on live websites with screenshots, page structure, accessibility trees, grounded actions and reasoning |
| Possible use | pull single parts later if a perception alternative needs screenshot plus accessibility-tree pairs |
