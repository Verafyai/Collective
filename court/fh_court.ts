// fh_court.ts: the Court's bridge to fusion-harness (P-006). Runs a batch of court turns in parallel, one clean-room pi
// child per turn, through fusion-harness's own child runner (runChild), exactly as /fh-opinion and /fh-debate fan out
// their slots. The court procedure (who speaks when, objections, ballots) lives in court/court.py; this file only
// executes turns and reports each one's text, model, tokens, and timing as JSON.
//
//   node court/fh_court.ts < jobs.json     jobs: [{"id", "model", "system", "prompt", "thinking"?, "timeoutMs"?}]
//
// Extension to fusion-harness (documented in docs/plugin-notes.md): runChild finds pi by re-running the entry script
// of the current process (process.argv[1]); a headless driver isn't pi, so this driver points argv[1] at pi's own
// entry script first. Nothing in the fusion-harness checkout is modified.
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { execFileSync } from "node:child_process";

const FH = process.env.FUSION_HARNESS_DIR ?? path.join(os.homedir(), ".local/share/collective/fusion-harness");
const { runChild } = await import(path.join(FH, "extensions/fusion-harness/modules/child-runner.ts"));

// point runChild's pi lookup at the real pi entry script
const piBin = execFileSync("sh", ["-c", "command -v pi"]).toString().trim();
process.argv[1] = fs.realpathSync(piBin);

type Job = { id: string; model: string; system: string; prompt: string; thinking?: string; timeoutMs?: number };
const jobs: Job[] = JSON.parse(fs.readFileSync(0, "utf8"));
const base = fs.mkdtempSync(path.join(os.tmpdir(), "court-"));

function newRun(model: string): any {
	return { role: "builder", model, status: "pending", ms: 0, tokensIn: 0, tokensOut: 0, costUsd: 0, toolCalls: 0, toolNames: [],
		toolEvents: [], ctxTokens: 0, tpsSeconds: 0, flow: [], flowMark: 0, streamText: "", streamThinking: "", text: "", exitCode: 0 };
}

const results = await Promise.all(jobs.map(async (job) => {
	const run = newRun(job.model);
	await runChild({ run, prompt: job.prompt, systemPrompt: job.system, tools: "none", thinking: (job.thinking ?? "low") as any,
		sessionDir: path.join(base, job.id), cwd: base, timeoutMs: job.timeoutMs ?? 240_000 });
	return { id: job.id, model: run.model, text: run.text, status: run.status, exitCode: run.exitCode, error: run.errorMessage ?? null,
		tokensIn: run.tokensIn, tokensOut: run.tokensOut, costUsd: run.costUsd, ms: run.ms, startedAt: run.startedAt, endedAt: run.endedAt };
}));
fs.rmSync(base, { recursive: true, force: true });
process.stdout.write(JSON.stringify(results));
