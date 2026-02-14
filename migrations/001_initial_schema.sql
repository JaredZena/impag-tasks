-- ============================================================
-- IMPAG Tasks — Initial Schema Migration
-- Run this against the shared Neon PostgreSQL database
-- ============================================================

BEGIN;

-- 1. Task Users (fixed, manually seeded)
CREATE TABLE task_user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    role VARCHAR(20) DEFAULT 'member' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ
);

-- 2. Task Categories (user-managed)
CREATE TABLE task_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT '#6366f1' NOT NULL,
    icon VARCHAR(50),
    created_by INTEGER NOT NULL REFERENCES task_user(id),
    sort_order INTEGER DEFAULT 0 NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ
);

CREATE INDEX idx_task_category_active ON task_category(is_active);

-- 3. Tasks
CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    priority VARCHAR(10) DEFAULT 'medium' NOT NULL,
    due_date DATE,
    category_id INTEGER REFERENCES task_category(id),
    created_by INTEGER NOT NULL REFERENCES task_user(id),
    assigned_to INTEGER REFERENCES task_user(id),
    completed_at TIMESTAMPTZ,
    archived_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ
);

CREATE INDEX idx_task_status ON task(status);
CREATE INDEX idx_task_assigned_to ON task(assigned_to);
CREATE INDEX idx_task_created_by ON task(created_by);
CREATE INDEX idx_task_due_date ON task(due_date);
CREATE INDEX idx_task_archived_at ON task(archived_at);
CREATE INDEX idx_task_category_id ON task(category_id);

-- 4. Task Comments
CREATE TABLE task_comment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES task(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES task_user(id),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ
);

CREATE INDEX idx_task_comment_task_id ON task_comment(task_id);

-- ============================================================
-- SEED DATA
-- ============================================================

-- Users
INSERT INTO task_user (email, display_name, role) VALUES
    ('jaredzenahernandez@gmail.com', 'Jared', 'admin'),
    ('zena.hernandez.010195@gmail.com', 'Zena', 'admin');

-- Categories (created_by = 1, i.e. Jared)
INSERT INTO task_category (name, color, icon, created_by, sort_order) VALUES
    ('General',                     '#64748b', 'clipboard-list', 1, 0),
    ('Envíos en tránsito',          '#f59e0b', 'truck',          1, 1),
    ('Por enviar',                  '#6366f1', 'package',        1, 2),
    ('Compras por realizar',        '#22c55e', 'shopping-cart',  1, 3),
    ('Instalaciones',               '#8b5cf6', 'wrench',         1, 4),
    ('Rastreo de guías',            '#ec4899', 'map-pin',        1, 5),
    ('Solicitud de facturas',       '#14b8a6', 'receipt',        1, 6),
    ('Seguimiento a cotizaciones',  '#f97316', 'file-text',      1, 7);

-- Sample tasks for testing (remove before production if desired)
INSERT INTO task (title, description, status, priority, due_date, category_id, created_by, assigned_to) VALUES
    (
        'Instalación de Geomembrana Juan Herrera',
        'Ya está la plancha, esperamos la malla y la geomembrana. Pedir geotextil a Geoliners, falta factura y envío.',
        'pending', 'high', '2026-02-20', 5, 1, 1
    ),
    (
        'Entrega de material Miguel Herrera Tepehuanes',
        'Preguntar si bajan o lo envío. A Sandra se le dará un reintegro en efectivo.',
        'pending', 'medium', '2026-02-18', 2, 1, 1
    ),
    (
        'Cotización línea de regado con Xcel Wobler',
        'Con elevador manguera externa.',
        'pending', 'medium', NULL, 8, 1, 1
    ),
    (
        'Transportar lámparas solares 240w a IMPAG',
        'Mundo Lúcido. Las tiene el Ing. David en Estado de México.',
        'in_progress', 'high', '2026-02-17', 2, 1, 2
    ),
    (
        'Responder mensajes y solicitudes de redes sociales',
        'General. Actualizar al finalizar el día.',
        'pending', 'low', '2026-02-14', 1, 1, 2
    ),
    (
        'Pago pendiente Sora Gurrola - 2 mallas $15,400',
        'Pagará el sábado/lunes. Las mallas ya se pidieron.',
        'pending', 'urgent', '2026-02-15', 1, 1, 1
    ),
    (
        'Cotización geomembrana Tuxpan 34x37x2 de talud',
        '12,000 m². Osvaldo.',
        'pending', 'medium', '2026-02-21', 8, 1, 1
    ),
    (
        'Recibir malla electro soldada de Cofiasa',
        'Entrega por la tarde del viernes 13/02/2026. Si no contesta, marcar a la 1pm.',
        'done', 'high', '2026-02-13', 3, 1, 2
    ),
    (
        'Pago de Credencial Comercial con la presidencia',
        'Municipio $586.50. Solicitar datos para facturar. Mandar a Adrián. Pagar hoy.',
        'pending', 'urgent', '2026-02-14', 7, 1, 1
    ),
    (
        'Rastreo 2 mallas Popusa guía cot 493HJL pedido #440',
        'Seguimiento a rastreo.',
        'in_progress', 'medium', NULL, 6, 1, 2
    );

-- Sample comments for testing
INSERT INTO task_comment (task_id, user_id, content) VALUES
    (1, 1, 'Ya contacté a Geoliners, dicen que envían factura mañana.'),
    (1, 2, 'Perfecto, en cuanto llegue la factura avísame para procesar el pago.'),
    (4, 1, 'El Ing. David confirma que las tiene listas. Falta coordinar transporte.'),
    (6, 2, 'Sora dice que el lunes sin falta deposita.'),
    (8, 1, 'Ya llegó la malla. Revisar que esté completa.');

COMMIT;
