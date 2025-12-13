# Social Media Analytics Platform

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Ne05oVw_)

A comprehensive analytics platform for comparing and analyzing social media engagement patterns across 4chan and Reddit, featuring AI-powered insights using LangChain and CopilotKit.

## 🚀 Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.13+)
- **Database:** PostgreSQL (2 separate databases for 4chan and Reddit data)
- **AI/LLM:**
  - LangChain (0.3.27)
  - LangChain Core (0.3.76)
  - LangChain OpenAI (0.3.33)
  - CopilotKit (0.1.65)
- **Database Connector:** psycopg2 (2.9.11)
- **Web Scraping:** ScrapeGraphAI (1.65.0)
- **Server:** Uvicorn (0.38.0)
- **Development Tools:** Ruff (linter)
- **Environment Management:** python-dotenv (1.2.1)

### Frontend
- **Framework:** Next.js 16.0.7 (React 19.2.0)
- **Language:** TypeScript 5
- **Styling:** Tailwind CSS 4
- **Data Visualization:** 
  - ApexCharts (5.3.6)
  - React ApexCharts (1.9.0)
  - React Simple Maps (3.0.0)
- **State Management:** TanStack React Query (5.90.12)
- **AI Integration:**
  - CopilotKit React Core (1.10.6)
  - CopilotKit React UI (1.10.6)
  - CopilotKit Runtime (1.10.6)
  - OpenAI (6.10.0)
- **HTTP Client:** Axios (1.13.2)
- **UI Components:**
  - React Icons (5.5.0)
  - React Animated Numbers (1.1.1)
  - React Spinners (0.17.0)
- **Development Tools:** ESLint 9

## 📦 Database Configuration

The application uses two separate PostgreSQL databases:

- **4chan Database:** `CHAN_DATABASE_URL` - Stores 4chan board posts, comments, and engagement metrics
- **Reddit Database:** `REDDIT_DATABASE_URL` - Stores Reddit posts, comments, and subreddit data

Configure these in your `.env` file in the Backend directory:
```env
CHAN_DATABASE_URL=postgresql://user:password@host:port/chan_db
REDDIT_DATABASE_URL=postgresql://user:password@host:port/reddit_db
OPENAI_API_KEY=your_openai_api_key
```

## 🔧 Installation & Setup

### Backend Setup
```bash
cd Backend
uv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On Linux/Mac
uv sync
```

### Frontend Setup
```bash
cd frontend
pnpm install
```

## ▶️ Running the Application

### Start Backend Server
```bash
cd Backend
python -m uvicorn app.main:app --reload
```
Backend will run on: `http://localhost:8000`

### Start Frontend Development Server
```bash
cd frontend
pnpm dev --port 8080
```
Frontend will run on: `http://localhost:8080`

## Frontend Pages

Access the following dashboards once the frontend is running:

- **4chan Dashboard:** http://localhost:3000/chan
  - View 4chan board statistics and analytics
  - Daily/hourly activity trends
  - Engagement metrics by post type
  - Country-based statistics
  - Interactive filters and date ranges

- **Reddit Dashboard:** http://localhost:3000/reddit
  - View Reddit subreddit analytics
  - Daily post counts by subreddit
  - Top subscribers statistics
  - Engagement metrics and trends
  - Interactive visualizations

- **Platform Comparison:** http://localhost:3000/comparison
  - Side-by-side comparison of 4chan vs Reddit
  - Engagement pattern analysis
  - Toxicity comparison across platforms
  - Event-related discussion trends
  - Unified analytics view

## 📚 API Documentation

Once the backend is running, access the interactive API documentation:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔌 API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### 4chan Endpoints (`/chan`)

#### Boards & Statistics
- `GET /chan/boards` - Get list of all available 4chan boards
- `GET /chan/stats/summary` - Get summary statistics (total posts, unique boards, toxicity)
- `GET /chan/stats/daily` - Get daily post statistics with optional filtering
  - Query params: `board_name`, `start_date`, `end_date`
- `GET /chan/stats/countries` - Get country-based post statistics

#### Activity Analysis
- `GET /chan/activity/daily` - Get daily activity by post type
  - Query params: `board_name` (required), `start_date` (required), `end_date` (required), `post_types` (optional)
- `GET /chan/activity/hourly` - Get hourly activity breakdown for a specific date
  - Query params: `board_name` (required), `selected_date` (required), `post_types` (optional)

#### Engagement Metrics
- `GET /chan/engagement/by-type` - Get engagement metrics by post type
  - Query params: `board_name` (required), `start_date` (required), `end_date` (required)

#### Debug
- `GET /chan/debug/posts` - Debug endpoint to check posts data
  - Query params: `board_name` (default: "pol")

### Reddit Endpoints (`/reddit`)

#### Subreddits & Statistics
- `GET /reddit/subreddits` - Get list of available subreddits (top 20 by post count)
- `GET /reddit/stats/summary` - Get summary statistics (total posts, unique subreddits, toxicity, comments)
- `GET /reddit/subreddit/top-subscribers` - Get top subreddits by subscriber count

#### Posts & Activity
- `GET /reddit/posts/daily-counts` - Get daily post counts by subreddit
  - Query params: `start_date` (default: "2025-11-01"), `end_date` (optional)

#### Engagement Metrics
- `GET /reddit/engagement/by-type` - Get engagement metrics by post type
  - Query params: `subreddit` (required), `start_timestamp` (required), `end_timestamp` (required)

