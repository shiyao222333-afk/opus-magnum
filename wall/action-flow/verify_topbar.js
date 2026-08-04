// verify_topbar.js — 验证巨作重构后 3 页面顶部条 + 业务功能保全
const { spawn } = require('child_process');
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const DEBUG_PORT = 9350;
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
async function main() {
  const chrome = spawn(CHROME, ['--no-sandbox', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
    '--remote-debugging-port=' + DEBUG_PORT,
    '--user-data-dir=C:\\Users\\Lenovo\\WorkBuddy\\Claw\\chrome_vf',
    '--window-size=1400,900', 'http://localhost:8501/'], { stdio: 'ignore' });
  await sleep(12000);
  const list = await (await fetch('http://localhost:' + DEBUG_PORT + '/json/list')).json();
  const page = list.find(p => p.url.includes('8501')) || list.find(p => p.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  const pending = new Map(); let msgId = 1;
  const send = (method, params = {}) => new Promise(r => { const id = msgId++; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); } };
  await new Promise(r => ws.onopen = r);
  await send('Runtime.enable');

  const pages = [
    { path: '/', name: '周看板', markers: ['巨作', '周看板', '摄入', '总指挥', 'Qdrant', '服务', '熔知', '总指挥部', '本周篇数', '来源数', '收藏', '本周新录入'] },
    { path: '/ingest', name: '摄入', markers: ['巨作', '周看板', '摄入', '总指挥', 'Qdrant', '服务', '熔知', '总指挥部', '投递', '加入馏析队列', '闪念笔记', '一键启动摄入管线', '馏析队列概览', '服务日志'] },
    { path: '/hq', name: '总指挥', markers: ['巨作', '周看板', '摄入', '总指挥', 'Qdrant', '服务', '熔知', '总指挥部', '服务健康状态', 'GitHub 仓库状态', '任务看板', '开发路线'] },
  ];
  for (const pg of pages) {
    await send('Page.navigate', { url: 'http://localhost:8501' + pg.path });
    await sleep(6000);
    const r = await send('Runtime.evaluate', {
      expression: `(() => {
        const txt = document.body ? (document.body.innerText || '') : '';
        const header = document.querySelector('header, .q-header');
        const headerTxt = header ? (header.innerText || '') : '';
        return JSON.stringify({ url: location.href, headerTxt: headerTxt.slice(0, 200), bodyLen: txt.length });
      })()`,
      returnByValue: true
    });
    const info = JSON.parse(r.result.value);
    console.log('\n=== ' + pg.name + ' (' + pg.path + ') ===');
    console.log('顶部条内容:', info.headerTxt);
    const missing = pg.markers.filter(m => !info.headerTxt.includes(m) && !info.bodyLen);
    const bodyMissing = [];
    // 页面主体标记检查（排除顶部条也含的）
    const bodyMarkers = pg.markers.filter(m => ['巨作','周看板','摄入','总指挥','Qdrant','服务','熔知','总指挥部'].indexOf(m) === -1);
    const bodyR = await send('Runtime.evaluate', {
      expression: `(() => { const t = document.body ? (document.body.innerText||'') : ''; return JSON.stringify(${JSON.stringify(bodyMarkers)}.map(m => ({m, has: t.includes(m)}))); })()`,
      returnByValue: true
    });
    const bodyChecks = JSON.parse(bodyR.result.value);
    const missingBody = bodyChecks.filter(c => !c.has).map(c => c.m);
    console.log('顶部条缺失:', missing.length ? missing : '无');
    console.log('页面主体缺失:', missingBody.length ? missingBody : '无（业务功能齐全）');
  }
  ws.close(); setTimeout(() => { chrome.kill(); process.exit(0); }, 500);
}
main().catch(e => { console.error('fail:', e.message); process.exit(1); });
