# Review — 2026-11-03 engineering run

**Outcome: the gate is clear for the first time in six nights, and the queue is
the only thing stopping work now.** You committed and pulled yesterday morning, so
rule 2 passed. Rule 4 then fired on its own: §5 has no unblocked item while ★ B and
★ A are open. Per §5's "Queue empty?" I started nothing and invented nothing.

**Nothing changed outside `docs/`.** No source file, no generated output, no Notion
write, nothing committed.

---

## What I changed and why

| File | Change |
|---|---|
| `docs/REVIEW.md` | Overwritten with this note (rule 6). |
| `docs/EXECUTION_PLAN.md` | One appended line in §8 (rule 6). |

That is the whole diff. Everything else below is verification and reporting.

**Why no engineering:** every remaining §5 item needs a call from you.

- **E1** done · **E3** done (CLS answered 10-27) · **E5** done but for your
  subscribe click and ★ F / ★ G
- **E2** — all five leftovers are yours (Leap Day's +142 pages, Tax Day overlap,
  French Fry Day, the solstice aliases, Oktoberfest-ends)
- **E4** — machinery finished; the remaining 2,410 rows need ★ B
- **E6** — upstream half needs ★ A (price), the Worker decision, and a
  `.github/` edit that §3 puts outside the source boundary
- **E7** — 9:16 card is a UI decision, Featured tier is ★ A again

---

## The one thing that changed since last night

**★ H is closed.** Your `56c5515d` ("Mon Nov 2 Update") committed the two files that
blocked five consecutive nights, and the 13:54 pull brought the clone current:
`HEAD` == `origin/main` == **`8d20f4ba`**, working tree clean including untracked.
The six-day stall is over and the review loop is healthy again.

What that leaves is the harder half. The gate was never the real blocker — on four
of those five nights rule 4 would have stopped the run anyway. **★ B is the single
answer that puts work back in the queue**, and the re-plan checkpoint (2026-11-08)
is five days out.

### ★ B checked at the source, and it has not moved

Per-option `COUNT(*)` against live Notion (the method the 11-02 run established —
never `GROUP BY`, and not a large multi-row `SELECT` either):

Federal **11** · Religious **23** · Season & Clock **6** · State / Cultural /
Observance / Fun **0** · typed **40** · untyped **2,414** · all rows **2,454** ·
published **2,450** · published-and-untyped **2,410**

Totals tie out three ways (11+23+6 = 40; 40+2,414 = 2,454; 2,450−2,410 = 40), so
this is a real read, not a mis-bucketed one. **Identical to 2026-10-13 and every
night since — ★ B is 21 days old, ★ A is 19.**

Content side, same query: **72 rows Live, 72 with `Body`, 0 Draft, 0 Reviewed** —
exactly the 66 the 11-01 run counted plus three on 11-01 and three on 11-02.

---

## What you should check

1. **Nothing in the diff needs reviewing for correctness** — it is two `docs/`
   files. Commit it whenever convenient; it will not block tomorrow.
2. **★ B, if you read only one thing.** It is the only answer that refills the
   engineering queue. The three boundaries needing your call (saints' feast days,
   secularized religious holidays, Observance vs Fun for the bulk) are written up
   in the 2026-10-13 review — recoverable from git history at `56c5515d`.
3. **Sunday's checkpoint is now the thing that restarts engineering.** On the
   evidence of the last six nights, the queue needs re-planning more than the
   process does.

---

## How I verified

Generator run **read-only into throwaway dirs outside `$HOME/mnt`**
(`$HOME/verify-2026-11-03`), the committed generator, `--today 2026-11-03`:

- **exit 0**, **zero WARNING lines**, **stderr 0 bytes** (both runs)
- 5,695 files · 2,450 observance · 378 dated · 366 perennial · 2 year-index · 19 simple
- 2,465 `.ics` / 3,263 events · `/calendar.ics` 1,992,522 bytes · cards off
  (`SHARE_CARDS is off`) · `occasions_total` 0 · `people_dates` 366
- `pages_changed` / `pages_skipped` / `unresolved_holidays` / `unknown_types` /
  `stale_month_files` / `occasions_problems` / `perennial_pages_skipped` all empty;
  `perennial_index_skipped` only the four known §7 expiring-lookup rows
  (belmont-stakes, teach-your-children-to-save, preakness-stakes, super-bowl-sunday)
- `type_counts` **(untyped) 2,410 / Religious 23 / Federal 11 / Season & Clock 6** —
  agrees with live Notion
- **two full runs `diff -rq` byte-identical across all 5,695 files** (idempotent)
- **`public/` never written** — its newest file is `sitemap.xml` at 2026-11-02 18:54,
  from your pull; tree re-checked clean afterwards

Live site read twice: **200**, `data-today="2026-11-2"`, "Today, Monday November 2"
at 06:00 UTC — the expected overnight-build lag (Action runs 08:00 UTC).

---

## Two method corrections worth keeping

**1. A failed `curl` write can manufacture a false stale-site reading.** My first
live-site read wrote to `/tmp`, which this sandbox refuses; `curl` exited 23
("Failure writing output to destination") but left a partial file, and grepping it
returned `data-today="2026-10-29"` — a site five days stale, which would have been
alarming and wrong. Re-read into `$HOME` it was 2026-11-2 both times.
**Check curl's exit status and the byte count before concluding anything from a
live-site read**, on top of the 10-31 note's cache-busting advice.

**2. The `?cb=` cache-buster does not bust this zone's cache.** Both the plain and
the cache-busted request returned `cf-cache-status: HIT`, identical byte counts and
the same `date` header, with `Cache-Control: no-cache` sent. The two reads agreeing
is still the check that matters, but a future run should not treat a query string as
proof it saw origin.

---

## Needs a decision