#### Debug
- `GET /reddit/debug/posts` - Debug endpoint to check Reddit posts data
  - Query params: `subreddit` (default: "technology")

### Platform Comparison Endpoints (`/comparison`)

- `GET /comparison/forums` - Get forum counts from both platforms
  - Returns: 4chan board count and Reddit subreddit count

- `GET /comparison/engagement/by-type` - Compare engagement metrics across platforms
  - Query params: `board_name` (required), `subreddit` (required), `start_date` (required), `end_date` (required)

- `GET /comparison/top-toxic` - Get top toxic forums from both platforms sorted by toxicity

- `GET /comparison/event-related-timeline` - Get timeline of event-related posts (e.g., Cloudflare outage)
  - Query params: `platform` (required: "reddit", "chan", or "all"), `community` (optional), `event_date` (required), `window` (default: 7 days)

### AI Agent Endpoints

- `POST /copilotkit` - CopilotKit endpoint for AI-powered interactions
- `POST /copilotkit/agent` - Stream SQL agent responses for natural language queries

## 📊 Sample API Requests

### Get All 4chan Boards
```http
GET http://localhost:8000/chan/boards
```

### Get Daily Activity for /pol/
```http
GET http://localhost:8000/chan/activity/daily?board_name=pol&start_date=2025-11-01&end_date=2025-12-08
```

### Get Hourly Activity
```http
GET http://localhost:8000/chan/activity/hourly?board_name=pol&selected_date=2025-12-04
```

### Filter by Post Types
```http
GET http://localhost:8000/chan/activity/daily?board_name=pol&start_date=2025-11-01&end_date=2025-12-08&post_types=news&post_types=opinion
```

### 4chan Engagement by Type
```http
GET http://localhost:8000/chan/engagement/by-type?board_name=pol&start_date=2025-12-01&end_date=2025-12-05
```

### Reddit Engagement by Type
```http
GET http://localhost:8000/reddit/engagement/by-type?subreddit=geopolitics&start_timestamp=1760013696&end_timestamp=1761285425
```

### Platform Comparison
```http
GET http://localhost:8000/comparison/forums
```

### Compare Engagement Across Platforms
```http
GET http://localhost:8000/comparison/engagement/by-type?board_name=pol&subreddit=geopolitics&start_date=2025-12-01&end_date=2025-12-05
```

## 🤖 AI Features

The platform includes an AI-powered SQL agent that allows natural language queries:
- Ask questions about data trends
- Compare engagement patterns
- Generate insights from 4chan and Reddit data
- Powered by LangChain and OpenAI GPT models

## 📊 Sample Outputs & Visualizations

The platform provides rich visualizations and analytics. Sample outputs are available in the `frontend/outputs/` directory:

### 4chan Analytics
- **Board Statistics:** Summary stats including total posts, unique boards, and toxicity scores
  ![4chan Stats](frontend/outputs/Chan_stats.png)

- **Daily Posts by Boards:** Time-series visualization of daily posting activity across boards
  ![Daily Posts](frontend/outputs/Daily%20Posts%20Chan%20By%20boards%20and%20date.png)

- **Posts by Country:** Geographic distribution of 4chan posts

  ![Posts by Country](frontend/outputs/Posts%20by%20Country%20Chan.png)

### Reddit Analytics
- **Subreddit Statistics:** Overview of Reddit activity including posts, subreddits, and engagement
  ![Reddit Stats](frontend/outputs/reddit_stats.png)

- **Daily Posts by Subreddits:** Trending analysis of subreddit posting activity
  ![Daily Posts by Subreddit](frontend/outputs/Daily%20Posts%20By%20Subreddits.png)

- **Top Subscribers:** Most popular subreddits by subscriber count
  ![Top Subscribers](frontend/outputs/Top%20Subscribers%20by%20Subreddits.png)

### Platform Comparison
- **Engagement by Post Type:** Compare how different post types perform across platforms
  ![Engagement by Type](frontend/outputs/Engagement%20by%20Post%20Type.png)

- **Average Toxicity Comparison:** Toxicity levels across boards and subreddits
  ![Toxicity Comparison](frontend/outputs/Average%20Toxicity%20Per%20Boards_Subreddit.png)

- **Event-Related Timeline:** Track discussion trends around specific events (e.g., Cloudflare Outage)
  ![Event Timeline](frontend/outputs/Cloudflare%20Outage%20Discussion%20Trends%20(2025-11-18).png)

## 📁 Project Structure

```
├── Backend/
│   ├── app/
│   │   ├── agent/          # LangChain SQL agents
│   │   ├── constants/      # SQL queries
│   │   ├── models/         # Pydantic models
│   │   ├── routes/         # API endpoints
│   │   └── utils/          # Helper utilities
│   ├── logs/               # Application logs
│   └── pyproject.toml      # Python dependencies
├── frontend/
│   └── src/
│       └── app/
│           ├── api/        # API client functions
│           ├── components/ # React components
│           ├── hooks/      # Custom React hooks
│           ├── chan/       # 4chan dashboard
│           ├── reddit/     # Reddit dashboard
│           └── comparison/ # Comparison dashboard
└── README.md
```

## 🔒 Environment Variables

Create a `.env` file in the Backend directory:
```env
CHAN_DATABASE_URL=postgresql://user:password@host:port/chan_database
REDDIT_DATABASE_URL=postgresql://user:password@host:port/reddit_database
OPENAI_API_KEY=sk-...
```

## 📝 License

This project is part of an academic assignment.
