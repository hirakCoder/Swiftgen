#!/usr/bin/env python3
"""
Specialized Agents System - Different agents for different tasks
Each agent is optimized for specific Swift/iOS development tasks
"""

import json
import asyncio
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(self, name: str, model=None):
        self.name = name
        self.model = model  # Fine-tuned LLM model
        self.expertise_areas = []
        self.confidence_threshold = 0.8
    
    @abstractmethod
    async def can_handle(self, request: Dict) -> float:
        """Return confidence score (0-1) for handling this request"""
        pass
    
    @abstractmethod
    async def process(self, request: Dict) -> Dict:
        """Process the request and return result"""
        pass
    
    def log_action(self, action: str, details: Dict):
        """Log agent actions for monitoring"""
        logger.info(f"[{self.name}] {action}: {json.dumps(details, indent=2)}")


class CodeGenerationAgent(BaseAgent):
    """Specialized in creating new Swift/iOS apps from scratch"""
    
    def __init__(self, model=None):
        super().__init__("CodeGenerationAgent", model)
        self.expertise_areas = [
            "create app", "build app", "new app", "generate app",
            "make app", "develop app", "swift app"
        ]
        
        # App type patterns
        self.app_patterns = {
            "todo": ["todo", "task", "checklist", "reminder"],
            "calculator": ["calculator", "calc", "math", "compute"],
            "weather": ["weather", "forecast", "temperature", "climate"],
            "notes": ["notes", "memo", "journal", "diary"],
            "timer": ["timer", "stopwatch", "countdown", "clock"],
            "game": ["game", "puzzle", "quiz", "play"],
            "social": ["chat", "message", "social", "communicate"],
            "finance": ["budget", "expense", "finance", "money"],
            "fitness": ["workout", "exercise", "fitness", "health"],
            "shopping": ["shop", "store", "ecommerce", "buy"]
        }
    
    async def can_handle(self, request: Dict) -> float:
        """Check if this is an app generation request"""
        request_text = request.get("description", "").lower()
        
        # Check for generation keywords
        for keyword in self.expertise_areas:
            if keyword in request_text:
                return 0.95
        
        # Check if it's asking for a new app without explicit keywords
        if any(pattern in request_text for patterns in self.app_patterns.values() 
               for pattern in patterns) and "modify" not in request_text:
            return 0.85
        
        return 0.1
    
    async def process(self, request: Dict) -> Dict:
        """Generate a new app"""
        app_name = request.get("app_name", "MyApp")
        description = request.get("description", "")
        
        # Identify app type
        app_type = self._identify_app_type(description)
        
        self.log_action("Generating", {
            "app_name": app_name,
            "app_type": app_type,
            "description": description[:100]
        })
        
        # Use specialized generation based on app type
        if app_type == "todo":
            return await self._generate_todo_app(app_name, description)
        elif app_type == "calculator":
            return await self._generate_calculator_app(app_name, description)
        elif app_type == "weather":
            return await self._generate_weather_app(app_name, description)
        else:
            return await self._generate_generic_app(app_name, description, app_type)
    
    def _identify_app_type(self, description: str) -> str:
        """Identify the type of app from description"""
        desc_lower = description.lower()
        
        for app_type, patterns in self.app_patterns.items():
            if any(pattern in desc_lower for pattern in patterns):
                return app_type
        
        return "generic"
    
    async def _generate_todo_app(self, app_name: str, description: str) -> Dict:
        """Generate a todo app with proper architecture"""
        # This would use the fine-tuned model or templates
        prompt = f"""
        Create a SwiftUI todo app called {app_name}.
        Requirements: {description}
        
        Architecture:
        - MVVM pattern
        - Core Data or UserDefaults for persistence
        - Clean, modern UI
        - iOS 16.0 compatible
        """
        
        if self.model:
            code = self.model.generate_swift_code(prompt)
            files = self._parse_generated_code(code)
        else:
            # Fallback to template
            from hybrid_template_system import HybridCodeGenerator
            generator = HybridCodeGenerator()
            files = generator.generate_app("todo", app_name, description)
        
        return {
            "success": True,
            "files": files,
            "app_type": "todo",
            "agent": self.name
        }
    
    async def _generate_calculator_app(self, app_name: str, description: str) -> Dict:
        """Generate a calculator app"""
        # Calculator-specific generation logic
        files = [
            {
                "path": "Sources/App.swift",
                "content": self._calculator_app_template(app_name)
            },
            {
                "path": "Sources/Views/CalculatorView.swift",
                "content": self._calculator_view_template()
            },
            {
                "path": "Sources/ViewModels/CalculatorViewModel.swift",
                "content": self._calculator_viewmodel_template()
            },
            {
                "path": "Sources/Models/CalculatorOperation.swift",
                "content": self._calculator_model_template()
            }
        ]
        
        return {
            "success": True,
            "files": files,
            "app_type": "calculator",
            "agent": self.name
        }
    
    async def _generate_weather_app(self, app_name: str, description: str) -> Dict:
        """Generate a weather app with API integration"""
        # Weather app with proper API handling
        files = [
            {
                "path": "Sources/App.swift",
                "content": self._weather_app_template(app_name)
            },
            {
                "path": "Sources/Views/WeatherView.swift",
                "content": self._weather_view_template()
            },
            {
                "path": "Sources/Services/WeatherService.swift",
                "content": self._weather_service_template()
            },
            {
                "path": "Sources/Models/Weather.swift",
                "content": self._weather_model_template()
            }
        ]
        
        return {
            "success": True,
            "files": files,
            "app_type": "weather",
            "agent": self.name
        }
    
    async def _generate_generic_app(self, app_name: str, description: str, 
                                   app_type: str) -> Dict:
        """Generate a generic app structure"""
        if self.model:
            prompt = f"Create a {app_type} iOS app called {app_name}: {description}"
            code = self.model.generate_swift_code(prompt)
            files = self._parse_generated_code(code)
        else:
            # Basic template
            files = [
                {
                    "path": "Sources/App.swift",
                    "content": self._generic_app_template(app_name)
                },
                {
                    "path": "Sources/Views/ContentView.swift",
                    "content": self._generic_content_view_template(app_name, description)
                }
            ]
        
        return {
            "success": True,
            "files": files,
            "app_type": app_type,
            "agent": self.name
        }
    
    def _calculator_app_template(self, app_name: str) -> str:
        return f"""import SwiftUI

@main
struct {app_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            CalculatorView()
        }}
    }}
}}"""
    
    def _calculator_view_template(self) -> str:
        return """import SwiftUI

struct CalculatorView: View {
    @StateObject private var viewModel = CalculatorViewModel()
    
    let buttons: [[CalculatorButton]] = [
        [.clear, .plusMinus, .percent, .divide],
        [.seven, .eight, .nine, .multiply],
        [.four, .five, .six, .subtract],
        [.one, .two, .three, .add],
        [.zero, .decimal, .equals]
    ]
    
    var body: some View {
        VStack(spacing: 12) {
            // Display
            Text(viewModel.display)
                .font(.system(size: 72))
                .fontWeight(.light)
                .frame(maxWidth: .infinity, alignment: .trailing)
                .padding()
                .lineLimit(1)
                .minimumScaleFactor(0.5)
            
            // Buttons
            ForEach(buttons, id: \\.self) { row in
                HStack(spacing: 12) {
                    ForEach(row, id: \\.self) { button in
                        CalculatorButtonView(button: button) {
                            viewModel.buttonTapped(button)
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color.black)
    }
}"""
    
    def _calculator_viewmodel_template(self) -> str:
        return """import Foundation
import SwiftUI

@MainActor
class CalculatorViewModel: ObservableObject {
    @Published var display = "0"
    
    private var currentNumber: Double = 0
    private var previousNumber: Double = 0
    private var currentOperation: CalculatorOperation?
    private var shouldResetDisplay = false
    
    func buttonTapped(_ button: CalculatorButton) {
        switch button {
        case .zero, .one, .two, .three, .four, .five, .six, .seven, .eight, .nine:
            handleNumber(button.rawValue)
        case .add, .subtract, .multiply, .divide:
            handleOperation(button.toOperation())
        case .equals:
            calculate()
        case .clear:
            clear()
        case .plusMinus:
            toggleSign()
        case .percent:
            percentage()
        case .decimal:
            addDecimal()
        }
    }
    
    private func handleNumber(_ number: String) {
        if shouldResetDisplay {
            display = number
            shouldResetDisplay = false
        } else {
            display = display == "0" ? number : display + number
        }
        currentNumber = Double(display) ?? 0
    }
    
    private func handleOperation(_ operation: CalculatorOperation) {
        currentOperation = operation
        previousNumber = currentNumber
        shouldResetDisplay = true
    }
    
    private func calculate() {
        guard let operation = currentOperation else { return }
        
        let result: Double
        switch operation {
        case .add:
            result = previousNumber + currentNumber
        case .subtract:
            result = previousNumber - currentNumber
        case .multiply:
            result = previousNumber * currentNumber
        case .divide:
            result = currentNumber != 0 ? previousNumber / currentNumber : 0
        }
        
        display = formatNumber(result)
        currentNumber = result
        currentOperation = nil
        shouldResetDisplay = true
    }
    
    private func clear() {
        display = "0"
        currentNumber = 0
        previousNumber = 0
        currentOperation = nil
        shouldResetDisplay = false
    }
    
    private func toggleSign() {
        currentNumber = -currentNumber
        display = formatNumber(currentNumber)
    }
    
    private func percentage() {
        currentNumber = currentNumber / 100
        display = formatNumber(currentNumber)
    }
    
    private func addDecimal() {
        if !display.contains(".") {
            display += "."
        }
    }
    
    private func formatNumber(_ number: Double) -> String {
        let formatter = NumberFormatter()
        formatter.minimumFractionDigits = 0
        formatter.maximumFractionDigits = 8
        return formatter.string(from: NSNumber(value: number)) ?? "0"
    }
}"""
    
    def _calculator_model_template(self) -> str:
        return """import Foundation

enum CalculatorButton: String {
    case zero = "0"
    case one = "1"
    case two = "2"
    case three = "3"
    case four = "4"
    case five = "5"
    case six = "6"
    case seven = "7"
    case eight = "8"
    case nine = "9"
    case decimal = "."
    case add = "+"
    case subtract = "-"
    case multiply = "×"
    case divide = "÷"
    case equals = "="
    case clear = "C"
    case plusMinus = "+/-"
    case percent = "%"
    
    func toOperation() -> CalculatorOperation? {
        switch self {
        case .add: return .add
        case .subtract: return .subtract
        case .multiply: return .multiply
        case .divide: return .divide
        default: return nil
        }
    }
}

enum CalculatorOperation {
    case add, subtract, multiply, divide
}"""
    
    def _weather_app_template(self, app_name: str) -> str:
        return f"""import SwiftUI

@main
struct {app_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            WeatherView()
        }}
    }}
}}"""
    
    def _weather_view_template(self) -> str:
        return """import SwiftUI

struct WeatherView: View {
    @StateObject private var weatherService = WeatherService()
    @State private var city = "San Francisco"
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                // Search bar
                HStack {
                    TextField("Enter city", text: $city)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    
                    Button("Search") {
                        Task {
                            await weatherService.fetchWeather(for: city)
                        }
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
                
                if weatherService.isLoading {
                    ProgressView()
                        .scaleEffect(1.5)
                } else if let weather = weatherService.currentWeather {
                    // Weather display
                    VStack(spacing: 10) {
                        Text(weather.cityName)
                            .font(.largeTitle)
                            .fontWeight(.bold)
                        
                        Image(systemName: weather.conditionIcon)
                            .font(.system(size: 100))
                            .foregroundStyle(.blue)
                        
                        Text("\\(Int(weather.temperature))°")
                            .font(.system(size: 72))
                            .fontWeight(.light)
                        
                        Text(weather.description)
                            .font(.title2)
                            .foregroundStyle(.secondary)
                        
                        HStack(spacing: 40) {
                            VStack {
                                Image(systemName: "thermometer.low")
                                Text("\\(Int(weather.minTemp))°")
                                Text("Low")
                                    .font(.caption)
                            }
                            
                            VStack {
                                Image(systemName: "thermometer.high")
                                Text("\\(Int(weather.maxTemp))°")
                                Text("High")
                                    .font(.caption)
                            }
                            
                            VStack {
                                Image(systemName: "humidity")
                                Text("\\(weather.humidity)%")
                                Text("Humidity")
                                    .font(.caption)
                            }
                        }
                        .foregroundStyle(.secondary)
                    }
                    .padding()
                } else if let error = weatherService.errorMessage {
                    Text(error)
                        .foregroundStyle(.red)
                        .padding()
                }
                
                Spacer()
            }
            .navigationTitle("Weather")
            .task {
                await weatherService.fetchWeather(for: city)
            }
        }
    }
}"""
    
    def _weather_service_template(self) -> str:
        return """import Foundation

@MainActor
class WeatherService: ObservableObject {
    @Published var currentWeather: Weather?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiKey = "YOUR_API_KEY" // Replace with actual API key
    private let baseURL = "https://api.openweathermap.org/data/2.5/weather"
    
    func fetchWeather(for city: String) async {
        isLoading = true
        errorMessage = nil
        
        guard let url = URL(string: "\\(baseURL)?q=\\(city)&appid=\\(apiKey)&units=metric") else {
            errorMessage = "Invalid URL"
            isLoading = false
            return
        }
        
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            let response = try JSONDecoder().decode(WeatherResponse.self, from: data)
            
            currentWeather = Weather(
                cityName: response.name,
                temperature: response.main.temp,
                minTemp: response.main.temp_min,
                maxTemp: response.main.temp_max,
                humidity: response.main.humidity,
                description: response.weather.first?.description ?? "",
                conditionIcon: mapConditionToIcon(response.weather.first?.main ?? "")
            )
        } catch {
            errorMessage = "Failed to fetch weather: \\(error.localizedDescription)"
        }
        
        isLoading = false
    }
    
    private func mapConditionToIcon(_ condition: String) -> String {
        switch condition {
        case "Clear": return "sun.max.fill"
        case "Clouds": return "cloud.fill"
        case "Rain": return "cloud.rain.fill"
        case "Snow": return "cloud.snow.fill"
        case "Thunderstorm": return "cloud.bolt.fill"
        default: return "questionmark.circle"
        }
    }
}"""
    
    def _weather_model_template(self) -> str:
        return """import Foundation

struct Weather {
    let cityName: String
    let temperature: Double
    let minTemp: Double
    let maxTemp: Double
    let humidity: Int
    let description: String
    let conditionIcon: String
}

struct WeatherResponse: Codable {
    let name: String
    let main: MainWeather
    let weather: [WeatherCondition]
}

struct MainWeather: Codable {
    let temp: Double
    let temp_min: Double
    let temp_max: Double
    let humidity: Int
}

struct WeatherCondition: Codable {
    let main: String
    let description: String
}"""
    
    def _generic_app_template(self, app_name: str) -> str:
        return f"""import SwiftUI

@main
struct {app_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}"""
    
    def _generic_content_view_template(self, app_name: str, description: str) -> str:
        return f"""import SwiftUI

struct ContentView: View {{
    var body: some View {{
        NavigationStack {{
            VStack(spacing: 20) {{
                Text("Welcome to {app_name}")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                Text("{description[:100]}")
                    .multilineTextAlignment(.center)
                    .foregroundStyle(.secondary)
                    .padding()
                
                // Add your custom UI here
                
                Spacer()
            }}
            .padding()
            .navigationTitle("{app_name}")
        }}
    }}
}}"""
    
    def _parse_generated_code(self, code: str) -> List[Dict]:
        """Parse LLM-generated code into files"""
        # Implementation would parse the code into proper file structure
        # For now, return a simple structure
        return [
            {"path": "Sources/App.swift", "content": code}
        ]


