# modules/dashboard_widgets.py
class Widget:
    def __init__(self, theme):
        self.theme = theme
    
    def render(self):
        return render_template(f'themes/{self.theme}/widgets/{self.type}.html',
                           data=self.get_data())

class UserStatsWidget(Widget):
    type = 'user_stats'
    
    def get_data(self):
        return {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(active=True).count()
        }