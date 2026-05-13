import datetime


class DialogueMemory:
    def __init__(self):
        # 存储格式: {"role": role_name, "content": content}
        self.history = []

    def add_message(self, role_name, content):
        self.history.append({
            "role": role_name,
            "content": content
        })

    def get_context(self):
        """生成带编号的对话历史，方便 Judge Agent 参考"""
        if not self.history:
            return "The meeting has just started."

        context_lines = []
        for i, msg in enumerate(self.history):
            context_lines.append(f"{i + 1}. [{msg['role']}]: {msg['content']}")# 消息按时间顺序排列，最新的消息被放在了列表的最末尾
        return "\n".join(context_lines)

    def get_recent_summary(self, limit=5):# 只取最后 limit 条
        """获取最近几条消息，给 memory 增加权重（最近的消息权重更高）"""
        recent = self.history[-limit:]
        return "\n".join([f"[{m['role']}]: {m['content']}" for m in recent])