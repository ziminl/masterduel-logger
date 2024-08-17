import tkinter as tk
from tkinter import messagebox
import json
import os

class GameRecord:
    def __init__(self, my_deck, opponent_deck, is_first, result):
        self.my_deck = my_deck
        self.opponent_deck = opponent_deck
        self.is_first = is_first  # True for first, False for second
        self.result = result  # True for win, False for lose

    def __str__(self):
        first_or_second = "선공" if self.is_first else "후공"
        result_str = "승리" if self.result else "패배"
        return f"나의 덱: {self.my_deck}, 상대 덱: {self.opponent_deck}, {first_or_second}, 결과: {result_str}"

    def to_dict(self):
        return {
            "my_deck": self.my_deck,
            "opponent_deck": self.opponent_deck,
            "is_first": self.is_first,
            "result": self.result
        }

    @staticmethod
    def from_dict(data):
        return GameRecord(
            my_deck=data["my_deck"],
            opponent_deck=data["opponent_deck"],
            is_first=data["is_first"],
            result=data["result"]
        )

class Player:
    def __init__(self, tier, points):
        self.tier = tier
        self.points = points
        self.losing_streak = 0
        self.records = []

    def get_tier_name(self):
        if self.tier > 5:
            return f"다이아 {self.tier - 5}티어"
        else:
            return f"마스터 {self.tier}티어"

    def win(self, my_deck, opponent_deck, is_first):
        self.points += 1
        self.losing_streak = 0
        self.records.append(GameRecord(my_deck, opponent_deck, is_first, True))
        if (self.tier > 5 and self.points >= 4) or (self.tier <= 5 and self.points >= 5):
            self.promote()

    def lose(self, my_deck, opponent_deck, is_first):
        if self.points > 0:
            self.points -= 1
        else:
            self.losing_streak += 1
            if self.losing_streak >= 3:
                self.demote()
        self.records.append(GameRecord(my_deck, opponent_deck, is_first, False))

    def promote(self):
        if self.tier > 1:
            self.tier -= 1
            self.points = 0
            messagebox.showinfo("승급", f"승급! 현재 티어: {self.get_tier_name()}")
        else:
            messagebox.showinfo("최고 티어", "최고 티어에 도달했습니다!")

    def demote(self):
        if self.tier < 10 and self.tier != 5:
            self.tier += 1
            self.points = 0
            self.losing_streak = 0
            messagebox.showinfo("강등", f"강등되었습니다. 현재 티어: {self.get_tier_name()}")
        else:
            messagebox.showinfo("강등 불가", f"{self.get_tier_name()}에서 더 이상 강등되지 않습니다.")

    def status(self):
        return f"현재 티어: {self.get_tier_name()}, 승점: {self.points}, 연패 포인트: {self.losing_streak}"

    def show_records(self):
        records_str = "\n".join(str(record) for record in self.records)
        return records_str if records_str else "기록된 게임이 없습니다."

    def win_rate(self):
        total_games = len(self.records)
        if total_games == 0:
            messagebox.showinfo("승률", "기록된 게임이 없습니다.")
            return
        wins = sum(1 for record in self.records if record.result)
        win_rate = wins / total_games * 100
        messagebox.showinfo("승률", f"총 승률: {win_rate:.2f}% ({total_games}판 플레이)")

    def first_second_rate(self):
        total_games = len(self.records)
        if total_games == 0:
            messagebox.showinfo("선공/후공 비율", "기록된 게임이 없습니다.")
            return
        first_games = sum(1 for record in self.records if record.is_first)
        second_games = total_games - first_games
        first_rate = first_games / total_games * 100
        second_rate = second_games / total_games * 100
        messagebox.showinfo("선공/후공 비율", f"선공 비율: {first_rate:.2f}%, 후공 비율: {second_rate:.2f}%")

    def first_second_win_rate(self):
        total_games = len(self.records)
        if total_games == 0:
            messagebox.showinfo("선공/후공 승률", "기록된 게임이 없습니다.")
            return
        first_games = sum(1 for record in self.records if record.is_first)
        first_win = sum(1 for record in self.records if record.is_first and record.result)
        second_games = total_games - first_games
        second_win = sum(1 for record in self.records if not record.is_first and record.result)
        first_win_rate = first_win / first_games * 100 if first_games > 0 else 0
        second_win_rate = second_win / second_games * 100 if second_games > 0 else 0
        messagebox.showinfo("선공/후공 승률", f"선공 승률: {first_win_rate:.2f}%, 후공 승률: {second_win_rate:.2f}%")

    def deck_win_rate(self, deck_name):
        total_games = sum(1 for record in self.records if record.my_deck == deck_name)
        if total_games == 0:
            messagebox.showinfo("덱 승률", f"{deck_name} 덱으로 기록된 게임이 없습니다.")
            return
        wins = sum(1 for record in self.records if record.my_deck == deck_name and record.result)
        deck_win_rate = wins / total_games * 100
        messagebox.showinfo("덱 승률", f"{deck_name} 덱의 승률: {deck_win_rate:.2f}% ({total_games}판 플레이)")

    def matchup_win_rate(self, deck_name):
        matchup_stats = {}
        for record in self.records:
            if record.my_deck == deck_name:
                matchup_key = (record.my_deck, record.opponent_deck)
                if matchup_key not in matchup_stats:
                    matchup_stats[matchup_key] = {"total": 0, "wins": 0}
                matchup_stats[matchup_key]["total"] += 1
                if record.result:
                    matchup_stats[matchup_key]["wins"] += 1

        matchup_details = []
        for (my_deck, opponent_deck), stats in matchup_stats.items():
            matchup_win_rate = stats["wins"] / stats["total"] * 100
            matchup_details.append(f"{my_deck} vs {opponent_deck}: {matchup_win_rate:.2f}% ({stats['total']}번 플레이)")

        messagebox.showinfo("상성 승률", "\n".join(matchup_details) if matchup_details else f"{deck_name} 덱으로 기록된 게임이 없습니다.")

    def opponent_deck_distribution(self):
        total_games = len(self.records)
        if total_games == 0:
            messagebox.showinfo("상대 덱 분포", "기록된 게임이 없습니다.")
            return
        opponent_deck_distribution = {}
        for record in self.records:
            if record.opponent_deck not in opponent_deck_distribution:
                opponent_deck_distribution[record.opponent_deck] = 0
            opponent_deck_distribution[record.opponent_deck] += 1

        distribution_details = []
        for opponent_deck, count in opponent_deck_distribution.items():
            distribution_rate = count / total_games * 100
            distribution_details.append(f"{opponent_deck}: {distribution_rate:.2f}%")

        messagebox.showinfo("상대 덱 분포", "\n".join(distribution_details))

    def save_to_file(self, filename):
        data = {
            "tier": self.tier,
            "points": self.points,
            "losing_streak": self.losing_streak,
            "records": [record.to_dict() for record in self.records]
        }
        with open(filename, 'w') as file:
            json.dump(data, file)
        messagebox.showinfo("저장", "데이터가 저장되었습니다.")

    @staticmethod
    def load_from_file(filename):
        if not os.path.exists(filename):
            messagebox.showerror("오류", "저장된 데이터가 없습니다.")
            return None

        with open(filename, 'r') as file:
            data = json.load(file)

        player = Player(data["tier"], data["points"])
        player.losing_streak = data["losing_streak"]
        player.records = [GameRecord.from_dict(record) for record in data["records"]]
        return player

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("게임 기록 프로그램")
        self.geometry("800x600")  # 창 크기를 조정하여 오른쪽에 공간 확보

        self.player = None

        self.create_widgets()

    def create_widgets(self):
        # 왼쪽 패널
        left_panel = tk.Frame(self)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)

        self.tier_label = tk.Label(left_panel, text="현재 티어 (다이아 5티어는 10, 마스터 1티어는 1):")
        self.tier_label.pack()

        self.tier_entry = tk.Entry(left_panel)
        self.tier_entry.pack()

        self.points_label = tk.Label(left_panel, text="현재 승점 (다이아: 0~3, 마스터: 0~4):")
        self.points_label.pack()

        self.points_entry = tk.Entry(left_panel)
        self.points_entry.pack()

        self.start_button = tk.Button(left_panel, text="시작", command=self.start_game)
        self.start_button.pack()

        self.status_label = tk.Label(left_panel, text="")
        self.status_label.pack()

        self.my_deck_label = tk.Label(left_panel, text="나의 덱:")
        self.my_deck_label.pack()

        self.my_deck_entry = tk.Entry(left_panel)
        self.my_deck_entry.pack()

        self.opponent_deck_label = tk.Label(left_panel, text="상대 덱:")
        self.opponent_deck_label.pack()

        self.opponent_deck_entry = tk.Entry(left_panel)
        self.opponent_deck_entry.pack()

        self.is_first_label = tk.Label(left_panel, text="선공 여부 (예/아니오):")
        self.is_first_label.pack()

        self.is_first_entry = tk.Entry(left_panel)
        self.is_first_entry.pack()

        self.win_button = tk.Button(left_panel, text="승리", command=lambda: self.record_game(True), state=tk.DISABLED)
        self.win_button.pack()

        self.lose_button = tk.Button(left_panel, text="패배", command=lambda: self.record_game(False), state=tk.DISABLED)
        self.lose_button.pack()

        self.win_rate_button = tk.Button(left_panel, text="승률 보기", command=self.show_win_rate, state=tk.DISABLED)
        self.win_rate_button.pack()

        self.first_second_rate_button = tk.Button(left_panel, text="선공/후공 비율", command=self.show_first_second_rate, state=tk.DISABLED)
        self.first_second_rate_button.pack()

        self.first_second_win_rate_button = tk.Button(left_panel, text="선공/후공 승률", command=self.show_first_second_win_rate, state=tk.DISABLED)
        self.first_second_win_rate_button.pack()

        self.deck_win_rate_label = tk.Label(left_panel, text="덱 승률 확인할 덱 이름:")
        self.deck_win_rate_label.pack()

        self.deck_win_rate_entry = tk.Entry(left_panel)
        self.deck_win_rate_entry.pack()

        self.deck_win_rate_button = tk.Button(left_panel, text="덱 승률", command=self.show_deck_win_rate, state=tk.DISABLED)
        self.deck_win_rate_button.pack()

        self.matchup_win_rate_label = tk.Label(left_panel, text="상성 승률 확인할 덱 이름:")
        self.matchup_win_rate_label.pack()

        self.matchup_win_rate_entry = tk.Entry(left_panel)
        self.matchup_win_rate_entry.pack()

        self.matchup_win_rate_button = tk.Button(left_panel, text="상성 승률", command=self.show_matchup_win_rate, state=tk.DISABLED)
        self.matchup_win_rate_button.pack()

        self.opponent_deck_distribution_button = tk.Button(left_panel, text="상대 덱 분포", command=self.show_opponent_deck_distribution, state=tk.DISABLED)
        self.opponent_deck_distribution_button.pack()

        self.save_button = tk.Button(left_panel, text="저장하기", command=self.save_data, state=tk.DISABLED)
        self.save_button.pack()

        self.load_button = tk.Button(left_panel, text="불러오기", command=self.load_data)
        self.load_button.pack()

        # 오른쪽 패널
        right_panel = tk.Frame(self)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.records_text = tk.Text(right_panel, state=tk.DISABLED)
        self.records_text.pack(fill=tk.BOTH, expand=True)

    def start_game(self):
        try:
            tier = int(self.tier_entry.get())
            points = int(self.points_entry.get())
            if not (1 <= tier <= 10):
                raise ValueError("티어는 1에서 10 사이여야 합니다.")
            if (tier > 5 and not (0 <= points <= 3)) or (tier <= 5 and not (0 <= points <= 4)):
                raise ValueError("승점이 유효한 범위를 벗어났습니다.")
            self.player = Player(tier, points)
            self.update_status()
            self.enable_buttons()
            self.hide_initial_widgets()
        except ValueError as e:
            messagebox.showerror("입력 오류", str(e))

    def record_game(self, is_win):
        if self.player:
            my_deck = self.my_deck_entry.get()
            opponent_deck = self.opponent_deck_entry.get()
            is_first_input = self.is_first_entry.get().strip().lower()
            is_first = True if is_first_input == "예" else False

            if not my_deck or not opponent_deck:
                messagebox.showerror("입력 오류", "덱 정보를 입력하세요.")
                return

            if is_win:
                self.player.win(my_deck, opponent_deck, is_first)
            else:
                self.player.lose(my_deck, opponent_deck, is_first)
            self.update_status()
            self.update_records_display()

    def update_status(self):
        if self.player:
            self.status_label.config(text=self.player.status())

    def enable_buttons(self):
        self.win_button.config(state=tk.NORMAL)
        self.lose_button.config(state=tk.NORMAL)
        self.win_rate_button.config(state=tk.NORMAL)
        self.first_second_rate_button.config(state=tk.NORMAL)
        self.first_second_win_rate_button.config(state=tk.NORMAL)
        self.deck_win_rate_button.config(state=tk.NORMAL)
        self.matchup_win_rate_button.config(state=tk.NORMAL)
        self.opponent_deck_distribution_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)

    def hide_initial_widgets(self):
        self.tier_label.pack_forget()
        self.tier_entry.pack_forget()
        self.points_label.pack_forget()
        self.points_entry.pack_forget()
        self.start_button.pack_forget()

    def update_records_display(self):
        if self.player:
            records_str = self.player.show_records()
            self.records_text.config(state=tk.NORMAL)
            self.records_text.delete(1.0, tk.END)
            self.records_text.insert(tk.END, records_str)
            self.records_text.config(state=tk.DISABLED)

    def show_win_rate(self):
        if self.player:
            self.player.win_rate()

    def show_first_second_rate(self):
        if self.player:
            self.player.first_second_rate()

    def show_first_second_win_rate(self):
        if self.player:
            self.player.first_second_win_rate()

    def show_deck_win_rate(self):
        deck_name = self.deck_win_rate_entry.get()
        if self.player and deck_name:
            self.player.deck_win_rate(deck_name)
        else:
            messagebox.showerror("입력 오류", "덱 이름을 입력하세요.")

    def show_matchup_win_rate(self):
        deck_name = self.matchup_win_rate_entry.get()
        if self.player and deck_name:
            self.player.matchup_win_rate(deck_name)
        else:
            messagebox.showerror("입력 오류", "덱 이름을 입력하세요.")

    def show_opponent_deck_distribution(self):
        if self.player:
            self.player.opponent_deck_distribution()

    def save_data(self):
        if self.player:
            self.player.save_to_file("game_data.json")

    def load_data(self):
        player = Player.load_from_file("game_data.json")
        if player:
            self.player = player
            self.update_status()
            self.enable_buttons()
            self.hide_initial_widgets()
            self.update_records_display()

if __name__ == "__main__":
    app = Application()
    app.mainloop()
