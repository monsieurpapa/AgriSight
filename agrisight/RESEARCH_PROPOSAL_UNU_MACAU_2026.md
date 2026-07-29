# Research Proposal — UNU Macau Visiting Research Fellowship 2026

**Applicant:** [Your full name]
**Institutional affiliation:** [Your academic/research affiliation — required for eligibility]
**Proposed project:** AgriSight — Hybrid AI and Human-in-the-Loop Multi-Agent Architecture for Conflict-Aware Food Security Monitoring
**Track:** [Early-Career / Senior]
**Word count:** ~1,000

---

## 1. Strategic Alignment

AgriSight is a satellite-driven agricultural monitoring platform built for the Democratic Republic of Congo's Great Lakes region, where chronic conflict and climate stress compound to produce some of the world's most acute and least-monitored food security crises. The platform ingests Sentinel-2/Landsat imagery, computes vegetation indices (NDVI, EVI, NDWI, SAVI), and correlates crop stress against a live conflict-event layer to flag agricultural risk in near real time. This directly operationalizes UNU's mandate on "Digital Emerging Technologies for Sustainable Development" against three of its four named pillars:

- **Hybrid AI frameworks combining multiple learning approaches** — AgriSight already fuses statistical anomaly detection (historical NDVI deviation thresholds) with a scikit-learn classification layer, and the fellowship would extend this into a genuine hybrid architecture combining remote-sensing statistics, supervised ML, and lightweight language-model reasoning for stakeholder-facing outputs.
- **Multi-agent systems and computational modeling** — the current pipeline (ingestion → index calculation → anomaly detection → alerting) is implemented as a linear Celery task chain. The fellowship's core technical contribution is to re-architect this as a coordinated multi-agent system, detailed in Section 3.
- **Ethical human-AI collaboration and decision-making frameworks** — because false positives in conflict-zone alerting carry real humanitarian cost (misallocated aid, credibility loss with local partners), AgriSight's `is_verified` / `verification_notes` fields already encode a human-in-the-loop pattern. The fellowship formalizes this into a reusable decision framework.

This work is explicitly designed for operationalization by UN agencies and member states: the platform's existing user model already distinguishes `humanitarian`, `government`, `cooperative`, and `researcher` roles, mirroring exactly the stakeholder structure WFP, FAO, and OCHA field offices use for IPC (Integrated Food Security Phase Classification) reporting. UNU Macau's position at the intersection of AI research and UN operational bodies makes it the ideal host institution to pressure-test this pipeline against real IPC methodology and connect it to potential deployment partners.

## 2. Operational Feasibility

The proposal is scoped for a 2-month onsite residency and builds on a working system rather than a greenfield idea, which materially de-risks delivery within the fellowship window:

- **Weeks 1–2:** Formalize the multi-agent architecture design in collaboration with UNU Macau researchers; benchmark the existing anomaly-detection accuracy against publicly available IPC classification data for eastern DRC as ground truth.
- **Weeks 3–5:** Implement the agent decomposition (Section 3) and the human-verification decision framework; integrate a lightweight LLM-based reporting agent that translates raw index/anomaly output into plain-language French-and-Swahili briefings for field staff with varying technical literacy — directly addressing the "technologically-assisted learning models" pillar.
- **Weeks 6–7:** Run a validation study across 3–5 pilot regions using historical satellite and conflict-event data already in the platform's PostGIS store; produce a comparative evaluation against the current single-pipeline baseline.
- **Week 8:** Write up findings as a joint UNU-authored paper/technical report and package the multi-agent module for open release.

The technical prerequisites are already met: a working Django/GeoDjango/PostGIS backend, Sentinel Hub API integration, Celery-based async infrastructure, and a populated schema of regions, satellite imagery, vegetation indices, stress events, and conflict events. No new infrastructure procurement is required — the residency's compute needs are modest (CPU-bound ML inference plus API calls to Sentinel Hub) and can run on UNU Macau's existing research infrastructure or a modest cloud budget.

## 3. Innovation

The core innovation is decomposing AgriSight's monolithic processing pipeline into a coordinated multi-agent system with distinct, auditable responsibilities:

1. **Ingestion Agent** — schedules and retrieves satellite imagery per region, handles cloud-cover filtering and retry logic.
2. **Index Agent** — computes vegetation indices and maintains rolling historical baselines per region.
3. **Conflict-Correlation Agent** — cross-references detected stress against the conflict-event layer to distinguish climate-driven stress from conflict-driven land abandonment — a distinction current threshold-based systems conflate.
4. **Anomaly-Reasoning Agent** — a hybrid layer combining the existing statistical/ML detectors with a constrained LLM reasoning step that weighs multiple signals (index deviation, conflict proximity, seasonal norms) and produces a calibrated confidence score with an explanation, rather than a bare severity integer.
5. **Human-Verification Agent** — surfaces flagged events to human reviewers (humanitarian/government users) through a structured interface, captures their verification decisions, and feeds disagreements back as a supervised signal to recalibrate the Anomaly-Reasoning Agent — a concrete, auditable instance of ethical human-AI collaboration rather than a black-box override.
6. **Reporting Agent** — generates localized, role-appropriate briefings (technical for researchers, operational for field humanitarian staff) in French and Swahili.

This design is a novel contribution beyond existing satellite-based agricultural monitoring tools (which are typically single-model, English-only, and non-conflict-aware): it treats explainability, multilingual accessibility, and human oversight as first-class architectural components rather than post-hoc additions, and it produces an auditable record of every AI-to-human handoff — directly answering UNU's call for "ethical human-AI collaboration and decision-making frameworks."

## 4. Measurable Social Impact

The fellowship will report against concrete, pre-registered metrics:

- **Detection quality:** precision/recall of the hybrid multi-agent detector against IPC ground truth, benchmarked against the current single-pipeline baseline.
- **Time-to-alert:** median hours from satellite acquisition to verified, actionable alert reaching a humanitarian/government user.
- **Verification burden:** reduction in false-positive rate requiring human review, as a proxy for field-staff time saved.
- **Reach:** number of hectares and regions under active monitoring by residency's end, and number of partner organizations (target: at least one UN agency or DRC government body) engaged for pilot deployment discussion.
- **Knowledge transfer:** one peer-reviewed or UNU working paper, one open-source multi-agent module, and one reusable ethical human-AI verification framework documented for reuse by other UNU-affiliated sustainability projects.

Together these outputs meet the fellowship's requirement for a collaborative digital tool, a clear path to UN/member-state operationalization, and a rigorously measured social impact case rooted in one of the world's most under-monitored food security crises.
