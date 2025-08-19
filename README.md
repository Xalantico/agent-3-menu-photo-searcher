# 🍕 Lexia Food Menu Analyzer

> AI agent that analyzes food menu photos and finds food images online using Serper API

## 🎯 What's This?

Ever wondered what that mysterious dish on a menu actually looks like? This fun AI agent does exactly that! Upload a food menu photo, and watch as it:

- 🔍 **Analyzes** the menu using AI vision
- 🍽️ **Extracts** all the food names
- 🌐 **Searches** the internet for photos of each dish
- 📱 **Shows** you beautiful food images inline
- 🔗 **Lets you click** to open full-size photos in new tabs

## 🚀 Features

- **Real-time streaming** - See results as they're found!
- **Inline image display** - Beautiful food photos right in the chat
- **Clickable links** - Open any photo in a new tab
- **Smart food extraction** - Handles various menu formats
- **Internet photo search** - Powered by Serper API
- **Markdown formatting** - Clean, professional presentation

## 🎬 Inspiration

This project was inspired by [Andrej Karpathy's amazing talk "Software Is Changing (Again)"](https://www.youtube.com/watch?v=LCEmiRjPEtQ).Watch the video, worth a million. 

## 🛠️ Tech Stack

- **Lexia Platform** - AI agent infrastructure
- **OpenAI Vision** - Menu image analysis
- **Serper API** - Internet photo search
- **FastAPI** - Web framework
- **Python** - Backend logic
- **Markdown** - Beautiful formatting

## 🚀 Quick Start

1. **Clone the repo**
   ```bash
   git clone https://github.com/Xalantico/agent-3-menu-photo-searcher.git
   cd agent-3-menu-photo-searcher
   ```

2. **Set up environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   - Set `SERPER_API_KEY` in your Lexia project variables
   - Ensure OpenAI API key is configured in your Lexia project variables

4. **Run the agent**
   ```bash
   python main.py
   ```

5. **Upload a food menu photo** and watch the magic happen! 🎉

## 🎨 How It Works

1. **Upload** a food menu photo to your Lexia chat
2. **AI analyzes** the image to detect if it's a food menu
3. **Food names** are extracted from the menu
4. **Internet search** finds photos for each dish
5. **Real-time streaming** shows results as they're found
6. **Beautiful display** with inline images and clickable links

## 🤝 Contributing

**This is a fun project and we'd love your contributions!** 🎉

### Ways to Contribute

- 🐛 **Bug fixes** - Found an issue? Fix it!
- ✨ **New features** - Have a cool idea? Build it!
- 📚 **Documentation** - Make things clearer for everyone
- 🎨 **UI improvements** - Make it look even better
- 🧪 **Testing** - Help ensure everything works smoothly
- 💡 **Ideas** - Share your thoughts and suggestions

### Getting Started

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Contribution Ideas

- Add support for more menu formats
- Implement food category classification
- Add nutritional information lookup
- Create a web interface
- Add multi-language support
- Implement food rating/review system
- Add dietary restriction filtering

## 📸 Example Output

```
# 🍽️ Food Menu Analysis Results

## 🍕 Sopa Miso
📸 ![Sopa Miso](https://example.com/miso-soup.jpg)

🔗 **[Click to open in new tab](https://example.com/miso-soup.jpg)**

---

## 🍕 Tempura Mixta
📸 ![Tempura mixta](https://example.com/tempura.jpg)

🔗 **[Click to open in new tab](https://example.com/tempura.jpg)**

---
```

## 🎯 Use Cases

- **Food bloggers** - See what dishes look like before ordering
- **Travelers** - Understand foreign language menus
- **Food enthusiasts** - Discover new dishes and their appearances
- **Restaurant reviewers** - Document menu items with photos
- **Language learners** - Connect food names with visual representations

## 🚧 Current Limitations

- Works best with clear, readable menu photos
- Limited to first 10 food items for performance
- Requires internet connection for photo search
- Photo quality depends on Serper API results

## 🔮 Future Ideas

- **Multi-language menu support**
- **Food allergy detection**
- **Price estimation**
- **Nutritional information**
- **Recipe suggestions**
- **Restaurant recommendations**
- **Social sharing features**

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Andrej Karpathy** - For the inspiring talk that sparked this project
- **Lexia Team** - For the amazing AI agent platform
- **OpenAI** - For the powerful vision capabilities
- **Serper** - For the internet search API
- **All contributors** - For making this project better!

## 🎉 Have Fun!

This project is all about having fun with AI and making food discovery more engaging. Whether you're contributing code, testing features, or just using the agent, we hope you enjoy it!

---

**Made with ❤️ and 🍕 by the open source community**

*Questions? Ideas? Want to chat? Open an issue or join the discussion!*
