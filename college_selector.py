import pygame
import requests
import sys

class CollegeSelector:
    def __init__(self):
        pygame.init()
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (240, 240, 240)
        self.DARK_GRAY = (64, 64, 64)
        self.BLUE = (41, 128, 185)
        self.GREEN = (39, 174, 96)
        self.RED = (231, 76, 60)
        self.ORANGE = (230, 126, 34)
        self.PURPLE = (142, 68, 173)

        # Fonts
        self.FONT_LARGE = pygame.font.SysFont('Arial', 32, bold=True)
        self.FONT_MEDIUM = pygame.font.SysFont('Arial', 24)
        self.FONT_SMALL = pygame.font.SysFont('Arial', 18)
        self.FONT_TINY = pygame.font.SysFont('Arial', 14)

        # API Configuration
        self.API_KEY = "R6LQsOSW7UcAfY0TbifD68coA5Ue42rGY7gAYAVE"
        self.BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"

        # Screen setup
        self.WIDTH, self.HEIGHT = 1200, 800
        self.SCREEN = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Choose Your College")

        # State variables
        self.colleges = []
        self.selected_college = None
        self.loading = False
        self.error_message = ""
        self.scroll_offset = 0.0
        self.scroll_velocity = 0.0

    class Button:
        def __init__(self, x, y, width, height, text, color, text_color=(255, 255, 255), font=None, border_radius=8):
            self.rect = pygame.Rect(x, y, width, height)
            self.text = text
            self.color = color
            self.text_color = text_color
            self.font = font
            self.border_radius = border_radius
            self.hover = False

        def draw(self, surface):
            color = tuple(min(255, c + 20) for c in self.color) if self.hover else self.color
            pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
            pygame.draw.rect(surface, (64, 64, 64), self.rect, 2, border_radius=self.border_radius)
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

        def is_clicked(self, pos):
            return self.rect.collidepoint(pos)
        
        def update_hover(self, pos):
            self.hover = self.rect.collidepoint(pos)

    class SearchBar:
        def __init__(self, x, y, width, height):
            self.rect = pygame.Rect(x, y, width, height)
            self.text = ""
            self.active = False
            self.cursor_visible = True
            self.cursor_timer = 0

        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.active = self.rect.collidepoint(event.pos)
            elif event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    return True
                elif len(self.text) < 30:
                    self.text += event.unicode
            return False

        def update(self, dt):
            self.cursor_timer += dt
            if self.cursor_timer >= 500:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

        def draw(self, surface):
            color = (255, 255, 255) if self.active else (240, 240, 240)
            pygame.draw.rect(surface, color, self.rect, border_radius=8)
            pygame.draw.rect(surface, (64, 64, 64) if self.active else (128, 128, 128), self.rect, 2, border_radius=8)

            display_text = self.text if self.text or self.active else "Search colleges..."
            text_color = (0, 0, 0) if self.text or self.active else (128, 128, 128)

            text_surf = pygame.font.SysFont('Arial', 24).render(display_text, True, text_color)
            surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))

            if self.active and self.cursor_visible:
                cursor_x = self.rect.x + 10 + text_surf.get_width()
                pygame.draw.line(surface, (0, 0, 0), (cursor_x, self.rect.y + 8), (cursor_x, self.rect.y + self.rect.height - 8), 2)

    class CollegeCard:
        def __init__(self, x, y, width, height, college_data):
            self.rect = pygame.Rect(x, y, width, height)
            self.college_data = college_data
            self.hover = False

        def draw(self, surface, selected=False):
            color = (230, 245, 255) if self.hover else (255, 255, 255)
            if selected:
                color = (200, 255, 200)

            pygame.draw.rect(surface, color, self.rect, border_radius=12)
            border_color = (41, 128, 185) if selected else ((230, 126, 34) if self.hover else (240, 240, 240))
            pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=12)

            name = self.college_data.get('school.name', 'Unknown College')
            name = name[:42] + "..." if len(name) > 45 else name
            name_surf = pygame.font.SysFont('Arial', 24).render(name, True, (0, 0, 0))
            surface.blit(name_surf, (self.rect.x + 20, self.rect.y + 15))

            state = self.college_data.get('school.state', 'N/A')
            city = self.college_data.get('school.city', 'N/A')
            location_surf = pygame.font.SysFont('Arial', 18).render(f"{city}, {state}", True, (128, 128, 128))
            surface.blit(location_surf, (self.rect.x + 20, self.rect.y + 45))

            left_col_x = self.rect.x + 20
            right_col_x = self.rect.x + self.rect.width // 2 + 10

            size = self.college_data.get('latest.student.size')
            if size:
                size_surf = pygame.font.SysFont('Arial', 18).render(f"Students: {size:,}", True, (0, 0, 0))
                surface.blit(size_surf, (left_col_x, self.rect.y + 75))

            admission_rate = self.college_data.get('latest.admissions.admission_rate.overall')
            if admission_rate is not None:
                admission_surf = pygame.font.SysFont('Arial', 18).render(f"Admission: {admission_rate:.0%}", True, (0, 0, 0))
                surface.blit(admission_surf, (left_col_x, self.rect.y + 100))

            earnings = self.college_data.get('latest.earnings.10_yrs_after_entry.median')
            if earnings:
                label = pygame.font.SysFont('Arial', 18).render("10-Year Median Salary:", True, (128, 128, 128))
                surface.blit(label, (right_col_x, self.rect.y + 75))
                color = (39, 174, 96) if earnings >= 60000 else (230, 126, 34) if earnings >= 45000 else (231, 76, 60)
                earnings_surf = pygame.font.SysFont('Arial', 24).render(f"${earnings:,}/year", True, color)
                surface.blit(earnings_surf, (right_col_x, self.rect.y + 95))

        def is_clicked(self, pos):
            return self.rect.collidepoint(pos)
        
        def update_hover(self, pos):
            self.hover = self.rect.collidepoint(pos)

    def fetch_colleges(self, search_query=""):
        self.loading = True
        self.error_message = ""
        try:
            params = {
                'api_key': self.API_KEY,
                'fields': 'id,school.name,school.state,school.city,latest.student.size,latest.earnings.10_yrs_after_entry.median,latest.admissions.admission_rate.overall',
                'per_page': 20,
                'sort': 'latest.earnings.10_yrs_after_entry.median:desc',
                'latest.earnings.10_yrs_after_entry.median__not': 'null',
                'latest.student.size__range': '1000..'
            }

            if search_query:
                if search_query.upper() in ['UC', 'UNIVERSITY OF CALIFORNIA']:
                    params['school.name'] = 'University of California'
                elif search_query.upper() in ['CSU', 'CALIFORNIA STATE', 'CAL STATE']:
                    params['school.name'] = 'California State University'
                else:
                    params['school.name'] = search_query
            else:
                params['school.name'] = 'California'

            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.loading = False

            results = data.get('results', [])
            uc_csu_schools = [s for s in results if 'university of california' in s.get('school.name', '').lower() or 'california state university' in s.get('school.name', '').lower()]
            others = [s for s in results if s not in uc_csu_schools]

            return uc_csu_schools + others[:10]

        except Exception as e:
            self.loading = False
            self.error_message = f"Error loading colleges: {str(e)}"
            return []

    def run(self):
        back_button = self.Button(50, 50, 100, 50, "← Back", self.GRAY, font=self.FONT_MEDIUM)
        uc_button = self.Button(480, 120, 140, 50, "UC Schools", self.BLUE, font=self.FONT_MEDIUM)
        csu_button = self.Button(640, 120, 140, 50, "CSU Schools", self.ORANGE, font=self.FONT_MEDIUM)
        all_button = self.Button(800, 120, 140, 50, "All CA", self.GREEN, font=self.FONT_MEDIUM)
        select_button = self.Button(self.WIDTH//2 - 100, self.HEIGHT - 80, 200, 50, "Continue →", self.GREEN, font=self.FONT_MEDIUM)

        search_bar = self.SearchBar(50, 120, 380, 50)
        college_cards = []
        card_height = 140

        self.colleges = self.fetch_colleges()
        clock = pygame.time.Clock()
        running = True

        while running:
            dt = clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()
            self.SCREEN.fill(self.WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if search_bar.handle_event(event):
                    self.colleges = self.fetch_colleges(search_bar.text)
                    self.scroll_offset = 0
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.is_clicked(event.pos): return None
                    elif uc_button.is_clicked(event.pos): self.colleges = self.fetch_colleges("University of California"); self.scroll_offset = 0
                    elif csu_button.is_clicked(event.pos): self.colleges = self.fetch_colleges("California State University"); self.scroll_offset = 0
                    elif all_button.is_clicked(event.pos): self.colleges = self.fetch_colleges(); self.scroll_offset = 0
                    elif select_button.is_clicked(event.pos) and self.selected_college: return self.selected_college
                    for card in college_cards:
                        if card.is_clicked(event.pos): self.selected_college = card.college_data; break
                if event.type == pygame.MOUSEWHEEL:
                    self.scroll_velocity += -event.y * 10

            # Update scroll with proper bounds checking
            self.scroll_offset += self.scroll_velocity
            self.scroll_velocity *= 0.85

            # Calculate proper scroll bounds
            card_height = 140
            card_spacing = 10
            total_card_height = len(self.colleges) * (card_height + card_spacing)
            visible_area_height = self.HEIGHT - 320  # Room for header + continue panel
            max_scroll = max(0, total_card_height - visible_area_height)

            # Clamp scroll offset and stop velocity if hitting bounds
            if self.scroll_offset < 0:
                self.scroll_offset = 0
                self.scroll_velocity = 0
            elif self.scroll_offset > max_scroll:
                self.scroll_offset = max_scroll
                self.scroll_velocity = 0

            # Stop momentum if it's too small
            if abs(self.scroll_velocity) < 0.1:
                self.scroll_velocity = 0

            # Update UI elements
            back_button.update_hover(mouse_pos)
            uc_button.update_hover(mouse_pos)
            csu_button.update_hover(mouse_pos)
            all_button.update_hover(mouse_pos)
            select_button.update_hover(mouse_pos)
            search_bar.update(dt)

            # Draw UI elements
            title = self.FONT_LARGE.render("Choose Your College", True, self.BLACK)
            title_rect = title.get_rect(center=(self.WIDTH//2, 35))
            self.SCREEN.blit(title, title_rect)

            back_button.draw(self.SCREEN)
            search_bar.draw(self.SCREEN)

            filter_label = self.FONT_SMALL.render("Quick Filters:", True, self.GRAY)
            self.SCREEN.blit(filter_label, (480, 100))
            uc_button.draw(self.SCREEN)
            csu_button.draw(self.SCREEN)
            all_button.draw(self.SCREEN)

            if self.loading:
                loading_text = self.FONT_MEDIUM.render("Loading colleges...", True, self.GRAY)
                self.SCREEN.blit(loading_text, (self.WIDTH//2 - 100, self.HEIGHT//2))
            elif self.error_message:
                error_text = self.FONT_SMALL.render(self.error_message, True, self.RED)
                self.SCREEN.blit(error_text, (50, self.HEIGHT//2))
            else:
                # Set clipping rectangle to prevent cards from drawing over the header area
                clip_top = 190  # Just above where cards should start
                clip_bottom = self.HEIGHT - 140 if self.selected_college else self.HEIGHT - 20
                clip_rect = pygame.Rect(0, clip_top, self.WIDTH, clip_bottom - clip_top)
                self.SCREEN.set_clip(clip_rect)
                
                college_cards = []
                for i, college in enumerate(self.colleges):
                    card_y = 200 + i * (card_height + 10) - self.scroll_offset
                    # Allow partial cards to show - only skip if completely out of bounds
                    if card_y > clip_bottom or card_y + card_height < clip_top:
                        continue
                    card = self.CollegeCard(50, card_y, self.WIDTH - 100, card_height, college)
                    college_cards.append(card)
                    selected = self.selected_college and self.selected_college.get('id') == college.get('id')
                    card.draw(self.SCREEN, selected)

                # Remove clipping
                self.SCREEN.set_clip(None)

                # Update hover states for visible cards
                for card in college_cards:
                    card.update_hover(mouse_pos)

            if self.selected_college:
                pygame.draw.rect(self.SCREEN, self.LIGHT_GRAY, (0, self.HEIGHT - 120, self.WIDTH, 120))
                pygame.draw.line(self.SCREEN, self.GRAY, (0, self.HEIGHT - 120), (self.WIDTH, self.HEIGHT - 120), 2)

                name_text = self.FONT_MEDIUM.render(f"Selected: {self.selected_college.get('school.name', 'Unknown')}", True, self.BLACK)
                self.SCREEN.blit(name_text, (50, self.HEIGHT - 100))

                earnings = self.selected_college.get('latest.earnings.10_yrs_after_entry.median')
                if earnings:
                    earnings_text = self.FONT_MEDIUM.render(f"Expected 10-year median salary: ${earnings:,}", True, self.GREEN)
                    self.SCREEN.blit(earnings_text, (50, self.HEIGHT - 70))

                select_button.draw(self.SCREEN)

            pygame.display.flip()