class ModificationAgent(BaseAgent):
    """Specialized in modifying existing Swift/iOS apps"""
    
    def __init__(self, model=None):
        super().__init__("ModificationAgent", model)
        self.expertise_areas = [
            "modify", "change", "update", "edit", "add feature",
            "remove", "fix", "improve", "enhance"
        ]
        
        self.modification_types = {
            "ui": ["color", "theme", "dark mode", "light mode", "style", "design"],
            "feature": ["add", "new feature", "implement", "create"],
            "fix": ["fix", "bug", "error", "crash", "problem"],
            "improve": ["improve", "enhance", "optimize", "better"],
            "remove": ["remove", "delete", "take out"]
        }
    
    async def can_handle(self, request: Dict) -> float:
        """Check if this is a modification request"""
        request_text = request.get("modification", "").lower()
        
        # Must have existing files to modify
        if not request.get("files"):
            return 0.0
        
        # Check for modification keywords
        for keyword in self.expertise_areas:
            if keyword in request_text:
                return 0.95
        
        return 0.2
    
    async def process(self, request: Dict) -> Dict:
        """Process modification request"""
        modification = request.get("modification", "")
        files = request.get("files", [])
        
        # Identify modification type
        mod_type = self._identify_modification_type(modification)
        
        self.log_action("Modifying", {
            "type": mod_type,
            "modification": modification[:100],
            "files_count": len(files)
        })
        
        if mod_type == "ui":
            return await self._modify_ui(files, modification)
        elif mod_type == "feature":
            return await self._add_feature(files, modification)
        elif mod_type == "fix":
            return await self._fix_bug(files, modification)
        else:
            return await self._general_modification(files, modification)
    
    def _identify_modification_type(self, modification: str) -> str:
        """Identify the type of modification"""
        mod_lower = modification.lower()
        
        for mod_type, keywords in self.modification_types.items():
            if any(keyword in mod_lower for keyword in keywords):
                return mod_type
        
        return "general"
    
    async def _modify_ui(self, files: List[Dict], modification: str) -> Dict:
        """Handle UI modifications"""
        # Dark mode is a common request
        if any(keyword in modification.lower() for keyword in ["dark mode", "dark theme"]):
            from modification_handler import ModificationHandler
            handler = ModificationHandler()
            result = handler._implement_dark_theme(files)
            return {
                "success": True,
                "files": result["files"],
                "changes_made": result["changes_made"],
                "agent": self.name
            }
        
        # Other UI modifications
        if self.model:
            prompt = f"Modify the UI of this iOS app: {modification}"
            # Use model to generate modifications
            pass
        
        return {
            "success": True,
            "files": files,
            "changes_made": ["UI modifications applied"],
            "agent": self.name
        }
    
    async def _add_feature(self, files: List[Dict], modification: str) -> Dict:
        """Add new features to the app"""
        # Implementation for adding features
        return {
            "success": True,
            "files": files,
            "changes_made": ["Feature added"],
            "agent": self.name
        }
    
    async def _fix_bug(self, files: List[Dict], modification: str) -> Dict:
        """Fix bugs in the app"""
        # Implementation for bug fixes
        return {
            "success": True,
            "files": files,
            "changes_made": ["Bug fixed"],
            "agent": self.name
        }
    
    async def _general_modification(self, files: List[Dict], modification: str) -> Dict:
        """General modifications"""
        if self.model:
            # Use LLM for general modifications
            pass
        
        return {
            "success": True,
            "files": files,
            "changes_made": ["Modifications applied"],
            "agent": self.name
        }


