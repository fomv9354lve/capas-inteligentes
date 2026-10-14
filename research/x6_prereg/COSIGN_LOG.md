# Co-signature log: PREREG_CAPAS_VS_LLM_JUDGE.md

Each entry: the reviewing model, the sha256 of the document it reviewed, its verbatim reply. Replies by the authors follow each entry.

## 2026-10-14T17:20:01 · gemini / gemini-3.8-flash · prereg sha256 0fb31a9179b6bf7a592da6a74602f9744f6724191a8ccbaeb37afca63b39d52d

```json
{
  "decision": "OBJECT",
  "blocking_objections": [
    {
      "section": "§3 and §8",
      "objection": "Judge prompts and evaluation harness are not hashed in SEAL.json. Section 8 specifies that SEAL.json freezes engine tag, rule_table_sha256, capas_check.py, and judge model IDs, but omits the sha256 of the judge prompts and runner scripts. Because LLM judge performance is highly sensitive to prompt framing, unsealed prompts permit post-hoc prompt engineering that degrades judge performance.",
      "required_change": "Include the verbatim prompt templates for Judge A, B, A-perm, and A-key directly in the pre-registration, and require `judge_prompts_sha256` (and the execution harness sha256) inside `SEAL.json` prior to co-signature and push."
    },
    {
      "section": "§3 and §4",
      "objection": "The judge verdict space includes REWRITE (ACCEPT / REWRITE / REJECT / HOLD), while CAPAS only outputs ACCEPT / REJECT / HOLD. Section 4 defines FA as 'bad claims ACCEPTed / bad claims' and FR as 'good claims REJECTed / good claims', but never specifies how REWRITE is treated. If REWRITE on a bad claim does not count as an ACCEPT, a judge could achieve zero FA simply by defaulting to REWRITE; conversely, if REWRITE on a good claim is not counted as an FR, FR is distorted.",
      "required_change": "Formally pre-register the exact mapping of REWRITE for all metric denominators and numerators (e.g., whether REWRITE is collapsed into REJECT, treated as HOLD, or excluded) so that judge verdicts map unambiguously onto binary accept/reject comparisons."
    },
    {
      "section": "§2 and §8",
      "objection": "The claim extraction and sampling mechanism is completely unspecified. Claims are extracted from an unnamed 'project's repository' after sealing (Step 5) with only a quota ('at least 20 bad and 20 good clean claims'). Without a deterministic selection script, frozen commit range, or pre-committed sampling seed, the authors can cherry-pick claims known to match CAPAS's rule table or trip LLMs.",
      "required_change": "Specify the exact repository, commit hash/range, and a deterministic extraction script (frozen by sha256 in SEAL.json) or an immutable list of candidate claims with a pre-registered pseudo-random selection procedure."
    },
    {
      "section": "§5",
      "objection": "CAPAS and the LLM judges are tested on the exact same claims (within-subject / paired data), but Section 5 specifies an independent-sample Newcombe difference of proportions interval. Applying independent-sample confidence intervals to paired proportions is statistically invalid and misrepresents the standard error.",
      "required_change": "Specify a paired-sample method for the difference in proportions (e.g., Newcombe's paired-sample method 10 or Tango's score test) for comparing CAPAS FA against judge arms."
    }
  ],
  "non_blocking_notes": [
    "Ground truth definition 'bueno = never corrected' carries an inherent survival bias: obscure false claims that nobody audited remain 'bueno'.",
    "Allowing both coders to be Krenn-IQ sessions (the authors' own system) even with a 'self-run' tag poses an epistemic conflict of interest; independent coders should be required for any confirmatory run.",
    "A sample size of 20 bad claims yields very wide Wilson 95% intervals (e.g., 0/20 has an upper Wilson bound of ~0.16; 3/20 already reaches ~0.36), making the upper-bound threshold of 0.30 fragile under modest sample sizes."
  ]
}
```

## 2026-10-14T17:21:36 · gemini / gemini-3.8-flash · prereg sha256 88ccefd8d51af91fcbfe640a712e7d728099f872fcb22f55c779d43a47ce54dd

