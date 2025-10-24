# ⚡ MegaBonk Shop Scanner

A memory scanner tool for MegaBonk that helps you view all available shop items and their prices during your runs.

![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## 🎮 How to Use

### Download & Run (Recommended)

1. **Download** the latest `MegaBonk Shop Scanner.exe` from the [Releases](../../releases) page
2. **Launch MegaBonk** and start a run
3. **Run the scanner** executable
4. **First Time Setup:**
   - Click **"FULL SCAN"** button
   - This will take **1-2 minutes** as it learns shop memory locations
   - Wait for the scan to complete
5. **Subsequent Runs:**
   - Just click **"QUICK SCAN"** 
   - Scan completes in seconds using learned locations
   - View all shops and items instantly!

### What You'll See

The scanner displays:
- 🏪 All shop instances in your current run
- 💰 Item prices
- ⭐ Item rarities (Common, Rare, Epic, Legendary)
- 📝 Item descriptions
- ✓ Whether you've already visited the shop

## ⚠️ Disclaimer

**THIS IS AN UNOFFICIAL, COMMUNITY-CREATED TOOL**

- ❌ Not officially supported or endorsed by MegaBonk developers
- ❌ Use at your own risk
- ❌ May break with game updates
- ⚠️ Could potentially trigger anti-cheat systems (though unlikely as it's read-only)
- 📋 The author is not responsible for any consequences of using this tool

This tool only **reads** game memory and does not modify anything. However, proceed with caution.

## 🛠️ For Developers

### Requirements

```bash
pip install pymem tkinter
```

### Project Structure

```
MegaBonk-Shop-Scanner/
├── scanner.py      # Memory scanning logic
├── gui.py          # GUI interface
└── README.md
```

### Running from Source

```bash
python gui.py
```

### Building Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "MegaBonk Shop Scanner" gui.py
```

The executable will be in the `dist/` folder.

### How It Works

1. **Full Scan**: Searches all readable/writable memory regions for shop structures
2. **Pattern Matching**: Identifies shops by their memory structure (pointers, rarity values, item lists)
3. **Learning**: Saves regions where shops were found to `shop_scanner_config.json`
4. **Quick Scan**: Only scans previously learned regions for instant results

## 🤝 Contributing

Contributions are welcome! Feel free to: 
- 🐛 Report bugs via Issues
- 💡 Suggest features
- 🔧 Submit pull requests
- 📖 Improve documentation

## 📜 License

**Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**

You are free to:
- ✅ Share — copy and redistribute the material
- ✅ Adapt — remix, transform, and build upon the material

Under the following terms:
- 📝 **Attribution** — You must give appropriate credit
- 🚫 **NonCommercial** — You may not use the material for commercial purposes without permission
- 🔓 **No additional restrictions**

For commercial use, please contact the repository owner.

Full license text: https://creativecommons.org/licenses/by-nc/4.0/

## 🙏 Acknowledgments

- Built with [Pymem](https://github.com/srounet/Pymem) for memory reading
- Thanks to the MegaBonk community

## 📞 Support

- 🐛 **Bug Reports**: [Open an Issue](../../issues)
- 💬 **Questions**: [Discussions](../../discussions)

---

**Made with ❤️ for the MegaBonk community**

*Last updated: 2025*