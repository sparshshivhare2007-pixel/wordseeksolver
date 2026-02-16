import json
import re
from typing import List, Set, Dict
from telethon import TelegramClient, events
from config import API_ID, API_HASH, START_WORD, WORDLIST_FILE, GUESS_DELAY, AUTO_LOOP

class WordleSolver:
    def __init__(self, session_name: str):
        self.client = TelegramClient(session_name, API_ID, API_HASH)
        self.possible: List[str] = []
        self.used_words: Set[str] = set()
        self.last_guess: str = None
        self.game_active = False
        self.chat_id = None
        self.greens: Dict[int, str] = {}
        self.yellows: Dict[str, Set[int]] = {}
        self.grays: Set[str] = set()

    async def start(self):
        await self.client.start()
        @self.client.on(events.NewMessage(outgoing=True))
        async def outgoing_handler(event):
            if event.raw_text.lower().strip().startswith("/new") and self.chat_id is None:
                self.chat_id = event.chat_id
                print(f"[LOCKED] chat = {self.chat_id}")

        @self.client.on(events.NewMessage(incoming=True))
        async def game_listener(event):
            await self._handle_game(event)

    async def _handle_game(self, event):
        if self.chat_id is None or event.chat_id != self.chat_id:
            return

        sender = await event.get_sender()
        if not sender or not sender.bot:
            return

        raw = event.raw_text
        text = raw.lower()
        print(f"[BOT] {raw}")

        # GAME START
        if "game started" in text:
            await self._start_new_game()
            return

        # WIN DETECTION
        if any(msg in text for msg in ["congrats", "guessed it correctly", "start with /new"]):
            print("[WIN] detected → auto new")
            if AUTO_LOOP:
                await asyncio.sleep(2)
                await self.client.send_message(self.chat_id, "/new")
            return

        # HINT HANDLING
        if self.game_active and any(e in text for e in ["🟩", "🟨", "🟥"]):
            emojis = re.findall("[🟩🟨🟥]", text)
            if len(emojis) >= 5 and self.last_guess:
                hint = "".join(emojis[-5:])
                self._update_constraints(self.last_guess, hint)
                
                if hint == "🟩🟩🟩🟩🟩":
                    print("[WIN] emoji solved")
                    if AUTO_LOOP:
                        await asyncio.sleep(2)
                        await self.client.send_message(self.chat_id, "/new@WordSeekBot")
                    return

                self._make_next_guess()

    def _start_new_game(self):
        self.game_active = True
        self.used_words.clear()
        self.greens.clear()
        self.yellows.clear()
        self.grays.clear()

        with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
            self.possible = [w for w in json.load(f) if len(w) == 5]

        asyncio.create_task(self._send_first_guess())

    async def _send_first_guess(self):
        await asyncio.sleep(GUESS_DELAY)
        await self.client.send_message(self.chat_id, START_WORD)
        self.last_guess = START_WORD
        self.used_words.add(START_WORD)
        print(f"[START] {START_WORD}")

    def _update_constraints(self, word: str, hint: str):
        local_present = set()
        local_greens = {}

        for i, sym in enumerate(hint):
            l = word[i]
            if sym == "🟩":
                local_greens[i] = l
                local_present.add(l)
            elif sym == "🟨":
                self.yellows.setdefault(l, set()).add(i)
                local_present.add(l)

        self.greens = local_greens

        for i, sym in enumerate(hint):
            l = word[i]
            if sym == "🟥" and l not in local_present:
                self.grays.add(l)

    def _valid(self, word: str) -> bool:
        for i, l in self.greens.items():
            if word[i] != l:
                return False

        for l, bad_pos in self.yellows.items():
            if l not in word:
                return False
            if any(word[i] == l for i in bad_pos):
                return False

        if any(l in word for l in self.grays):
            return False
        return True

    def _best_guess(self) -> str:
        filtered = [w for w in self.possible if self._valid(w) and w not in self.used_words]
        if not filtered:
            return None
        return max(filtered, key=lambda w: len(set(w)))

    def _make_next_guess(self):
        self.possible = [w for w in self.possible if self._valid(w) and w not in self.used_words]
        guess = self._best_guess()

        if not guess:
            print("[STOP] no possible words")
            self.game_active = False
            return

        self.used_words.add(guess)
        self.last_guess = guess
        asyncio.create_task(self._send_guess(guess))

    async def _send_guess(self, guess: str):
        await asyncio.sleep(GUESS_DELAY)
        await self.client.send_message(self.chat_id, guess)
        print(f"[GUESS] {guess}")

    async def stop(self):
        await self.client.disconnect()