```json
```json
{
  "decision": "OBJECT",
  "blocking_objections": [
    {
      "section": "9. Sealing order & 2. Batch X6",
      "objection": "The ground-truth outcome file and/or the rules determining outcomes are neither frozen nor hashed in SEAL.json. Section 2 defines the outcome as 'the project's own later correction (bueno = never corrected)', but does not specify the terminal commit horizon for corrections or hash the outcome table prior to sealing. This allows the authors to classify claims as bueno or corrected with post-hoc knowledge of CAPAS and judge verdicts.",
      "required_change": "Explicitly specify the exact commit hash defining the outcome evaluation horizon (or hash the ground-truth outcomes dataset directly in SEAL.json before coding begins), and include its sha256 in SEAL.json."
    },
    {
      "section": "2. Batch X6 (Contamination)",
      "objection": "The contamination clause ('A claim is excluded if a coder could see its outcome. The exclusion count and its causes are published.') lacks an operational, objective definition and does not specify when contamination exclusions occur. This creates post-hoc researcher discretion to drop false accepts by asserting coder exposure after outcomes are observed.",
      "required_change": "Specify an objective, deterministic rule for detecting contamination (e.g., git log inspection for coder username/session overlap prior to verdict generation), and mandate that all contamination exclusions must be logged and frozen before verdict generation and unblinding."
    },
    {
      "section": "3. Arms & 9. Sealing order",
      "objection": "Judge model IDs are omitted from the pre-registration text and deferred to SEAL.json with the vague constraint 'from at least two companies'. This allows the authors to unilaterally select underpowered or uncalibrated models at sealing without reviewer sign-off. Additionally, it is unclear which model serves as Judge A vs Judge B, or how multiple models are aggregated into 'the best judge arm'.",
      "required_change": "Name the specific model IDs, providers, and exact inference parameters (e.g., top_p, seed) in the pre-registration text prior to co-signing, and specify how arms map to distinct models."
    },
    {
      "section": "5. Pre-specified pass/fail for CAPAS & 6. What would count against CAPAS",
      "objection": "The core research question of §1 ('does a deterministic claim gate produce fewer false accepts than LLM judges?') is not included in the five numbered pass/fail criteria of §5. If CAPAS achieves criteria 1–5 but fails to demonstrate a significantly lower FA than the LLM judges, §6 does not mark this as a failure of CAPAS, allowing the authors to declare success on X6 despite failing the comparative hypothesis.",
      "required_change": "Add a sixth mandatory pass criterion to §5: the 95% Newcombe paired-difference interval between CAPAS FA and the best eligible judge arm's FA must lie strictly below zero. Amend §6 to state that failing this comparison constitutes an overall study failure."
    },
    {
      "section": "2. Batch X6 (Coders) & 3. Arms",
      "objection": "Two blind coders code each claim independently, but the protocol does not define which coder's output is fed into CAPAS and Judge B when both coders agree on required fields but disagree on non-required fields or formatting. Arbitrary selection of coder records permits post-hoc optimization for CAPAS.",
      "required_change": "Pre-specify a deterministic resolution rule (e.g., automated tie-breaking via primary designated coder or strict consensus requirement across all coded fields) before feeding inputs to CAPAS and Judge B."
    }
  ],
  "non_blocking_notes": [
    "Generating the candidate shuffle seed from the sha256 of this document allows authors to search for favorable candidate subsets by making trivial cosmetic edits before sealing. Using an external future entropy source (e.g., a specific future Bitcoin block hash) is standard best practice.",
    "Section 5 should define eligibility criteria for a judge arm (e.g., meeting the minimum ACCEPT floor of 40%) so that a degenerate judge that emits REWRITE or HOLD for all claims cannot force an FA of 0 and render the comparative test vacuous."
  ]
}
```
```

## 2026-10-14T17:23:48 · gemini / gemini-3.8-flash · prereg sha256 36e683d91f5edda20df8a288bc3fdc00442464bdb6b6a468dbfb45e25a211ae0

