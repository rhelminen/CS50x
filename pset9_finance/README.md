# Problem Set 9 - Finance

https://cs50.harvard.edu/x/2021/psets/9/finance/

This web app lets you buy and sell stocks in a fake-money portfolio, pulling market data from an API. It is made with Flask (python) and SQLite on the back-end and HTML and CSS (with quite a bit of Bootstrap) on the front-end. JavaScript wasn't required for the assignment, but I did write a couple of JS functions as well.

The main things provided in the distribution code were `layout.html` (and some CSS), `helpers.py` and the skeleton of `application.py`, where `login()` and `logout()` had been implemented already. Most of the other functions and templates were fully implemented by me, and I did make small tweaks to a lot of the distribution code as well (except for helpers.py, which I didn't touch at all).

I added a lot of extra features to this on top of the required features. Probably the biggest extra feature I implemented was profit/loss calculation by keeping track of the user's cost basis on each stock. I felt it was such an integral part of any stock trading app that I had to implement it, even though it wasn't required. I also got a few ideas from the staff's suggestions for extra features and implemented them on a new settings.html page.

I spent most of my time working on the back-end, making sure that the database is designed well and that everything works as it should. This was my first time working with flask, or any kind of back-end framework, so it did take a while to familiarize myself with it. The [CS50 staff's implementation of the website](https://finance.cs50.net/) made heavy use of the `apology()` function on the back-end, but I tried to design my HTML in such a way that incorrect user input will in most cases be caught before reaching the back-end. I did of course also implement back-end checks for every scenario I could think of in case the user is messing with the HTML using their browser's dev tools. Go ahead and try to submit information outside the accepted values in the forms ;)

I also added a password strength meter in JavaScript just for fun. Coming up with the scoring formula was a lot of fun, and I think it turned out to be quite usable. I didn't feed it dictionary data or anything, so it is mostly based on password length and special characters etc., but it does seem to give pretty accurate scores (imo). Although of course I would think that the scores are accurate since I created it! :grin: So try out a couple of different passwords and see what you think.

This was definitely a fun project to work on, and I still have a lot of feature ideas that I would like to add to it. I might even turn it into a full-fledged portfolio tracking app at some point with good-looking charts and everything!

## HOW TO USE

1. Make sure you have all the required libraries installed (cs50, Flask, Flask-Session, requests). Alternatively, you can use the [CS50 IDE](https://ide.cs50.io) with your github account, where all the required libraries should be installed by default.

2. Get an API key from IEX
    * Visit https://iexcloud.io/cloud-login#/register/.
    * Select the “Individual” account type, then enter your email address and a password, and click “Create account”.
    * Once registered, scroll down to “Get started for free” and click “Select Start” to choose the free plan.
    * Once you’ve confirmed your account via a confirmation email, visit https://iexcloud.io/console/tokens.
    * Copy the key that appears under the Token column (it should begin with pk_).
    * In a terminal window, execute:
        ```
        $ export API_KEY=YOUR_API_KEY_HERE
        ```
        (or use your preferred method of working with environment variables)

3. Tell Flask what file to work with by executing the following command in a terminal window:
    ```
    $ export FLASK_APP=application.py
    ```
    If that doesn't work, see https://flask.palletsprojects.com/en/1.1.x/quickstart/ for help.

4. Execute:
    ```
    $ flask run
    ```
