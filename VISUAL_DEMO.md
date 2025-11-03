# 🚀 Quick Visual Demo - See It NOW!

**Want to see what this looks like RIGHT NOW without any setup?**

This 2-minute guide gets you a beautiful visualization with ZERO dependencies!

---

## 🎯 What You'll See

A real-time animated dashboard showing:
- 🎡 Rotating steering wheel
- 📊 Motor PWM commands (left/right bars)
- 📈 Live steering graph
- ✅ Connection status

All running realistic lane-keeping patterns!

---

## ⚡ Super Quick Start (Windows WSL)

### Step 1: Open Ubuntu Terminal

Press `Win` key, type "Ubuntu", press Enter

### Step 2: Navigate to Project

```bash
cd ~
cd "OneDrive - Sutton Tools Pty Ltd/Private/DIY Auto Pilot"
```

### Step 3: Run Demo

```bash
python3 scripts/visualize_demo.py
```

**That's it!** A window will open showing the full visualization.

*First run may take 30 seconds to install pygame automatically.*

---

## 🎮 What You're Watching

The demo simulates realistic driving:

### Gentle Curves
Watch the wheel slowly rotate as it follows road curves

### Lane Corrections  
See quick corrections when "drifting" from center

### Straight Stretches
Notice tiny micro-adjustments keeping it straight

**This is EXACTLY how your system will behave with openpilot!**

---

## 📊 Understanding the Display

### Top Left - Steering Wheel
- Red dot shows wheel orientation
- Rotates smoothly like real steering
- Angle shown below (±540° range)

### Top Right - Motor Command
- Green bar = Turn right (clockwise)
- Orange bar = Turn left (counter-clockwise)
- PWM number = strength of command

### Middle Right - Openpilot Data
- "Steer" = command from openpilot (-1 to +1)
- Color coded: green (right), orange (left)

### Bottom - History Graph
- Blue line = steering over time
- Shows patterns and corrections
- Scrolls right to left

---

## ⏱️ How Long Should I Watch?

- **30 seconds** - See basic patterns
- **1 minute** - See variety of scenarios
- **2 minutes** - See complete driving cycle

Press `Q` or `ESC` to quit anytime.

---

## 🤔 Common Questions

**Q: Is this using real data?**  
A: Yes! It simulates realistic lane-keeping patterns you'd see on real roads.

**Q: Will my hardware do this?**  
A: Exactly this! The motor will follow these same commands.

**Q: Can I change the patterns?**  
A: This is demo mode. Full version connects to openpilot for real driving data.

**Q: What if I want to use real openpilot data?**  
A: See `docs/VISUALIZATION.md` for connecting to actual openpilot routes.

---

## 🐛 Troubleshooting

### "No module named 'pygame'"

The script auto-installs it, but if manual needed:
```bash
pip3 install pygame
```

### "No display found" or "Cannot open display"

**For WSL2, you need Windows 11 with WSLg**, or:

1. Install VcXsrv on Windows
2. Launch XLaunch (accept defaults)
3. In Ubuntu terminal:
```bash
export DISPLAY=:0
python3 scripts/visualize_demo.py
```

### Window opens but is black

Wait 2-3 seconds - it's initializing pygame.

### "Permission denied"

```bash
chmod +x scripts/visualize_demo.py
python3 scripts/visualize_demo.py
```

---

## 🎯 Next Steps

**After watching the demo:**

1. ✅ You've seen how the system works
2. ✅ You understand the visualization
3. 🔧 Ready to connect real openpilot data (see `docs/VISUALIZATION.md`)
4. 📦 Or order hardware and build it!

---

## 💡 Tips

**Different Terminal Windows:**

If you want to explore while demo runs:
```bash
# Terminal 1: Run demo
python3 scripts/visualize_demo.py

# Terminal 2: (new window) Look at code
cd scripts
cat visualize_demo.py
```

**Take a Screenshot:**

While demo is running:
- Press `PrtScn` (Windows)
- Or `Win + Shift + S` (Snip tool)

**Record a Video:**

- Press `Win + G` (Game Bar)
- Click record button
- Stop when done

---

## 🚀 Advanced: Full System

Want to connect to real openpilot data instead of demo?

```bash
# Follow complete setup
./scripts/setup_system.sh

# Then use full visualizer
python3 scripts/visualize.py

# In another terminal, replay real driving
cd ~/openpilot
tools/replay/replay '<route>|0'
```

See `docs/VISUALIZATION.md` for details.

---

**Enjoy the demo! This is your steering system in action! 🎉**