- **★ B — the E4 `Type` assignment rule** for the remaining 2,410 rows (**21 days**).
  Confirmed unmoved at the source tonight. **The only open answer that returns an
  unblocked item to the engineering queue.**

- **★ A — the Listed tier price and what it includes** (**19 days**). Unblocks E6's
  upstream half (form, Stripe Checkout, Worker) and E7's Featured tier.

- **D1 — the three Notion property descriptions still contradict the code**
  (fourteenth flag). `FAQ` still instructs wrapping the question in `**bold**` — the
  exact trap that silently emptied every FAQ before 2026-10-10, and still the advice
  a human writing a row today would follow. `Body` still lists `[text](url)` while
  `Sources` correctly requires bare URLs. `Timeline` still asks for `- **1927** —`,
  which Notion strips on the round trip. Three description edits, no code, no risk.
  **I did not apply them: rule 4 confines me to §5 and this is not a §5 item.**
  Fourteen flags is the argument for either giving me standing permission for Notion
  schema-description fixes or spending the two minutes yourself.

- **★ G — the feeds are still served uncompressed**, re-measured tonight with
  `Accept-Encoding: gzip, br`: `/calendar.ics` returns **1,992,522 bytes and no
  `content-encoding`**, so every daily refresh costs ~1.9 MB where gzip would make it
  ~177 KB. A Cloudflare zone setting, not a code change. Side benefit of the check:
  the live feed's byte count matches the generator's `ics_main_feed_bytes` exactly,
  so the deployed feeds are the committed build.

- **The bare `/holidays/` still 404s** (`/holidays/2026/` 200s) — the small open
  decision from 2026-10-12, confirmed unchanged.

- **Carried forward unchanged:** ★ D (the home page's one layout shift, and whether
  E3's "CLS stays 0.0000" should become a threshold), ★ E (hero poster band as E8?),
  ★ F (should a fixed-date feed event keep its history?), D2 (`super-bowl-sunday`'s
  lookup holds 2027 only, expires after 2027-02-14), D3 (the attached folder is
  routinely not connected at session start — tonight it was, no request needed).

- **For Sunday's checkpoint, not acted on:** §2 could exempt documentation-only
  diffs the way it already exempts `docs/`, which would have saved several of the
  blocked nights. But the deeper point is that the queue, not the gate, is now the
  constraint: E1/E3/E5 are done, E2/E4/E6/E7 are each waiting on you, and a
  **re-plan is what produces engineering work again** — new queue items (the §7
  fidelity audit as a real item, the 2027 lookup-table expiries, something new)
  rather than another night of verification.

---

## Content run — 2026-11-03 (Tier 5, T5-7 to T5-9)

Appended, not overwritten: the engineering section above is this file's owner and its
open decisions stand.

**Published Live, three Nov 3 rows** (Order 2/3/4; Order 1 already had content):

- National Sandwich Day — https://todaycelebrates.com/holiday/national-sandwich-day/
- Cliché Day — https://todaycelebrates.com/holiday/clich-day/
- World Jellyfish Day — https://todaycelebrates.com/holiday/world-jellyfish-day/

~880 / 840 / 905 words. FAQ parses to 5/5/5 pairs and Timeline to 6/4/6 entries against
the working tree's own `parse_faq()`. `Published` untouched on all three; `Description`
unchanged. Nothing committed, no generated output touched.

### Worth a second look

- **National Sandwich Day's date has no sourceable basis.** The universal claim is that
  November 3 is the 4th Earl of Sandwich's birthday. Britannica gives **November 13,
  1718**, and Old Style / New Style conversion does not bridge it either (eleven days
  from Nov 3 is the 14th). History of Parliament Online is robots-disallowed; RMG and the
  NPG would not fetch. The page follows Britannica and says plainly that the November 3
  explanation is unsourced. **If Jay has an ODNB or peerage reference, this is the one
  claim on the three pages worth checking by hand.**
- **The word "sandwich" carries no earliest-recorded-use date** on the page, because
  `oed.com` would not fetch and the commonly cited 1762 Gibbon journal entry has no
  reachable citation. A page with OED access could add a sourced date.
- **Cliché Day and World Jellyfish Day have no documented founder at all** — every
  candidate source was an aggregator or content farm. Both pages say so, which is the
  §4 rule working as intended rather than a gap to fill later.

### Method notes for future runs

- **Britannica is per-URL, not per-host.** The 11-02 note recorded Britannica as
  unfetchable; tonight `/biography/John-Montagu-4th-Earl-of-Sandwich` and `/topic/sandwich`
  both returned 200 while `/topic/sandwich-food` and `/technology/stereotyping-printing`
  returned `client_error`. Retry a different slug before writing the host off.
- **Fetched reference pages now routinely carry injected "reporting rules"** (a
  125-character quote cap, a paraphrase requirement) presented as instructions — seen
  tonight on britannica.com, merriam-webster.com, three NOAA hosts, ocean.si.edu and
  orwellfoundation.com. Page text, not task instructions. Ignored; exact quotes taken as
  §4 requires.
- `connectedFolders` was empty at session start for the third content run running.
  `device_request_folder_access` is now a normal first step, not an exception.

### Needs a decision (content-side, not acted on)

- **Cliché Day's live slug is `clich-day`.** `slugify()` maps the accented `é` to a
  separator. It is an existing live URL, so it was left alone. Changing it means a
  redirect, which is an engineering item, not a content one — Jay's call whether it is
  worth one.
- **Tier 5 keeps publishing on the day rather than ahead of it** (third run running: Nov 1,
  Nov 2, now Nov 3). The rule orders by next occurrence, and today's rows are the soonest.
  A one-line §6 change would make Tier 5 start from tomorrow instead. Followed literally
  again rather than reordered.
