const $ = (s) => document.querySelector(s);
const api = (p, opt) => fetch(p, opt).then(r => r.ok ? r.json() : r.json().then(e => Promise.reject(e)));

document.querySelectorAll('.tab').forEach(t => {
  t.onclick = () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    $('#tab-' + t.dataset.tab).classList.add('active');
    if (t.dataset.tab === 'wrong') loadWrong();
    if (t.dataset.tab === 'progress') loadProgress();
  };
});

function esc(s) { return String(s ?? '').replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

/* ② 错题本 */
$('#w-submit').onclick = async () => {
  const body = {
    stem: $('#w-stem').value.trim(),
    user_answer: $('#w-answer').value.trim() || null,
    error_reason: $('#w-reason').value.trim() || null,
  };
  if (!body.stem) return alert('请输入题目内容');
  try {
    await api('/api/wrong', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) });
    $('#w-stem').value = $('#w-answer').value = $('#w-reason').value = '';
    loadWrong();
  } catch (e) { alert('录入失败：' + (e.detail || JSON.stringify(e))); }
};

async function loadWrong() {
  try {
    const list = await api('/api/wrong');
    $('#w-list').innerHTML = list.length ? list.map(w => `
      <div class="card">
        <span class="kp">${esc(w.kp_name || w.kp_id || '未归类')}</span>
        <span class="kp">${esc(w.qtype || '')}</span>
        <div style="margin-top:6px">${esc(w.stem)}</div>
        ${w.user_answer ? `<div class="meta">作答：${esc(w.user_answer)}</div>` : ''}
        ${w.error_reason ? `<div class="meta">错误原因：${esc(w.error_reason)}</div>` : ''}
        <div class="meta">${esc(w.created_at)}</div>
      </div>`).join('') : '<p style="color:#999">暂无错题</p>';
  } catch (e) { $('#w-list').innerHTML = '<p style="color:#c62828">加载失败</p>'; }
}

/* ③ 练习 */
$('#p-seed').onclick = async () => {
  try {
    const qs = await api('/api/practice/seed?limit=1');
    renderQuestion(qs[0]);
  } catch (e) { alert('取题失败：' + (e.detail || '')); }
};

$('#p-gen').onclick = async () => {
  try {
    const qs = await api('/api/practice/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({top_n:3,count:1}) });
    renderQuestion(qs[0]);
  } catch (e) { alert('生成失败：' + (e.detail || '')); }
};

function renderQuestion(q) {
  if (!q) return $('#p-area').innerHTML = '<p style="color:#999">无题目</p>';
  $('#p-area').innerHTML = `
    <div class="q-card">
      <div class="stem"><b>${esc(q.kp_name || q.kp_id || '')}</b> · ${esc(q.stem)}</div>
      <textarea id="p-code" rows="6" placeholder="在此写 Python 代码..."></textarea>
      <button class="btn" id="p-judge" style="margin-top:10px">提交判题</button>
      <div id="p-result"></div>
    </div>`;
  $('#p-judge').onclick = async () => {
    const code = $('#p-code').value;
    if (!code) return;
    try {
      const r = await api(`/api/practice/submit?qid=${encodeURIComponent(q.qid)}`, {
        method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({user_answer:code})
      });
      const detail = (r.detail||[]).map(d => `<br>　${d.passed?'✅':'❌'} ${esc(d.call)} → ${esc(d.got||d.error)}${d.passed?'':` (期望 ${esc(d.expected)})`}`).join('');
      $('#p-result').innerHTML = `<div class="result ${r.passed?'ok':'fail'}">${r.passed?'全部通过！':'未通过。'}${detail}</div>`;
    } catch (e) { $('#p-result').innerHTML = `<div class="result fail">判题失败：${esc(e.detail||'')}</div>`; }
  };
}

/* ④ 进度 */
async function loadProgress() {
  try {
    const [sum, mas] = await Promise.all([api('/api/progress/summary'), api('/api/progress/mastery')]);
    $('#pg-summary').innerHTML = `
      <div class="card">覆盖知识点：${sum.knowledge_covered}　练习总次数：${sum.total_attempts}
      　正确：${sum.total_correct}　错误：${sum.total_wrong}　正确率：${(sum.accuracy*100).toFixed(1)}%</div>`;
    $('#pg-mastery').innerHTML = mas.length ? mas.map(m => `
      <div class="mastery-row">
        <span class="name">${esc(m.kp_name)}</span>
        <span class="bar"><i style="width:${Math.round(m.mastery_score*100)}%"></i></span>
        <span class="score">掌握度 ${(m.mastery_score*100).toFixed(0)}% · 对${m.correct}/错${m.wrong}</span>
      </div>`).join('') : '<p style="color:#999">暂无练习记录，先去做几道题吧</p>';
  } catch (e) { $('#pg-mastery').innerHTML = '<p style="color:#c62828">加载失败</p>'; }
}

/* ① 问答 */
$('#q-submit').onclick = async () => {
  const q = $('#q-input').value.trim();
  if (!q) return;
  $('#q-answer').innerHTML = '<p style="color:#999">思考中...</p>';
  try {
    const r = await api('/api/qa', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question:q}) });
    $('#q-answer').innerHTML = r.answer;
  } catch (e) { $('#q-answer').innerHTML = `<p style="color:#c62828">失败：${esc(e.detail||'')}</p>`; }
};

loadWrong();