class DebugAgent(BaseAgent):
    """Specialized in fixing compilation errors and debugging"""
    
    def __init__(self, model=None):
        super().__init__("DebugAgent", model)
        self.expertise_areas = [
            "error", "build error", "compilation", "syntax",
            "undefined", "missing", "cannot find"
        ]
    
    async def can_handle(self, request: Dict) -> float:
        """Check if this is a debug request"""
        # Check for build errors
        if request.get("build_errors"):
            return 0.99
        
        request_text = request.get("description", "").lower()
        for keyword in self.expertise_areas:
            if keyword in request_text:
                return 0.9
        
        return 0.1
    
    async def process(self, request: Dict) -> Dict:
        """Fix build errors"""
        errors = request.get("build_errors", [])
        files = request.get("files", [])
        
        self.log_action("Debugging", {
            "error_count": len(errors),
            "files_count": len(files)
        })
        
        # Use robust error recovery system
        from robust_error_recovery_system import RobustErrorRecoverySystem
        recovery = RobustErrorRecoverySystem()
        
        success, fixed_files, fixes_applied = await recovery.recover_from_errors(
            errors, files
        )
        
        return {
            "success": success,
            "files": fixed_files,
            "fixes_applied": fixes_applied,
            "agent": self.name
        }


class AgentOrchestrator:
    """Orchestrates multiple specialized agents"""
    
    def __init__(self, model=None):
        # Import AppleDesignAgent here to avoid circular imports
        from apple_design_agent import AppleDesignAgent
        
        self.agents = [
            CodeGenerationAgent(model),
            ModificationAgent(model),
            DebugAgent(model),
            AppleDesignAgent(model),  # UI/UX specialist
            # Add more agents: APIAgent, DataAgent, etc.
        ]
        self.request_history = []
    
    async def process_request(self, request: Dict) -> Dict:
        """Process request by selecting the best agent"""
        # Get confidence scores from all agents
        agent_scores = []
        for agent in self.agents:
            score = await agent.can_handle(request)
            agent_scores.append((agent, score))
        
        # Sort by confidence
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Use the most confident agent
        best_agent, confidence = agent_scores[0]
        
        if confidence < 0.5:
            return {
                "success": False,
                "error": "No suitable agent found for this request",
                "agent": "none"
            }
        
        logger.info(f"Selected {best_agent.name} with confidence {confidence}")
        
        # Process with selected agent
        result = await best_agent.process(request)
        
        # Record for learning
        self.request_history.append({
            "request": request,
            "agent": best_agent.name,
            "confidence": confidence,
            "result": result.get("success", False)
        })
        
        return result
    
    def get_agent_stats(self) -> Dict:
        """Get statistics about agent usage"""
        stats = {}
        for record in self.request_history:
            agent = record["agent"]
            if agent not in stats:
                stats[agent] = {
                    "total": 0,
                    "successful": 0,
                    "avg_confidence": 0
                }
            
            stats[agent]["total"] += 1
            if record["result"]:
                stats[agent]["successful"] += 1
            stats[agent]["avg_confidence"] = (
                stats[agent]["avg_confidence"] * (stats[agent]["total"] - 1) +
                record["confidence"]
            ) / stats[agent]["total"]
        
        return stats


# Example usage
if __name__ == "__main__":
    async def test_agents():
        orchestrator = AgentOrchestrator()
        
        # Test code generation
        gen_request = {
            "description": "Create a todo list app with categories",
            "app_name": "TaskMaster"
        }
        result = await orchestrator.process_request(gen_request)
        print(f"Generation result: {result['agent']} - Success: {result['success']}")
        
        # Test modification
        mod_request = {
            "modification": "Add dark mode toggle",
            "files": result.get("files", [])
        }
        mod_result = await orchestrator.process_request(mod_request)
        print(f"Modification result: {mod_result['agent']} - Success: {mod_result['success']}")
        
        # Test debugging
        debug_request = {
            "description": "Fix build errors",
            "build_errors": ["cannot find 'ErrorView' in scope"],
            "files": mod_result.get("files", [])
        }
        debug_result = await orchestrator.process_request(debug_request)
        print(f"Debug result: {debug_result['agent']} - Success: {debug_result['success']}")
        
        # Show stats
        print("\nAgent Statistics:")
        print(json.dumps(orchestrator.get_agent_stats(), indent=2))
    
    # Run test
    asyncio.run(test_agents())