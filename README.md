# Internship

This is a repository that auto-crawls new companies' names from [CSE](https://internship.cse.hcmut.edu.vn/) and sends a notification via a [Telegram bot](https://t.me/CampInternshipbot).

| Status | Message Structure |
| --- | --- |
| Have new company | 📢 Có `<number>` công ty mới được thêm vào:<br>✅ `<name> of the first company`<br>✅ `<name> of the second company` |
| Don't have new company | ❌ Chưa có công ty nào được thêm vào |

# How to run it locally?

1. Clone this repository.

```bash
git clone https://github.com/Hailam2104/Internship
```

2. Cd to **Internship** directory

```bash
cd Internship
```

3. Create `.env` file like this

```bash
# Your telegram bot token
TELEGRAM_BOT_TOKEN = <token>

# Your telegram ID
MY_TELEGRAM_ID = <id>

# Your fernet key used for Symmetric Encryption
FERNET_KEY = <key>
```

4. Install all dependences

```bash
pip install -r requirements.txt
```

5. Start program

```bash
python ./campInternship.py
```
