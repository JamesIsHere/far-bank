import g3Package from "../g3-workflow-package.json";
import Link from "next/link";

export default function EvidencePage() {
  return (
    <>
      <a className="skip-link" href="#gate-evidence">Skip to Gate evidence</a>
      <header className="app-header">
        <Link className="app-brand" href="/"><span>FAR BANK</span><strong>G3 Review</strong></Link>
        <nav className="mode-nav" aria-label="Review workspace sections">
          <Link href="/">Review queue</Link><Link aria-current="page" href="/evidence">Gate evidence</Link>
        </nav>
        <div className="gate-status"><span aria-hidden="true" /><div><strong>G3 verdict pending</strong><small>Local review only</small></div></div>
      </header>

      <main className="evidence-page" id="gate-evidence">
        <header className="evidence-hero">
          <div><p className="eyebrow">GATE EVIDENCE</p><h1>Why this workflow is ready to inspect</h1><p>The audit material is separated from the working queue so it remains available without competing with the review task.</p></div>
          <div className="verdict-stamp"><span>G3 verdict</span><strong>NOT ISSUED</strong><small>Human decision required</small></div>
        </header>

        <section className="evidence-grid" aria-label="Gate evidence summary">
          <article><span>Action routes</span><strong>{g3Package.workflow.actions.length} / 4</strong><p>Approve · Reject · Revise · Comment</p></article>
          <article><span>Cold reconstruction</span><strong>{g3Package.projection.equivalent_to_cold_reconstruction ? "AGREES" : "MISMATCH"}</strong><p>{g3Package.projection.canonical_input_count} canonical inputs</p></article>
          <article><span>Coverage effect</span><strong>{g3Package.sample.production_coverage_contribution}</strong><p>Historical sample only</p></article>
          <article><span>Package status</span><strong>READY</strong><p>Human verdict still required</p></article>
        </section>

        <section className="revision-boundary" aria-labelledby="revision-heading">
          <div><p className="eyebrow">REVISION BOUNDARY</p><h2 id="revision-heading">Approval does not cross versions</h2><p>The same question received new content and a new hash. Its earlier approval was automatically invalidated.</p></div>
          <div className="version-flow">
            {g3Package.revision_boundary.exact_version_state.map((state, index) => (
              <article className={`version-state ${state.learner_ready ? "ready" : "invalidated"}`} key={state.version_id}>
                <span>{index === 0 ? "PRIOR VERSION" : "NEW VERSION"}</span><strong>{state.version_id}</strong><code>{state.content_sha256}</code>
                <p>{state.latest_decisive_action === "auto_invalidate" ? "AUTO-INVALIDATED · NOT READY" : "EXACT APPROVAL · READY"}</p>
              </article>
            ))}
            <div className="carry-forward"><strong>NO</strong><span>approval carry-forward</span></div>
          </div>
        </section>

        <section className="audit-sections">
          <details open>
            <summary>Hands-on Gate G3 checklist <span>{g3Package.hands_on_steps.length} steps</span></summary>
            <ol>{g3Package.hands_on_steps.map((step, index) => <li key={step}><span>{index + 1}</span><p>{step}</p></li>)}</ol>
          </details>
          <details>
            <summary>Preserved limitations <span>{g3Package.limitations.length} limits</span></summary>
            <ul>{g3Package.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul>
          </details>
          <details>
            <summary>Exact evidence artifact hashes <span>{g3Package.evidence_artifacts.length} files</span></summary>
            <div className="source-manifest">{g3Package.evidence_artifacts.map((source) => <div key={source.path}><span>{source.path}</span><code>{source.sha256}</code></div>)}</div>
          </details>
        </section>

        <Link className="back-to-review" href="/">← Return to the review queue</Link>
      </main>
    </>
  );
}
