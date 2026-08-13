import reviewData from "./review-data-v002.json";
import { ReviewActions } from "./review-actions";

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function displayValue(value: { value_type: string; value: string | number | boolean | null; unit?: string }) {
  if (value.value_type === "number" && value.unit === "USD") return money.format(Number(value.value));
  return `${String(value.value)}${value.unit && value.unit !== "USD" ? ` ${value.unit}` : ""}`;
}

function pretty(value: string) {
  return value.replaceAll("_", " ");
}

type ReviewItem = (typeof reviewData.items)[number];

function QuestionReview({ item, number }: { item: ReviewItem; number: number }) {
  const question = item.question;
  const keyedOption = question.options.find((option) => option.is_keyed);
  const topic = item.blueprint.labels.topic ?? item.blueprint.labels.group;

  return (
    <section className="queue-item" id={item.identity.version_id} aria-labelledby={`question-heading-${number}`}>
      <div className="item-divider">
        <span>Candidate {String(number).padStart(2, "0")} of {reviewData.queue_summary.item_count}</span>
        <code>{item.identity.version_id}</code>
        <span>{item.blueprint.labels.area}</span>
      </div>

      <div className="workbench">
        <article className="review-column">
          <section className="question-panel panel">
            <div className="panel-kicker">
              <span>{item.identity.question_id}</span>
              <span>{pretty(item.blueprint.skill_level)}</span>
            </div>
            <h2 id={`question-heading-${number}`}>{question.stem}</h2>
            <div className="options" aria-label={`Answer options for ${item.identity.question_id}`}>
              {question.options.map((option) => (
                <div className={`option ${option.is_keyed ? "keyed" : ""}`} key={option.option_id}>
                  <span className="option-letter">{option.option_id}</span>
                  <span className="option-text">{option.text}</span>
                  {option.is_keyed && <span className="key-label">Keyed</span>}
                </div>
              ))}
            </div>
          </section>

          <section className="path-panel panel" aria-labelledby={`blueprint-heading-${number}`}>
            <div className="section-heading">
              <div>
                <p className="eyebrow">BLUEPRINT BINDING</p>
                <h2 id={`blueprint-heading-${number}`}>{topic}</h2>
              </div>
              <code>{item.blueprint.representative_task_id}</code>
            </div>
            <div className="breadcrumb" aria-label="Blueprint hierarchy">
              <span>{item.blueprint.labels.area}</span><b>→</b>
              <span>{item.blueprint.labels.group}</span>
              {item.blueprint.labels.topic && <><b>→</b><span>{item.blueprint.labels.topic}</span></>}
            </div>
            <blockquote>{item.blueprint.labels.task}</blockquote>
            <p className="scope-limit"><strong>MCQ boundary:</strong> {item.blueprint.mcq_scope_limit}</p>
          </section>

          <section className="panel" aria-labelledby={`solution-heading-${number}`}>
            <div className="section-heading">
              <div><p className="eyebrow">WORKED EVIDENCE</p><h2 id={`solution-heading-${number}`}>Solution and end ask</h2></div>
              <span className="answer-chip">Answer {keyedOption?.option_id}: {keyedOption?.text}</span>
            </div>
            <div className="end-ask"><span>What the question asks</span><strong>{question.solution.end_ask}</strong></div>
            <div className="setup-line"><span>{pretty(question.solution.representation.kind)}</span><code>{question.solution.representation.setup}</code></div>
            <ol className="solution-steps">
              {question.solution.steps.map((step) => (
                <li key={step.step_number}><span>{step.step_number}</span><div><strong>{step.instruction}</strong><p>{step.result}</p></div></li>
              ))}
            </ol>
            <div className="two-up callouts">
              <div><span>Why the key works</span><p>{question.solution.keyed_answer_rationale}</p></div>
              <div><span>Faster / safer route</span><p>{question.solution.faster_or_safer_route}</p></div>
            </div>
          </section>

          <section className="panel" aria-labelledby={`facts-heading-${number}`}>
            <div className="section-heading">
              <div><p className="eyebrow">FACT SELECTION</p><h2 id={`facts-heading-${number}`}>Structured fact set</h2></div>
              <span>{question.facts.length} facts · {question.assumptions.length} assumptions</span>
            </div>
            <div className="facts-table" role="table" aria-label="Relevant and irrelevant facts">
              {question.facts.map((fact) => (
                <div className="fact-row" role="row" key={fact.fact_id}>
                  <span className={`relevance ${fact.relevance}`}>{fact.relevance}</span>
                  <strong>{fact.statement}</strong>
                  <code>{displayValue(fact.structured_value)}</code>
                  <p>{"use_in_solution" in fact ? fact.use_in_solution : fact.irrelevance_reason}</p>
                </div>
              ))}
            </div>
            {question.assumptions.length > 0 && (
              <div className="assumption-list">
                <strong>Explicit assumptions</strong>
                {question.assumptions.map((assumption) => <p key={assumption.assumption_id}>{assumption.statement}</p>)}
              </div>
            )}
          </section>

          <section className="panel" aria-labelledby={`distractors-heading-${number}`}>
            <div className="section-heading">
              <div><p className="eyebrow">DISTRACTOR DIAGNOSTICS</p><h2 id={`distractors-heading-${number}`}>Named error models</h2></div>
              <span>3 / 3 reproduced</span>
            </div>
            <div className="distractor-grid">
              {question.options.filter((option) => !option.is_keyed).map((option) => (
                <article key={option.option_id}>
                  <div className="distractor-title"><span>{option.option_id}</span><strong>{option.error_model?.name}</strong><code>{option.text}</code></div>
                  <p>{option.error_model?.misconception}</p><small>{option.error_model?.derivation}</small>
                </article>
              ))}
            </div>
          </section>

          <section className="panel" aria-labelledby={`rule-heading-${number}`}>
            <div className="section-heading">
              <div><p className="eyebrow">RULE + SOURCE TRACE</p><h2 id={`rule-heading-${number}`}>{item.rule.content.title}</h2></div>
              <span className="authority-chip">Admitted authority</span>
            </div>
            <p className="rule-statement">{item.rule.content.rule_statement}</p>
            <div className="trace-grid">
              <div><span>Rule version</span><code>{item.rule.rule_version_id}</code></div>
              <div><span>Reference version</span><code>{item.reference.reference_version_id}</code></div>
              <div><span>Exact locator</span><strong>{item.rule.content.source_citations[0].locator}</strong></div>
              <div><span>Currency</span><strong>{item.rule.content.currency.assessment}</strong></div>
            </div>
            <p className="warning-note">{item.rule.content.currency.basis}</p>
          </section>

          <section className="panel" aria-labelledby={`difficulty-heading-${number}`}>
            <div className="section-heading">
              <div><p className="eyebrow">ITEM PROFILE</p><h2 id={`difficulty-heading-${number}`}>Challenge and provisional difficulty</h2></div>
              <span className="provisional-chip">Proposed for G2</span>
            </div>
            <div className="mechanics">{item.challenge_mechanics.map((mechanic) => <span key={mechanic.tag}>{pretty(mechanic.tag)}</span>)}</div>
            <div className="difficulty-grid">
              {item.difficulty_profile.map((dimension) => (
                <article key={dimension.dimension_id}>
                  <div className="level">{dimension.provisional_level}<small>/5</small></div>
                  <strong>{pretty(dimension.dimension_id)}</strong>
                  <p>{dimension.observable_measurements[0].interpretation}</p>
                  <code>{dimension.observable_measurements[0].measure_id}: {String(dimension.observable_measurements[0].value)}</code>
                </article>
              ))}
            </div>
          </section>

          <section className="panel" aria-labelledby={`checks-heading-${number}`}>
            <div className="section-heading">
              <div><p className="eyebrow">MECHANICAL VERIFICATION</p><h2 id={`checks-heading-${number}`}>Individual check results</h2></div>
              <span>{item.verification.checks.length} / {item.verification.checks.length} checks pass</span>
            </div>
            <div className="check-list">
              {item.verification.checks.map((check) => (
                <details key={check.check_id}>
                  <summary><span className="pass-mark">PASS</span><strong>{check.check_id}</strong><span>{check.category}</span></summary>
                  <p>{check.detail}</p><ul>{check.evidence.map((evidence) => <li key={evidence}>{evidence}</li>)}</ul>
                </details>
              ))}
            </div>
          </section>
        </article>

        <aside className="action-column">
          <section className="binding-card">
            <p className="eyebrow">EXACT VERSION BINDING</p><strong>{item.identity.version_id}</strong>
            <span>{item.identity.question_id} · version {item.identity.version_number}</span><code>{item.identity.content_sha256}</code>
          </section>
          <section className="readiness-card" aria-labelledby={`readiness-heading-${number}`}>
            <div className="readiness-title"><span className="hold-mark">{item.derived_readiness.learner_ready ? "READY" : "HOLD"}</span><h2 id={`readiness-heading-${number}`}>{item.derived_readiness.learner_ready ? "Exact version approved" : "Not learner-ready"}</h2></div>
            <ul>{item.derived_readiness.reasons.map((reason) => <li key={reason}>{pretty(reason)}</li>)}</ul>
          </section>
          <ReviewActions identity={item.identity} reviewer={reviewData.review_actions.reviewer} canonicalNote={reviewData.surface_scope.canonical_event_note} />
        </aside>
      </div>
    </section>
  );
}

