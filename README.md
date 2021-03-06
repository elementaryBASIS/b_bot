# Project on Motivation bot: MISIS BASIS

MISIS BASIS: **Neto** – motivation bot, specially for [Netology](https://netology.ru)

# Table of content
-  [General description](#general-description)
-  [Structure](#struct)
-  [Running](#running)
-  [Testing](#testing)
-  [Closing remarks](#contact)

# General description <a name="general-description"></a>
This Telegram bot is considered to make you feel more confident and motivated about learning courses.

You will study more effectively with the special reflection program.
It is based on so-called **SSDL** system, which describes an average studying curve.
According to this system, *Neto* detects your current mental state and asks specific questions,
which help you to learn without struggle but with full understanding of the reason
why you are doing it.

![algo](media/algo.jpeg)
# Structure <a name="struct"></a>
Here are the structure of package, there you can find additional information:
- [**workspace**](workspace) all bot sources are here
- [**docker**](docker) docker file and running scripts
- [**neto pics**](workspace/neto_pics) mascot animations
- [**question database**](workspace/question_base) json files with questions and answers

# Running <a name="running"></a>
```bash
git clone https://github.com/elemtaryBASIS/b_bot
pyton3 -m pip install -r docker/requirements.txt # or run in docker instead
cd b_bot/workspace
python3 main.py
```
# Testing <a name="testing"></a>
You are able to test it now: [@netlogic_bot](https://t.me/netlogic_bot)
# Contact info <a name="contact"></a>
- Maintainer: [Yaroslav](https://github.com/atokagzx)
- Filling: [Artem](https://github.com/cymdaspec)
- Design: Anstasia
- Analyst:[Danya](https://github.com/triflt)
