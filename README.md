# Vakantieveilingen Bot

This script checks the highest bid right before an auction expires and places your bid two euro higher. A selenium docker with headless firefox is used to place the bid. It doesn't guarantee your win because of latency and/or someone placing a bid right after the latest check from the script before it places its bid.

## How it works
1. Pull this repo
2. Install Docker on your local machine
3. From Docker Hub pull image `selenium/standalone-firefox`
4. After building run the container `docker run -it -p 4444:4444 selenium/standalone-firefox`
5. Install requirements `pip install selenium requests`
6. Run the script e.g. `python vakantieveiling_bot.py --username 'xxxxxxxxxx@gmail.com' --password 'xxxxxxxxx' --url-auction 'https://www.vakantieveilingen.nl/beauty/wellnessresorts/saunabon-iii_belgie.html' --max-price '28'`
