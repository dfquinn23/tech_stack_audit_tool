# Tech Stack Audit Report
_Generated: 2025-08-12 09:50_

---
### Advent Axys
_Category: Operations • Users: Portfolio Management • Criticality: High_

> No changelogs found for this tool (mock source).

### CSSI
_Category: Distribution • Users: Distribution • Criticality: Low_

> No changelogs found for this tool (mock source).

### FactSet
_Category: Research • Users: Portfolio Management • Criticality: High_

**Summaries**
- Introduced a new ESG scoring model that uses more detailed, globally sourced metrics to deliver broader and more consistent ESG assessments.

**Audit Insights**
- Update: New ESG scoring model leveraging more detailed, globally sourced metrics for broader, more consistent ESG assessments.
- Why it matters:
  - Improves comparability and global coverage, enabling consistent ESG screens/tilts across multi-region portfolios.
  - Enhances portfolio construction inputs for ESG-integrated strategies (constraints, targets, factor control).
  - Strengthens client reporting and regulatory alignment (SFDR 8/9, CSRD, stewardship), reducing manual reconciliation.
  - Supports scalable product development across equity and credit.
  - Better risk management via earlier ESG outlier/controversy detection; aids pre-trade compliance and engagement.
  - Reduces single-vendor dependence; offers triangulation for robust decisions and RFP defensibility.
  - Potentially improves backtesting fidelity if sufficient history and stable methodology are provided.
- Risks/challenges:
  - Methodology divergence vs. incumbent providers may drive score drift and unintended turnover.
  - Limited/evolving history or backfill practices can bias backtests.
  - Opaque inputs/weights risk “black box” perceptions and greenwashing claims.
  - Embedded regional/sector/size biases may lift tracking error.
  - Coverage gaps (SMID, private issuers, certain FI) and issuer-entity mapping complexities.
  - Integration effort: security master mapping, screen recalibration, compliance/risk rule updates.
  - ESG scores alone may not fulfill SFDR PAI/Taxonomy disclosure requirements.
  - Change management: disclosures, marketing updates, and client consents where vendor is specified.
  - Vendor dependency/costs; monitor SLAs, cadence, versioning, change notices.
  - Model risk from methodology updates; requires variance monitoring and exception handling.
  - Data/controversy timeliness and correction workflows affect trust.
  - Performance impacts on factor exposures/risk budgets; needs ex-ante/ex-post analysis.
- Recommendation: Pilot now; defer full production until validated via a 1–2 quarter parallel test across representative equity and credit strategies.
  - Actions:
    - Obtain methodology, data lineage, coverage stats, history, change log; map to SFDR PAIs and frameworks (TCFD/ISSB).
    - Analyze portfolio impact: score dispersion, holdings migration, turnover, tracking error, factor shifts, performance sensitivity.
    - Validate data quality across regions/sectors; assess controversy timeliness and corrections.
    - Governance: route through Model Risk/ESG Committee; document use case, limits, monitoring, rollback; enable versioning/audit trail.
    - Client/compliance: draft disclosures; identify mandates needing consent; align stewardship narratives.
    - Integration: set entitlements, map to security master, stage in research; hold production screens until sign-off.
- Timeline: Start immediate evaluation/shadow use; target go/no-go in 8–12 weeks with phased rollout by strategy if favorable.

**Integration Opportunities**
- ESG Drift Monitor — Trigger: Daily 7:00am ET. Key nodes: Cron, SharePoint/Teams (Graph), CSV, FactSet API, Code. Steps: Pull Axys holdings, fetch ESG/controversies, compare vs prior snapshot, write snapshot/exceptions, alert PMs in Teams. Value: Catches ESG drift; cuts manual reviews ~60–80%; speeds PM response.
- Pre-Trade ESG Gate — Trigger: New file in SharePoint “Proposed Trades.” Key nodes: Graph (SharePoint/Outlook/Teams), CSV, FactSet API, Code. Steps: Parse trades, fetch ESG/controversy flags, apply mandate rules, write pass/warn/block file, notify Trader + Compliance. Value: Reduces pre-trade checks from hours to minutes; creates audit trail; lowers breach risk.
- Client ESG Snapshot Pack — Trigger: Quarter-end or new Axys positions. Key nodes: Cron, Graph (SharePoint/Outlook), CSV/Excel, FactSet API, Wealthbox API. Steps: Join holdings with ESG, compute portfolio metrics, produce one-tab Excel per household, create Wealthbox note/task, email RM summary. Value: Saves ~30–60 min per review; strengthens ESG communication and retention.
- ESG Vendor Divergence Scorecard — Trigger: Weekly “Bloomberg ESG Export.” Key nodes: Graph (SharePoint/Teams), CSV, FactSet API, Code, Excel. Steps: Compare Bloomberg vs FactSet ESG, flag variances, publish scorecard, update exceptions, post Teams summary. Value: Manages methodology divergence; reduces unintended turnover; documents due diligence.
- Schwab ESG Restriction Breach Log — Trigger: IMAP email with Schwab daily positions. Key nodes: IMAP, CSV, FactSet API, Wealthbox API, Graph (SharePoint/Outlook). Steps: Ingest positions, map to households/restrictions, classify vs restricted themes/controversies, log breaches with evidence, create Wealthbox note/task, email Compliance. Value: Near real-time mandate adherence; audit-ready logs; fewer manual reconciliations.

