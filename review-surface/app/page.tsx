"use client";

import { useState } from "react";
import Link from "next/link";
import reviewData from "./review-data-v002.json";
import { ReviewActions } from "./review-actions";

function pretty(value: string) {
  return value.replaceAll("_", " ");
}

const workflowExercises = [
  { action: "Approve", instruction: "Confirm a reviewer can record why an exact version is ready." },
  { action: "Reject", instruction: "Confirm a reviewer can stop an item and explain why it should not proceed." },
  { action: "Request revision", instruction: "Confirm the new-version consequence is clear before requesting a change." },
  { action: "Comment", instruction: "Confirm a reviewer can leave a non-decisive note without changing readiness." },
];

export default function Home() {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const item = reviewData.items[selectedIndex];
  const question = item.question;
  const keyedOption = question.options.find((option) => option.is_keyed);
  const exercise = workflowExercises[selectedIndex];
  const topic = item.blueprint.labels.topic ?? item.blueprint.labels.group;
  const shortHash = `${item.identity.content_sha256.slice(0, 12)}…${item.identity.content_sha256.slice(-8)}`;

  return (
    <>
      <a className="skip-link" href="#review-workspace">Skip to current question</a>
      <header className="app-header">
        <Link className="app-brand" href="/"><span>FAR BANK</span><strong>G3 Review</strong></Link>
        <nav className="mode-nav" aria-label="Review workspace sections">
          <Link aria-current="page" href="/">Review queue</Link>
          <Link href="/evidence">Gate evidence</Link>
        </nav>
        <div className="gate-status"><span aria-hidden="true" /><div><strong>G3 verdict pending</strong><small>Local review only</small></div></div>
      </header>

      <main className="review-page" id="review-workspace">
        <section className="review-intro" aria-labelledby="review-title">
          <div><p className="eyebrow">G3 WORKFLOW EXERCISE</p><h1 id="review-title">Test the review decision flow</h1></div>
          <p>You are testing how a reviewer records an exact-version decision—not re-approving the accounting content.</p>
        </section>

        <nav className="item-switcher workflow-switcher" aria-label="Choose a workflow exercise">
          {workflowExercises.map((queueItem, index) => (
            <button
              aria-current={selectedIndex === index ? "step" : undefined}
              className={selectedIndex === index ? "current" : ""}
              key={queueItem.action}
              onClick={() => setSelectedIndex(index)}
              type="button"
            >
              <span>{index + 1}</span>
              <span><strong>{queueItem.action}</strong><small>Exercise {index + 1}</small></span>
            </button>
          ))}
        </nav>

        <div className="review-layout">
          <article className="item-workspace workflow-sample" aria-labelledby="question-heading">
            <section className="exercise-brief" aria-labelledby="exercise-heading">
              <span>EXERCISE {selectedIndex + 1} OF {workflowExercises.length}</span>
              <div><h2 id="exercise-heading">Test the {exercise.action} path</h2><p>{exercise.instruction}</p></div>
            </section>
            <header className="item-header">
              <div><span>SAMPLE ITEM · {item.identity.version_id}</span><span>{item.derived_readiness.learner_ready ? "APPROVED" : "HOLD"}</span></div>
              <h2 id="question-heading">{question.stem}</h2>
            </header>

            <details className="full-item-evidence">
              <summary><span>View full question evidence</span><small>Answer, solution, source, checks, and history</small></summary>
              <div className="full-item-evidence-body">
            <div className="answer-list" aria-label={`Answer options for ${item.identity.question_id}`}>
              {question.options.map((option) => (
                <div className={`answer-option ${option.is_keyed ? "keyed" : ""}`} key={option.option_id}>
                  <span>{option.option_id}</span><strong>{option.text}</strong>{option.is_keyed && <small>KEYED</small>}
                </div>
              ))}
            </div>

            <section className="core-explanation" aria-labelledby="core-explanation-heading">
              <div><p className="eyebrow">CORE EXPLANATION</p><h3 id="core-explanation-heading">Why {keyedOption?.option_id} is correct</h3></div>
              <p>{question.solution.keyed_answer_rationale}</p>
            </section>

            <div className="evidence-disclosures">
              <details className="evidence-disclosure" open>
                <summary><span>Solution and reasoning</span><small>{question.solution.steps.length} steps</small></summary>
                <div className="disclosure-content">
                  <div className="end-ask"><span>What the question asks</span><strong>{question.solution.end_ask}</strong></div>
                  <div className="setup-line"><span>{pretty(question.solution.representation.kind)}</span><code>{question.solution.representation.setup}</code></div>
                  <ol className="solution-steps">
                    {question.solution.steps.map((step) => (
                      <li key={step.step_number}><span>{step.step_number}</span><div><strong>{step.instruction}</strong><p>{step.result}</p></div></li>
                    ))}
                  </ol>
                  <p className="safer-route"><strong>Faster / safer route:</strong> {question.solution.faster_or_safer_route}</p>
                </div>
              </details>

              <details className="evidence-disclosure">
                <summary><span>Blueprint and source</span><small>{item.blueprint.representative_task_id}</small></summary>
                <div className="disclosure-content evidence-stack">
                  <section>
                    <p className="eyebrow">BLUEPRINT BINDING</p><h3>{topic}</h3><p>{item.blueprint.labels.task}</p>
                    <p className="muted"><strong>MCQ boundary:</strong> {item.blueprint.mcq_scope_limit}</p>
                  </section>
                  <section>
                    <p className="eyebrow">RULE + SOURCE</p><h3>{item.rule.content.title}</h3><p>{item.rule.content.rule_statement}</p>
                    <dl className="compact-facts">
                      <div><dt>Rule version</dt><dd>{item.rule.rule_version_id}</dd></div>
                      <div><dt>Reference</dt><dd>{item.reference.reference_version_id}</dd></div>
                      <div><dt>Locator</dt><dd>{item.rule.content.source_citations[0].locator}</dd></div>
                      <div><dt>Currency</dt><dd>{item.rule.content.currency.assessment}</dd></div>
                    </dl>
                  </section>
                </div>
              </details>

              <details className="evidence-disclosure">
                <summary><span>Facts and distractors</span><small>{question.facts.length} facts · 3 error models</small></summary>
                <div className="disclosure-content evidence-stack">
                  <section>
                    <p className="eyebrow">STRUCTURED FACT SET</p>
                    {question.facts.map((fact) => (
                      <div className="compact-row" key={fact.fact_id}>
                        <span className={fact.relevance}>{fact.relevance}</span><strong>{fact.statement}</strong>
                        <p>{"use_in_solution" in fact ? fact.use_in_solution : fact.irrelevance_reason}</p>
                      </div>
                    ))}
                  </section>
                  <section>
                    <p className="eyebrow">DISTRACTOR DIAGNOSTICS</p>
                    {question.options.filter((option) => !option.is_keyed).map((option) => (
                      <div className="compact-row distractor" key={option.option_id}>
                        <span>{option.option_id}</span><strong>{option.error_model?.name}</strong><code>{option.text}</code>
                        <p>{option.error_model?.misconception}</p>
                      </div>
                    ))}
                  </section>
                </div>
              </details>

              <details className="evidence-disclosure">
                <summary><span>Difficulty and mechanical checks</span><small>{item.verification.checks.length}/{item.verification.checks.length} pass</small></summary>
                <div className="disclosure-content">
                  <div className="mechanics">{item.challenge_mechanics.map((mechanic) => <span key={mechanic.tag}>{pretty(mechanic.tag)}</span>)}</div>
                  <div className="difficulty-summary">
                    {item.difficulty_profile.map((dimension) => (
                      <div key={dimension.dimension_id}><strong>{dimension.provisional_level}/5</strong><span>{pretty(dimension.dimension_id)}</span><small>{dimension.observable_measurements[0].interpretation}</small></div>
                    ))}
                  </div>
                  <div className="check-summary">
                    {item.verification.checks.map((check) => <div key={check.check_id}><span>PASS</span><strong>{check.check_id}</strong><p>{check.detail}</p></div>)}
                  </div>
                </div>
              </details>

              <details className="evidence-disclosure">
                <summary><span>Version details and review history</span><small>{shortHash}</small></summary>
                <div className="disclosure-content">
                  <dl className="compact-facts">
                    <div><dt>Question</dt><dd>{item.identity.question_id}</dd></div>
                    <div><dt>Exact version</dt><dd>{item.identity.version_id}</dd></div>
                    <div><dt>Content SHA-256</dt><dd>{item.identity.content_sha256}</dd></div>
                  </dl>
                  <div className="history-list">
                    {item.review_history.map((event) => <article key={event.event_id}><span>{event.action}</span><div><strong>{event.comment}</strong><small>{event.recorded_at} · {event.event_id}</small></div></article>)}
                  </div>
                </div>
              </details>
            </div>
              </div>
            </details>

            <footer className="item-pagination">
              <button disabled={selectedIndex === 0} onClick={() => setSelectedIndex((index) => index - 1)} type="button">← Previous</button>
              <span>Exercise {selectedIndex + 1} of {workflowExercises.length}</span>
              <button disabled={selectedIndex === workflowExercises.length - 1} onClick={() => setSelectedIndex((index) => index + 1)} type="button">Next exercise →</button>
            </footer>
          </article>

          <aside className="review-rail" aria-label="Current item review controls">
            <details className="review-context">
              <summary>
                <span className={item.derived_readiness.learner_ready ? "ready-dot" : "hold-dot"} />
                <span><small>{item.derived_readiness.learner_ready ? "APPROVED EXACT VERSION" : "NOT LEARNER-READY"}</small><strong>{item.identity.version_id}</strong><code>{shortHash}</code></span>
              </summary>
              <div><code>{item.identity.content_sha256}</code><ul>{item.derived_readiness.reasons.map((reason) => <li key={reason}>{pretty(reason)}</li>)}</ul></div>
            </details>
            <ReviewActions canonicalNote={reviewData.surface_scope.canonical_event_note} identity={item.identity} key={item.identity.version_id} reviewer={reviewData.review_actions.reviewer} />
          </aside>
        </div>
      </main>
    </>
  );
}
