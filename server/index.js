const express = require('express');
const Database = require('better-sqlite3');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const DB_PATH = path.join(__dirname, '..', 'data', 'lab-board.db');

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'public')));

// Initialize Database
const db = new Database(DB_PATH);
db.pragma('journal_mode = WAL');

// Create tables
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    avatar_url TEXT,
    color TEXT DEFAULT '#3b82f6',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    start_time TEXT,
    end_time TEXT,
    type TEXT DEFAULT 'busy',
    color TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
  );

  CREATE TABLE IF NOT EXISTS available (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    start_time TEXT,
    end_time TEXT,
    is_available INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
  );
`);

// Seed demo data if empty
const userCount = db.prepare('SELECT COUNT(*) as count FROM users').get();
if (userCount.count === 0) {
  const insertUser = db.prepare('INSERT INTO users (name, color, avatar_url) VALUES (?, ?, ?)');
  const demoUsers = [
    ['王小明', '#3b82f6', 'https://api.dicebear.com/7.x/avataaars/svg?seed=wang'],
    ['陳同學', '#22c55e', 'https://api.dicebear.com/7.x/avataaars/svg?seed=chen'],
    ['李同學', '#ef4444', 'https://api.dicebear.com/7.x/avataaars/svg?seed=li'],
    ['林同學', '#f59e0b', 'https://api.dicebear.com/7.x/avataaars/svg?seed=lin'],
    ['張小美', '#ec4899', 'https://api.dicebear.com/7.x/avataaars/svg?seed=chang'],
  ];
  demoUsers.forEach(u => insertUser.run(...u));

  // Demo events
  const insertEvent = db.prepare('INSERT INTO events (user_id, title, start_date, end_date, type, color) VALUES (?, ?, ?, ?, ?, ?)');
  const today = new Date();
  const formatDate = (d) => d.toISOString().split('T')[0];
  
  insertEvent.run(1, '實驗室meeting', formatDate(today), formatDate(today), 'busy', '#3b82f6');
  insertEvent.run(2, '論文討論', formatDate(today), formatDate(today), 'busy', '#22c55e');
  insertEvent.run(3, '程式開發', formatDate(new Date(today.getTime() + 86400000)), formatDate(new Date(today.getTime() + 86400000)), 'busy', '#ef4444');
  insertEvent.run(1, '國外研討會', formatDate(new Date(today.getTime() + 172800000)), formatDate(new Date(today.getTime() + 518400000)), 'busy', '#3b82f6');
  insertEvent.run(4, '專題演講', formatDate(new Date(today.getTime() + 259200000)), formatDate(new Date(today.getTime() + 259200000)), 'busy', '#f59e0b');
  insertEvent.run(5, '論文口試', formatDate(new Date(today.getTime() + 432000000)), formatDate(new Date(today.getTime() + 432000000)), 'busy', '#ec4899');
}

// ============== User APIs ==============
app.get('/api/users', (req, res) => {
  const users = db.prepare('SELECT * FROM users ORDER BY name').all();
  res.json(users);
});

app.post('/api/users', (req, res) => {
  const { name, avatar_url, color } = req.body;
  const result = db.prepare('INSERT INTO users (name, avatar_url, color) VALUES (?, ?, ?)').run(name, avatar_url, color);
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(result.lastInsertRowid);
  res.json(user);
});

app.put('/api/users/:id', (req, res) => {
  const { name, avatar_url, color } = req.body;
  db.prepare('UPDATE users SET name = ?, avatar_url = ?, color = ? WHERE id = ?').run(name, avatar_url, color, req.params.id);
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.params.id);
  res.json(user);
});

app.delete('/api/users/:id', (req, res) => {
  db.prepare('DELETE FROM events WHERE user_id = ?').run(req.params.id);
  db.prepare('DELETE FROM available WHERE user_id = ?').run(req.params.id);
  db.prepare('DELETE FROM users WHERE id = ?').run(req.params.id);
  res.json({ success: true });
});

// ============== Event APIs ==============
app.get('/api/events', (req, res) => {
  const events = db.prepare(`
    SELECT e.*, u.name as user_name, u.color as user_color, u.avatar_url 
    FROM events e 
    JOIN users u ON e.user_id = u.id 
    ORDER BY e.start_date
  `).all();
  res.json(events);
});

app.get('/api/events/:userId', (req, res) => {
  const events = db.prepare('SELECT * FROM events WHERE user_id = ? ORDER BY start_date').all(req.params.userId);
  res.json(events);
});

app.get('/api/calendar/:year/:month', (req, res) => {
  const { year, month } = req.params;
  const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
  const endDate = `${year}-${String(month).padStart(2, '0')}-31`;
  
  const events = db.prepare(`
    SELECT e.*, u.name as user_name, u.color as user_color, u.avatar_url 
    FROM events e 
    JOIN users u ON e.user_id = u.id 
    WHERE e.start_date >= ? AND e.start_date <= ?
    ORDER BY e.start_date
  `).all(startDate, endDate);
  
  res.json(events);
});

app.post('/api/events', (req, res) => {
  const { user_id, title, description, start_date, end_date, start_time, end_time, type, color } = req.body;
  const result = db.prepare(`
    INSERT INTO events (user_id, title, description, start_date, end_date, start_time, end_time, type, color) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(user_id, title, description, start_date, end_date, start_time, end_time, type, color);
  
  const event = db.prepare(`
    SELECT e.*, u.name as user_name, u.color as user_color, u.avatar_url 
    FROM events e JOIN users u ON e.user_id = u.id 
    WHERE e.id = ?
  `).get(result.lastInsertRowid);
  
  res.json(event);
});

