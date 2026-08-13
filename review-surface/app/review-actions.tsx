"use client";

import { useMemo, useState } from "react";

type ReviewAction = "approve" | "reject" | "revise" | "comment";

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
  const [action, setAction] = useState<ReviewAction>("comment");
  const [comment, setComment] = useState("");
  const [recordedAt, setRecordedAt] = useState<string | null>(null);
  const subject = useMemo(() => ({
    question_id: identity.question_id,
    version_id: identity.version_id,
    content_sha256: identity.content_sha256,
  }), [identity.content_sha256, identity.question_id, identity.version_id]);

  const event = useMemo(() => {
    if (!recordedAt) return null;
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
    <section className="actions-card" aria-labelledby="actions-heading">
      <p className="eyebrow">REVIEW EVENT COMPOSER</p>
      <h2 id="actions-heading">Record a verdict shape</h2>
      <div className="action-buttons" role="group" aria-label="Review action">
        {(["approve", "reject", "revise", "comment"] as ReviewAction[]).map((item) => (
          <button
            className={action === item ? "active" : ""}
            key={item}
            onClick={() => selectAction(item)}
            type="button"
          >
            {item}
          </button>
        ))}
      </div>
      <label htmlFor="review-comment">Comment</label>
      <textarea
        id="review-comment"
        onChange={(event) => setComment(event.target.value)}
        onFocus={() => recordedAt ?? setRecordedAt(new Date().toISOString())}
        placeholder="State the evidence or requested revision…"
        rows={4}
        value={comment}
      />
      <div className="event-preview">
        <span>Append-only event preview</span>
        <pre>{event ? JSON.stringify(event, null, 2) : "Choose an action or enter a comment to bind a timestamp."}</pre>
      </div>
      <button className="download-button" disabled={!comment.trim()} onClick={downloadEvent} type="button">
        Download event for validation
      </button>
      <p className="event-note">{canonicalNote}</p>
      <p className="invalidation-note">
        Content is immutable. Any substantive edit creates a new version and the prior version’s approval cannot carry forward.
      </p>
    </section>
  );
}
