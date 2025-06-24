# Zomato Restaurant Finder

> Hello! This project is a complete website and server for finding restaurants using Zomato's data. It was built to show skills in creating a backend, designing an API, working with databases, and making a modern, interactive website.

## What it Does

The goal was to build a useful and good-looking app. I started with the raw data, created an organized database for it, built a backend to send that data to the website, and finally designed a user-friendly site to display everything.

---

## Features

This app has a lot of cool features:

* **Modern Homepage:** A beautiful main page with animations that shows featured restaurants and different food categories.

* **Restaurant Details Page:** You can click on any restaurant to see its own special page with more information.

* **Easy Text Search:** A main search bar that lets you find restaurants by typing in a name or a type of food (like "Pizza" or "Burger").

* **Advanced Search Options:** A hidden panel slides out to let you filter restaurants by Country, price, and other specific details.

* **Search for Restaurants Nearby:** A very fast location search that finds all restaurants within a certain distance of you. This uses a special database tool called PostGIS to make it extra efficient.

* **Search with a Photo:** You can upload a picture of food, and the app uses an AI model to figure out what it is and then shows you restaurants that serve that dish.

* **Smart Page Loading:** The app loads restaurant lists page-by-page, so it always feels fast and responsive, even with thousands of restaurants.

* **Clean and Organized Code:** The code for the website is split into separate HTML, CSS, and JavaScript files, which is a professional practice that makes it easy to manage.

---

## Technology Used

| Category          | Technologies                                                    |
| ----------------- | --------------------------------------------------------------- |
| **Backend** | Python, Flask                                                   |
| **Database** | PostgreSQL with PostGIS                                         |
| **Frontend** | HTML, CSS, JavaScript                                           |
| **Other Tools** | Pandas (for data loading), Hugging Face (for image search AI)   |

---

## How to Run This Project

Here’s how you can get this application running on your computer.

### 1. What You Need

* Python 3

* PostgreSQL (version 14 is a good choice)

* An API Token (a password) from a Hugging Face account

### 2. How to Set it Up

1. **Download the code:**

   ```bash
   git clone [https://github.com/your-username/zomato-restaurant-app.git](https://github.com/your-username/zomato-restaurant-app.git)
   cd zomato-restaurant-app
   ```

2. **Install the required tools:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your database:**

   * Make sure your PostgreSQL server is running.

   * Create a new database and a user for this project.

   * Enter your database details into the `load_data.py` file.

4. **Load the data:**

   * Make sure the `zomato.csv` and `Country-Code.xlsx` files are in your project folder.

   * Run this command in your terminal:

     ```bash
     python3 load_data.py
     ```

5. **Set up the location search feature:**

   * Connect to your database.

   * Run these commands one by one:

     ```sql
     CREATE EXTENSION postgis;
     ALTER TABLE restaurants ADD COLUMN geog geography(POINT, 4326);
     UPDATE restaurants SET geog = ST_MakePoint(longitude, latitude)::geography;
     CREATE INDEX restaurants_geog_idx ON restaurants USING GIST (geog);
     ```

### 3. Run the App

1. **Add your details to the main app file:**

   * Open `app.py` and enter your database details.

   * Add your Hugging Face API Token to the `HF_API_TOKEN` variable.

2. **Start the server:**

   ```bash
   python3 app.py
   ```

3. **See the website:** Open your web browser and go to `http://127.0.0.1:5000/`

---

Thanks for taking a look at this project!
