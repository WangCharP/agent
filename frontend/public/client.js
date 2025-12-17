// 1. 初始化 Mermaid
mermaid.initialize({
    startOnLoad: false, // 手动控制渲染
    theme: 'default',
    securityLevel: 'loose',
});

// 2. 配置 Marked 自定义渲染器
const renderer = new marked.Renderer();

// 重写 code 解析逻辑：支持 mermaid 和 代码高亮
renderer.code = function (code, language) {
    // 如果是 mermaid 图表
    if (language === 'mermaid') {
        return `<div class="mermaid">${code}</div>`;
    }
    // 其他语言使用 highlight.js
    const validLang = !!(language && hljs.getLanguage(language));
    const highlighted = validLang ? hljs.highlight(code, { language }).value : hljs.highlightAuto(code).value;
    return `<pre><code class="hljs ${language}">${highlighted}</code></pre>`;
};

// 重写 table 解析逻辑：自动包裹 div 以便横向滚动
renderer.table = function (header, body) {
    return `<div class="table-wrapper"><table><thead>${header}</thead><tbody>${body}</tbody></table></div>`;
};

// 应用配置
marked.use({
    renderer: renderer,
    gfm: true, // 开启 GitHub 风格 Markdown
    breaks: true
});

const elInp = document.getElementById('inpMsg');
const elFlow = document.getElementById('uiFlow');
const elRefs = document.getElementById('uiRefs');
const elAvatarStatus = document.querySelector('.avatar-status');
const elAvatarIcon = document.querySelector('.avatar-face i');
const btnSend = document.getElementById('btnSend');

let isProcessing = false;

// 滚动到底部
function scrollToBottom() {
    elFlow.scrollTo({
        top: elFlow.scrollHeight,
        behavior: 'smooth'
    });
}

async function handleSend() {
    const txt = elInp.value.trim();
    if (!txt || isProcessing) return;

    isProcessing = true;
    elInp.value = '';

    const welcome = document.querySelector('.welcome-text');
    if (welcome) welcome.style.display = 'none';

    appendLog('user', txt);
    setAvatarState('thinking');
    elAvatarStatus.innerText = "Connecting...";

    // 创建一个新的 Agent 消息容器
    const agentContentDiv = createAgentLogEntry();
    let fullContent = "";

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ msg: txt })
        });

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // 处理粘包和半包
            const lines = buffer.split('\n');
            buffer = lines.pop(); // 保留最后一个可能不完整的块

            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const json = JSON.parse(line);

                    switch (json.type) {
                        case 'status':
                            // 显示后端的多 Agent 调度状态
                            elAvatarStatus.innerText = json.data;
                            setAvatarState('thinking');
                            appendSystemLog(json.data);
                            break;

                        case 'sources':
                            updateRefs(json.data);
                            break;

                        case 'content':
                            setAvatarState('speaking');
                            fullContent += json.data;

                            // 实时渲染 Markdown
                            agentContentDiv.innerHTML = marked.parse(fullContent);
                            scrollToBottom();
                            break;

                        case 'error':
                            showToast(`❌ ${json.data}`, 'error');
                            fullContent += `\n\n> **System Error:** ${json.data}`;
                            agentContentDiv.innerHTML = marked.parse(fullContent);
                            break;
                    }
                } catch (e) {
                    console.warn("JSON Parse Error (Chunk skipped):", e);
                }
            }
        }

        // 🔥 流结束后，触发 Mermaid 渲染 🔥
        try {
            await mermaid.run({
                nodes: agentContentDiv.querySelectorAll('.mermaid')
            });
        } catch (err) {
            console.warn('Mermaid rendering incomplete:', err);
        }

        showToast('✅ 回答完毕', 'success');
        setAvatarState('idle');

    } catch (err) {
        showToast('❌ 请求失败', 'error');
        setAvatarState('idle');
        agentContentDiv.innerHTML += `<p style="color:red; font-weight:bold;">Network Error: ${err.message}</p>`;
    } finally {
        isProcessing = false;
        scrollToBottom();
    }
}

function createAgentLogEntry() {
    const entry = document.createElement('div');
    entry.className = `log-entry agent`;
    // 初始光标
    entry.innerHTML = `
        <div class="log-meta"><i class="fa-solid fa-robot"></i> <span class="role-badge role-agent">Agent</span></div>
        <div class="log-content markdown-body"><span class="cursor-blink">|</span></div>
    `;
    elFlow.appendChild(entry);
    scrollToBottom();
    return entry.querySelector('.log-content');
}

function appendLog(type, text) {
    const entry = document.createElement('div');
    entry.className = `log-entry user`;
    entry.innerHTML = `
        <div class="log-meta"><i class="fa-regular fa-user"></i> <span class="role-badge role-user">User</span></div>
        <div class="log-content markdown-body">${text}</div>
    `;
    elFlow.appendChild(entry);
    scrollToBottom();
}

function updateRefs(refs) {
    if (!refs || !refs.length) {
        // 不要清空，可能是追加的引用
        if (elRefs.innerHTML.includes('暂无引用')) {
            elRefs.innerHTML = '';
        }
    }

    // 生成新的引用列表项
    const html = refs.map(r => `
        <li>
            <a href="${r.url}" target="_blank" title="${r.title}">
                <div class="ref-title">${r.title || 'Untitled'}</div>
                <div class="ref-link"><i class="fa-solid fa-link"></i> 点击跳转</div>
            </a>
        </li>
    `).join('');

    // 追加模式，防止并行搜索覆盖
    if (elRefs.innerHTML.includes('暂无引用')) {
        elRefs.innerHTML = html;
    } else {
        elRefs.innerHTML += html;
    }
}

function setAvatarState(state) {
    elAvatarIcon.className = '';
    if (state === 'thinking') {
        elAvatarIcon.className = 'fa-solid fa-brain fa-shake';
        elAvatarIcon.style.color = '#fbbf24'; // 黄色
    } else if (state === 'speaking') {
        elAvatarIcon.className = 'fa-solid fa-microphone-lines fa-beat-fade';
        elAvatarIcon.style.color = '#34d399'; // 绿色
    } else {
        // Idle
        elAvatarStatus.innerText = 'Standby';
        elAvatarIcon.className = 'fa-solid fa-face-smile';
        elAvatarIcon.style.color = '#a0aec0'; // 灰色
    }
}

function showToast(msg, type) {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerText = msg;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    });

    setTimeout(() => {
        toast.style.transform = 'translateX(120%)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 绑定事件
btnSend.addEventListener('click', handleSend);
elInp.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
});

function appendSystemLog(text) {
    // 过滤掉无意义的状态
    if (!text || text === 'Standby') return;

    const entry = document.createElement('div');
    //以此保持和你原有的 log-entry 结构一致，但内容自定义
    entry.className = 'log-entry system';

    // 这里直接写死样式，显示为灰色小字，带有终端图标
    entry.innerHTML = `
        <div style="
            padding: 8px 12px; 
            margin: 5px 0; 
            color: #94a3b8; 
            font-size: 0.85em; 
            font-family: monospace; 
            background: rgba(0,0,0,0.05); 
            border-radius: 6px; 
            border-left: 3px solid #3b82f6;">
            <i class="fa-solid fa-terminal"></i> ${text}
        </div>
    `;

    elFlow.appendChild(entry);
    scrollToBottom();
}