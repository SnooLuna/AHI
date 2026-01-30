from customtkinter import *
from tkinter import messagebox
import json
from textdistance import damerau_levenshtein
from random import randint, choices

class Deck:
    def __init__(self, cards):
        print(cards, '\n\n')
        self.questions = cards["Questions"]
        self.name = cards["Name"]

        
class System(CTk):
    def __init__(self, title, decks):
        super().__init__()
        set_default_color_theme("green")

        self._file = decks
        self._decks = self._read_decks(decks)
        self._current_deck = None

        with open("home.json", "r") as file:
            home = json.load(file)
        self._home = home

        self._currentQ = None
        self._answer = StringVar()
        self._accept_typos = BooleanVar(value=True)
        self._level = StringVar(value="Sometimes")
        self._freq = DoubleVar(value=50)

        self.title(title)
        self.geometry("750x600")
        self._screen = []

        self.protocol("WM_DELETE_WINDOW", self._quit)

        self._frame = CTkFrame(self)
        self._frame.grid(row=0, column=0, pady=20, padx=20, ipadx=50, ipady=5)

        self._settings = CTkFrame(self)
        self._settings.grid(row=1, column=0, pady=20, padx=20)
        start = CTkButton(self._settings, text="Home", command=self._start_screen, font=("Arial", 16))
        start.grid(row=0, column=0, pady=10, padx=10, ipadx=15, ipady=5)
        button = CTkButton(self._settings, text="Settings", command=self._settings_screen, font=("Arial", 16))
        button.grid(row=0, column=1, pady=10, padx=10, ipadx=15, ipady=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._start_screen()

    def _quit(self):
        save = []
        for i, d in enumerate(self._decks):
            save.append({})
            save[i].update({"Name": d.name})
            save[i].update({"Questions": d.questions})
        
        prompt = messagebox.askyesnocancel("Quit", "Do you want to save before you quit?")
        if prompt:
            with open(self._file, 'w') as file:
                json.dump(save, file, indent=4, default=lambda x: list(x) if isinstance(x, tuple) else str(x))
            self.destroy()
        elif prompt != None:
            self.destroy()

    def _read_decks(self, name):
        ds = []
        with open(name, "r") as file:
            decks = json.load(file)
        for deck in decks:
            ds.append(Deck(deck))
        return ds

    def _make_label(self, text=None, wraplength=700, pady=10, padx=0, fontsize=18, anchor="center"):
        label = CTkLabel(self._frame, text=text, wraplength=wraplength, font=("Arial", fontsize))
        label.pack(pady=pady, padx=padx, anchor=anchor)
        self._screen.append(label)
        return label

    def _make_button(self, text=None, command=None, pady=10, padx=0, anchor="center"):
        button = CTkButton(self._frame, text=text, command=command, font=("Arial", 16))
        button.pack(pady=pady, padx=padx, ipadx=15, ipady=5, anchor=anchor)
        self._screen.append(button)
        return button

    def _make_check(self, text=None, command=None, var=None, on=True, off=False, pady=40, padx=40, anchor="center"):
        check = CTkCheckBox(self._frame, text=text, command=command, variable=var, onvalue=on, offvalue=off,
                            border_width=2, font=("Arial", 14))
        check.pack(pady=pady, padx=padx, anchor=anchor)
        self._screen.append(check)
        return check

    def _make_dropdown(self, options=None, var=None, pady=40, padx=40, anchor="center"):
        DD = CTkComboBox(self._frame, variable=var, values=options,
                            font=("Arial", 14))
        DD.pack(pady=pady, padx=padx, anchor=anchor)
        self._screen.append(DD)
        return DD
    
    def _make_entry(self, textvar, fontname="Arial", fontsize=18, pady=10, padx=40, anchor="center"):
        entry = CTkEntry(self._frame, textvariable=textvar, font=(fontname, fontsize))
        entry.pack(pady=pady, padx=padx, anchor=anchor)
        self._screen.append(entry)
        return entry
    
    def _make_slider(self, var, orientation="horizontal", from_=0, to=100, pady=10, padx=40, anchor="center"):
        slider = CTkSlider(self._frame, variable=var, orientation=orientation, from_=from_, to=to)
        slider.pack(pady=pady, padx=padx, anchor=anchor)
        self._screen.append(slider)
        return slider
    
    def _make_seg_button(self, options=None, var=None, command=None, pady=40, padx=40, anchor="center"):
        button = CTkSegmentedButton(self._frame, variable=var, values=options, command=command,
                            font=("Arial", 14))
        button.pack(pady=pady, padx=padx, anchor=anchor)
        self._screen.append(button)
        return button

    def _clear_screen(self):
        for widget in self._screen:      # Clear all widgets on the screen
            widget.destroy()
        self._screen = []                # Return it to be an empty list

    def _start_screen(self):
        self._clear_screen()
        self._make_label("Start your learning journey!", pady=20, fontsize=25)
        self._make_label(self._home["Text"], pady=20)
        for d in self._decks:
            self._make_button(d.name, lambda d=d: self._choose_deck(d))

    def _start_deck(self, deck):
        self._clear_screen()
        self._current_deck = deck
        self._make_label("hi")

    def _choose_deck(self, deck):
        self._current_deck = deck
        self._next_question()

    def _next_question(self, event=None):
        self._answer = StringVar()           # reset the answer variable
        self._currentQ = choices(self._current_deck.questions, weights=[1.5 - (q['correct'] / q['total']) if q['total'] > 0 else 1.5 for q in self._current_deck.questions])[0]
        self._display(self._currentQ)        # Display the chosen question to the user

    def _display(self, question):
        self._clear_screen()                 # clear anything previously on screen

        self._make_label(question["question"], 700, pady=50)
        if question["total"] == 0:
            self._make_label(question["answer"])
        self._make_entry(textvar=self._answer).focus()
        self.bind('<Return>', self._submit)
    
    def _submit(self, event=None):
        self._currentQ["total"] += 1
        if self._correct():
            self._make_label(f"{self._currentQ["answer"]} is correct!")
            self._currentQ["correct"] += 1
            if self._level.get() == "Always" or (self._level.get() == "Sometimes" and randint(0, 100) < self._freq.get()):
                self._make_button("This answer should not have been correct", self._remove_answer)
        else:
            self._make_label(f"{self._answer.get()} was incorrect. The correct answer is:\n{self._currentQ["answer"]}")
            if self._level.get() == "Always" or (self._level.get() == "Sometimes" and randint(0, 100) < self._freq.get()):
                self._make_button("This answer should have been correct", self._add_answer)
        self.bind('<Return>', self._next_question)

    def _add_answer(self):
        self._currentQ["options"].append(self._answer.get())
        if self._accept_typos:
            self._currentQ["STH"] += 1
        self._next_question()
    
    def _remove_answer(self):
        self._currentQ["removed"].append(self._answer.get())
        self._next_question()

    def _settings_screen(self, value=None):
        self._clear_screen()
        self._make_label("Settings", fontsize=24, pady=25)
        
        self._make_label("How often do you want to be prompted for alternative answers?", pady=2, padx=45, anchor='w')
        self._make_seg_button(["Never", "Sometimes", "Always"], self._level, anchor='w', pady=5, command=self._settings_screen)
        if self._level.get() == "Sometimes":
            self._make_label("How frequent?", pady=2, padx=45, anchor='w')
            self._make_slider(self._freq, anchor='w')

        self._make_check("Accept spelling errors?", var=self._accept_typos, anchor='w')

        self._make_button("Return", self._start_screen if self._current_deck is None else self._next_question)

    def _correct(self):
        if self._accept_typos.get():
            if self._answer.get() in self._currentQ["removed"]:
                return False
            return min(damerau_levenshtein(self._answer.get(), opt) for opt in self._currentQ["options"]) <= self._currentQ["STH"]
        else:
            return self._answer.get().upper() == self._currentQ["answer"].upper()
            

if __name__ == "__main__":
    sys = System("Learning", "cards.json")
    sys.mainloop()