import random
import time

class Game:
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

    def apply_harry_trait(self, card_name, card_info, is_player=True):
        """应用哈利的特性"""
        if (is_player and self.current_role == "哈利") or (not is_player and self.ai_role == "哈利"):
            if card_info["cost"] <= 3:
                # 低于三费的卡牌伤害增加50%
                return int(card_info["damage"] * 1.5)
        return card_info["damage"]

    def apply_hermione_trait(self, is_player=True):
        """应用赫敏的特性"""
        if (is_player and self.current_role == "赫敏") or (not is_player and self.ai_role == "赫敏"):
            cards_used = self.player_cards_used if is_player else self.ai_cards_used
            if cards_used % 3 == 0 and cards_used > 0:
                # 每使用三张卡牌，费用最高的卡牌费用减半
                cards = self.player_cards if is_player else self.ai_cards
                highest_cost_card = None
                highest_cost = 0
                
                for card_name, card_info in cards.items():
                    if card_info["cost"] > highest_cost:
                        highest_cost = card_info["cost"]
                        highest_cost_card = card_name
                
                if highest_cost_card:
                    new_cost = max(1, highest_cost // 2)  # 向下取整，不为0
                    cards[highest_cost_card]["cost"] = new_cost
                    print(f"✨ {self.current_role if is_player else self.ai_role} 的特性触发！{highest_cost_card} 的费用减半为 {new_cost}")

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
                    damage = original_card["damage"]
                    print(f"🌀 {card_name} 复制了 {last_card}，造成 {damage} 点伤害！")
                    return damage
            return 0

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
        self.play_card(card_name, card_info, True)

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
            self.play_card(card_name, card_info, False)

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

    def play_card(self, card_name, card_info, is_player=True):
        """执行出牌逻辑"""
        if is_player:
            mana = self.player_mana
            health = self.ai_health
            cards_used = self.player_cards_used
            last_card = self.player_last_card
        else:
            mana = self.ai_mana
            health = self.player_health
            cards_used = self.ai_cards_used
            last_card = self.ai_last_card
        
        # 扣除魔力值
        cost = card_info["cost"]
        if is_player:
            self.player_mana -= cost
        else:
            self.ai_mana -= cost
        
        # 计算伤害
        if card_info["special"] == "copy":
            damage = self.apply_special_effects(card_name, card_info, is_player)
        else:
            damage = self.apply_harry_trait(card_name, card_info, is_player)
        
        # 应用特殊效果
        special_damage = self.apply_special_effects(card_name, card_info, is_player)
        if special_damage is not None:
            damage = special_damage
        
        # 造成伤害
        if is_player:
            self.ai_health = max(0, self.ai_health - damage)
        else:
            self.player_health = max(0, self.player_health - damage)
        
        # 更新使用计数和最后使用的卡牌
        if is_player:
            self.player_cards_used += 1
            self.player_last_card = card_name
        else:
            self.ai_cards_used += 1
            self.ai_last_card = card_name
        
        # 应用赫敏的特性
        self.apply_hermione_trait(is_player)
        
        # 显示出牌信息
        role_name = self.current_role if is_player else self.ai_role
        print(f"{role_name} 使用了 {card_name}，造成 {damage} 点伤害！")

    def restore_mana(self):
        """每回合恢复魔力值"""
        self.player_mana = min(self.max_mana, self.player_mana + 2)
        self.ai_mana = min(self.max_mana, self.ai_mana + 2)

    def clear_banned_cards(self):
        """清除上回合的禁用效果"""
        self.player_banned_card = None
        self.ai_banned_card = None

    def check_game_over(self):
        """检查游戏是否结束"""
        if self.player_health <= 0 or self.ai_health <= 0:
            return True
        if self.round_count >= self.max_rounds:
            return True
        return False

    def get_winner(self):
        """确定获胜者"""
        if self.player_health > self.ai_health:
            return self.current_role
        elif self.ai_health > self.player_health:
            return self.ai_role
        else:
            return "平局"

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
        
        while not self.check_game_over():
            self.round_count += 1
            
            # 清除上回合的禁用效果
            self.clear_banned_cards()
            
            # 显示状态
            self.display_status()
            
            # 玩家回合
            self.player_turn()
            
            # 检查游戏是否提前结束
            if self.check_game_over():
                break
            
            # AI回合
            self.ai_turn()
            
            # 恢复魔力值
            self.restore_mana()
            
            # 回合结束显示
            print(f"\n回合 {self.round_count} 结束:")
            print(f"{self.current_role} 生命值: {self.player_health}, 魔力值: {self.player_mana}/10")
            print(f"{self.ai_role} 生命值: {self.ai_health}, 魔力值: {self.ai_mana}/10")
            
            time.sleep(1)
        
        # 游戏结束
        self.end_game()

    def get_trait_description(self):
        """获取角色特性描述"""
        if self.current_role == "哈利":
            return "使用低于三费的卡牌伤害增加50%"
        else:
            return "每使用三张卡牌，费用最高的卡牌费用减半"

    def end_game(self):
        """结束游戏"""
        print(f"\n{'='*50}")
        print("游戏结束！")
        print(f"{'='*50}")
        print(f"最终结果:")
        print(f"{self.current_role}: {self.player_health} 生命值")
        print(f"{self.ai_role}: {self.ai_health} 生命值")
        
        winner = self.get_winner()
        if winner == "平局":
            print("🎉 游戏以平局结束！")
        else:
            print(f"🎉 获胜者是: {winner}！")

# 运行游戏
if __name__ == "__main__":
    game = Game()
    game.start_game()