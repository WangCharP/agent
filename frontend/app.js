const express = require('express');
const path = require('path');
const axios = require('axios'); // 引入请求库
const app = express();
const PORT = 3000;

// FastAPI 的地址
const LLM_API_URL = 'http://127.0.0.1:8000/api/chat';

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// 代理接口：前端 -> Node -> FastAPI
app.post('/api/chat', async (req, res) => {
    try {
        // 1. 将前端的数据转发给 Python
        const pyRes = await axios.post(LLM_API_URL, req.body);

        // 2. 将 Python 的返回结果直接回传给前端
        res.json(pyRes.data);

    } catch (error) {
        // 错误处理
        console.error('FastAPI Error:', error.message);
        res.status(500).json({
            flow: '错误: 无法连接到 AI 核心服务 (FastAPI)',
            avatar: { state: 'idle', mood: 'neutral' },
            refs: []
        });
    }
});

app.listen(PORT, () => {
    console.log(`> Node Web Server: http://localhost:${PORT}`);
    console.log(`> Linked to FastAPI: ${LLM_API_URL}`);
});