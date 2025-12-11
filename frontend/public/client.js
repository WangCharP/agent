const elInp = document.getElementById('inpMsg');
const elFlow = document.getElementById('uiFlow');
const elRefs = document.getElementById('uiRefs');
const elAvatarStatus = document.querySelector('.avatar-status');
const elAvatarIcon = document.querySelector('.avatar-face i');
const btnSend = document.getElementById('btnSend');

// 简单的状态管理
let isProcessing = false;

// 格式化当前时间
const getTime = () => new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });

async function handleSend() {
    const txt = elInp.value.trim();
    if (!txt || isProcessing) return;

    // 1. UI 准备
    isProcessing = true;
    elInp.value = '';

    // 清除欢迎语（如果是第一次）
    const welcome = document.querySelector('.welcome-text');
    if (welcome) welcome.style.display = 'none';

    // 添加用户指令日志
    appendLog('user', txt);

    // 改变数字人状态
    setAvatarState('thinking');

    try {
        // 2. 请求后端
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ msg: txt, type: 'text' })
        });
        const data = await res.json();

        // 3. 处理响应
        if (data.flow) appendLog('agent', data.flow);
        if (data.refs) updateRefs(data.refs);

        setAvatarState('speaking');
        setTimeout(() => setAvatarState('idle'), 3000); // 3秒后恢复待机

    } catch (err) {
        appendLog('agent', `System Error: ${err.message}`);
        setAvatarState('idle');
    } finally {
        isProcessing = false;
    }
}

// 日志追加函数（带打字机效果的容器）
function appendLog(type, text) {
    const div = document.createElement('div');
    div.className = 'log-entry';

    const meta = document.createElement('div');
    meta.className = type === 'user' ? 'log-user' : 'log-agent';
    meta.innerHTML = type === 'user'
        ? `<i class="fa-regular fa-user"></i> You <span style="font-size:12px;opacity:0.5">${getTime()}</span>`
        : `<i class="fa-solid fa-cube"></i> Agent <span style="font-size:12px;opacity:0.5">${getTime()}</span>`;

    const content = document.createElement('div');
    content.style.whiteSpace = 'pre-wrap';

    div.appendChild(meta);
    div.appendChild(content);
    elFlow.appendChild(div);

    // 简单的打字机效果
    if (type === 'agent') {
        let i = 0;
        function type() {
            if (i < text.length) {
                content.textContent += text.charAt(i);
                elFlow.scrollTop = elFlow.scrollHeight;
                i++;
                requestAnimationFrame(type); // 极速打字
            }
        }
        type();
    } else {
        content.textContent = text;
        elFlow.scrollTop = elFlow.scrollHeight;
    }
}

// 更新引用列表
function updateRefs(refs) {
    elRefs.innerHTML = refs.map(r => `
        <li>
            <a href="${r.link}" target="_blank">
                <div style="display:flex;justify-content:space-between">
                    <span>${r.txt}</span>
                    <i class="fa-solid fa-external-link-alt" style="font-size:12px;opacity:0.5"></i>
                </div>
            </a>
        </li>
    `).join('');
}

// 数字人状态切换视觉
function setAvatarState(state) {
    const icon = elAvatarIcon;
    const label = elAvatarStatus;

    if (state === 'thinking') {
        label.innerText = 'Analyzing...';
        label.style.color = '#fbbf24';
        icon.className = 'fa-solid fa-brain fa-shake'; // 思考时抖动
        icon.style.color = '#fbbf24';
    } else if (state === 'speaking') {
        label.innerText = 'Speaking';
        label.style.color = '#34d399';
        icon.className = 'fa-solid fa-microphone-lines';
        icon.style.color = '#34d399';
    } else {
        label.innerText = 'Standby';
        label.style.color = '#fff';
        icon.className = 'fa-solid fa-face-smile';
        icon.style.color = '#a0aec0';
    }
}

// 事件绑定
btnSend.addEventListener('click', handleSend);
elInp.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
});