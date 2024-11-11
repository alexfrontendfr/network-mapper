# Network Mapper

A full-stack application for scanning and visualizing network devices. Built with Python (Flask) backend and React frontend.

## 🚀 Features

- Real-time network device scanning
- Device type identification
- Interactive network visualization
- List and graph views
- Device vendor detection
- Network topology mapping

## 🛠️ Prerequisites

- Python 3.8+
- Node.js 14+
- Nmap (Network Mapper)
  - [Download Nmap](https://nmap.org/download.html)
  - Install with "Add to PATH" option checked

## ⚡ Quick Start

1. Clone the repository:

```bash
git clone https://github.com/alexfrontendfr/network-mapper.git
cd network-mapper
```

2. Set up backend:

```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # On Windows with Git Bash
# OR
.\venv\Scripts\activate  # On Windows CMD

pip install -r requirements.txt
```

3. Set up frontend:

```bash
cd ../frontend
npm install
```

4. Run the application:

Backend (in administrator mode):

```bash
cd backend
python api.py
```

Frontend (in a new terminal):

```bash
cd frontend
npm run dev
```

The application will be available at:

- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

## 🔧 Configuration

- Default network range: Auto-detected
- Scan timeout: 3 seconds
- Port scan range: Common ports (20-3389)

## 🔒 Security Note

Run network scans only on networks you own or have permission to test.

## 📝 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Alexandre Frontend**

- Github: [@alexfrontendfr](https://github.com/alexfrontendfr)
- Email: contactalexfr@gmail.com

## 🤝 Contributing

1. Fork it
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
