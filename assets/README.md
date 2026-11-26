# Practice assets: Pebble & Pine Outfitters

A fictional online outdoor-gear store. All names, policies, codes and contact details are invented,
and `.example` domains are reserved and never real.

| File | Used in |
|---|---|
| `system-prompt.md` | ShopBot's system prompt (M01 onward). Contains a confidential code used as a red-team target in M08. |
| `kb/*.md` | Knowledge base: the "source of truth" for policy questions, RAG (M06) and the pricing rules (M11) |
| `fixtures/orders.json` | Mock order store for the agent (M07) and security tests (M08) |

**Rules for the practice world**

- The knowledge base is always correct. If ShopBot contradicts it, ShopBot is wrong.
- The mock store's "today" is fixed at `store_today` in `orders.json`, so return eligibility is
  deterministic in tests.
- You may add docs or orders for exercises, such as planted injections in M08, but keep the originals
  intact or restore them with git.
