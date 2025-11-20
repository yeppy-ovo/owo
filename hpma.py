import requests
import json
import random

from requests.utils import stream_decode_response_unicode
from xunfei_tts import text_to_speech 

from requests.utils import stream_decode_response_unicode

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.5   
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

# 游戏设置
role_system = ["哈利", "赫敏"]
current_role = random.choice(role_system)

# 系统提示词
game_system = f"""你正在玩卡牌对策游戏，用户作为一方，你作为另一方去对抗，想办法获胜，总共五个回合

游戏规则：
1. 每个人的生命值是100，初始魔力是10，每回合恢复2，魔力值最大为10
2. 有人生命值降为0时结束游戏，生命值高的一方获胜
3. 完成五个回合的情况下，生命值高的一方获胜
4. 哈利的特性是用低于三费的卡牌伤害增加50%，赫敏的特性是每使用三张卡牌费用最高的卡牌费用减半，向下取整不为0
5. 哈利的卡组是
昏昏倒地4费40点攻击
飞沙走石2费20点攻击
万弹齐发2费20点攻击
火焰熊熊4费30点攻击
除你武器3费30点攻击，特殊效果使对方下一回合禁用卡组剩余卡中费用费用最高的卡牌
6. 赫敏的卡组的
清水如泉3费30点攻击
变形咒2费10点攻击
冰冻咒4费30点攻击
霹雳爆炸5费50点攻击
闪回咒，特殊效果复制自己使用上一张牌的费用和攻击
7. 每轮出牌前列出当前状态和可使用卡牌，每轮使用完总结双方的生命值费用和剩余卡牌
8. 使用卡牌后依据多少费扣除魔力值
9. 当用户确定角色后只能决定当前角色的行动，每回合只可操作自己角色的行动，另一方由机器人操控。依据示例的列举操控，保持不变
10. 一回合为哈利赫敏各出一张卡牌
11. 一方使用卡牌后，根据攻击扣除对方生命值，双方生命值都减少

示例：
- 如果你是"哈利"，使用了卡牌
  使用了低于等于3费的卡牌：当前卡牌伤害增加50%
  使用了大于3费的卡牌：使用了卡牌造成攻击
  优先使用3费及以下的卡牌，以利用特质增伤。
  如果法力值足够，且存在可以击败对手的卡牌，则使用该卡牌。
  否则，选择当前可用的伤害最高的卡牌（考虑特质增伤后）。
  

- 如果你是"赫敏"，使用了卡牌 
  满足了使用三张卡牌给最高费用卡牌费用减半：费用最高卡牌费用减半
  未满足条件：使用了卡牌造成攻击
  记录已使用的卡牌数量，每3张触发一次减费。
  优先使用高费卡牌（因为减费后更容易使用），但也要考虑当前法力值。
  如果闪回咒可用，且上一张卡牌是强力的，则使用闪回咒复制。

现在开始游戏，用户会随机成为哈利或者赫敏，开始前介绍基本规则，你将成为另一方使用卡牌，用户扮演的角色卡牌使用情况需要输入才能使用，用陈述语句说明每回合卡牌使用情况"""

import random
import time

