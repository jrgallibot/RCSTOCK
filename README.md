Project Overview: Web Scraping and Drone Price Tracking Dashboard
🛠 Project Description
This project is a web scraping system that collects information about drones from various online stores registered in the system. The scraped data is displayed in a dashboard, where users can see:
✅ Top 10 drones ranked based on price, reviews, or popularity
✅ Real-time stock updates (if a drone is available or out of stock)
✅ Historical price trends (optional feature)

The system will automate scraping and updating drone listings at regular intervals.

🚀 Key Features
1️⃣ Web Scraping Module
Scrapes data from multiple e-commerce websites selling drones (Amazon, BestBuy, eBay, etc.).
Extracts key details such as:
🏷 Drone Name
💰 Price
⭐ Ratings/Reviews
📦 Availability (In Stock/Out of Stock)
🏪 Store Name
🖼 Image URL
Stores the scraped data in a database.
Automated Scheduler: Runs scraping at fixed intervals (daily/hourly).
2️⃣ Ranking System & Dashboard
Displays a dashboard ranking the Top 10 Drones based on:
Price (lowest to highest)
Popularity (most reviews)
Availability
Dynamic Sorting & Filtering: Users can filter drones by price range, rating, or store.
Graphical Data Representation:
Line chart for price trends
Pie chart for availability percentage
3️⃣ Real-Time Updates & Notifications
If a drone goes out of stock, the system updates it on the dashboard.
Sends notifications (email/SMS) for price drops.
Uses WebSockets to push live updates to the dashboard.
