# 🍼 Baby Metric Tracker 1.0

Baby metric tracking suite.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+ 
- Node.js 18+
- npm

### 2. Setup
Clone the repository and install dependencies.

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Run the Suite
Use the integrated runner script to start both the backend and frontend simultaneously:

```bash
python run.py
```

- **Dashboard**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`

---

## 📝 Configuration
Update `config.yaml` to customize the baby's name, date of birth, and preferred timezone.

```yaml
user:
  name: "Baby"
  date_of_birth: 2024-01-01
timezone: "Europe/London"
```

