# SwiftGen Quick Reference Card

## 🚀 GitHub Repository
**URL**: https://github.com/hirakCoder/Swiftgen.git

## 🎯 Important Branches
- **stable-baseline-july15** - Our stable reference point (USE THIS!)
- **stable-v1.0** - First stable version
- **main** - Development branch

## ✅ To Return to Stable Baseline
```bash
git fetch origin
git checkout stable-baseline-july15
git pull origin stable-baseline-july15
```

## 🔧 To Start Fresh from Baseline
```bash
# Clone the repository
git clone https://github.com/hirakCoder/Swiftgen.git
cd Swiftgen

# Switch to stable baseline
git checkout stable-baseline-july15

# Set up environment
cd backend
cp .env.example .env  # Edit with your API keys

# Start the server
python main.py
```

## 📝 Key Files
- **MASTER_SYSTEM_STATUS.md** - Complete system documentation
- **STABLE_BASELINE_README.md** - What's in the baseline
- **backend/.env** - API keys (create from .env.example)

## 🎭 If Things Go Wrong
1. Stash current changes: `git stash`
2. Return to baseline: `git checkout stable-baseline-july15`
3. Pull latest: `git pull origin stable-baseline-july15`
4. Start fresh!

---
**Remember**: The `stable-baseline-july15` branch is your safe harbor!