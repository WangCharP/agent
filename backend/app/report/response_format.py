import json

def _format_response(self, type_: str, data: any) -> str:
        """
        辅助方法：将数据格式化为 JSON 字符串，并添加换行符
        """
        # 1. 构造标准的数据包
        packet = {
            "type": type_,  # 消息类型: 'status' | 'sources' | 'content' | 'error'
            "data": data    # 消息内容: 字符串、列表或字典
        }
        
        # 2. 转为 JSON 字符串
        # ensure_ascii=False 让中文能正常显示，而不是显示成 \uXXXX
        json_str = json.dumps(packet, ensure_ascii=False)
        
        # 3. 添加换行符 (流式传输的关键)
        return json_str + "\n"