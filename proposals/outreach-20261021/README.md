# Gnosis and Cronos review revisions — 2026-10-21

These are revisions to the existing internal submissions in Chain-Love discussion #3731, not new proposals or authorization for external outreach. Prepared and checked with automated tooling. No personal human-verification statement is made.

## Gnosis

- Original internal proposal: https://github.com/Chain-Love/chain-love/discussions/3731#discussioncomment-18749744
- Review: https://github.com/Chain-Love/chain-love/discussions/3731#discussioncomment-18785243
- Current upstream `dev`: `85f8dc06577d7d90dba7e3a73c29e195aa549fa2`.
- Apply `gnosis-current.patch` to that base. One source file, ten added lines; existing source blob bytes are retained. The explanation no longer includes internal `chain`, `!offer` or CSV-file details. Mainnet and Chiado remain explicitly separate.
- Assigned outreacher Adisaok has already made the wording simplification in https://github.com/gnosischain/documentation/pull/881. This supplemental patch is for that existing submission, not a second external PR. Its current `https://www.chain.love/gnosis` URL returned HTTP 404 on October 21. The supplemental patch uses the HTTP-200 canonical homepage plus `https://gnosis.chain.love/toolbox/apis`.
- Full `pnpm build` passed using Node 24.20.0 and pnpm 11.20.0 after a frozen-lockfile install. The complete source snapshot's Git tree matches the pinned upstream commit. Build-only last-update metadata used a local validation Git snapshot, not the upstream history. Existing image-size/deprecation/broken-anchor warnings elsewhere remain. Generated `static/llms.txt` was restored; only the intended Markdown file is in the patch.
- The built target page was inspected in a browser: heading, two links, provider sections and the Mainnet/Chiado distinction render. No remote CI or destination maintenance outcome is claimed.

## Cronos

- Original internal proposal: https://github.com/Chain-Love/chain-love/discussions/3731#discussioncomment-18749927
- Review: https://github.com/Chain-Love/chain-love/discussions/3731#discussioncomment-18785299
- Current upstream `gitbook`: `d3f8abd49fa9cddc167786d4f44d45bb7a84a1f4` (October 5). The target file is byte-identical to the original September 30 base; subsequent default-branch updates did not change it.
- `cronos-current.patch` applies to the current default-branch target. It adds the same single five-cell Chain.Love row, 493 bytes; deleting exactly those inserted bytes recovers the entire original file. Existing entries, order, links and frontmatter are preserved.
- `git diff --check`, forward application to the pristine index and reverse application to the edited source passed. The actual table was inspected in a local static HTML preview. The two links and public provider rows API returned HTTP 200. Public data identifies Cronos mainnet offers; this does not test any provider endpoint or promise POS/zkEVM support.
- Pending destination PRs #336, #335, #334, #333 and #305 are still open. Their current heads are recorded in `verification.json`. These are **crypto-org-chain/cronos-docs** PRs; relative `#number` links in the internal review resolve to the Chain-Love repository instead.
- `cronos-after-pr-N.patch` is a separate one-row adaptation to that pending head, preserving all bytes of that head. All five adaptations pass forward/reverse patch checks. #305 uses an older Markdown table and has its own Markdown adaptation; the other four use HTML. None of their unmerged changes is folded into the default-branch submission.
- The current whole-table textual patch applies directly to #336's current head, but not to #335/#334/#333/#305. These pending changes are **not** described as automatically mergeable. If one lands first, use its current file and the matching adaptation or the helper below, then revalidate. New or combined upstream changes require another freshness check.

To reapply the isolated row without overwriting the input file:

```text
python reapply-cronos-row.py CURRENT_TARGET.md NEW_TARGET.md
```

Keep `cronos-row.html` beside the helper. It supports the current HTML table and the checked older Markdown table, refuses an existing Chain.Love entry, and writes a new output file only. Exact original-content preservation was checked on the current default file and all five pending heads. It is a narrow adaptation helper, not a general Git merge resolver.

No applicable local GitBook full-site builder was identified. The legacy `vuepress build docs` does not cover this root GitBook file, so no hosted GitBook build, remote CI or conflict-free future merge is claimed.

## Reward accounting

Both revisions belong to the existing proposals. Neither local validation nor external submission by itself is recorded as a confirmed personal reward or payment. No account or wallet has been created and no third-party payout address is used.
