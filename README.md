# Hobby Tracker CS50 Final Project
#### Video Demo: <https://youtu.be/AONrw-ohgVg>
#### Description:

This hobby tracker app was made for my CS50 final project. It is a full-stack web app made with Python, Flask, JavaScript, HTML, CSS, and Bootstrap. Many people want to become disciplined; many people want to start new hobbies, but many people also don't know how to start. More importantly, if they start, they don't know how to hold themselves accountable. Therefore, I built this web app in the hopes of helping people stay consistent and disciplined with their habits. This hobby tracker web app allows users to add hobbies they're interested in, set a goal, and work towards achieving this goal. After a user creates a hobby, they are then allowed to log any sessions of this hobby by choosing the hobby they just did, the amount of time they spent on it, how much they enjoyed it, and any personal notes.

---

### Key Features & Technical Highlights

* **User Authentication:**  
  I implemented modern, sleek-looking registration and login pages (`/register` and `/login`). First, the user registers with a username and password, but must repeat their password twice in order to confirm it. All of this data is validated first before allowing the user to continue to the next step. I included my validation checks in both the frontend and backend of the web app to reduce any possibilities of unwanted or unexpected data. After the user successfully registers, his username is stored, and for safety measures, only the user's hashed password (which was hashed using the Werkzeug library) is stored before being allowed to log in. The user enters his username and password, which once again are validated both in the frontend and backend to reduce errors, and if all is correct, he is then directed to the home page (`/`) of the web app.

* **Dynamic Cover Images:**  
  After a user adds a hobby to his account on the `/add_hobby` page, this hobby appears in the dashboard (`/`) as a card. In order to make the web app more vivid and lively, I wanted each hobby added to have a picture. However, since I cannot guess the hobby the user will add, I had to look for an API to which I can send the hobby name, and it will return a relevant picture to me; so, I ended up using the Unsplash API. In conclusion, I integrated the Unsplash API to fetch relevant images based on hobby names. The first image received was placed at the top of the hobby card in the dashboard, and this same image was also used as a background in the `/log` page. When a user visits the session logging page and chooses which hobby he wants to log but still hasn't filled out the rest of the form, the background automatically changes from black to the hobby-related image.

* **Glassmorphic UI:**  
  From the frontend side, my main goal was to make everything look clean, sleek, modern, and glassy. As a fan of dark mode, I also made sure the main theme of this web app was dark. Using some education I received on UI/UX and some visual feeding off of websites like "Mobbin" and "Dribbble", I was able to envision how exactly I wanted my web app to look, what vibe to give off, and how interactive I wanted my web app to be. Therefore, I overrode standard CSS with my custom CSS for blurred backgrounds, expandable and collapsible cards, and responsive dark layouts.

* **Dynamic Quotes:**  
  Since this is a hobby tracking web app, whenever the user visits the web app, I wanted to encourage them, give them some positive energy, and at the same time spread some warm, friendly energy. Therefore, I implemented a feature where, on the home/dashboard page (`/`), I greet the user with random quotes which I fetched from the "ZenQuotes API".

* **Live Activity Timer:**  
  In the `/log` page, I added a feature using JavaScript where, when a user logs a session, they can start a real-time session tracker, which is a stopwatch that they can start, pause, and end.

* **Weekly Progress Aggregation:**  
  I added a tracker which sums up, based on the logged sessions, how much you've performed a certain hobby and shows it to the user to allow them to compare their current progress with the goal they set for this specific hobby—all of which is displayed on the hobby card in the dashboard (`/`).

* **Log History and CSV Export:**  
  In the `/history` page, I present a complete activity audit log with star ratings, notes, and dynamic file streaming to the user. A button on the top, "Export to CSV" (`/export`), allows the user to download all of this log history as a CSV file for personal use.

---

### File Structure and Design Choices

1. **`app.py`:**  
   The main Flask application controller containing all route handlers (`/`, `/register`, `/login`, `/logout`, `/add_hobby`, `/log`, `/history`, `/export`, `/delete`). It manages user sessions, database transactions, and date arithmetic for weekly progress calculations.

2. **`helpers.py`:**  
   Since I wanted to keep `app.py` mainly for the routes a user can take in the web app, I left any other functions in a file called `helpers.py`. I took this idea from a previous CS50 assignment. `helpers.py` includes functions I manually created in order to reduce redundant code in `app.py` and any API fetching functions. Additionally, inside these API fetching functions, as a safety measure, I included fallback error handling. For example, if the Unsplash API was unable to return an image relevant to the hobby name for any reason, a fallback image was ready to be placed. The ZenQuotes API also had fallback error handling where a fallback quote would appear to the user.

3. **`hobbies.db`:**  
   My database `hobbies.db` includes 3 tables:
   * **`users`**: `id` (PRIMARY KEY), `username`, `hash`
   * **`hobbies`**: `id` (PRIMARY KEY), `user_id` (FOREIGN KEY), `hobby_name`, `measure_type`, `goal`, `image_url`
   * **`logs`**: `id` (PRIMARY KEY), `user_id` (FOREIGN KEY), `hobby_id` (FOREIGN KEY), `amount`, `logged_at`, `rating`, `notes`

4. **`static/style.css`:**  
   Custom CSS overrides that establish the dark glassmorphic design system, defining `.glass-card`, `.glass-input`, custom backdrop filters (`blur(12px)`), hover state transitions, and responsive grid behaviors.

5. **`static/script.js`:**  
   Client-side JavaScript responsible for driving the live stopwatch on `/log` (start, pause, reset mechanics) and dynamically updating theme backgrounds when options change.

6. **`templates/` directory:**  
   Contains Jinja2 HTML templates inheriting from `layout.html` (`index.html`, `add_hobby.html`, `log.html`, `history.html`, `login.html`, `register.html`).

---

### Challenges Overcome and Design Debates
* **Table or Cards for hobbies:**  
My first debate was whether the dashboard should show the hobbies as cards or tables. Tables offered a structured view similar to CS50 Finance, but cards allowed for custom cover photos, collapsible sections, and individual weekly progress highlights that made the UI feel significantly more modern and interactive.

* **API Key Security & Environment Configuration:**  
  When integrating external services like the Unsplash API, I initially faced a challenge with securing sensitive credentials while pushing code to GitHub. To prevent committing hardcoded API keys directly to version control, I implemented environment variable management using `.env` files and `python-dotenv`. This allowed the app to securely load API credentials locally while ensuring secret keys remained private and unexposed in public repositories.

---

### How To Run The Application

1. **Clone the repository:**
```bash
git clone <YOUR_REPOSITORY_URL>
cd hobby_tracker
```
   
2. **Install required dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables:**
Create a .env file in the root directory and add your keys:
```bash
UNSPLASH_ACCESS_KEY=your_unsplash_api_key
```

4. **Run Flask development server:**
```bash
flask run
```