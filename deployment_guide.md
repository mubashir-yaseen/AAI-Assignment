# Deployment Guide: Karachi Transport Planner

Yes, pushing your code to GitHub is highly recommended as a first step. Modern deployment platforms pull your code directly from GitHub to build and host it.

Here is the best strategy for your specific project stack (FastAPI Backend + Flutter Web Frontend):

### Where to Deploy?
- **Backend (Python/FastAPI):** Use **Render** (Free Tier). 
  - *Why not Vercel?* Vercel uses "Serverless Functions", meaning your backend would turn off and on for every request. Since your backend loads a large map graph into memory when it starts up, a serverless environment would be extremely slow. Render gives you a continuous server container that stays awake, which is perfect for this.
- **Frontend (Flutter Web):** Use **Netlify** or **Vercel** (Free Tier).

---

## Phase 1: Push to GitHub

1. Go to [GitHub](https://github.com/) and create a new repository (e.g., `karachi-transport-planner`). Do not initialize it with a README.
2. Open your terminal in the root of your project (`d:\projects\AAI-Assignment`).
3. Run the following commands to push all your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: full project"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/karachi-transport-planner.git
   git push -u origin main
   ```

---

## Phase 2: Deploy Backend to Render

1. Create a free account on [Render](https://render.com/).
2. Click **New +** and select **Web Service**.
3. Choose **Build and deploy from a Git repository** and connect your GitHub account.
4. Select your `karachi-transport-planner` repository.
5. Configure the deployment settings as follows:
   - **Name:** `karachi-api` (or whatever you prefer)
   - **Root Directory:** `backend` (This is crucial so Render knows where the Python app is).
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn routing_api:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
6. Click **Create Web Service**. 
7. It will take a few minutes to build. Once it says "Live", copy the deployment URL (e.g., `https://karachi-api-xyz.onrender.com`).

---

## Phase 3: Update Frontend API Links

Now that the backend is live on the internet, you need to point your Flutter app to it instead of `localhost`.

1. Open `d:\projects\AAI-Assignment\karachi_transport_app\lib\screens\assignment_mode_screen.dart` and locate line 6:
   ```dart
   const String baseUrl = "http://localhost:8000";
   ```
2. Open `d:\projects\AAI-Assignment\karachi_transport_app\lib\screens\real_mode_screen.dart` and locate line 8:
   ```dart
   const String baseUrl = "http://localhost:8000";
   ```
3. Replace both instances with your new Render URL:
   ```dart
   const String baseUrl = "https://karachi-api-xyz.onrender.com"; // Replace with your actual Render URL
   ```
4. Save the files. (You don't need to push this change to GitHub right away if you use the Netlify Drag & Drop method below).

---

## Phase 4: Build and Deploy Frontend

Platforms like Vercel and Netlify don't have the Flutter SDK pre-installed to build your app from GitHub automatically. The easiest and fastest way to deploy a Flutter Web app is to build it locally and upload the output folder.

1. Open your terminal and navigate to your frontend folder:
   ```bash
   cd karachi_transport_app
   ```
2. Run the command to build the app for the web:
   ```bash
   flutter build web
   ```
   *This creates a highly optimized static website in the `build/web` folder inside your `karachi_transport_app` directory.*

3. Create a free account on [Netlify](https://www.netlify.com/).
4. Once logged in, go to your **Team Overview** or **Sites** page.
5. Click **Add new site** -> **Deploy manually**.
6. Open your file explorer (`d:\projects\AAI-Assignment\karachi_transport_app\build\web`).
7. **Drag and drop** the entire `web` folder into the upload circle on Netlify.
8. Netlify will publish it instantly! You can go to "Site Settings" to change the random URL to something nicer (e.g., `karachi-transport.netlify.app`).

**You are fully deployed!**
