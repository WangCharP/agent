const express = require('express');
const path = require('path');
const axios = require('axios');
const app = express();
const PORT = 3000;

// 【重要】确保这里是 Python 后端的地址
const BACKEND_URL = 'http://127.0.0.1:8000/api/chat';

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.post('/api/chat', async (req, res) => {
    try {
        console.log(`[Proxy] Request -> ${BACKEND_URL}`);

        const response = await axios({
            method: 'post',
            url: BACKEND_URL,
            data: req.body,
            responseType: 'stream' // 关键
        });

        res.setHeader('Content-Type', 'application/x-ndjson');
        res.setHeader('Connection', 'keep-alive');

        response.data.pipe(res);

    } catch (error) {
        console.error('[Proxy Error]', error.message);
        const errorMsg = error.code === 'ECONNREFUSED'
            ? '后端连接失败 (Connection Refused)'
            : `Error: ${error.message}`;

        res.status(500).send(JSON.stringify({ type: 'error', data: errorMsg }) + "\n");
    }
});

app.listen(PORT, () => {
    console.log(`Frontend running at http://localhost:${PORT}`);
});