### Bloomberg
_Category: Research • Users: Portfolio Management • Criticality: High_

**Summaries**
- Nov 5, 2024: Terminal Chat updated with improved query suggestions and enhanced portfolio tagging to speed information retrieval and portfolio organization.

**Audit Insights**
- Why it matters
  - Faster research workflows; quicker access to relevant functions, news, filings, estimates, and market data during pre-trade and monitoring.
  - Reduces reliance on mnemonics; aids onboarding and cross-coverage; improves search consistency.
  - Portfolio-centric tagging anchors queries, news, and notes to mandates/sleeves; streamlines morning prep and client-ready commentary.
  - Better recall of material events tied to holdings; fewer misses impacting performance or risk.
  - Potentially improves auditability if tagged research/retrieval trails are linked to investment decisions (subject to retention/integration).
  - Enhances collaboration by standardizing tags and views across PM/analyst pods.

- Risks and challenges
  - AI suggestion quality; risk of irrelevant/incomplete outputs—requires human validation.
  - Mis-tagging governance; risk of cross-client contamination or inappropriate distribution.
  - Data privacy/IP; avoid pasting PII, MNPI, or proprietary models; confirm Bloomberg data handling and model-training posture.
  - Records retention/supervision; verify archiving coverage (e.g., Bloomberg Vault/firm archives) to avoid regulatory gaps.
  - Information barriers; ensure restricted list controls and least-privilege visibility for portfolio-linked items.
  - Taxonomy sprawl; enforce standards to prevent noisy retrieval.
  - Complex mapping for derivatives/custom baskets/sleeves; align to the firm’s portfolio/security master.
  - Vendor/operational dependency; maintain fallbacks for outages.
  - Research inducement/entitlements (MiFID II); ensure surfaced broker content respects entitlements and cost-allocation policies.

- Adoption recommendation
  - Proceed with a limited, controlled pilot on 1–2 desks (low lift, clear productivity upside) with guardrails.
  - Pre-requisites:
    - Define a tagging taxonomy aligned to portfolio master (IDs, sleeves, benchmarks); assign data stewards.
    - Configure role-based access; restrict cross-user sharing per policy.
    - User guidance: no PII/MNPI/proprietary models; verify AI outputs; document use in investment memos as needed.
    - Compliance/Legal/InfoSec review: confirm data handling, logging, archiving/supervision; obtain vendor assurances (SOC 2, DPA, model-training statements).
    - Integration decision: determine export of tags/notes to RMS vs. Bloomberg-only to avoid split knowledge bases.
  - KPIs: search-to-insight time, missed material events, PM satisfaction, onboarding time reduction, percent of correctly tagged items.
  - Broader rollout contingent on accuracy, governance adherence, confirmed records capture, and stable user adoption; if retention/governance lag, monitor and revisit next quarterly review.

**Integration Opportunities**
- Portfolio-Tagged Chat to SharePoint + CRM
  - Trigger: Outlook “research@” receives Terminal Chat export with portfolio tag in subject/header.
  - Key Nodes: Microsoft Graph (Mail), Code (parse), SharePoint, Microsoft Teams, Wealthbox.
  - Steps: Parse [PORT:…]/tickers; normalize to PDF/HTML; save to SharePoint /Research/<Portfolio>/ with retention label; create Wealthbox note + follow-up task; post Teams message with link/tickers.
  - Value: Centralizes tagged research; improves recall/collaboration; saves 1–2 hours/week per analyst; auditable portfolio linkage.

- Tagged News-to-PM Pod Triage
  - Trigger: Bloomberg news alert email with portfolio tag hits Outlook.
  - Key Nodes: Microsoft Graph (Mail), SharePoint (Advent Axys holdings CSV), CSV, Code, Microsoft Teams, Wealthbox.
  - Steps: Extract tickers/portfolio tag; filter to held names and add weights; post prioritized Teams card; create Wealthbox task; archive to SharePoint.
  - Value: Cuts noise and missed events; faster pre-market triage; 40–60% fewer irrelevant pings; better coverage of material items.

