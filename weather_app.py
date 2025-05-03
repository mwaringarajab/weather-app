import tkinter as tk
from tkinter import messagebox, ttk
import requests
from datetime import datetime
import json
import os
from PIL import Image, ImageTk
import io
import threading

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Weather App")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # API key for OpenWeatherMap
        # In a real application, you should store this securely
        # or use environment variables (os.environ.get('API_KEY'))
        self.api_key = "be863505946cf6524ea53cf88df0c548" 
        
        # Add predefined cities for easier access
        self.predefined_cities = ["New York", "London", "Tokyo", "Paris", "Sydney", 
                                  "Berlin", "Dubai", "Moscow", "Rio de Janeiro", "Cairo"]
        
        # Sample API key usage message
        if self.api_key == "YOUR_API_KEY":
            tk.Label(
                self.root, 
                text="Note: Replace 'YOUR_API_KEY' with an actual OpenWeatherMap API key for live data", 
                fg="red",
                bg="#f0f0f0",
                font=("Arial", 8)
            ).pack(pady=(5, 0))
            
            tk.Label(
                self.root,
                text="Demo Mode: You can search for any city name and mock data will be generated",
                fg="blue",
                bg="#f0f0f0",
                font=("Arial", 8)
            ).pack(pady=(0, 5))
        
        self.setup_ui()
        
        # For demonstration, load mock data if no API key is provided
        if self.api_key == "be863505946cf6524ea53cf88df0c548":
            self.load_mock_data("New York")
    
    def setup_ui(self):
        # Search frame
        search_frame = tk.Frame(self.root, bg="#f0f0f0")
        search_frame.pack(fill="x", padx=20, pady=20)
        
        # City entry
        self.city_var = tk.StringVar()
        self.city_entry = tk.Entry(
            search_frame, 
            textvariable=self.city_var, 
            font=("Arial", 14),
            width=30
        )
        self.city_entry.pack(side="left", padx=(0, 10))
        self.city_entry.bind("<Return>", lambda event: self.get_weather())
        self.city_var.set("New York")  # Default city
        
        # Search button
        search_button = tk.Button(
            search_frame,
            text="Search",
            font=("Arial", 12),
            bg="#4a7abc",
            fg="white",
            activebackground="#3d6ca8",
            activeforeground="white",
            command=self.get_weather
        )
        search_button.pack(side="left")
        
        # Add dropdown for predefined cities
        cities_frame = tk.Frame(self.root, bg="#f0f0f0")
        cities_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        tk.Label(
            cities_frame,
            text="Quick Select:",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(side="left", padx=(0, 10))
        
        # Create combobox for city selection
        self.city_combo = ttk.Combobox(
            cities_frame,
            values=self.predefined_cities,
            width=15,
            state="readonly"
        )
        self.city_combo.pack(side="left")
        self.city_combo.bind("<<ComboboxSelected>>", self.on_city_selected)
        
        # Weather info frame
        self.weather_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.weather_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # City name and date/time
        self.city_label = tk.Label(
            self.weather_frame,
            text="",
            font=("Arial", 22, "bold"),
            bg="#f0f0f0"
        )
        self.city_label.pack(pady=(0, 5))
        
        self.date_label = tk.Label(
            self.weather_frame,
            text="",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#555555"
        )
        self.date_label.pack()
        
        # Weather icon and temperature
        self.icon_temp_frame = tk.Frame(self.weather_frame, bg="#f0f0f0")
        self.icon_temp_frame.pack(pady=15)
        
        self.weather_icon_label = tk.Label(self.icon_temp_frame, bg="#f0f0f0")
        self.weather_icon_label.pack(side="left", padx=10)
        
        self.temp_label = tk.Label(
            self.icon_temp_frame,
            text="",
            font=("Arial", 32),
            bg="#f0f0f0"
        )
        self.temp_label.pack(side="left")
        
        # Weather description
        self.description_label = tk.Label(
            self.weather_frame,
            text="",
            font=("Arial", 14),
            bg="#f0f0f0"
        )
        self.description_label.pack(pady=(0, 15))
        
        # Details frame
        details_frame = tk.Frame(self.weather_frame, bg="white", relief="solid", bd=1)
        details_frame.pack(fill="x", pady=10)
        
        # Create a 2x2 grid for details
        for i in range(2):
            details_frame.columnconfigure(i, weight=1)
        
        # Feels like
        tk.Label(details_frame, text="Feels Like", font=("Arial", 12), bg="white").grid(row=0, column=0, padx=10, pady=(10, 0))
        self.feels_like_label = tk.Label(details_frame, text="", font=("Arial", 14, "bold"), bg="white")
        self.feels_like_label.grid(row=1, column=0, padx=10, pady=(0, 10))
        
        # Humidity
        tk.Label(details_frame, text="Humidity", font=("Arial", 12), bg="white").grid(row=0, column=1, padx=10, pady=(10, 0))
        self.humidity_label = tk.Label(details_frame, text="", font=("Arial", 14, "bold"), bg="white")
        self.humidity_label.grid(row=1, column=1, padx=10, pady=(0, 10))
        
        # Wind
        tk.Label(details_frame, text="Wind", font=("Arial", 12), bg="white").grid(row=2, column=0, padx=10, pady=(10, 0))
        self.wind_label = tk.Label(details_frame, text="", font=("Arial", 14, "bold"), bg="white")
        self.wind_label.grid(row=3, column=0, padx=10, pady=(0, 10))
        
        # Pressure
        tk.Label(details_frame, text="Pressure", font=("Arial", 12), bg="white").grid(row=2, column=1, padx=10, pady=(10, 0))
        self.pressure_label = tk.Label(details_frame, text="", font=("Arial", 14, "bold"), bg="white")
        self.pressure_label.grid(row=3, column=1, padx=10, pady=(0, 10))
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#eeeeee",
            fg="#555555"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def get_weather(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showerror("Error", "Please enter a city name")
            return
        
        self.status_bar.config(text="Fetching weather data...")
        
        # Use threading to prevent GUI from freezing during API call
        threading.Thread(target=self._fetch_weather_data, args=(city,), daemon=True).start()
    
    def on_city_selected(self, event):
        """Handle city selection from dropdown"""
        selected_city = self.city_combo.get()
        if selected_city:
            self.city_var.set(selected_city)
            self.get_weather()
    
    def _fetch_weather_data(self, city):
        try:
            if self.api_key == "YOUR_API_KEY":
                # Use mock data if API key isn't set
                self.load_mock_data(city)
                return
                
            # Make API request
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
            
            # Show status while fetching
            self.root.after(0, lambda: self.status_bar.config(text=f"Connecting to OpenWeatherMap API..."))
            
            response = requests.get(url, timeout=10)  # Add timeout for better error handling
            data = response.json()
            
            if response.status_code != 200:
                error_message = data.get('message', 'Unknown error occurred')
                
                # More user-friendly error messages
                if error_message == "city not found":
                    error_message = f"City '{city}' not found. Please check the spelling and try again."
                elif "Invalid API key" in error_message:
                    error_message = "Invalid API key. Please check your API key in the code."
                
                self.root.after(0, lambda: messagebox.showerror("Error", error_message))
                self.root.after(0, lambda: self.status_bar.config(text="Failed to fetch weather data"))
                return
            
            # Update UI with the received data
            self.root.after(0, lambda: self.update_weather_ui(data))
            self.root.after(0, lambda: self.status_bar.config(text=f"Weather data updated for {city}"))
            
        except requests.exceptions.Timeout:
            self.root.after(0, lambda: messagebox.showerror("Error", "Connection timed out. Please check your internet connection and try again."))
            self.root.after(0, lambda: self.status_bar.config(text="Connection timed out"))
        except requests.exceptions.ConnectionError:
            self.root.after(0, lambda: messagebox.showerror("Error", "Connection failed. Please check your internet connection and try again."))
            self.root.after(0, lambda: self.status_bar.config(text="Connection failed"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, lambda: self.status_bar.config(text="Failed to fetch weather data"))
    
    def load_mock_data(self, city):
        """Load mock data for demonstration purposes with more cities and dynamic generation"""
        mock_data = {
            "New York": {
                "name": "New York",
                "dt": int(datetime.now().timestamp()),
                "main": {
                    "temp": 20.5,
                    "feels_like": 19.8,
                    "humidity": 65,
                    "pressure": 1013
                },
                "weather": [
                    {
                        "description": "clear sky",
                        "icon": "01d"
                    }
                ],
                "wind": {
                    "speed": 5.2
                }
            },
            "London": {
                "name": "London",
                "dt": int(datetime.now().timestamp()),
                "main": {
                    "temp": 15.2,
                    "feels_like": 14.5,
                    "humidity": 78,
                    "pressure": 1008
                },
                "weather": [
                    {
                        "description": "light rain",
                        "icon": "10d"
                    }
                ],
                "wind": {
                    "speed": 6.8
                }
            },
            "Tokyo": {
                "name": "Tokyo",
                "dt": int(datetime.now().timestamp()),
                "main": {
                    "temp": 26.7,
                    "feels_like": 27.9,
                    "humidity": 70,
                    "pressure": 1015
                },
                "weather": [
                    {
                        "description": "scattered clouds",
                        "icon": "03d"
                    }
                ],
                "wind": {
                    "speed": 3.5
                }
            },
            "Sydney": {
                "name": "Sydney",
                "dt": int(datetime.now().timestamp()),
                "main": {
                    "temp": 22.8,
                    "feels_like": 22.5,
                    "humidity": 55,
                    "pressure": 1020
                },
                "weather": [
                    {
                        "description": "sunny",
                        "icon": "01d"
                    }
                ],
                "wind": {
                    "speed": 8.2
                }
            },
            "Paris": {
                "name": "Paris",
                "dt": int(datetime.now().timestamp()),
                "main": {
                    "temp": 18.3,
                    "feels_like": 17.8,
                    "humidity": 60,
                    "pressure": 1012
                },
                "weather": [
                    {
                        "description": "partly cloudy",
                        "icon": "02d"
                    }
                ],
                "wind": {
                    "speed": 4.5
                }
            },
            "Berlin": {
                "name": "Berlin",
                "dt": int(datetime.now().timestamp()),
                "main": {
                    "temp": 16.8,
                    "feels_like": 16.2,
                    "humidity": 65,
                    "pressure": 1010
                },
                "weather": [
                    {
                        "description": "overcast clouds",
                        "icon": "04d"
                    }
                ],
                "wind": {
                    "speed": 5.8
                }
            },
            "Dubai": {
                "name": "Dubai",
                "dt": int(datetime.now().timestamp()),
                "main": {
                    "temp": 34.5,
                    "feels_like": 36.2,
                    "humidity": 45,
                    "pressure": 1008
                },
                "weather": [
                    {
                        "description": "clear sky",
                        "icon": "01d"
                    }
                ],
                "wind": {
                    "speed": 7.2
                }
            },
            "Moscow": {
                "name": "Moscow",
                "dt": int(datetime.now().timestamp()),
                "main": {
                    "temp": 8.7,
                    "feels_like": 6.5,
                    "humidity": 75,
                    "pressure": 1015
                },
                "weather": [
                    {
                        "description": "light snow",
                        "icon": "13d"
                    }
                ],
                "wind": {
                    "speed": 9.3
                }
            },
            "Rio de Janeiro": {
                "name": "Rio de Janeiro",
                "dt": int(datetime.now().timestamp()),
                "main": {
                    "temp": 28.6,
                    "feels_like": 30.2,
                    "humidity": 68,
                    "pressure": 1011
                },
                "weather": [
                    {
                        "description": "few clouds",
                        "icon": "02d"
                    }
                ],
                "wind": {
                    "speed": 4.8
                }
            },
            "Cairo": {
                "name": "Cairo",
                "dt": int(datetime.now().timestamp()),
                "main": {
                    "temp": 30.4,
                    "feels_like": 29.8,
                    "humidity": 40,
                    "pressure": 1009
                },
                "weather": [
                    {
                        "description": "clear sky",
                        "icon": "01d"
                    }
                ],
                "wind": {
                    "speed": 6.5
                }
            }            
        }
        
        # Find the closest match in our mock data
        city_lower = city.lower()
        selected_city = None
        
        for key in mock_data:
            if key.lower() == city_lower:
                selected_city = key
                break
        
        if selected_city:
            self.update_weather_ui(mock_data[selected_city])
            self.status_bar.config(text=f"Mock weather data loaded for {selected_city}")
        else:
            # Generate dynamic mock data for unknown city
            import random
            weather_conditions = [
                {"description": "clear sky", "icon": "01d"},
                {"description": "few clouds", "icon": "02d"},
                {"description": "scattered clouds", "icon": "03d"},
                {"description": "broken clouds", "icon": "04d"},
                {"description": "light rain", "icon": "10d"},
                {"description": "moderate rain", "icon": "10d"},
                {"description": "light snow", "icon": "13d"},
                {"description": "mist", "icon": "50d"}
            ]
            
            # Generate realistic temperature based on first letter of city
            first_char = city[0].lower()
            temp_base = (ord(first_char) - ord('a')) % 15 + 10  # Temp between 10-25°C
            
            generated_data = {
                "name": city,
                "dt": int(datetime.now().timestamp()),
                "main": {
                    "temp": temp_base + random.uniform(-3, 3),
                    "feels_like": temp_base + random.uniform(-4, 2),
                    "humidity": random.randint(40, 85),
                    "pressure": random.randint(1000, 1025)
                },
                "weather": [
                    random.choice(weather_conditions)
                ],
                "wind": {
                    "speed": random.uniform(2, 12)
                }
            }
            
            self.update_weather_ui(generated_data)
            self.status_bar.config(text=f"Generated weather data for {city} (demo mode)")
            messagebox.showinfo("Demo Mode", f"Generated mock data for '{city}'. For real weather data, please add an OpenWeatherMap API key.")
    

    def update_weather_ui(self, data):
        """Update the UI with weather data"""
        # City name
        self.city_label.config(text=data["name"])
        
        # Date and time
        timestamp = data.get("dt", 0)
        date_time = datetime.fromtimestamp(timestamp)
        formatted_date = date_time.strftime("%A, %d %B %Y, %H:%M")
        self.date_label.config(text=formatted_date)
        
        # Temperature
        temp = data["main"]["temp"]
        self.temp_label.config(text=f"{temp:.1f}°C")
        
        # Weather description
        weather_desc = data["weather"][0]["description"].capitalize()
        self.description_label.config(text=weather_desc)
        
        # Weather icon (would fetch from OpenWeatherMap in a real app)
        icon_code = data["weather"][0]["icon"]
        self.display_weather_icon(icon_code)
        
        # Details
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        pressure = data["main"]["pressure"]
        
        self.feels_like_label.config(text=f"{feels_like:.1f}°C")
        self.humidity_label.config(text=f"{humidity}%")
        self.wind_label.config(text=f"{wind_speed} m/s")
        self.pressure_label.config(text=f"{pressure} hPa")
    
    def display_weather_icon(self, icon_code):
        """Display weather icon (simplified version with text representations)"""
        # In a real app, you would download the icon from OpenWeatherMap
        # For simplicity, we'll use text representation
        icon_text = {
            "01d": "☀️",  # Clear sky (day)
            "01n": "🌙",  # Clear sky (night)
            "02d": "⛅",  # Few clouds (day)
            "02n": "☁️",  # Few clouds (night)
            "03d": "☁️",  # Scattered clouds
            "03n": "☁️",
            "04d": "☁️",  # Broken clouds
            "04n": "☁️",
            "09d": "🌧️",  # Shower rain
            "09n": "🌧️",
            "10d": "🌦️",  # Rain (day)
            "10n": "🌧️",  # Rain (night)
            "11d": "⛈️",  # Thunderstorm
            "11n": "⛈️",
            "13d": "❄️",  # Snow
            "13n": "❄️",
            "50d": "🌫️",  # Mist
            "50n": "🌫️"
        }
        
        # Default icon if not found
        icon = icon_text.get(icon_code, "🌤️")
        
        # Create a text-based icon (in a real app, you'd use actual images)
        self.weather_icon_label.config(text=icon, font=("Arial", 48))

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()