```json
{
  "decision": "OBJECT",
  "blocking_objections": [
    {
      "section": "2. Batch X6 (Outcome rule) & 9. Sealing order",
      "objection": "C2 is defined as the source repository's HEAD at 23:59 UTC on the 30th day after the tag push, while verdicts are sealed immediately after coding (step 6). Because the source repository is the project's own repository ('Paper - Inverse Ginibre Overlap'), the authors retain write/commit access during the 30-day window after their verdicts are already known. This allows retroactive commits that mark specific claims as corrected, withdrawn, or refuted (or deliberately withhold corrections), enabling direct manipulation of ground-truth labels (malo vs bueno) to engineer a CAPAS victory.",
      "required_change": "C2 must be frozen to a historical commit hash that exists prior to the push of the tag, or the protocol must mandate that the source repository is an immutable public mirror with all commit access cryptographically locked/revoked from the authors and affiliated accounts upon sealing. No commits made after verdict sealing may be used to determine outcome labels."
    },
    {
      "section": "2. Batch X6 (Coders) & 5. Pre-specified pass/fail for CAPAS",
      "objection": "The protocol permits the batch to be coded entirely by two author-controlled 'Krenn-IQ sessions' (§2), merely downgrading the label to 'self-run' (§7). However, §5 states that 'The study succeeds only if all six criteria hold' without requiring coder independence. Because CAPAS operates directly on the structured evidence fields extracted by these coders, author-run LLM sessions can code evidence fields in a manner tailored to CAPAS's deterministic rule table while leaving Judge A on raw text. This allows the authors to claim an official study success on an unblinded, non-independent evaluation.",
      "required_change": "Add an explicit criterion to §5 specifying that a pass/success of the pre-registered study requires independent external coders with no affiliation to the authors or Krenn-IQ. If coders are self-run Krenn-IQ sessions, the protocol must pre-specify that the run is invalid for confirmatory pass/fail claims."
    },
    {
      "section": "3. Arms & Appendix A. Judge prompt templates",
      "objection": "Judge A is prompted with 'Source excerpt the claim was taken from: «{excerpt}»', but the protocol never defines how {excerpt} is constructed, bounded, or extracted from the source file. If coders or authors manually choose the excerpt, they can starve Judge A of context or select biased snippets. If it is extracted automatically, no deterministic window, character limit, or algorithm is specified or hashed in SEAL.json.",
      "required_change": "Provide a fully deterministic, automated specification for {excerpt} (e.g., fixed symmetric line/character window around the claim line, or verbatim full-file insertion with explicit token truncation rules), implement it in a hashed script referenced in SEAL.json, and prohibit coders from selecting or modifying the excerpt seen by Judge A."
    },
    {
      "section": "2. Batch X6 (Coders) & 4. Measures (HOLD share)",
      "objection": "§2 states that 'A claim whose coders disagree on a required field of its claim type is excluded and recorded as HOLD.' It is ambiguous whether this exclusion removes the claim from the 'clean' set entirely, whether it applies to Judge A (which does not depend on coded fields), and how it is categorized under §4 ('with each HOLD labelled field_absent or engine_gap'). Disagreements on required fields are coder divergences, not field absence or engine gaps. If difficult claims are shunted into coder-disagreement HOLDs, they can artificially suppress CAPAS's false accept rate and distort paired comparisons against Judge A.",
      "required_change": "Clarify that clean claims include all non-contaminated claims, specify whether coder disagreement forces HOLD across all arms (including Judge A), and add a distinct HOLD category ('coder_disagreement') that is accounted for in the HOLD share cap (Criterion 4) so coder disagreements cannot be used to discard unlicensable claims."
    },
    {
      "section": "2. Batch X6 (Size) & 5. Pre-specified pass/fail for CAPAS",
      "objection": "The protocol requires 'At least 20 bad and 20 good clean claims', but does not define what happens if the extraction and 30-day labeling yield fewer than 20 bad or 20 good clean claims. Without a pre-specified abort/invalidation rule, the authors could claim a pass on an underpowered sample under the 'pilot-grade' label despite violating the sample size constraint.",
      "required_change": "Explicitly state in §5 that if the clean sample yields fewer than 20 bad or fewer than 20 good claims, the study is declared inconclusive/void and cannot be claimed as a study pass or success under any label."
    }
  ],
  "non_blocking_notes": [
    "Judge B is asked whether evidence fields license the claim without being supplied the claim-type schema or rule table definitions, which systematically disadvantages Judge B relative to CAPAS.",
    "If CAPAS and the best judge both achieve FA = 0, the paired-difference interval will not lie strictly below zero, causing CAPAS to fail Criterion 6 despite zero false accepts; confirm whether ties at zero are intended as study failures."
  ]
}
```

