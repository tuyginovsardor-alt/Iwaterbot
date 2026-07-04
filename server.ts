import express from 'express';
import path from 'path';
import fs from 'fs';
import { createServer as createViteServer } from 'vite';

const app = express();
const PORT = 3000;

app.use(express.json());

const DB_FILE = path.join(process.cwd(), 'database', 'db_mock.json');

// Ensure database directory exists
if (!fs.existsSync(path.dirname(DB_FILE))) {
  fs.mkdirSync(path.dirname(DB_FILE), { recursive: true });
}

interface Order {
  id: number;
  user_id: number; // 0 for Web, Telegram User ID for Bot
  username?: string;
  full_name: string;
  phone: string;
  items: string;
  total_price: number;
  address: string;
  latitude: number;
  longitude: number;
  status: 'new' | 'accepted' | 'on_the_way' | 'delivered' | 'pending_payment' | 'rejected';
  payment_type: string;
  payment_check_file_id?: string; // photo data url or name
  rejection_reason?: string;
  admin_name?: string;
  created_at: string;
}

interface Channel {
  id: string;
  name: string;
  invite_link: string;
}

interface DbData {
  settings: Record<string, string>;
  orders: Order[];
  channels: Channel[];
  start_images: string[];
}

const defaultData: DbData = {
  settings: {
    water_price: '15000',
    manual_payment_status: '1', // default to on so we can test Card payment!
    web_site_status: '1',
    terms_uz: 'Rasmiy iWater foydalanish shartlari: toza va sifatli 19L suv yetkazib berish.',
    terms_ru: 'Официальные правила использования iWater: быстрая доставка чистой воды 19л.',
    warehouse_lat: '41.2995',
    warehouse_lon: '69.2401'
  },
  orders: [
    {
      id: 1001,
      user_id: 87492041,
      username: 'sarvar_dev',
      full_name: 'Sarvar Tuyginov',
      phone: '+998901234567',
      items: '2 dona 19L',
      total_price: 30000,
      address: 'Toshkent sh., Chilonzor 9-daha, 4-uy',
      latitude: 41.2825,
      longitude: 69.2134,
      status: 'delivered',
      payment_type: 'Naqd',
      admin_name: 'Super Admin',
      created_at: new Date(Date.now() - 4 * 3600 * 1000).toISOString()
    },
    {
      id: 1002,
      user_id: 0, // Web Order
      full_name: 'Dildora Ahmedova',
      phone: '+998935552211',
      items: '4 dona 19L (Web)',
      total_price: 60000,
      address: 'Yunusobod 4-mavze, 12-uy',
      latitude: 41.3524,
      longitude: 69.2891,
      status: 'new',
      payment_type: 'Naqd',
      created_at: new Date(Date.now() - 20 * 60 * 1000).toISOString()
    }
  ],
  channels: [
    { id: '@iwater_official', name: 'iWater Rasmiy Kanali', invite_link: 'https://t.me/iwater_bot' }
  ],
  start_images: []
};

function readDb(): DbData {
  try {
    if (fs.existsSync(DB_FILE)) {
      const content = fs.readFileSync(DB_FILE, 'utf-8');
      return JSON.parse(content);
    }
  } catch (err) {
    console.error('Error reading db_mock.json:', err);
  }
  return defaultData;
}

function writeDb(data: DbData) {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), 'utf-8');
  } catch (err) {
    console.error('Error writing db_mock.json:', err);
  }
}

// Ensure initial database exists
if (!fs.existsSync(DB_FILE)) {
  writeDb(defaultData);
}

// API Routes

// Get settings
app.get('/api/settings', (req, res) => {
  const db = readDb();
  res.json(db.settings);
});

// Update specific setting
app.post('/api/settings', (req, res) => {
  const db = readDb();
  const { key, value } = req.body;
  if (key) {
    db.settings[key] = String(value);
    writeDb(db);
    res.json({ success: true, settings: db.settings });
  } else {
    res.status(400).json({ error: 'Missing key or value' });
  }
});

