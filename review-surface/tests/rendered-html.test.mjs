import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the exact-version review evidence", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();

  assert.match(html, /<title>FAR Bank · Exact-version review<\/title>/i);
  assert.match(html, /Exact-version sample queue/);
  assert.match(html, /far-p1-g2-sample\.v002/);
  assert.match(html, /far-q-000101\.v001/);
  for (let number = 2; number <= 6; number += 1) {
    assert.match(html, new RegExp(`far-q-00010${number}\\.v002`));
  }
  assert.match(html, /Exact version approved|Not learner-ready/);
  assert.match(html, /0 coverage contribution/);
  assert.match(html, /RECOMPUTE_INDEPENDENT/);
  assert.match(html, /Named error models/);
  assert.match(html, /RULE \+ SOURCE TRACE/);
  assert.match(html, /Record a verdict shape/);
  assert.match(html, /Admitted authority/);
  assert.match(html, /Superseded-version decisions remain append-only history/);
  assert.match(html, /Any substantive edit creates a new version/);
  assert.match(html, /Approve/i);
  assert.match(html, /Reject/i);
  assert.match(html, /Revise/i);
  assert.match(html, /Comment/i);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);
});

test("keeps the review surface local, candidate-bound, and free of account scope", async () => {
  const [page, layout, packageJson, hosting, data] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
    readFile(new URL("../.openai/hosting.json", import.meta.url), "utf8"),
    readFile(new URL("../app/review-data-v002.json", import.meta.url), "utf8"),
  ]);
  assert.match(page, /derived_readiness/);
  assert.match(page, /data\.items\.map/);
  assert.doesNotMatch(page + layout, /signin|account|learner dashboard|analytics/i);
  assert.doesNotMatch(packageJson, /react-loading-skeleton|drizzle/);
  assert.match(page, /identity=\{item.identity\}/);
  const actions = await readFile(new URL("../app/review-actions.tsx", import.meta.url), "utf8");
  assert.match(actions, /subject,/);
  assert.doesNotMatch(actions, /subject:\s*identity/);
  assert.deepEqual(JSON.parse(hosting), { d1: null, r2: null });
  const parsed = JSON.parse(data);
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
