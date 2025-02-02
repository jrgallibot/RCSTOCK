# 🛒 Web Scraping and Drone Price Tracking Dashboard  

## 🛠 Project Description  
This project is a **web scraping system** that collects information about **drones** from various online stores registered in the system. The scraped data is displayed in a **dashboard**, where users can see:  

✅ **Top 10 drones ranked** based on price, reviews, or popularity  
✅ **Real-time stock updates** (if a drone is available or out of stock)  
✅ **Historical price trends** (optional feature)  

The system **automates scraping and updates drone listings** at regular intervals.  

---

## 🚀 Key Features  

### 1️⃣ Web Scraping Module  
🔹 Scrapes data from multiple **e-commerce websites** selling drones (**Amazon, BestBuy, eBay, etc.**).  
🔹 Extracts key details such as:  
   - 🏷 **Drone Name**  
   - 💰 **Price**  
   - ⭐ **Ratings/Reviews**  
   - 📦 **Availability (In Stock/Out of Stock)**  
   - 🏪 **Store Name**  
   - 🖼 **Image URL**  
🔹 **Stores the scraped data in a database.**  
🔹 **Automated Scheduler:** Runs scraping at fixed intervals (**daily/hourly**).  

---

### 2️⃣ Ranking System & Dashboard  
🔹 Displays a **dashboard** ranking the **Top 10 Drones** based on:  
   - **Price** (lowest to highest)  
   - **Popularity** (most reviews)  
   - **Availability**  
🔹 **Dynamic Sorting & Filtering:** Users can filter drones by **price range, rating, or store.**  
🔹 **Graphical Data Representation:**  
   - 📈 **Line Chart** for **price trends**  
   - 🏆 **Pie Chart** for **availability percentage**  

---

### 3️⃣ Real-Time Updates & Notifications  
🔹 If a drone **goes out of stock**, the system **updates it on the dashboard**.  
🔹 Sends **notifications (email/SMS)** for **price drops**.  
🔹 Uses **WebSockets** to push **live updates** to the dashboard.  

---

## 🏗️ Tech Stack  
- **Backend:** Django, Django REST Framework  
- **Frontend:** HTML, CSS, JavaScript, Chart.js  
- **Scraping:** BeautifulSoup / Scrapy  
- **Database:** PostgreSQL / MySQL  
- **Real-time:** Django Channels (WebSockets)  
- **Scheduler:** Celery + Redis  

---

## 📌 Installation Guide  

1️⃣ **Clone the repository**  
```sh
git clone https://github.com/your-username/drone-scraper-dashboard.git
cd drone-scraper-dashboard
2️⃣ Create a virtual environment & install dependencies

sh
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
3️⃣ Run database migrations

sh
Copy
Edit
python manage.py migrate
4️⃣ Start the Django development server

sh
Copy
Edit
python manage.py runserver
5️⃣ Run the scraping script manually (or let Celery schedule it)

sh
Copy
Edit
python manage.py scrape_drones
🖥️ Usage
1️⃣ Open the dashboard in your browser:

http://127.0.0.1:8000/
2️⃣ View real-time price updates

3️⃣ Enable notifications for price drops & stock changes

🔮 Future Enhancements
✅ Add AI-powered price prediction
✅ Integrate user accounts & wishlists
✅ Implement machine learning for better ranking

🤝 Contributing
Feel free to fork this project and submit pull requests!

📜 License
This project is MIT Licensed.