## 2026-10-14T17:28:36 · gemini / gemini-3.8-flash · prereg sha256 44bc709157fe4140aeee894e6d22251fa71b7af46cb1b2e40af473c230e2e65f

```json
{
  "decision": "OBJECT",
  "blocking_objections": [
    {
      "section": "§9. Sealing order (and §2. Batch X6)",
      "objection": "§2 states that 'C2 is the source repository's HEAD at sealing, and its hash is in SEAL.json', but §9 step 2 specifies recording 'commits C0 and C1 of the source repository, and the date that fixes C2'. Recording a date rather than the cryptographic commit hash leaves commit C2 mutable or ambiguous against git commit date manipulation, creating a loophole where the outcome boundary is not cryptographically pinned.",
      "required_change": "Reconcile §9 with §2 so that the exact git commit hash of C2 (HEAD at sealing) and the repository's canonical remote URL are explicitly listed as required fields in SEAL.json."
    },
    {
      "section": "§3. Arms (Judge models) & Appendix A",
      "objection": "The inference parameter is capped at max 8 output tokens without a pre-registered parsing/extraction rule. Real LLMs often produce leading whitespace, markdown formatting (e.g., '**ACCEPT**'), or trailing punctuation. If run_judges.py implements a brittle exact-match parser, valid judge verdicts will fail to parse and lower the judge's ACCEPT floor below the 40% eligibility threshold, allowing CAPAS to eliminate competitors via artificial disqualification.",
      "required_change": "Pre-specify the verdict normalization and parsing rule in the text (e.g., case-insensitive regex extracting the first occurrence of ACCEPT, REWRITE, REJECT, or HOLD, ignoring markdown, whitespace, and punctuation) and define the explicit fallback handling for any output lacking a valid token."
    },
    {
      "section": "§2. Batch X6 (Coders) & §7. Known limits",
      "objection": "Validity condition V3 in §5 strictly requires that 'Both coders are independent of the authors and of Krenn-IQ' for a pass to be claimed. However, §2 states 'If both are Krenn-IQ sessions, the batch is labelled self-run and its rates are not called independent', and §7 states 'With two Krenn-IQ coders the run is exploratory'. This phrasing leaves an opening to claim a confirmatory run if only one coder is an author or Krenn-IQ session.",
      "required_change": "Harmonize §2 and §7 with V3 by explicitly stating that if *either* coder is affiliated with the authors or Krenn-IQ, the batch is exploratory/self-run and V3 fails."
    }
  ],
  "non_blocking_notes": [
    "Verify that the judge model IDs ('gemini-3.8-flash' and 'openai/gpt-oss-120b') actually resolve on their designated endpoints prior to sealing; under §5 Criterion 6, failure of all judge arms to run will cause the evaluation to fail outright.",
    "Since commits C0 and C1 and extract_candidates.py are fully fixed before coding, the pre-shuffle candidate pool and contamination list are fully deterministic; logging the contamination hash directly in SEAL.json rather than deferring to an unsealed successor record (CODING_START.json) would strengthen verification."
  ]
}
```

## 2026-10-14T17:31:21 · gemini / gemini-3.8-flash · prereg sha256 e4569ae93db5d342ef0db657b0796251a29ae04ec6d5d45f5910b5f120b324d2