- Terminal Chat Supervision Archive
  - Trigger: Event-driven on new Chat export or nightly schedule.
  - Key Nodes: Microsoft Graph (Mail), SharePoint (Records/Retention), Code (keyword scan), Microsoft Graph (Mail), CSV.
  - Steps: Ingest and render to PDF/HTML; store in immutable SharePoint Records; scan for MNPI/restricted terms; email Compliance exception report; append rolling CSV log.
  - Value: Closes retention/supervision gaps; audit-ready research trail tied to portfolios; reduces regulatory risk and review time.

- Morning Brief from Chat + FactSet
  - Trigger: 7:30am ET scheduled run.
  - Key Nodes: SharePoint (last 24h chat exports), Microsoft Graph (Mail) for FactSet snapshots, HTML template, Microsoft Teams, Microsoft Graph (Mail).
  - Steps: Aggregate portfolio-tagged Chat notes; extract FactSet EPS/rating/target changes overlapping holdings; generate HTML brief per portfolio; email distro; post to Teams; save to SharePoint.
  - Value: Speeds morning prep and alignment; consistent portfolio-centric brief; saves 30–45 minutes per pod daily.

- Trade Rationale Linker (Schwab/CSSI -> Chat)
  - Trigger: Executed trade file (CSV) from CSSI/Schwab via SFTP/SharePoint.
  - Key Nodes: SFTP or SharePoint, CSV, Code, SharePoint, Wealthbox, Microsoft Graph (Mail).
  - Steps: Parse trades (portfolio/ticker/timestamp); locate most recent tagged Chat note; attach permalink to trade record; create Wealthbox “Trade rationale” note; email Compliance summary; save enriched trade file to SharePoint.
  - Value: Tightens research-to-trade traceability; accelerates compliance responses; eliminates manual stitching of rationale to trades.

### Right Capital
_Category: Distribution/CS • Users: Distribution • Criticality: High_

> No changelogs found for this tool (mock source).

### Wealth Box
_Category: CRM • Users: Advisors • Criticality: High_

> No changelogs found for this tool (mock source).

### Schwab
_Category: Custodian • Users: Advisors • Criticality: High_

> No changelogs found for this tool (mock source).

### Zoom
_Category: Productivity • Users: All • Criticality: Medium_

**Summaries**
- [2024-12-25] Added post-meeting summaries and smart highlights to speed review of key points.
- [2025-03-01] Improved Outlook calendar syncing for more reliable cross-platform invitations.

**Audit Insights**
- Post-meeting summaries and smart highlights (12/25/2024)
  - Why it matters: Faster follow-ups; less admin for PMs/analysts; consistent capture of decisions/actions; better client recaps; stronger knowledge retention.
  - Risks: AI accuracy/nuance gaps; MNPI/confidentiality leakage; books-and-records retention; vendor/data residency concerns; consent/disclosure; access controls; licensing/training and over-reliance.
  - Recommendation: Pilot 6–8 weeks with guardrails. Disable vendor/model training; set strict retention; integrate with archiving/eDiscovery; map to data classification and auto-disable for Restricted/MNPI; require consent prompts and host confirmation with externals. Mandate human review before distribution/CRM push; apply disclaimers; reconcile with official minutes. Expand phased rollout if KPIs (time saved, error rates, policy exceptions) are met.
- Outlook calendar syncing improvements (03/01/2025)
  - Why it matters: More reliable client/broker scheduling; fewer ghost events; better room/resource booking; reduced helpdesk load.
  - Risks: API scope/permission changes; rollout glitches (duplicates/links); automation dependencies; notification volume/throttling.
  - Recommendation: Quick pilot across time zones and shared/delegated mailboxes. Validate Zoom app scopes, CA/MFA compatibility, DLP/classification. Test reschedules/cancellations/series updates; monitor invite failures/duplicates/join errors/helpdesk tickets 2–4 weeks. If stable, enable org-wide; minor policy updates only.

**Integration Opportunities**
- Client Meeting Summary → SharePoint + Wealthbox + Draft Email — Trigger: Zoom meeting.ended; Steps: fetch summary/transcript, file to client SharePoint, create Wealthbox note/tasks, draft Outlook recap; Value: save 20–30 min/meeting, consistent documentation with human review.
- Investment Committee Summary Compliance Archive — Trigger: meeting.ended with “[IC]” or host=Investment; Steps: store highlights in restricted SharePoint with metadata, upsert SharePoint List of decisions, email compliance/PMO digest; Value: centralized audit trail, faster exam prep.
- Outlook↔Zoom Invite Integrity + CRM Enrichment — Trigger: Outlook event with Zoom link; Steps: cross-check Zoom owner/time, upsert Wealthbox meeting from attendees, notify organizer of conflicts/missing IDs; Value: fewer failed joins/double-bookings, complete CRM capture.
- Webinar Attendees → Wealthbox + Right Capital Nurture — Trigger: Zoom webinar.ended; Steps: sync registrants/attendees, tag contacts, draft personalized follow-ups with planning link, create advisor tasks; Value: higher webinar-to-meeting conversion.
- Schwab Service Call Capture to CRM + Compliance — Trigger: meeting.ended with “Schwab” or external client; Steps: pull summary, create Wealthbox service case with SLA, file to SharePoint with metadata, email Ops/Compliance; Value: better SLA adherence and defensible records.

