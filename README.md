# Discord Bot

A Discord bot for managing and displaying song scores.

## Features

- Add and remove songs with scores.
- Display the best 30 songs with ratings.
- Calculate and show average ratings.

## Setup

### Prerequisites

- Python 3.6+
- Discord account and server
- Discord bot token

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot:**

   - Create a `config.json` file in the root directory:

     ```json
     {
         "DISCORD_BOT_TOKEN": "YOUR_DISCORD_BOT_TOKEN"
     }
     ```

   - Alternatively, set the `DISCORD_BOT_TOKEN` as an environment variable.

4. **Run the bot:**

   ```bash
   python bot.py
   ```

## Usage

- **Add a song:** `!addsong`
- **Remove a song:** `!rmsong`
- **Show best 30 songs:** `!b30`

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes and commit them: `git commit -m 'Add feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Submit a pull request.

## License

This project is licensed under the MIT License.