// Update multiple settings at once
app.post('/api/settings/bulk', (req, res) => {
  const db = readDb();
  const settings = req.body;
  if (typeof settings === 'object') {
    db.settings = { ...db.settings, ...settings };
    writeDb(db);
    res.json({ success: true, settings: db.settings });
  } else {
    res.status(400).json({ error: 'Invalid payload' });
  }
});

// Get orders
app.get('/api/orders', (req, res) => {
  const db = readDb();
  res.json(db.orders);
});

// Create new order
app.post('/api/orders', (req, res) => {
  const db = readDb();
  const newOrder = req.body;
  
  const id = db.orders.length > 0 ? Math.max(...db.orders.map(o => o.id)) + 1 : 1001;
  const order: Order = {
    id,
    user_id: newOrder.user_id ?? 0,
    username: newOrder.username,
    full_name: newOrder.full_name || 'Guest User',
    phone: newOrder.phone || '',
    items: newOrder.items || '1 dona 19L',
    total_price: Number(newOrder.total_price) || 15000,
    address: newOrder.address || "📍 Noma'lum manzil",
    latitude: Number(newOrder.latitude) || 0,
    longitude: Number(newOrder.longitude) || 0,
    status: newOrder.status || 'new',
    payment_type: newOrder.payment_type || 'Naqd',
    payment_check_file_id: newOrder.payment_check_file_id,
    created_at: new Date().toISOString()
  };

  db.orders.unshift(order); // Put new orders at the top
  writeDb(db);
  res.json({ success: true, order });
});

// Update order status
app.post('/api/orders/:id/status', (req, res) => {
  const db = readDb();
  const orderId = Number(req.params.id);
  const { status, admin_name, rejection_reason, payment_check_file_id } = req.body;
  
  const idx = db.orders.findIndex(o => o.id === orderId);
  if (idx !== -1) {
    if (status) db.orders[idx].status = status;
    if (admin_name) db.orders[idx].admin_name = admin_name;
    if (rejection_reason) db.orders[idx].rejection_reason = rejection_reason;
    if (payment_check_file_id) db.orders[idx].payment_check_file_id = payment_check_file_id;
    
    writeDb(db);
    res.json({ success: true, order: db.orders[idx] });
  } else {
    res.status(404).json({ error: 'Order not found' });
  }
});

// Delete all orders (reset)
app.post('/api/orders/reset', (req, res) => {
  const db = readDb();
  db.orders = defaultData.orders;
  writeDb(db);
  res.json({ success: true, orders: db.orders });
});

// Channels API
app.get('/api/channels', (req, res) => {
  const db = readDb();
  res.json(db.channels);
});

app.post('/api/channels', (req, res) => {
  const db = readDb();
  const { id, name, invite_link } = req.body;
  if (id && name && invite_link) {
    // Avoid duplicates
    db.channels = db.channels.filter(c => c.id !== id);
    db.channels.push({ id, name, invite_link });
    writeDb(db);
    res.json({ success: true, channels: db.channels });
  } else {
    res.status(400).json({ error: 'Missing channel details' });
  }
});

app.delete('/api/channels/:id', (req, res) => {
  const db = readDb();
  const chId = req.params.id;
  db.channels = db.channels.filter(c => c.id !== chId && c.id !== '@' + chId);
  writeDb(db);
  res.json({ success: true, channels: db.channels });
});

// Start Images API
app.get('/api/images', (req, res) => {
  const db = readDb();
  res.json(db.start_images);
});

app.post('/api/images', (req, res) => {
  const db = readDb();
  const { image } = req.body;
  if (image) {
    db.start_images.push(image);
    writeDb(db);
    res.json({ success: true, images: db.start_images });
  } else {
    res.status(400).json({ error: 'Missing image data' });
  }
});

app.delete('/api/images', (req, res) => {
  const db = readDb();
  db.start_images = [];
  writeDb(db);
  res.json({ success: true, images: db.start_images });
});


// Serve static/compiled Vite site
async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