### 365
_Category: Productivity • Users: All • Criticality: High_

**Summaries**
- Jan 22, 2025: Copilot is fully embedded in Word and Excel to create summaries and automate common tasks.

**Audit Insights**
- Why it matters
  - Speeds client materials (commentaries, factsheets, RFP/DDQs, board packs), shortening month/quarter-end cycles and time-to-market.
  - Boosts Excel productivity (data cleaning, reconciliations, variance analysis, pivots/charts) while reducing routine errors.
  - Standardizes tone/structure using reusable prompts and templates for brand and compliance consistency.
  - Improves internal productivity (meeting notes, actions, policy drafts) and quality control via summaries and inconsistency flags.
  - Expected 10–30% uplift for Marketing/Client Reporting, Operations, PMO, and Research support.
- Risks and challenges
  - Accuracy/hallucination risk in text, formulas, and summaries; must enforce human review, especially for NAV, attribution, and client reports.
  - Data leakage via oversharing in M365; permissions hygiene is critical to avoid exposing MNPI/PII/confidential memos.
  - Compliance/recordkeeping: preserve AI-assisted drafts and approvals; align with SEC/UK FCA/ESMA advertising and retention rules.
  - Model risk/governance: avoid overreliance; align with firm AI policy and emerging regulations (e.g., EU AI Act obligations for deployers).
  - Data residency/privacy: confirm tenant boundaries and Microsoft commitments (no training on your content).
  - Change management/training: prompt discipline and role-based enablement required to avoid uneven output.
  - Cost: ~$30/user/month; ROI hinges on targeting high-impact roles and measuring outcomes.
  - Technical/controls: macro/add-in interactions, workbook size; Track Changes/versioning; eDiscovery/audit of Copilot; needs mature IA, sensitivity labels/DLP, least-privilege, Conditional Access, managed devices.
- Adoption recommendation
  - Run a 6–12 week controlled pilot; target Marketing/Client Reporting, Operations/Finance, PMO/Research support (exclude front-office investment decision-making).
  - Prerequisites: permission recertification; Purview Sensitivity Labels (default non-public), auto-labeling, DLP; acceptable-use policy and human-in-the-loop for client comms; Purview Audit (Premium)/eDiscovery coverage; Conditional Access and verified tenant/EU-UK data boundary; role-specific prompt libraries, QA checklists; KPI tracking (cycle time, error/rework rates, adoption, incidents).
  - Commercials: restrict licenses to pilot; scale in phases post-pilot if controls and ROI validate; otherwise remediate IA/compliance gaps before broader rollout.

**Integration Opportunities**
- Quarterly Commentary Packager (FactSet/Bloomberg → 365): Trigger—new performance/attribution export in SharePoint; generates Word draft with Copilot narrative, routes for review, emails approved PDF, and logs to Wealthbox. Value: 30–50% faster cycle; standardized tone; full CRM/records trail.
- Zoom Meeting → Word Summary + Wealthbox: Trigger—Zoom recording/transcript available; creates Word summary with Copilot prompt, logs note + link to Wealthbox, and emails owner. Value: 20–40 minutes saved per meeting; consistent, retained notes.
- Schwab Daily Activity → Excel Variance + CRM Tasks: Trigger—daily CSV to Outlook; loads Excel with pivots + Copilot variance sheet, creates Wealthbox tasks, archives, and emails Compliance. Value: faster break triage; reduced manual Excel work; audit-ready artifacts.
- Axys Recon → Client Pack and Filing: Trigger—new Axys recon/performance export in SharePoint; builds Excel + Word summary with Copilot prompts; on approval, PDFs to client folder, emails, and logs to Wealthbox. Value: hours saved at month/quarter-end; standardized deliverables; complete records capture.
- RightCapital Plan Deliverable Orchestrator: Trigger—new/updated plan in RightCapital; files PDF to SharePoint, creates Word cover letter with Copilot highlights, drafts client email, logs to Wealthbox. Value: faster, consistent plan delivery with automated retention and CRM updates.