```json
{
  "decision": "OBJECT",
  "blocking_objections": [
    {
      "section": "2. Batch X6 (Excerpt & Contamination)",
      "objection": "There is a direct contradiction regarding coder information access that risks unblinding coders without triggering contamination exclusions. Under 'Excerpt', the protocol states coders and Judge A see lines L−40 to L+40. Under 'Contamination', it states 'The coder sees the claim's source file at its assert commit (git show <commit>:<file>), nothing later', while contamination is evaluated solely on whether 'that excerpt already contains an outcome word'. If coders inspect the full file via git show, any outcome word appearing outside lines L−40 to L+40 unblinds the coder to the outcome while evading the excerpt-only contamination filter, creating an asymmetric leak that directly informs the evidence fields passed to CAPAS and Judge B.",
      "required_change": "Explicitly restrict coders to viewing exclusively the identical excerpt provided to Judge A (lines L−40 to L+40), OR expand the pre-sealing contamination filter in extract_candidates.py to scan the entire source file at the assert commit rather than just the excerpt."
    },
    {
      "section": "2. Batch X6 (Coders)",
      "objection": "The coder disagreement exclusion rule only specifies that 'A claim whose coders disagree on a required field of its claim type is excluded'. It fails to specify what happens if the two blind coders disagree on the 'claim_type' itself. If coders assign different claim types (e.g., one codes as a benchmark metric, the other as a theoretical proof), they will evaluate different required field sets, leaving the agreement calculation undefined or subject to post-hoc resolution via the primary coder.",
      "required_change": "Explicitly state that a disagreement between the two coders on 'claim_type' is an automatic coder-disagreement exclusion that removes the candidate claim from the clean set of all arms under V2."
    },
    {
      "section": "3. Arms (Eligibility) and 5. Pre-specified pass/fail for CAPAS (Criterion 6)",
      "objection": "'The best judge arm' is defined as the eligible Judge A or Judge B arm with the lowest FA. If two or more eligible judge arms tie on the lowest FA (e.g., both yield 1 false accept out of 20 bad claims), the protocol provides no tie-breaking rule. Because discordant pairs with CAPAS can differ across tied judges, the Newcombe paired-difference interval could fall strictly below zero against one tied judge but cross zero against another, creating an unearned researcher degree of freedom to select the favorable comparison post hoc.",
      "required_change": "Specify an unambiguous, deterministic tie-breaker when multiple eligible judge arms tie for the lowest FA (e.g., the tied arm with the higher ACCEPT floor, breaking further ties by Judge A over Judge B; or requiring CAPAS's paired-difference interval to lie strictly below zero against ALL tied lowest-FA judge arms)."
    }
  ],
  "non_blocking_notes": [
    "Section 9, Step 5 states 'Only then are the claims extracted and coded', but Step 2 already includes the sha256 of the candidate list in SEAL.json. Clarify Step 5 phrasing to 'Only then is the 120-claim sample drawn via the NIST beacon seed and coded'.",
    "Ensure the designated judge endpoints and model IDs ('gemini-3.8-flash' and 'openai/gpt-oss-120b' on Groq) are verified as active and accessible immediately prior to sealing, as unresolvable model endpoints will cause arms to be marked 'not run', and if all judge arms fail to run, Criterion 6 will automatically fail the study."
  ]
}
```

## 2026-10-14T17:34:01 · gemini / gemini-3.8-flash · prereg sha256 a5e999e50d070a3b1560e714a7472a7baaa68c8d7305612c9c3ad72399722af0

```json
{"decision": "CO-SIGN", "blocking_objections": [], "non_blocking_notes": ["In Appendix A, Judge B's prompt asks 'Do these fields license a claim of this type?' rather than referencing the specific claimed assertion or including {claim_text}. While this may disadvantage Judge B, it cannot be exploited to manufacture an unearned victory because Criterion 6 requires CAPAS to strictly outperform the best eligible judge arm (which includes Judge A with full excerpt access), and ties or an empty eligible set result in study failure.", "At the V1 floor of 20 bad claims, the requirement that the Newcombe 95% paired-difference interval lie strictly below zero demands a stark difference in discordant pairs (e.g., at least 5–6 discordant pairs favoring CAPAS with zero in the opposite direction for McNemar/Newcombe significance), meaning statistical power at pilot size is low and favors the null/failure rather than an unearned pass."]}
```

