# **Bitpanda Portfolio Telegram Bot** 📊🤖

A powerful **Telegram bot** that allows you to **track your Bitpanda portfolio**, check balances, view profits, and get live crypto prices—all within Telegram.

## **Features** ✨

✅ **Secure Login**: Users log in with their Bitpanda API key.  
✅ **Portfolio Balance**: Check your total or asset-specific balance.  
✅ **Profit Tracking**: View profit/loss for specific assets or the entire portfolio.  
✅ **Live Crypto Prices**: Get real-time cryptocurrency prices.  
✅ **Inline Commands**: Use `@bitpanda_portfoli_bot share` to share the bot with others.  
✅ **Secure API Key Storage**: API keys are **encrypted** before being stored.  
✅ **Logout Feature**: Remove your API key from the bot anytime.

---

## **Installation** 🛠️

### **1️⃣ Clone the Repository**

```sh
git clone https://github.com/loughness/bitpanda-telegram-bot.git
cd bitpanda-telegram-bot
```

### **2️⃣ Create a Virtual Environment (Optional but Recommended)**

```sh
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### **3️⃣ Install Dependencies**

```sh
pip install -r requirements.txt
```

### **4️⃣ Set Up Environment Variables**

1. **Create a `.env` file** inside the `src/` folder.
2. **Add your bot token and encryption key:**
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   ENCRYPTION_KEY=your_generated_encryption_key_here
   ```
3. **Make sure the `.env` file is in `.gitignore`** to prevent exposing secrets.

---

## **Usage** 🚀

### **Start the Bot**

```sh
python src/bot.py
```

### **Login (Set Your Bitpanda API Key)**

In Telegram, send:

```
/login YOUR_BITPANDA_API_KEY
```

✅ **Your API key is securely stored using encryption**.

### **Check Your Portfolio Balance**

🔹 **Total balance**:

```
/balance
```

🔹 **Specific asset (e.g., BTC)**:

```
/balance BTC
```

### **View Your Profit/Loss**

🔹 **Bitcoin profit in the last 7 days**:

```
/profit BTC --7d
```

🔹 **All-time profit for your entire portfolio**:

```
/profit --all-time
```

### **Get Live Crypto Prices**

🔹 **Bitcoin price**:

```
/price BTC
```

🔹 **Ethereum price**:

```
/price ETH
```

### **Set a Price Alert**

🔹 **Notify me when BTC drops below €40,000**:

```
/alerts BTC 40000
```

### **Logout (Remove API Key)**

```
/logout
```

✅ **Your API key will be deleted from the database**.

---

## **Inline Features** 🔎

You can use the bot **inside any chat** by mentioning it:

```
@bitpanda_portfoli_bot share
```

This posts a **pre-written message** promoting the bot.

---

## **Security & Notes** 🔐

- **Your API key is encrypted before being stored.**
- **Use `/logout` to delete your API key anytime.**
- **Ensure your `.env` file is ignored in `.gitignore` to prevent leaking sensitive info.**
- **API rate limits apply—check Bitpanda’s API docs for details.**

---

## **Contributing** 🤝

Feel free to **fork this repo** and submit a **pull request** if you want to improve it!  
If you find a bug, **open an issue** on GitHub.

---

## **License** 📜

This project is licensed under the **MIT License**.

---

📌 **Thank you for using the Bitpanda Portfolio Telegram Bot!** 🚀💰