export default function Home() {
  const data = reviewData;
  return (
    <main>
      <header className="masthead">
        <div><p className="eyebrow">FAR BANK / GATE G2 REVIEW LAB</p><h1>Exact-version sample queue</h1></div>
        <div className="masthead-status" aria-label="Current readiness status"><span className="status-dot" /><div><strong>{data.queue_summary.item_count} candidates · {data.queue_summary.ready_count} approved</strong><span>0 coverage contribution</span></div></div>
      </header>
      <section className="scope-banner" aria-label="Review scope warning"><strong>G2 candidate sample</strong><span>{data.surface_scope.claim}</span></section>
      <nav className="queue-nav" aria-label="Sample question queue">
        <div><p className="eyebrow">STABLE REVIEW ORDER</p><strong>{data.queue_summary.sample_id}</strong></div>
        {data.items.map((item, index) => <a href={`#${item.identity.version_id}`} key={item.identity.version_id}><span>{index + 1}</span><b>{item.identity.question_id}</b><small>{item.blueprint.labels.area}</small></a>)}
      </nav>
      {data.items.map((item, index) => <QuestionReview item={item} key={item.identity.version_id} number={index + 1} />)}
      <section className="global-audit panel" aria-labelledby="audit-heading">
        <div className="section-heading"><div><p className="eyebrow">QUEUE AUDIT</p><h2 id="audit-heading">Rendered from exact inputs</h2></div><span>{data.source_manifest.length} bound files</span></div>
        <p className="scope-limit"><strong>Review history:</strong> Canonical events are shown only when bound to the exact displayed version. Superseded-version decisions remain append-only history and never carry forward.</p>
        <div className="source-manifest">{data.source_manifest.map((source) => <div key={source.path}><span>{source.path}</span><code>{source.sha256}</code></div>)}</div>
      </section>
    </main>
  );
}