## 2026-10-14T17:35:35 · gemini / gemini-3.8-flash · prereg sha256 443b8b422966a9860cc3ddb0dfd90899db1bf5bb0808a4ff23089d758dde6cc5

```json
{
  "decision": "OBJECT",
  "blocking_objections": [
    {
      "section": "3. Arms (Verdict parsing)",
      "objection": "In Version 7, the token limit was raised from 8 to 1,024 tokens to accommodate reasoning models (`gpt-oss-120b` with `reasoning_effort: low`). However, verdict parsing still specifies 'the first case-insensitive match of \\b(ACCEPT|REWRITE|REJECT|HOLD)\\b in the output'. Reasoning models frequently discuss the candidate options during their chain of thought or preamble (e.g., 'We evaluate whether to ACCEPT... but find the claim contradicted, so we REJECT'). Taking the first match will misclassify rejections as ACCEPTs whenever 'ACCEPT' appears earlier in deliberation. This systematically inflates the LLM judge's false accept rate (FA) on bad claims, allowing CAPAS to claim an unearned victory on Criterion 6.",
      "required_change": "Specify that reasoning/thought blocks (such as `<think>...</think>` tags or API `reasoning_content` fields) must be stripped prior to parsing, and parse the final (last) match of `\\b(ACCEPT|REWRITE|REJECT|HOLD)\\b` in the terminal answer rather than the first match."
    }
  ],
  "non_blocking_notes": [
    "Verify that `run_judges.py` extracts completion text from `message.content` rather than concatenating `reasoning` or `reasoning_content` fields provided by Groq/OpenAI-compatible endpoints.",
    "The 40% ACCEPT floor eligibility requirement remains an effective safeguard against trivial REWRITE/HOLD spamming by judge arms."
  ]
}
```

## 2026-10-14T17:36:23 · gemini / gemini-3.8-flash · prereg sha256 1e5427f1f5a489b2f1c05bd6993e8290a6a53983a582d1a6d200c81e470db980

```json
```json
{
  "decision": "CO-SIGN",
  "blocking_objections": [],
  "non_blocking_notes": [
    "The parsing ambiguity from v7 has been resolved by cleanly separating reasoning/think blocks and anchoring verdict extraction to the last word-boundary match of the four canonical verdicts in message.content.",
    "The 1,024-token ceiling combined with reasoning_effort: low for gpt-oss-120b resolves the empty-completion failure mode observed in v7 while remaining bounded.",
    "Candidate selection, outcome labelling, and coder assignment are strictly locked against future external entropy (NIST beacon) and pre-sealing git commits (C0, C1, C2), preventing retrospective curation.",
    "Eligibility and tie-breaking rules in §3 and §5 strictly prevent claiming an unearned win against abstaining or tied judges."
  ]
}
```
```

## Status (2026-10-14)

- **Co-signature.** Version 8 (sha256 `1e5427f1f5a489b2f1c05bd6993e8290a6a53983a582d1a6d200c81e470db980`) is co-signed by `gemini-3.8-flash` (Google) with no open blocking
  objection.
- **Objections along the way.** Versions 1–5 drew 4, 5, 5, 3 and 3 blocking objections. Version 6 was co-signed.
  Before sealing, a check of the endpoints found that the 8-token output limit returned empty answers from
  `gpt-oss-120b`. Version 7 raised the limit and drew one objection about how the verdict is parsed. Version 8
  answered it and was co-signed.
- **Why Gemini.** xAI (`grok-4.7`) and DeepSeek were tried first and refused the request. xAI reported its credits
  were exhausted; DeepSeek reported an insufficient balance.
- **Not yet sealed.** Sealing (§9) still needs four things, each hashed in `SEAL.json` before the tag is pushed:
  - `extract_candidates.py`;
  - `label_outcomes.py`;
  - `run_judges.py`;
  - two coders independent of Krenn-IQ (V3).

  Any change to the document voids this co-signature, and a new one is requested.
