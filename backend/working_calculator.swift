import SwiftUI

struct CalculatorApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    @State private var display = "0"
    @State private var currentNumber = 0.0
    @State private var previousNumber = 0.0
    @State private var currentOperation: Operation? = nil
    
    enum Operation {
        case add, subtract, multiply, divide
    }
    
    var body: some View {
        VStack(spacing: 12) {
            // Display
            Text(display)
                .font(.system(size: 64))
                .lineLimit(1)
                .minimumScaleFactor(0.5)
                .frame(maxWidth: .infinity, alignment: .trailing)
                .padding()
            
            // Buttons
            VStack(spacing: 12) {
                HStack(spacing: 12) {
                    CalculatorButton(text: "C", action: clear)
                    CalculatorButton(text: "+/-", action: toggleSign)
                    CalculatorButton(text: "%", action: percentage)
                    CalculatorButton(text: "÷", action: { setOperation(.divide) })
                }
                
                HStack(spacing: 12) {
                    CalculatorButton(text: "7", action: { numberTapped(7) })
                    CalculatorButton(text: "8", action: { numberTapped(8) })
                    CalculatorButton(text: "9", action: { numberTapped(9) })
                    CalculatorButton(text: "×", action: { setOperation(.multiply) })
                }
                
                HStack(spacing: 12) {
                    CalculatorButton(text: "4", action: { numberTapped(4) })
                    CalculatorButton(text: "5", action: { numberTapped(5) })
                    CalculatorButton(text: "6", action: { numberTapped(6) })
                    CalculatorButton(text: "-", action: { setOperation(.subtract) })
                }
                
                HStack(spacing: 12) {
                    CalculatorButton(text: "1", action: { numberTapped(1) })
                    CalculatorButton(text: "2", action: { numberTapped(2) })
                    CalculatorButton(text: "3", action: { numberTapped(3) })
                    CalculatorButton(text: "+", action: { setOperation(.add) })
                }
                
                HStack(spacing: 12) {
                    CalculatorButton(text: "0", action: { numberTapped(0) })
                        .frame(maxWidth: .infinity)
                    CalculatorButton(text: ".", action: addDecimal)
                    CalculatorButton(text: "=", action: calculate)
                }
            }
            .padding()
        }
        .background(Color.black)
        .foregroundColor(.white)
    }
    
    func numberTapped(_ number: Int) {
        if display == "0" {
            display = String(number)
        } else {
            display += String(number)
        }
        currentNumber = Double(display) ?? 0
    }
    
    func clear() {
        display = "0"
        currentNumber = 0
        previousNumber = 0
        currentOperation = nil
    }
    
    func setOperation(_ operation: Operation) {
        currentOperation = operation
        previousNumber = currentNumber
        display = "0"
    }
    
    func calculate() {
        guard let operation = currentOperation else { return }
        
        switch operation {
        case .add:
            currentNumber = previousNumber + currentNumber
        case .subtract:
            currentNumber = previousNumber - currentNumber
        case .multiply:
            currentNumber = previousNumber * currentNumber
        case .divide:
            if currentNumber != 0 {
                currentNumber = previousNumber / currentNumber
            }
        }
        
        display = String(format: "%g", currentNumber)
        currentOperation = nil
    }
    
    func toggleSign() {
        currentNumber = -currentNumber
        display = String(format: "%g", currentNumber)
    }
    
    func percentage() {
        currentNumber = currentNumber / 100
        display = String(format: "%g", currentNumber)
    }
    
    func addDecimal() {
        if !display.contains(".") {
            display += "."
        }
    }
}

struct CalculatorButton: View {
    let text: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(text)
                .font(.system(size: 32))
                .frame(width: 80, height: 80)
                .background(Color.gray.opacity(0.3))
                .cornerRadius(40)
        }
    }
}
