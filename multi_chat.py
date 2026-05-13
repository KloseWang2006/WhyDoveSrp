from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from memory_manager import DialogueMemory


def main():
    # 1. 初始化模型 (保持不变)
    model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI,
        model_type=ModelType.GPT_4O_MINI,
        api_key="sk-Avpdz6EogreRqeFvZLYnFa84Iwuac6bwSaN58mBu3JkWBVSC",
        url="https://api.chatanywhere.tech/v1",
    )

    # 2. 角色定义
    A_name = "Undergraduate Student (A)"
    B_name = "Graduate Mentor (B)"
    C_name = "PhD Professor (C)"
    agents_dict = {A_name: "A", B_name: "B", C_name: "C"}  # 方便检索

    memory = DialogueMemory()

    # 3. 创建角色 Agent (增加具体的性格 Prompt)
    def create_role_agent(role_name, personality):
        sys_msg = BaseMessage.make_assistant_message(
            role_name=role_name,
            content=f"You are {role_name}. {personality} Speak naturally. NO tags."
        )
        return ChatAgent(sys_msg, model=model)

    agents = {
        A_name: create_role_agent(A_name, "Diligent, reporting data, respectful."),
        B_name: create_role_agent(B_name, "Caring mentor, offers technical critique and personal insights."),
        C_name: create_role_agent(C_name, "Gentle Professor, provides high-level strategic guidance.")
    }

    # 4. 创建 Judge Agent
    judge_sys_msg = BaseMessage.make_assistant_message(
        role_name="Judge",
        content=(
            f"You are a moderator. Based on the conversation history, decide who speaks next. "
            f"Candidates: {list(agents.keys())}. "
            "Output ONLY the name of the next speaker."
        )
    )
    judge_agent = ChatAgent(judge_sys_msg, model=model)

    # --- 设定结束条件：总发言次数 ---
    total_utterances_limit = 10  # 设定总共只允许 10 次发言
    current_utterance_count = 0  # 计数器

    # 5. 会议开始（计为第 1 次发言）
    initial_speech = "Professor C, Senior B, I've noticed a strange drop in accuracy when we use the new normalization method."
    print(f"\033[34m[1][{A_name}]:\033[0m {initial_speech}\n")
    memory.add_message(A_name, initial_speech)

    last_speaker = A_name
    current_utterance_count = 1

    # 6. 对话循环：直到达到总发言次数
    while current_utterance_count < total_utterances_limit:
        # A. Judge 决策
        context = memory.get_context()
        judge_prompt = f"History:\n{context}\n\nNext speaker? (Not {last_speaker})"
        judge_res = judge_agent.step(judge_prompt)
        next_speaker_raw = judge_res.msgs[0].content

        # 匹配候选人
        next_speaker = None
        for name in agents.keys():
            if name in next_speaker_raw:
                next_speaker = name
                break

        if not next_speaker:
            next_speaker = [n for n in agents.keys() if n != last_speaker][0]

        # B. 选定的人发言
        recent_memory = memory.get_recent_summary()
        agent_prompt = f"Recent context:\n{recent_memory}\n\nRespond naturally."

        response = agents[next_speaker].step(agent_prompt)
        content = response.msgs[0].content

        # C. 计数与打印
        current_utterance_count += 1

        color = {"Undergraduate Student (A)": "\033[34m",
                 "Graduate Mentor (B)": "\033[32m",
                 "PhD Professor (C)": "\033[35m"}[next_speaker]

        # 打印格式改为：[次数][角色名]: 内容
        print(f"{color}[{current_utterance_count}][{next_speaker}]:\033[0m {content}\n")

        # D. 更新记忆
        memory.add_message(next_speaker, content)
        last_speaker = next_speaker

    print(f"--- Meeting adjourned after {total_utterances_limit} utterances. ---")


if __name__ == "__main__":
    main()