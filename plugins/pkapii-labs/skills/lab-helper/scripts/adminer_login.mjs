// node adminer_login.mjs OUT.png SERVER [path] [driver] [user] [pass] -- logs in to Adminer (default http://127.0.0.1:8080/, override with BASE=...) through Chrome DevTools and saves a PNG.
// The login is a real form submit in headless Chrome. If `path` is given, it is opened after the login (for example '?pgsql=SERVER&username=U&db=DB').
import { spawn } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [out, server, path = "", driver = "pgsql", user = "postgres", pass = "postgres"] = process.argv.slice(2);
const BASE = process.env.BASE || "http://127.0.0.1:8080/";
const dir = mkdtempSync(join(tmpdir(), "chr-")), port = 9300 + Math.floor(Math.random() * 500);
const chrome = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  ["--headless=new", "--disable-gpu", "--hide-scrollbars", `--user-data-dir=${dir}`, `--remote-debugging-port=${port}`,
   "--window-size=1100,560", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let target;
for (let i = 0; i < 50 && !target; i++) {
  try { target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === "page"); } catch {}
  if (!target) await sleep(200);
}
const ws = new WebSocket(target.webSocketDebuggerUrl); await new Promise((r) => (ws.onopen = r));
let id = 0; const pending = new Map();
ws.onmessage = (m) => { const d = JSON.parse(m.data); pending.get(d.id)?.(d); };
const send = (method, params = {}) => new Promise((r) => { pending.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
const ev = (expr) => send("Runtime.evaluate", { expression: expr, returnByValue: true });
const waitLoad = async () => { for (let i = 0; i < 50; i++) { await sleep(200); if ((await ev("document.readyState")).result.result.value === "complete") return; } };
await send("Page.navigate", { url: BASE }); await sleep(800); await waitLoad();
await ev(`(()=>{const f=document.querySelector('form');
 const set=(n,v)=>{const e=f.querySelector('[name="'+n+'"]'); if(e) e.value=v;};
 set('auth[driver]','${driver}'); set('auth[server]','${server}'); set('auth[username]','${user}'); set('auth[password]','${pass}');
 f.querySelector('[type=submit]').click();})()`);
await sleep(2500); await waitLoad();
if (path) { await send("Page.navigate", { url: BASE + path }); await sleep(800); await waitLoad(); }
const shot = await send("Page.captureScreenshot", { format: "png" });
writeFileSync(out, Buffer.from(shot.result.data, "base64"));
ws.close(); chrome.kill(); console.log("saved", out);
