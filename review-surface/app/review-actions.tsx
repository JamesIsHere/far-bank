"use client";

import { useMemo, useState } from "react";

type ReviewAction = "approve" | "reject" | "revise" | "comment";

const actionLabels: Record<ReviewAction, string> = {
  approve: "Approve",
  reject: "Reject",
  revise: "Request revision",
  comment: "Comment",
};

const actionPrompts: Record<ReviewAction, string> = {
  approve: "Why is this ready?",
  reject: "Why should this not proceed?",
  revise: "What must change?",
  comment: "Add a non-decisive note",
};

type Props = {
  identity: {
    question_id: string;
    version_id: string;
    content_sha256: string;
  };
  reviewer: {
    actor_type: string;
    actor_id: string;
    display_name: string;
  };
  canonicalNote: string;
};

export function ReviewActions({ identity, reviewer, canonicalNote }: Props) {
  const [action, setAction] = useState<ReviewAction | null>(null);
  const [comment, setComment] = useState("");
  const [recordedAt, setRecordedAt] = useState<string | null>(null);
  const subject = useMemo(() => ({
    question_id: identity.question_id,
    version_id: identity.version_id,
    content_sha256: identity.content_sha256,
  }), [identity.content_sha256, identity.question_id, identity.version_id]);
  const idSuffix = identity.version_id.replace(/[^a-zA-Z0-9_-]/g, "-");
  const headingId = `actions-heading-${idSuffix}`;
  const commentId = `review-comment-${idSuffix}`;
  const noteId = `event-note-${idSuffix}`;

  const event = useMemo(() => {
    if (!recordedAt || !action) return null;
    const timestamp = recordedAt.replace(/[^0-9]/g, "");
    return {
      schema_version: "1.0.0",
      event_id: `far-review-${identity.question_id}-${action}-${timestamp}`,
      recorded_at: recordedAt,
      action,
      actor: reviewer,
      subject,
      comment: comment.trim(),
      ...(action === "revise" ? { reason_code: "revision_requested" } : {}),
    };
  }, [action, comment, identity.question_id, recordedAt, reviewer, subject]);

  function selectAction(next: ReviewAction) {
    setAction(next);
    setRecordedAt(new Date().toISOString());
  }

  function downloadEvent() {
    if (!action) return;
    const now = new Date().toISOString();
    setRecordedAt(now);
    const timestamp = now.replace(/[^0-9]/g, "");
    const payload = {
      schema_version: "1.0.0",
      event_id: `far-review-${identity.question_id}-${action}-${timestamp}`,
      recorded_at: now,
      action,
      actor: reviewer,
      subject,
      comment: comment.trim(),
      ...(action === "revise" ? { reason_code: "revision_requested" } : {}),
    };
    const blob = new Blob([`${JSON.stringify(payload, null, 2)}\n`], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${payload.event_id}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="actions-card" aria-labelledby={headingId}>
      <p className="eyebrow">REVIEW DECISION</p>
      <h2 id={headingId}>Choose a review decision</h2>
      <div className="action-buttons" role="group" aria-label="Review action">
        {(["approve", "reject", "revise", "comment"] as ReviewAction[]).map((item) => (
          <button
            className={action === item ? "active" : ""}
            aria-pressed={action === item}
            key={item}
            onClick={() => selectAction(item)}
            type="button"
          >
            {actionLabels[item]}
          </button>
        ))}
      </div>
      {!action && <p className="decision-empty">Choose one decision to continue.</p>}
      {action && (
        <div className="decision-form">
          <label htmlFor={commentId}>{actionPrompts[action]}</label>
          <textarea
            aria-describedby={noteId}
            id={commentId}
            onChange={(event) => setComment(event.target.value)}
            placeholder="State the evidence for this decision…"
            rows={4}
            value={comment}
          />
          {action === "revise" && <p className="invalidation-note">A revision creates a new exact version. Approval never carries forward.</p>}
          <button className="download-button" disabled={!comment.trim()} onClick={downloadEvent} type="button">
            Download decision file
          </button>
          <p className="proposal-note" id={noteId}>Creates a local proposal only. Approval and canonical history do not change.</p>
          <details className="rail-disclosure">
            <summary>Inspect decision file</summary>
            <div className="event-preview" aria-live="polite" aria-atomic="false">
              <span>Exact-version event preview</span>
              <pre>{event ? JSON.stringify(event, null, 2) : "Decision preview unavailable."}</pre>
            </div>
            <p className="event-note">{canonicalNote}</p>
          </details>
        </div>
      )}
    </section>
  );
}
