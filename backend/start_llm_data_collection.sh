#!/bin/bash
# Start LLM Data Collection - Runs all scrapers in parallel

echo "=================================="
echo "SwiftGen LLM Data Collection"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create log directory
mkdir -p logs

# Function to check if script exists
check_script() {
    if [ ! -f "$1" ]; then
        echo -e "${YELLOW}Warning: $1 not found${NC}"
        return 1
    fi
    return 0
}

# Start general Swift code scraper
echo -e "\n${BLUE}1. Starting Swift Code Scraper...${NC}"
if check_script "swift_code_scraper.py"; then
    # Run in background with logging
    nohup python3 swift_code_scraper.py > logs/swift_scraper.log 2>&1 &
    SWIFT_PID=$!
    echo -e "${GREEN}✓ Swift scraper started (PID: $SWIFT_PID)${NC}"
    echo "   Log: logs/swift_scraper.log"
fi

# Start UI-focused scraper
echo -e "\n${BLUE}2. Starting UI Code Scraper...${NC}"
if check_script "ui_code_scraper.py"; then
    # Run in background with logging
    nohup python3 ui_code_scraper.py > logs/ui_scraper.log 2>&1 &
    UI_PID=$!
    echo -e "${GREEN}✓ UI scraper started (PID: $UI_PID)${NC}"
    echo "   Log: logs/ui_scraper.log"
fi

# Create sample training data as backup
echo -e "\n${BLUE}3. Creating sample training data...${NC}"
if check_script "create_sample_training_data.py"; then
    python3 create_sample_training_data.py
    echo -e "${GREEN}✓ Sample data created${NC}"
fi

# Show monitoring commands
echo -e "\n${BLUE}Monitor Progress:${NC}"
echo "  tail -f logs/swift_scraper.log    # General Swift code"
echo "  tail -f logs/ui_scraper.log       # UI-focused code"

echo -e "\n${BLUE}Check Collection Status:${NC}"
echo "  ls -la swift_training_data/       # Swift code collected"
echo "  ls -la ui_training_data/          # UI code collected"

echo -e "\n${BLUE}Stop Scrapers:${NC}"
if [ ! -z "$SWIFT_PID" ]; then
    echo "  kill $SWIFT_PID                   # Stop Swift scraper"
fi
if [ ! -z "$UI_PID" ]; then
    echo "  kill $UI_PID                      # Stop UI scraper"
fi

# Save PIDs for later reference
echo -e "\n${BLUE}Saving process IDs...${NC}"
echo "$SWIFT_PID" > logs/swift_scraper.pid
echo "$UI_PID" > logs/ui_scraper.pid

echo -e "\n${GREEN}Data collection started successfully!${NC}"
echo "Scrapers are running in the background."
echo "This process may take several hours depending on GitHub rate limits."
echo ""
echo "Next steps:"
echo "1. Let scrapers run for 4-6 hours"
echo "2. Check collected data quality"
echo "3. Run training pipeline: python3 llama_finetuning_pipeline.py --train"
echo ""
echo "=================================="