class FixedGame:
    def __init__(self):
        # 角色系统
        self.role_system = ["哈利", "赫敏"]
        self.current_role = random.choice(self.role_system)
        self.ai_role = "赫敏" if self.current_role == "哈利" else "哈利"
        
        # 玩家和AI的状态
        self.player_health = 100
        self.ai_health = 100
        self.player_mana = 10
        self.ai_mana = 10
        self.max_mana = 10
        
        # 回合计数
        self.round_count = 0
        self.max_rounds = 5
        
        # 卡组定义
        self.harry_cards = {
            "昏昏倒地": {"cost": 4, "damage": 40, "special": None},
            "飞沙走石": {"cost": 2, "damage": 20, "special": None},
            "万弹齐发": {"cost": 2, "damage": 20, "special": None},
            "火焰熊熊": {"cost": 4, "damage": 30, "special": None},
            "除你武器": {"cost": 3, "damage": 30, "special": "disarm"}
        }
        
        self.hermione_cards = {
            "清水如泉": {"cost": 3, "damage": 30, "special": None},
            "变形咒": {"cost": 2, "damage": 10, "special": None},
            "冰冻咒": {"cost": 4, "damage": 30, "special": None},
            "霹雳爆炸": {"cost": 5, "damage": 50, "special": None},
            "闪回咒": {"cost": 0, "damage": 0, "special": "copy"}
        }
        
        # 游戏状态追踪
        self.player_cards_used = 0
        self.ai_cards_used = 0
        self.player_last_card = None
        self.ai_last_card = None
        self.ai_banned_card = None
        self.player_banned_card = None
        
        # 根据玩家角色确定卡组
        if self.current_role == "哈利":
            self.player_cards = self.harry_cards.copy()
            self.ai_cards = self.hermione_cards.copy()
        else:
            self.player_cards = self.hermione_cards.copy()
            self.ai_cards = self.harry_cards.copy()

    def display_status(self):
        """显示当前游戏状态"""
        print(f"\n{'='*50}")
        print(f"第 {self.round_count} 回合")
        print(f"{'='*50}")
        print(f"{self.current_role} (你): 生命值 {self.player_health}, 魔力值 {self.player_mana}/10")
        print(f"{self.ai_role} (AI): 生命值 {self.ai_health}, 魔力值 {self.ai_mana}/10")
        
        if self.player_banned_card:
            print(f"⚠️  你被禁用的卡牌: {self.player_banned_card}")
        if self.ai_banned_card:
            print(f"⚠️  AI被禁用的卡牌: {self.ai_banned_card}")

    def get_available_cards(self, is_player=True):
        """获取可用的卡牌列表"""
        if is_player:
            cards = self.player_cards
            mana = self.player_mana
            banned_card = self.player_banned_card
        else:
            cards = self.ai_cards
            mana = self.ai_mana
            banned_card = self.ai_banned_card
        
        available = []
        for card_name, card_info in cards.items():
            if card_info["cost"] <= mana and card_name != banned_card:
                available.append((card_name, card_info))
        
        return available

    def calculate_damage_and_health(self, card_name, card_info, is_player=True):
        """正确计算伤害并更新生命值"""
        # 计算基础伤害
        base_damage = card_info["damage"]
        
        # 应用角色特性
        if (is_player and self.current_role == "哈利") or (not is_player and self.ai_role == "哈利"):
            if card_info["cost"] <= 3:
                base_damage = int(base_damage * 1.5)  # 哈利特性：低费卡增伤50%
        
        # 处理特殊卡牌
        final_damage = base_damage
        if card_info["special"] == "copy":
            # 闪回咒复制上一张卡牌
            last_card = self.player_last_card if is_player else self.ai_last_card
            if last_card:
                original_card = self.player_cards.get(last_card) if is_player else self.ai_cards.get(last_card)
                if original_card:
                    final_damage = original_card["damage"]
        
        # 更新生命值
        if is_player:
            self.ai_health = max(0, self.ai_health - final_damage)
        else:
            self.player_health = max(0, self.player_health - final_damage)
        
        return final_damage

    def manage_mana(self, card_cost, is_player=True):
        """管理魔力值，防止溢出"""
        if is_player:
            # 检查魔力是否足够
            if self.player_mana < card_cost:
                raise ValueError("魔力值不足！")
            
            # 扣除魔力值
            self.player_mana -= card_cost
        else:
            if self.ai_mana < card_cost:
                raise ValueError("AI魔力值不足！")
            
            self.ai_mana -= card_cost

    def restore_mana_per_round(self):
        """每回合恢复魔力值，确保不超过最大值"""
        self.player_mana = min(self.max_mana, self.player_mana + 2)
        self.ai_mana = min(self.max_mana, self.ai_mana + 2)
        print(f"魔力恢复: {self.current_role} 魔力值 {self.player_mana}/10, {self.ai_role} 魔力值 {self.ai_mana}/10")

    def apply_special_effects(self, card_name, card_info, is_player=True):
        """应用卡牌的特殊效果"""
        if card_info["special"] == "disarm":
            # 除你武器：禁用对方下一回合费用最高的卡牌
            target_cards = self.ai_cards if is_player else self.player_cards
            highest_cost_card = None
            highest_cost = 0
            
            for target_card, target_info in target_cards.items():
                if target_info["cost"] > highest_cost:
                    highest_cost = target_info["cost"]
                    highest_cost_card = target_card
            
            if highest_cost_card:
                if is_player:
                    self.ai_banned_card = highest_cost_card
                else:
                    self.player_banned_card = highest_cost_card
                print(f"⚡ {card_name} 生效！下一回合 {self.ai_role if is_player else self.current_role} 无法使用 {highest_cost_card}")
        
        elif card_info["special"] == "copy":
            # 闪回咒：复制上一张使用的卡牌
            last_card = self.player_last_card if is_player else self.ai_last_card
            if last_card:
                original_card = self.player_cards.get(last_card) if is_player else self.ai_cards.get(last_card)
                if original_card:
                    print(f"🌀 {card_name} 复制了 {last_card}！")

    def check_hermione_trait(self):
        """检查并应用赫敏的特性"""
        # 玩家是赫敏
        if self.current_role == "赫敏":
            if self.player_cards_used % 3 == 0 and self.player_cards_used > 0:
                self.apply_hermione_discount(True)
        
        # AI是赫敏
        if self.ai_role == "赫敏":
            if self.ai_cards_used % 3 == 0 and self.ai_cards_used > 0:
                self.apply_hermione_discount(False)

    def apply_hermione_discount(self, is_player=True):
        """应用赫敏的费用减半特性"""
        cards = self.player_cards if is_player else self.ai_cards
        role_name = self.current_role if is_player else self.ai_role
        
        # 找到费用最高的卡牌
        highest_cost = 0
        highest_card = None
        
        for card_name, card_info in cards.items():
            if card_info["cost"] > highest_cost:
                highest_cost = card_info["cost"]
                highest_card = card_name
        
        if highest_card:
            new_cost = max(1, highest_cost // 2)  # 向下取整，不为0
            cards[highest_card]["cost"] = new_cost
            print(f"✨ {role_name} 的特性触发！{highest_card} 的费用减半为 {new_cost}")

    def player_turn(self):
        """玩家回合"""
        print(f"\n🎮 {self.current_role} 的回合")
        
        # 显示可用卡牌
        available_cards = self.get_available_cards(True)
        if not available_cards:
            print("没有可用的卡牌，跳过回合")
            return
        
        print("可用的卡牌:")
        for i, (card_name, card_info) in enumerate(available_cards, 1):
            special_indicator = " ⚡" if card_info["special"] else ""
            print(f"{i}. {card_name} (费用: {card_info['cost']}, 伤害: {card_info['damage']}{special_indicator})")
        
        # 玩家选择卡牌
        while True:
            try:
                choice = int(input("请选择卡牌 (输入数字): ")) - 1
                if 0 <= choice < len(available_cards):
                    break
                else:
                    print("无效的选择，请重新输入")
            except ValueError:
                print("请输入有效的数字")
        
        card_name, card_info = available_cards[choice]
        
        # 应用卡牌效果
        self.use_card(card_name, card_info, True)

    def ai_turn(self):
        """AI回合"""
        print(f"\n🤖 {self.ai_role} 的回合")
        time.sleep(1)
        
        available_cards = self.get_available_cards(False)
        if not available_cards:
            print("AI没有可用的卡牌，跳过回合")
            return
        
        # AI策略
        if self.ai_role == "哈利":
            card_choice = self.ai_harry_strategy(available_cards)
        else:
            card_choice = self.ai_hermione_strategy(available_cards)
        
        if card_choice:
            card_name, card_info = card_choice
            self.use_card(card_name, card_info, False)

    def ai_harry_strategy(self, available_cards):
        """哈利的AI策略"""
        # 优先使用3费及以下的卡牌以利用特质增伤
        low_cost_cards = [(name, info) for name, info in available_cards if info["cost"] <= 3]
        
        if low_cost_cards:
            # 选择伤害最高的低费卡牌（考虑增伤后）
            best_card = max(low_cost_cards, key=lambda x: int(x[1]["damage"] * 1.5))
        else:
            # 没有低费卡牌，选择伤害最高的可用卡牌
            best_card = max(available_cards, key=lambda x: x[1]["damage"])
        
        return best_card

    def ai_hermione_strategy(self, available_cards):
        """赫敏的AI策略"""
        # 检查是否有闪回咒可用且上一张卡牌强力
        flashback_available = any(name == "闪回咒" for name, info in available_cards)
        if flashback_available and self.ai_last_card:
            last_card_info = self.ai_cards.get(self.ai_last_card)
            if last_card_info and last_card_info["damage"] >= 30:
                return ("闪回咒", self.ai_cards["闪回咒"])
        
        # 优先使用高费卡牌（因为可能被减费）
        high_cost_cards = [(name, info) for name, info in available_cards if info["cost"] >= 3]
        if high_cost_cards:
            return max(high_cost_cards, key=lambda x: x[1]["damage"])
        else:
            return max(available_cards, key=lambda x: x[1]["damage"])

    def use_card(self, card_name, card_info, is_player=True):
        """使用卡牌的核心逻辑"""
        # 扣除魔力值
        self.manage_mana(card_info["cost"], is_player)
        
        # 计算伤害并更新生命值
        damage = self.calculate_damage_and_health(card_name, card_info, is_player)
        
        # 应用特殊效果
        self.apply_special_effects(card_name, card_info, is_player)
        
        # 更新使用计数
        if is_player:
            self.player_cards_used += 1
            self.player_last_card = card_name
        else:
            self.ai_cards_used += 1
            self.ai_last_card = card_name
        
        # 显示出牌信息
        role_name = self.current_role if is_player else self.ai_role
        print(f"{role_name} 使用了 {card_name}，造成 {damage} 点伤害！")

    def end_round_processing(self):
        """回合结束时的处理"""
        # 恢复魔力值
        self.restore_mana_per_round()
        
        # 检查赫敏的特性触发
        self.check_hermione_trait()
        
        # 显示回合总结
        print(f"\n=== 回合 {self.round_count} 结束 ===")
        print(f"{self.current_role}: 生命值 {self.player_health}, 魔力值 {self.player_mana}/10")
        print(f"{self.ai_role}: 生命值 {self.ai_health}, 魔力值 {self.ai_mana}/10")
        
        # 检查游戏是否结束
        if self.check_game_end():
            return True
        return False

    def check_game_end(self):
        """检查游戏是否应该结束"""
        if self.player_health <= 0 or self.ai_health <= 0:
            return True
        
        if self.round_count >= self.max_rounds:
            return True
        
        return False

    def declare_winner(self):
        """宣布获胜者"""
        print(f"\n🏆 游戏结束！")
        if self.player_health > self.ai_health:
            print(f"获胜者: {self.current_role}")
        elif self.ai_health > self.player_health:
            print(f"获胜者: {self.ai_role}")
        else:
            print("平局！")
        
        print(f"最终生命值 - {self.current_role}: {self.player_health}, {self.ai_role}: {self.ai_health}")

    def play_round(self):
        """执行一个完整的回合（双方各行动一次）"""
        self.round_count += 1
        print(f"\n🎯 第 {self.round_count} 回合开始")
        
        # 清除上回合的禁用效果
        self.player_banned_card = None
        self.ai_banned_card = None
        
        # 显示状态
        self.display_status()
        
        # 玩家回合
        self.player_turn()
        
        # 检查游戏是否提前结束
        if self.check_game_end():
            return True
        
        # AI回合
        self.ai_turn()
        
        # 回合结束处理
        if self.end_round_processing():
            return True
        
        return False

    def start_game(self):
        """开始游戏"""
        print("🧙‍♂️ 欢迎来到哈利波特卡牌对决！")
        print(f"你随机到的角色是: {self.current_role}")
        print("\n游戏规则:")
        print("1. 生命值100，初始魔力10，每回合恢复2，魔力值最大为10")
        print("2. 有人生命值降为0时结束游戏")
        print("3. 五个回合后生命值高的一方获胜")
        print(f"4. {self.current_role} 的特性: {self.get_trait_description()}")
        print("\n游戏开始！")
        
        while not self.check_game_end():
            if self.play_round():
                break
        
        # 游戏结束
        self.declare_winner()

    def get_trait_description(self):
        """获取角色特性描述"""
        if self.current_role == "哈利":
            return "使用低于三费的卡牌伤害增加50%"
        else:
            return "每使用三张卡牌，费用最高的卡牌费用减半"

# 运行游戏
if __name__ == "__main__":
    game = FixedGame()
    game.start_game()
# 维护对话历史
conversation_history = [
    {"role": "system", "content": game_system}
]

# 多轮对话循环
while True:
    user_input = input("我的行动：")
    
    # 添加用户消息到历史
    conversation_history.append({"role": "user", "content": user_input})
    
    # 调用API
    result = call_zhipu_api(conversation_history)
    assistant_reply = result['choices'][0]['message']['content']
    
    # 添加助手回复到历史
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    
    # 打印回复
    print(assistant_reply)

        # TTS语音播放
    # 需要安装playsound：pip install playsound
    text_to_speech(assistant_reply)
    
    # 检查是否猜对（模型回复"再见"）
    if "生命值为0""第五回合结束" in assistant_reply:
        print(f"\n游戏结束！")
        break