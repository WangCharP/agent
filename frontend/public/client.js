// 配置 Markdown 解析器
marked.setOptions({
    highlight: function (code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
    },
    breaks: true
});

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

        // 4. 显示完成提示
        showToast('✅ 回答完毕', 'success');

    } catch (err) {
        appendLog('agent', `System Error: ${err.message}`);
        showToast('❌ 请求失败', 'error');
        setAvatarState('idle');
    } finally {
        isProcessing = false;
    }
}

// 日志追加函数（带打字机效果的容器）
function appendLog(type, text) {
    const entryDiv = document.createElement('div');
    entryDiv.className = `log-entry ${type}`;

    const timeStr = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });

    // 1. 头部元数据
    const metaDiv = document.createElement('div');
    metaDiv.className = 'log-meta';

    const roleBadge = type === 'user'
        ? `<span class="role-badge role-user">User</span>`
        : `<span class="role-badge role-agent">Agent</span>`;

    const icon = type === 'user'
        ? '<i class="fa-regular fa-user"></i>'
        : '<i class="fa-solid fa-robot"></i>';

    metaDiv.innerHTML = `${icon} ${roleBadge} <span style="opacity:0.6">${timeStr}</span>`;

    // 2. 内容区域
    const contentDiv = document.createElement('div');
    contentDiv.className = 'log-content markdown-body';

    if (type === 'agent') {
        // 简单优化：给思考过程加粗，使其更像标题
        let processedText = text.replace(/(LangChain\s*思考过程[:：])/g, '\n### 🧠 $1\n');
        // 解析 Markdown
        contentDiv.innerHTML = marked.parse(processedText);
    } else {
        contentDiv.innerText = text;
    }

    // 3. 插入页面
    entryDiv.appendChild(metaDiv);
    entryDiv.appendChild(contentDiv);
    elFlow.appendChild(entryDiv);

    elFlow.scrollTop = elFlow.scrollHeight;

    // 代码高亮
    entryDiv.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
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

// 提示框函数
function showToast(message, type = 'info') {
    // 移除已有的 toast
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${type === 'success' ? '🎉' : type === 'error' ? '⚠️' : 'ℹ️'}</span>
        <span class="toast-message">${message}</span>
    `;
    document.body.appendChild(toast);

    // 触发动画
    requestAnimationFrame(() => {
        toast.classList.add('toast-show');
    });

    // 3秒后自动消失
    setTimeout(() => {
        toast.classList.remove('toast-show');
        toast.classList.add('toast-hide');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}