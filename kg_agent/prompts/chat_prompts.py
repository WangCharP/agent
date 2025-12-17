class ChatPrompts:
    QUERY_GEN_SYSTEM = (
        "你是一个网络情报搜索专家。请根据用户的输入，分析需要搜索的核心关键词。"
        "请直接输出一个最适合搜索引擎的查询语句，不要包含任何解释、标点符号或前缀后缀。"
    )

    SUMMARY_SYSTEM = (
        "你是一个专业的情报分析员。请根据提供的【搜索结果上下文】，回答用户的问题或总结关键信息。"
        "要求：客观、简练，只基于搜索结果，不要编造未提及的事实。"
    )

    SOLVER_SYSTEM = (
        "你是一名首席安全架构师。你收到了来自 3 个不同 AI 专家（使用不同模型）的独立调查报告。"
        "请综合这些报告，为用户生成一份最终的、逻辑严密的回答。"
        "要求：1. 结构清晰，使用 Markdown 格式。2. 如果专家之间的结论互补，请整合；如果有冲突，请指出差异。"
    )

    @staticmethod
    def build_summary_user(query: str, context: str) -> str:
        return f"我的搜索任务是: {query}\n\n【搜索结果上下文】:\n{context}\n\n请基于以上信息进行总结："

    @staticmethod
    def build_solver_user(original_question: str, reports: list) -> str:
        context_str = "\n\n".join(reports)
        return f"用户原始问题: {original_question}\n\n--- 各模型独立调查报告 ---\n{context_str}\n------------------------\n请开始你的最终汇总："