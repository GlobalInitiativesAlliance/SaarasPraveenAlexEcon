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
        done_button = self.Button(960, 120, 140, 50, "Done", self.GREEN, font=self.FONT_MEDIUM)

        self.colleges = self.fetch_colleges()
        college_cards = []

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
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.is_clicked(event.pos):
                        return None
                    elif uc_button.is_clicked(event.pos):
                        self.colleges = self.fetch_colleges("University of California")
                        self.selected_college = None
                    elif csu_button.is_clicked(event.pos):
                        self.colleges = self.fetch_colleges("California State University")
                        self.selected_college = None
                    elif all_button.is_clicked(event.pos):
                        self.colleges = self.fetch_colleges()
                        self.selected_college = None
                    elif done_button.is_clicked(event.pos) and self.selected_college:
                        return self.selected_college
                    else:
                        for card in college_cards:
                            if card["rect"].collidepoint(event.pos):
                                self.selected_college = card["data"]

            back_button.update_hover(mouse_pos)
            uc_button.update_hover(mouse_pos)
            csu_button.update_hover(mouse_pos)
            all_button.update_hover(mouse_pos)
            done_button.update_hover(mouse_pos)

            title = self.FONT_LARGE.render("Choose Your College", True, self.BLACK)
            title_rect = title.get_rect(center=(self.WIDTH//2, 35))
            self.SCREEN.blit(title, title_rect)

            back_button.draw(self.SCREEN)
            uc_button.draw(self.SCREEN)
            csu_button.draw(self.SCREEN)
            all_button.draw(self.SCREEN)
            done_button.draw(self.SCREEN)

            instruction = self.FONT_SMALL.render("Click on a college to select it, then click 'Done'", True, self.GRAY)
            instruction_rect = instruction.get_rect(center=(self.WIDTH//2, 180))
            self.SCREEN.blit(instruction, instruction_rect)

            if self.loading:
                loading_text = self.FONT_MEDIUM.render("Loading colleges...", True, self.GRAY)
                self.SCREEN.blit(loading_text, (self.WIDTH//2 - 100, self.HEIGHT//2))
            elif self.error_message:
                error_text = self.FONT_SMALL.render(self.error_message, True, self.RED)
                self.SCREEN.blit(error_text, (50, self.HEIGHT//2))
            else:
                college_cards = []
                for i, college in enumerate(self.colleges):
                    card_y = 220 + i * 150
                    rect = pygame.Rect(50, card_y, self.WIDTH - 100, 140)
                    pygame.draw.rect(self.SCREEN, (200, 255, 200) if self.selected_college and self.selected_college.get("id") == college.get("id") else self.WHITE, rect, border_radius=12)
                    pygame.draw.rect(self.SCREEN, self.BLUE, rect, 3, border_radius=12) if self.selected_college and self.selected_college.get("id") == college.get("id") else pygame.draw.rect(self.SCREEN, self.GRAY, rect, 1, border_radius=12)

                    name = college.get('school.name', 'Unknown College')
                    name = name[:42] + "..." if len(name) > 45 else name
                    name_surf = self.FONT_MEDIUM.render(name, True, self.BLACK)
                    self.SCREEN.blit(name_surf, (rect.x + 20, rect.y + 15))

                    state = college.get('school.state', 'N/A')
                    city = college.get('school.city', 'N/A')
                    location_surf = self.FONT_SMALL.render(f"{city}, {state}", True, self.GRAY)
                    self.SCREEN.blit(location_surf, (rect.x + 20, rect.y + 45))

                    size = college.get('latest.student.size')
                    if size:
                        size_surf = self.FONT_SMALL.render(f"Students: {size:,}", True, self.BLACK)
                        self.SCREEN.blit(size_surf, (rect.x + 20, rect.y + 75))

                    admission_rate = college.get('latest.admissions.admission_rate.overall')
                    if admission_rate is not None:
                        admission_surf = self.FONT_SMALL.render(f"Admission: {admission_rate:.0%}", True, self.BLACK)
                        self.SCREEN.blit(admission_surf, (rect.x + 20, rect.y + 100))

                    earnings = college.get('latest.earnings.10_yrs_after_entry.median')
                    if earnings:
                        earnings_surf = self.FONT_SMALL.render(f"10-Year Median Salary: ${earnings:,}/year", True, self.GREEN)
                        self.SCREEN.blit(earnings_surf, (rect.x + self.WIDTH//2, rect.y + 75))

                    college_cards.append({"rect": rect, "data": college})

            pygame.display.flip()
