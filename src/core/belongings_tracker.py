"""
Belongings Tracking System for Couch Surfing Chapter
Tracks items being lost/damaged during unstable housing
"""
import random

class BelongingsTracker:
    """System to track player's belongings through housing instability"""

    def __init__(self):
        # Initial belongings from foster home
        self.belongings = {
            'clothes': {
                'name': 'Spare Clothes',
                'status': 'safe',
                'location': 'backpack',
                'importance': 'medium',
                'description': 'Two changes of clothes from foster home'
            },
            'documents': {
                'name': 'Important Documents',
                'status': 'safe',
                'location': 'backpack',
                'importance': 'critical',
                'description': 'Birth certificate, SSN card, foster care papers'
            },
            'photo': {
                'name': 'Family Photo',
                'status': 'safe',
                'location': 'backpack',
                'importance': 'high',
                'description': 'Only photo of birth mother'
            },
            'phone_charger': {
                'name': 'Phone Charger',
                'status': 'safe',
                'location': 'backpack',
                'importance': 'critical',
                'description': 'Essential for staying connected'
            },
            'work_uniform': {
                'name': 'Work Uniform',
                'status': 'safe',
                'location': 'backpack',
                'importance': 'critical',
                'description': 'Required for part-time job'
            },
            'toothbrush': {
                'name': 'Toothbrush',
                'status': 'safe',
                'location': 'backpack',
                'importance': 'low',
                'description': 'Basic hygiene item'
            },
            'wallet': {
                'name': 'Wallet',
                'status': 'safe',
                'location': 'pocket',
                'importance': 'critical',
                'description': 'Contains $73 and ID'
            },
            'phone': {
                'name': 'Phone',
                'status': 'safe',
                'location': 'pocket',
                'importance': 'critical',
                'description': 'Lifeline to the world'
            },
            'notebook': {
                'name': 'Journal',
                'status': 'safe',
                'location': 'backpack',
                'importance': 'medium',
                'description': 'Personal thoughts and contact numbers'
            },
            'medication': {
                'name': 'Medication',
                'status': 'safe',
                'location': 'backpack',
                'importance': 'critical',
                'description': 'Anxiety medication (half bottle left)'
            }
        }

        # Track locations where items were lost
        self.lost_at = {}

        # Track total value/importance lost
        self.critical_items_lost = 0
        self.total_items_lost = 0

        # Current carrying capacity (decreases with exhaustion)
        self.max_carry_weight = 10
        self.current_weight = 10

    def lose_item(self, item_key, location="unknown", reason="misplaced"):
        """Lose a specific item"""
        if item_key in self.belongings and self.belongings[item_key]['status'] == 'safe':
            self.belongings[item_key]['status'] = 'lost'
            self.belongings[item_key]['location'] = 'unknown'
            self.lost_at[item_key] = {'location': location, 'reason': reason}

            # Track statistics
            self.total_items_lost += 1
            if self.belongings[item_key]['importance'] == 'critical':
                self.critical_items_lost += 1

            return True
        return False

    def damage_item(self, item_key, reason="wear and tear"):
        """Damage an item (still usable but degraded)"""
        if item_key in self.belongings and self.belongings[item_key]['status'] == 'safe':
            self.belongings[item_key]['status'] = 'damaged'
            return True
        return False

    def lose_random_item(self, importance_weights=None):
        """Randomly lose an item based on importance weights"""
        if importance_weights is None:
            importance_weights = {
                'low': 0.5,
                'medium': 0.3,
                'high': 0.15,
                'critical': 0.05
            }

        safe_items = [(k, v) for k, v in self.belongings.items() if v['status'] == 'safe']
        if not safe_items:
            return None

        # Weight items by inverse importance (more likely to lose less important items)
        weighted_items = []
        for key, item in safe_items:
            weight = importance_weights.get(item['importance'], 0.1)
            weighted_items.append((key, weight))

        # Normalize weights
        total_weight = sum(w for _, w in weighted_items)
        if total_weight == 0:
            return None

        # Random selection
        rand = random.random() * total_weight
        current = 0
        for key, weight in weighted_items:
            current += weight
            if rand <= current:
                self.lose_item(key)
                return key

        return None

    def get_safe_items(self):
        """Get all items that are still safe"""
        return {k: v for k, v in self.belongings.items() if v['status'] == 'safe'}

    def get_lost_items(self):
        """Get all lost items"""
        return {k: v for k, v in self.belongings.items() if v['status'] == 'lost'}

    def get_damaged_items(self):
        """Get all damaged items"""
        return {k: v for k, v in self.belongings.items() if v['status'] == 'damaged'}

    def get_critical_items(self):
        """Get all critical items regardless of status"""
        return {k: v for k, v in self.belongings.items() if v['importance'] == 'critical'}

    def calculate_burden(self):
        """Calculate psychological burden based on losses"""
        burden = 0

        # Each lost item adds burden
        burden += self.total_items_lost * 10

        # Critical items add more burden
        burden += self.critical_items_lost * 30

        # Lost work uniform = job at risk
        if self.belongings['work_uniform']['status'] == 'lost':
            burden += 50

        # Lost phone charger = isolation risk
        if self.belongings['phone_charger']['status'] == 'lost':
            burden += 30

        # Lost documents = bureaucratic nightmare
        if self.belongings['documents']['status'] == 'lost':
            burden += 40

        return min(100, burden)  # Cap at 100

    def get_status_summary(self):
        """Get a summary of current belongings status"""
        safe_count = len(self.get_safe_items())
        lost_count = len(self.get_lost_items())
        damaged_count = len(self.get_damaged_items())
        total_count = len(self.belongings)

        critical_safe = len([k for k, v in self.get_critical_items().items()
                            if self.belongings[k]['status'] == 'safe'])
        critical_total = len(self.get_critical_items())

        return {
            'safe': safe_count,
            'lost': lost_count,
            'damaged': damaged_count,
            'total': total_count,
            'critical_safe': critical_safe,
            'critical_total': critical_total,
            'burden': self.calculate_burden()
        }

    def simulate_move(self, stability_level=0.5):
        """Simulate effects of moving between locations"""
        # Lower stability = higher chance of losing items
        loss_chance = 1.0 - stability_level

        # Chance to lose 1-3 items based on stability
        num_losses = 0
        if random.random() < loss_chance:
            num_losses = random.randint(1, 3)

        lost_items = []
        for _ in range(num_losses):
            lost_item = self.lose_random_item()
            if lost_item:
                lost_items.append(lost_item)

        return lost_items

    def check_critical_losses(self):
        """Check if any critical losses have occurred that affect gameplay"""
        warnings = []

        if self.belongings['work_uniform']['status'] == 'lost':
            warnings.append("Without your work uniform, you'll lose your job!")

        if self.belongings['phone_charger']['status'] == 'lost':
            warnings.append("Your phone battery is dying. You'll be cut off from help.")

        if self.belongings['documents']['status'] == 'lost':
            warnings.append("Without documents, you can't apply for services or housing.")

        if self.belongings['medication']['status'] == 'lost':
            warnings.append("Without medication, your anxiety is becoming unmanageable.")

        if self.belongings['wallet']['status'] == 'lost':
            warnings.append("Your last $73 is gone. You have nothing.")

        return warnings