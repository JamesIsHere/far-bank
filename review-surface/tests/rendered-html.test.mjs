import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render(path = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request(`http://localhost${path}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders a focused one-question review workspace", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();

  assert.match(html, /<title>FAR Bank · G3 review workspace<\/title>/i);
  assert.match(html, /Test the review decision flow/);
  assert.match(html, /not re-approving the accounting content/i);
  assert.match(html, /Review queue/);
  assert.match(html, /Gate evidence/);
  assert.match(html, /far-q-000101\.v001/);
  assert.match(html, /Test the <!-- -->Approve<!-- --> path/);
  assert.match(html, /1<!-- --> OF <!-- -->4/);
  assert.match(html, /View full question evidence/);
  assert.match(html, /<details class="full-item-evidence">/);
  assert.match(html, /APPROVED EXACT VERSION/);
  assert.match(html, /RECOMPUTE_INDEPENDENT/);
  assert.match(html, /Choose a review decision/);
  assert.doesNotMatch(html, /Download decision file/);
  assert.doesNotMatch(html, /Inspect decision file/);
  assert.doesNotMatch(html, /A revision creates a new exact version/);
  assert.match(html, /Approve/i);
  assert.match(html, /Reject/i);
  assert.match(html, /Request revision/i);
  assert.match(html, /Comment/i);
  assert.doesNotMatch(html, /Why this workflow is ready to inspect|NOT ISSUED/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);
});

test("keeps gate-level audit evidence on its own route", async () => {
  const response = await render("/evidence");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Why this workflow is ready to inspect/);
  assert.match(html, /NOT ISSUED/);
  assert.match(html, /Approval does not cross versions/);
  assert.match(html, /AUTO-INVALIDATED · NOT READY/);
  assert.match(html, /EXACT APPROVAL · READY/);
  assert.match(html, /Coverage effect/);
  assert.match(html, /Hands-on Gate G3 checklist/);
  assert.match(html, /Exact evidence artifact hashes/);
});

test("renders keyboard and assistive-technology structure without duplicate composer ids", async () => {
  const response = await render();
  const html = await response.text();
  assert.match(html, /href="#review-workspace"[^>]*>Skip to current question</i);
  assert.match(html, /<main[^>]*id="review-workspace"/i);
  assert.doesNotMatch(html, /aria-live="polite"/i);
  assert.doesNotMatch(html, /aria-pressed="true"/i);
  assert.equal((html.match(/aria-pressed="false"/gi) ?? []).length, 4);
  assert.doesNotMatch(html, /<textarea/i);

  const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
  assert.equal(ids.length, new Set(ids).size, "rendered IDs must be unique");
  const commentIds = ids.filter((id) => id.startsWith("review-comment-"));
  assert.equal(commentIds.length, 0);
});

test("keeps the review surface local, candidate-bound, and free of account scope", async () => {
  const [page, layout, packageJson, hosting, data, g3Package] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
    readFile(new URL("../.openai/hosting.json", import.meta.url), "utf8"),
    readFile(new URL("../app/review-data-v002.json", import.meta.url), "utf8"),
    readFile(new URL("../app/g3-workflow-package.json", import.meta.url), "utf8"),
  ]);
  assert.match(page, /derived_readiness/);
  assert.match(page, /workflowExercises\.map/);
  assert.doesNotMatch(page + layout, /signin|\baccount\b|learner dashboard|analytics/i);
  assert.doesNotMatch(packageJson, /react-loading-skeleton|drizzle/);
  assert.match(page, /identity=\{item.identity\}/);
  const actions = await readFile(new URL("../app/review-actions.tsx", import.meta.url), "utf8");
  assert.match(actions, /subject,/);
  assert.doesNotMatch(actions, /subject:\s*identity/);
  assert.match(actions, /useState<ReviewAction \| null>\(null\)/);
  assert.match(actions, /aria-live="polite"/);
  assert.match(actions, /Download decision file/);
  assert.deepEqual(JSON.parse(hosting), { d1: null, r2: null });
  const parsed = JSON.parse(data);
  const parsedG3 = JSON.parse(g3Package);
  assert.equal(parsedG3.package_status, "ready_for_human_gate_not_approved");
  assert.equal(parsedG3.verdict.decision_state, "not_issued");
  assert.equal(parsedG3.verdict.automation_authority, false);
  assert.equal(parsed.items.length, 6);
  assert.equal(
    parsed.queue_summary.ready_count,
    parsed.items.filter((item) => item.derived_readiness.learner_ready).length,
  );
  assert.deepEqual(
    parsed.items.map((item) => item.question.solution.keyed_answer_option_id),
    ["A", "B", "C", "D", "B", "C"],
  );
});