app.put('/api/events/:id', (req, res) => {
  const { title, description, start_date, end_date, start_time, end_time, type, color } = req.body;
  db.prepare(`
    UPDATE events SET title = ?, description = ?, start_date = ?, end_date = ?, start_time = ?, end_time = ?, type = ?, color = ?
    WHERE id = ?
  `).run(title, description, start_date, end_date, start_time, end_time, type, color, req.params.id);
  
  const event = db.prepare(`
    SELECT e.*, u.name as user_name, u.color as user_color, u.avatar_url 
    FROM events e JOIN users u ON e.user_id = u.id 
    WHERE e.id = ?
  `).get(req.params.id);
  
  res.json(event);
});

app.delete('/api/events/:id', (req, res) => {
  db.prepare('DELETE FROM events WHERE id = ?').run(req.params.id);
  res.json({ success: true });
});

// ============== Available APIs ==============
app.get('/api/available/:date', (req, res) => {
  const available = db.prepare(`
    SELECT a.*, u.name as user_name, u.color as user_color, u.avatar_url 
    FROM available a 
    JOIN users u ON a.user_id = u.id 
    WHERE a.date = ?
  `).all(req.params.date);
  res.json(available);
});

app.post('/api/available', (req, res) => {
  const { user_id, date, start_time, end_time, is_available } = req.body;
  db.prepare('DELETE FROM available WHERE user_id = ? AND date = ?').run(user_id, date);
  const result = db.prepare('INSERT INTO available (user_id, date, start_time, end_time, is_available) VALUES (?, ?, ?, ?, ?)').run(user_id, date, start_time, end_time, is_available ? 1 : 0);
  res.json({ id: result.lastInsertRowid });
});

// ============== Static Pages ==============
app.get('/board', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'board', 'index.html'));
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'personal', 'index.html'));
});

// Start Server
app.listen(PORT, () => {
  console.log(`🔬 Lab Board server running at http://localhost:${PORT}`);
  console.log(`   個人儀表板: http://localhost:${PORT}/`);
  console.log(`   白板顯示:   http://localhost:${PORT}/board`);
});