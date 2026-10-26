"""
defense_defenders/ui/algorithm_lab.py

This module implements the Algorithm Lab educational inspection panel.
Toggled via the 'L' key or the HUD button, it visualizes the live data structures
(FIFO Queue contents, Max-Heap threat rankings, Greedy distance calculations)
in real time, along with theoretical time/space complexities and Viva Q&A notes.

Modules that interact with this:
- defense/targeting.py (supplies get_inspection_stats)
- game/game_manager.py (handles open/close toggle)
- ui/buttons.py (uses Button for tab selection and close)
"""

import pygame
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED,
    TARGET_MODE_QUEUE,
    TARGET_MODE_HEAP,
    TARGET_MODE_GREEDY,
)
from ui.buttons import Button


class AlgorithmLabPanel:
    """Interactive educational HUD panel for inspecting Defense data structures in real-time."""

    TAB_QUEUE = "QUEUE"
    TAB_HEAP = "HEAP"
    TAB_GREEDY = "GREEDY"
    TAB_VIVA = "VIVA"

    def __init__(self, on_close=None):
        self.is_open = False
        self.active_tab = self.TAB_QUEUE
        self.on_close = on_close

        # Panel dimensions
        self.width = 820
        self.height = 540
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Tab buttons
        tab_y = self.y + 55
        self.btn_tab_q = Button(self.x + 25, tab_y, 140, 34, text="1: FIFO Queue", font_size=12,
                                callback=lambda: self.set_tab(self.TAB_QUEUE))
        self.btn_tab_h = Button(self.x + 175, tab_y, 140, 34, text="2: Max-Heap", font_size=12,
                                callback=lambda: self.set_tab(self.TAB_HEAP))
        self.btn_tab_g = Button(self.x + 325, tab_y, 140, 34, text="3: Greedy", font_size=12,
                                callback=lambda: self.set_tab(self.TAB_GREEDY))
        self.btn_tab_v = Button(self.x + 475, tab_y, 140, 34, text="Viva Q&A Notes", font_size=12,
                                bg_color=(90, 50, 130), hover_color=(120, 70, 170),
                                callback=lambda: self.set_tab(self.TAB_VIVA))

        # Close button
        self.btn_close = Button(self.x + self.width - 50, self.y + 14, 34, 30, text="X",
                                font_size=14, bg_color=(180, 40, 40), hover_color=(220, 60, 60),
                                callback=self.close)

    def toggle(self) -> None:
        """Toggle panel visibility."""
        self.is_open = not self.is_open

    def close(self) -> None:
        """Close panel."""
        self.is_open = False
        if self.on_close:
            self.on_close()

    def set_tab(self, tab_name: str) -> None:
        """Switch active inspection tab."""
        self.active_tab = tab_name

    def handle_event(self, event) -> bool:
        """Consume UI events when panel is open."""
        if not self.is_open:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            self.close()
            return True

        for btn in (self.btn_close, self.btn_tab_q, self.btn_tab_h, self.btn_tab_g, self.btn_tab_v):
            if btn.handle_event(event):
                return True

        # Consume clicks within panel background to avoid firing game interactions
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True

        return False

    def update(self, mouse_pos) -> None:
        """Update button hover states."""
        if not self.is_open:
            return
        for btn in (self.btn_close, self.btn_tab_q, self.btn_tab_h, self.btn_tab_g, self.btn_tab_v):
            btn.update_hover(mouse_pos)

    def draw(self, surface: pygame.Surface, font_cache: dict, targeting_dispatcher,
             tower, alive_enemies) -> None:
        """Render panel overlay."""
        if not self.is_open:
            return

        # Semi-transparent dark background backdrop
        backdrop = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        backdrop.fill((10, 18, 30, 180))
        surface.blit(backdrop, (0, 0))

        # Main panel window
        pygame.draw.rect(surface, (22, 34, 52), self.rect, border_radius=14)
        pygame.draw.rect(surface, (0, 229, 255), self.rect, width=2, border_radius=14)

        # Header Title
        title_font = font_cache.get(20, pygame.font.SysFont("arial", 20, bold=True))
        title_surf = title_font.render("ALGORITHM LAB - LIVE Defense INSPECTION", True, (0, 229, 255))
        surface.blit(title_surf, (self.x + 25, self.y + 18))

        # Highlight active tab
        self.btn_tab_q.is_selected = (self.active_tab == self.TAB_QUEUE)
        self.btn_tab_h.is_selected = (self.active_tab == self.TAB_HEAP)
        self.btn_tab_g.is_selected = (self.active_tab == self.TAB_GREEDY)
        self.btn_tab_v.is_selected = (self.active_tab == self.TAB_VIVA)

        self.btn_tab_q.draw(surface, font_cache)
        self.btn_tab_h.draw(surface, font_cache)
        self.btn_tab_g.draw(surface, font_cache)
        self.btn_tab_v.draw(surface, font_cache)
        self.btn_close.draw(surface, font_cache)

        # Tab content container
        content_rect = pygame.Rect(self.x + 25, self.y + 100, self.width - 50, self.height - 120)
        pygame.draw.rect(surface, (14, 22, 36), content_rect, border_radius=10)
        pygame.draw.rect(surface, (40, 60, 90), content_rect, width=1, border_radius=10)

        # Query live stats from targeting dispatcher
        stats = targeting_dispatcher.get_inspection_stats(tower.x, tower.y, tower.range, alive_enemies)

        # Render corresponding tab view
        if self.active_tab == self.TAB_QUEUE:
            self._draw_queue_tab(surface, font_cache, content_rect, stats)
        elif self.active_tab == self.TAB_HEAP:
            self._draw_heap_tab(surface, font_cache, content_rect, stats)
        elif self.active_tab == self.TAB_GREEDY:
            self._draw_greedy_tab(surface, font_cache, content_rect, stats)
        elif self.active_tab == self.TAB_VIVA:
            self._draw_viva_tab(surface, font_cache, content_rect)

    def _draw_queue_tab(self, surface: pygame.Surface, font_cache: dict, rect: pygame.Rect, stats: dict) -> None:
        """Render FIFO Queue details and live slot inspection."""
        f_head = font_cache.get(16, pygame.font.SysFont("arial", 16, bold=True))
        f_body = font_cache.get(13, pygame.font.SysFont("arial", 13))
        f_mono = font_cache.get(13, pygame.font.SysFont("courier", 13))

        # Title & Theory
        surface.blit(f_head.render("Data Structure: FIFO Queue (First-In, First-Out)", True, (255, 215, 0)),
                     (rect.x + 18, rect.y + 16))
        surface.blit(f_body.render(f"Targeting Logic: {stats.get('rule', '')}", True, COLOR_TEXT_WHITE),
                     (rect.x + 18, rect.y + 40))
        surface.blit(f_mono.render(f"Time Complexity: {stats.get('complexity', '')}", True, (130, 220, 255)),
                     (rect.x + 18, rect.y + 62))
        surface.blit(f_body.render("Space Complexity: O(n) | Implementation: Manual array with head pointer", True, COLOR_TEXT_MUTED),
                     (rect.x + 18, rect.y + 84))

        # Live inspection box
        insp_rect = pygame.Rect(rect.x + 18, rect.y + 115, rect.width - 36, 280)
        pygame.draw.rect(surface, (20, 30, 48), insp_rect, border_radius=8)
        pygame.draw.rect(surface, (45, 70, 105), insp_rect, width=1, border_radius=8)

        surface.blit(f_head.render(f"Live Queue Contents (Total In Arena: {stats.get('queue_size', 0)}):", True, COLOR_TEXT_WHITE),
                     (insp_rect.x + 14, insp_rect.y + 12))

        items = stats.get("queue_items", [])
        if not items:
            surface.blit(f_body.render("Queue is currently EMPTY (no active enemies).", True, (160, 175, 195)),
                         (insp_rect.x + 14, insp_rect.y + 44))
        else:
            # Table headers
            headers = ["Order", "Spawn ID", "Enemy Type", "Current HP", "In Range? (Targetable)"]
            col_x = [insp_rect.x + 14, insp_rect.x + 80, insp_rect.x + 180, insp_rect.x + 320, insp_rect.x + 460]
            for h, cx in zip(headers, col_x):
                surface.blit(f_body.render(h, True, (0, 229, 255)), (cx, insp_rect.y + 42))

            pygame.draw.line(surface, (50, 75, 110), (insp_rect.x + 10, insp_rect.y + 64),
                             (insp_rect.right - 10, insp_rect.y + 64), 1)

            for i, itm in enumerate(items[:7]):
                row_y = insp_rect.y + 72 + (i * 26)
                is_first_in_range = (i == 0 and itm["in_range"]) or (itm["in_range"] and itm["id"] == getattr(stats.get("target"), "id", -1))
                row_col = (76, 175, 80) if is_first_in_range else COLOR_TEXT_WHITE

                tag = "HEAD -> 1st" if i == 0 else f"#{itm['pos']}"
                surface.blit(f_mono.render(tag, True, (255, 215, 0) if i == 0 else (180, 195, 215)), (col_x[0], row_y))
                surface.blit(f_mono.render(f"Enemy #{itm['id']}", True, row_col), (col_x[1], row_y))
                surface.blit(f_body.render(itm['type'].capitalize(), True, row_col), (col_x[2], row_y))
                surface.blit(f_mono.render(f"{itm['hp']} HP", True, row_col), (col_x[3], row_y))

                range_str = "YES (PRIMARY TARGET)" if is_first_in_range else ("YES" if itm["in_range"] else "NO (Out of range)")
                range_col = (76, 175, 80) if itm["in_range"] else (220, 80, 80)
                surface.blit(f_body.render(range_str, True, range_col), (col_x[4], row_y))

    def _draw_heap_tab(self, surface: pygame.Surface, font_cache: dict, rect: pygame.Rect, stats: dict) -> None:
        """Render Binary Max-Heap details and top threat score calculations."""
        f_head = font_cache.get(16, pygame.font.SysFont("arial", 16, bold=True))
        f_body = font_cache.get(13, pygame.font.SysFont("arial", 13))
        f_mono = font_cache.get(13, pygame.font.SysFont("courier", 13))

        surface.blit(f_head.render("Data Structure: Binary Max-Heap Priority Queue", True, (255, 215, 0)),
                     (rect.x + 18, rect.y + 16))
        surface.blit(f_body.render("Formula: Threat = (Dmg * 3) + (Spd * 1.5) + (1000 / (Dist + 1)) + TypeBonus - (HP * 0.05)", True, COLOR_TEXT_WHITE),
                     (rect.x + 18, rect.y + 40))
        surface.blit(f_mono.render(f"Time Complexity: {stats.get('complexity', '')}", True, (130, 220, 255)),
                     (rect.x + 18, rect.y + 62))
        surface.blit(f_body.render("Manual Implementation: Zero heapq imports. O(n) Floyd's bottom-up build_heap.", True, COLOR_TEXT_MUTED),
                     (rect.x + 18, rect.y + 84))

        # Live inspection box
        insp_rect = pygame.Rect(rect.x + 18, rect.y + 115, rect.width - 36, 280)
        pygame.draw.rect(surface, (20, 30, 48), insp_rect, border_radius=8)
        pygame.draw.rect(surface, (45, 70, 105), insp_rect, width=1, border_radius=8)

        surface.blit(f_head.render("Max-Heap Root & Top Threat Elements:", True, COLOR_TEXT_WHITE),
                     (insp_rect.x + 14, insp_rect.y + 12))

        threats = stats.get("top_threats", [])
        if not threats:
            surface.blit(f_body.render("Heap is currently EMPTY.", True, (160, 175, 195)),
                         (insp_rect.x + 14, insp_rect.y + 44))
        else:
            headers = ["Heap Pos", "Threat Score", "Archetype", "Distance", "Dmg/Spd", "Target Status"]
            col_x = [insp_rect.x + 14, insp_rect.x + 100, insp_rect.x + 230, insp_rect.x + 350, insp_rect.x + 470, insp_rect.x + 570]
            for h, cx in zip(headers, col_x):
                surface.blit(f_body.render(h, True, (0, 229, 255)), (cx, insp_rect.y + 42))

            pygame.draw.line(surface, (50, 75, 110), (insp_rect.x + 10, insp_rect.y + 64),
                             (insp_rect.right - 10, insp_rect.y + 64), 1)

            for i, itm in enumerate(threats[:6]):
                row_y = insp_rect.y + 72 + (i * 26)
                is_selected = itm["in_range"] and (i == 0 or itm["id"] == getattr(stats.get("target"), "id", -1))
                pos_label = "ROOT [0]" if i == 0 else f"Child [{i}]"

                surface.blit(f_mono.render(pos_label, True, (255, 215, 0) if i == 0 else COLOR_TEXT_MUTED), (col_x[0], row_y))
                surface.blit(f_mono.render(f"{itm['threat']:.1f}", True, (255, 100, 100) if i == 0 else COLOR_TEXT_WHITE), (col_x[1], row_y))
                surface.blit(f_body.render(itm['type'].capitalize(), True, COLOR_TEXT_WHITE), (col_x[2], row_y))
                surface.blit(f_mono.render(f"{itm['dist']} px", True, COLOR_TEXT_WHITE), (col_x[3], row_y))
                surface.blit(f_mono.render(f"{itm['dmg']} / {itm['spd']}", True, COLOR_TEXT_WHITE), (col_x[4], row_y))

                status_str = "SELECTED" if is_selected else ("In Range" if itm["in_range"] else "Out of Range")
                status_col = (76, 175, 80) if is_selected else ((120, 200, 255) if itm["in_range"] else (220, 80, 80))
                surface.blit(f_body.render(status_str, True, status_col), (col_x[5], row_y))

    def _draw_greedy_tab(self, surface: pygame.Surface, font_cache: dict, rect: pygame.Rect, stats: dict) -> None:
        """Render Greedy Nearest-Enemy details and Euclidean distance proofs."""
        f_head = font_cache.get(16, pygame.font.SysFont("arial", 16, bold=True))
        f_body = font_cache.get(13, pygame.font.SysFont("arial", 13))
        f_mono = font_cache.get(13, pygame.font.SysFont("courier", 13))

        surface.blit(f_head.render("Algorithm: Greedy Nearest Neighbor (Local Minimum)", True, (255, 215, 0)),
                     (rect.x + 18, rect.y + 16))
        surface.blit(f_body.render("Choice Heuristic: argmin( Euclidean_Distance(tower, enemy) ) for alive enemies in range", True, COLOR_TEXT_WHITE),
                     (rect.x + 18, rect.y + 40))
        surface.blit(f_mono.render("Optimization: Compares dx^2 + dy^2 (avoids costly sqrt because f(x)=x^2 is strictly monotonic)", True, (130, 220, 255)),
                     (rect.x + 18, rect.y + 62))
        surface.blit(f_body.render("Tradeoff: Local optimum doesn't guarantee global survival (can ignore lethal high-damage bosses).", True, COLOR_TEXT_MUTED),
                     (rect.x + 18, rect.y + 84))

        insp_rect = pygame.Rect(rect.x + 18, rect.y + 115, rect.width - 36, 280)
        pygame.draw.rect(surface, (20, 30, 48), insp_rect, border_radius=8)
        pygame.draw.rect(surface, (45, 70, 105), insp_rect, width=1, border_radius=8)

        surface.blit(f_head.render("Live Distance Rankings (Closest to Furthest):", True, COLOR_TEXT_WHITE),
                     (insp_rect.x + 14, insp_rect.y + 12))

        dists = stats.get("nearest_list", [])
        if not dists:
            surface.blit(f_body.render("No active enemies in arena.", True, (160, 175, 195)),
                         (insp_rect.x + 14, insp_rect.y + 44))
        else:
            headers = ["Rank", "Enemy Type", "Distance (px)", "Squared Dist (dx^2+dy^2)", "Greedy Target?"]
            col_x = [insp_rect.x + 14, insp_rect.x + 100, insp_rect.x + 250, insp_rect.x + 400, insp_rect.x + 600]
            for h, cx in zip(headers, col_x):
                surface.blit(f_body.render(h, True, (0, 229, 255)), (cx, insp_rect.y + 42))

            pygame.draw.line(surface, (50, 75, 110), (insp_rect.x + 10, insp_rect.y + 64),
                             (insp_rect.right - 10, insp_rect.y + 64), 1)

            for i, itm in enumerate(dists[:6]):
                row_y = insp_rect.y + 72 + (i * 26)
                is_greedy_choice = itm["in_range"] and i == 0
                row_col = (76, 175, 80) if is_greedy_choice else COLOR_TEXT_WHITE

                surface.blit(f_mono.render(f"#{i + 1}", True, (255, 215, 0) if i == 0 else COLOR_TEXT_MUTED), (col_x[0], row_y))
                surface.blit(f_body.render(itm['type'].capitalize(), True, row_col), (col_x[1], row_y))
                surface.blit(f_mono.render(f"{itm['dist']} px", True, row_col), (col_x[2], row_y))
                surface.blit(f_mono.render(str(itm['dist_sq']), True, row_col), (col_x[3], row_y))

                choice_str = "SELECTED (LOCAL OPT)" if is_greedy_choice else ("In Range" if itm["in_range"] else "Out of Range")
                choice_col = (76, 175, 80) if is_greedy_choice else ((120, 200, 255) if itm["in_range"] else (220, 80, 80))
                surface.blit(f_body.render(choice_str, True, choice_col), (col_x[4], row_y))

    def _draw_viva_tab(self, surface: pygame.Surface, font_cache: dict, rect: pygame.Rect) -> None:
        """Render high-yield Viva Voce examination questions and answers."""
        f_q = font_cache.get(14, pygame.font.SysFont("arial", 14, bold=True))
        f_a = font_cache.get(12, pygame.font.SysFont("arial", 12))

        qa_list = [
            ("Q1: Why choose a Binary Max-Heap instead of a Sorted Array for Priority Queue?",
             "A1: In a sorted array, extract-max is O(1) but insertion takes O(n) due to element shifting. In a heap,\n"
             "    both insert and extract-max are O(log n). Furthermore, Floyd's build_heap runs in O(n) total time."),
            ("Q2: Why is Greedy Nearest-Enemy not always globally optimal in tower defense?",
             "A2: Greedy picks the locally closest target (e.g. low-damage scout 50px away) while ignoring a\n"
             "    catastrophic high-threat boss 55px away. Local optimization can cause total defeat."),
            ("Q3: Why use squared Euclidean distance (dx^2 + dy^2) for distance comparisons?",
             "A3: Because f(x) = x^2 is strictly increasing for non-negative numbers, a^2 < b^2 <===> a < b.\n"
             "    Omitting math.sqrt() eliminates costly square root CPU instructions on every tick."),
            ("Q4: Why does our FIFO Queue use an integer head pointer instead of list.pop(0)?",
             "A4: list.pop(0) is an O(n) operation in Python because the entire contiguous memory block shifts left.\n"
             "    A head pointer gives O(1) dequeue with periodic amortized compaction."),
        ]

        curr_y = rect.y + 14
        for q, a in qa_list:
            surface.blit(f_q.render(q, True, (255, 215, 0)), (rect.x + 18, curr_y))
            curr_y += 20
            for line in a.split("\n"):
                surface.blit(f_a.render(line, True, COLOR_TEXT_WHITE), (rect.x + 28, curr_y))
                curr_y += 18
            curr_y += 10
