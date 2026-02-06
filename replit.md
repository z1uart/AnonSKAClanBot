# replit.md

## Overview

This is a **Telegram bot for anonymous messaging** built for the SKA Clan community. The bot allows users to anonymously send messages (text, photos, videos, voice messages, video notes, stickers) to a channel administrator. The admin can reply back to users through the bot. All anonymous messages are logged to a text file for record-keeping.

The project is written in Python using the `python-telegram-bot` library. It's currently partially implemented — the core structure exists but `bot.py` and `main.py` are incomplete and need to be finished.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Project Structure
- **`main.py`** — Entry point that should import and run the bot
- **`bot.py`** — Core bot logic: conversation handlers, command handlers, message forwarding, admin reply functionality
- **`config.py`** — Configuration loader that reads environment variables from `.env`
- **`logger.py`** — Message logging utility that writes anonymous messages to a text file
- **`user_stats.json`** — JSON file storing per-user message count statistics
- **`anonymous_log.txt`** — Plain text log of all anonymous messages received

### Bot Architecture
- **Conversation-based flow** using `python-telegram-bot`'s `ConversationHandler` with states: `CHOOSING` (main menu) and `SENDING_MESSAGE` (composing a message)
- **Main menu** has three options via `ReplyKeyboardMarkup`: "Write a message", "Statistics", and "Help"
- **Anonymous message forwarding**: Users send messages to the bot → bot forwards them to the admin (identified by `ADMIN_ID`) → admin can reply by replying to the forwarded message → bot delivers the reply back to the original sender
- **Supported message types**: text, photo, video, voice, video note, sticker
- **Maintenance mode**: Configurable via `BOT_MAINTENANCE_MODE` env var; when enabled, only the admin can use the bot

### Configuration Pattern
- Uses `python-dotenv` to load `.env` file
- Required environment variables:
  - `BOT_TOKEN` — Telegram Bot API token (obtained from @BotFather)
  - `ADMIN_ID` — Telegram user ID of the administrator (integer)
  - `BOT_MAINTENANCE_MODE` — Optional, set to `"true"` to enable maintenance mode

### Data Storage
- **No database** — all data is stored in flat files
- `user_stats.json`: Simple JSON dictionary mapping user ID strings to message counts
- `anonymous_log.txt`: Append-only text log with sequential message IDs, user info, timestamps, and message content
- The logger records: user's first/last name, username, user ID, timestamp, message type, and content — this is for admin reference only and is not exposed to users

### Key Design Decisions
1. **Flat file storage over database**: Chosen for simplicity since the bot serves a single community/admin. Trade-off is no concurrent write safety and limited query capability, but sufficient for this scale.
2. **Single admin model**: Only one admin (defined by `ADMIN_ID`) receives and responds to messages. This keeps the architecture simple but limits scalability.
3. **Reply mechanism**: The admin replies to forwarded messages in their chat with the bot, and the bot routes the reply back to the original anonymous sender. This requires tracking which forwarded message corresponds to which user (typically stored in `context.bot_data` or similar).
4. **Russian language UI**: All user-facing text is in Russian, matching the SKA Clan community.

## External Dependencies

### Python Packages
- **`python-telegram-bot`** — Core Telegram Bot API wrapper (v20+ with async support based on the `async/await` pattern in the code)
- **`python-dotenv`** — Loads environment variables from `.env` file

### External Services
- **Telegram Bot API** — The bot communicates with Telegram's servers; requires a valid bot token from @BotFather
- No database services, no web servers, no other external APIs

### Environment Variables Required
| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Telegram bot token from BotFather |
| `ADMIN_ID` | Yes | Telegram user ID of the admin (integer) |
| `BOT_MAINTENANCE_MODE` | No | Set to `"true"` to block non-admin users |