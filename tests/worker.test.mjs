import assert from "node:assert/strict";
import { test } from "node:test";
import { specTarget } from "../worker.js";

const rows = async () => ({ R345: "docs/spec/8.html#R345" });

test("a row id redirects to the page that states it", async () => {
  assert.equal(await specTarget("/docs/spec/R345", rows), "/docs/spec/8.html#R345");
});

test("a dotted section number redirects to its page and anchor", async () => {
  assert.equal(await specTarget("/docs/spec/4.2", rows), "/docs/spec/4.html#4.2");
});

test("other paths and unknown rows are left alone", async () => {
  assert.equal(await specTarget("/docs/spec/4.html", rows), null);
  assert.equal(await specTarget("/docs/spec/R99999", rows), null);
  assert.equal(await specTarget("/tour/", rows), null);
});
