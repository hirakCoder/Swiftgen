#!/usr/bin/env python3
"""
Create sample training data for testing the fine-tuning pipeline
"""

import json
import os
from pathlib import Path

def create_sample_training_data():
    """Create sample Swift training data for testing"""
    output_file = "swift_training_prompts.jsonl"
    
    # Sample training examples
    training_examples = [
        {
            "prompt": "Create a SwiftUI todo list app with categories",
            "completion": """import SwiftUI

@main
struct TodoApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    @State private var todos: [TodoItem] = []
    @State private var newTodoTitle = ""
    @State private var selectedCategory = TodoCategory.personal
    
    var body: some View {
        NavigationStack {
            VStack {
                // Add new todo
                HStack {
                    TextField("New todo", text: $newTodoTitle)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    
                    Picker("Category", selection: $selectedCategory) {
                        ForEach(TodoCategory.allCases, id: \\.self) { category in
                            Text(category.rawValue).tag(category)
                        }
                    }
                    .pickerStyle(MenuPickerStyle())
                    
                    Button("Add") {
                        addTodo()
                    }
                    .disabled(newTodoTitle.isEmpty)
                }
                .padding()
                
                // Todo list
                List {
                    ForEach(TodoCategory.allCases, id: \\.self) { category in
                        Section(header: Text(category.rawValue)) {
                            ForEach(todosForCategory(category)) { todo in
                                TodoRowView(todo: todo, toggleAction: {
                                    toggleTodo(todo)
                                })
                            }
                            .onDelete { offsets in
                                deleteTodos(at: offsets, category: category)
                            }
                        }
                    }
                }
            }
            .navigationTitle("My Todos")
        }
    }
    
    func addTodo() {
        let newTodo = TodoItem(
            title: newTodoTitle,
            category: selectedCategory
        )
        todos.append(newTodo)
        newTodoTitle = ""
    }
    
    func toggleTodo(_ todo: TodoItem) {
        if let index = todos.firstIndex(where: { $0.id == todo.id }) {
            todos[index].isCompleted.toggle()
        }
    }
    
    func todosForCategory(_ category: TodoCategory) -> [TodoItem] {
        todos.filter { $0.category == category }
    }
    
    func deleteTodos(at offsets: IndexSet, category: TodoCategory) {
        let todosInCategory = todosForCategory(category)
        for offset in offsets {
            if let index = todos.firstIndex(where: { $0.id == todosInCategory[offset].id }) {
                todos.remove(at: index)
            }
        }
    }
}

struct TodoItem: Identifiable {
    let id = UUID()
    var title: String
    var isCompleted = false
    var category: TodoCategory
}

enum TodoCategory: String, CaseIterable {
    case personal = "Personal"
    case work = "Work"
    case shopping = "Shopping"
}

struct TodoRowView: View {
    let todo: TodoItem
    let toggleAction: () -> Void
    
    var body: some View {
        HStack {
            Image(systemName: todo.isCompleted ? "checkmark.circle.fill" : "circle")
                .foregroundStyle(todo.isCompleted ? .green : .gray)
                .onTapGesture(perform: toggleAction)
            
            Text(todo.title)
                .strikethrough(todo.isCompleted)
                .foregroundStyle(todo.isCompleted ? .gray : .primary)
            
            Spacer()
        }
        .padding(.vertical, 4)
    }
}"""
        },
        {
            "prompt": "Create a SwiftUI calculator app",
            "completion": """import SwiftUI

@main
struct CalculatorApp: App {
    var body: some Scene {
        WindowGroup {
            CalculatorView()
        }
    }
}

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
}

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
}

enum CalculatorButton: String {
    case zero = "0", one = "1", two = "2", three = "3", four = "4"
    case five = "5", six = "6", seven = "7", eight = "8", nine = "9"
    case decimal = "."
    case add = "+", subtract = "-", multiply = "×", divide = "÷"
    case equals = "=", clear = "C", plusMinus = "+/-", percent = "%"
    
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
}

struct CalculatorButtonView: View {
    let button: CalculatorButton
    let action: () -> Void
    
    var buttonColor: Color {
        switch button {
        case .clear, .plusMinus, .percent:
            return Color(.lightGray)
        case .divide, .multiply, .subtract, .add, .equals:
            return .orange
        default:
            return Color(.darkGray)
        }
    }
    
    var textColor: Color {
        switch button {
        case .clear, .plusMinus, .percent:
            return .black
        default:
            return .white
        }
    }
    
    var body: some View {
        Button(action: action) {
            Text(button.rawValue)
                .font(.system(size: 32))
                .frame(width: buttonWidth(), height: buttonHeight())
                .background(buttonColor)
                .foregroundStyle(textColor)
                .clipShape(Circle())
        }
    }
    
    private func buttonWidth() -> CGFloat {
        button == .zero ? 148 : 70
    }
    
    private func buttonHeight() -> CGFloat {
        70
    }
}"""
        },
        {
            "prompt": "Add dark mode toggle to a SwiftUI app",
            "completion": """import SwiftUI

struct ContentView: View {
    @AppStorage("isDarkMode") private var isDarkMode = false
    
    var body: some View {
        NavigationStack {
            VStack {
                // Your existing content here
                
                // Dark mode toggle
                Toggle("Dark Mode", isOn: $isDarkMode)
                    .padding()
            }
            .navigationTitle("Settings")
            .preferredColorScheme(isDarkMode ? .dark : .light)
        }
    }
}"""
        },
        {
            "prompt": "Create a SwiftUI weather app with API integration",
            "completion": """import SwiftUI

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
}

@MainActor
class WeatherService: ObservableObject {
    @Published var currentWeather: Weather?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiKey = "YOUR_API_KEY"
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
        default: return "questionmark.circle"
        }
    }
}

struct Weather {
    let cityName: String
    let temperature: Double
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
}

struct WeatherCondition: Codable {
    let main: String
    let description: String
}"""
        }
    ]
    
    # Write training data
    with open(output_file, 'w') as f:
        for example in training_examples:
            f.write(json.dumps(example) + '\n')
    
    print(f"Created {output_file} with {len(training_examples)} training examples")
    print("This is sample data for testing the fine-tuning pipeline")
    print("For production, use the web scraper to collect more diverse data")

if __name__ == "__main__":
    create_sample_training_data()