-- ============================================================
-- IMPAG Tasks — Seed real tasks from WhatsApp (Feb 13, 2026)
-- All tasks assigned_to = 1 (Hernan), created_by = 2 (Jared)
-- ============================================================
-- Categories reference:
--   1 = General
--   2 = Envíos en tránsito
--   3 = Por enviar
--   4 = Compras por realizar
--   5 = Instalaciones
--   6 = Rastreo de guías
--   7 = Solicitud de facturas
--   8 = Seguimiento a cotizaciones
-- ============================================================

BEGIN;

-- Remove old sample/seed tasks and comments
DELETE FROM task_comment;
DELETE FROM task;

-- ============================================================
-- NUMBERED TASKS FROM THE LIST
-- ============================================================

-- #1
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Instalación de Geomembrana Juan Herrera',
  'Ya está la plancha, esperamos la malla y la geomembrana. Pedir geotextil a Geoliners, falta factura y envío.',
  'pending', 'high', 5, 2, 1
);

-- #2
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Entrega de material Miguel Herrera Tepehuanes',
  'Preguntar si bajan o lo envío. A Sandra se le dará un reintegro en efectivo.',
  'pending', 'medium', 2, 2, 1
);

-- #3
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Cotización línea de regado con Xcel Wobler',
  'Con elevador manguera externa.',
  'pending', 'medium', 8, 2, 1
);

-- #4
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Transportar lámparas solares 240W (Mundo Lúcido) a IMPAG',
  'Las tiene el Ing. David en Estado de México.',
  'pending', 'high', 2, 2, 1
);

-- #5
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Responder mensajes y solicitudes de redes sociales',
  'General. Actualizar al finalizar el día.',
  'pending', 'low', 1, 2, 1
);

-- #6
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Entregar nota de malla sombra al 50% de Idelfonso (Mezquital)',
  NULL,
  'pending', 'medium', 3, 2, 1
);

-- #7
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Pago pendiente Sora Gurrola - 2 mallas $15,400',
  'Pagará el sábado/lunes. Las mallas ya se pidieron.',
  'pending', 'high', 1, 2, 1
);

-- #8
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Cotización geomembrana Tuxpan 34x37x2 de talud (12,000 m²)',
  'Osvaldo.',
  'pending', 'medium', 8, 2, 1
);

-- #9
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Entregar malla - María García (Dgo capital, pagada) + 2 mallas Ing. Genesis (por comprar)',
  NULL,
  'pending', 'medium', 3, 2, 1
);

-- #10
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Marcos Limón - Picadora de forraje',
  'No le llegan los mensajes en Shopify. Se envía por correo la cotización.',
  'pending', 'medium', 8, 2, 1
);

-- #11
INSERT INTO task (title, description, status, priority, due_date, category_id, created_by, assigned_to)
VALUES (
  'Recibir malla electro soldada de Cofiasa',
  'Entrega por la tarde del viernes 13/02/2026. Si no contesta a la brevedad, marcar a la 1pm.',
  'pending', 'high', '2026-02-13', 3, 2, 1
);

-- #12
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Ángeles Hernández - Cotización plástico de invernadero',
  'Requiere cálculo para diferentes pliegos. Manda planos y solicitud de cotización formal.',
  'pending', 'medium', 8, 2, 1
);

-- #13
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Pago de Credencial Comercial con la presidencia',
  'Municipio $586.50. Solicitar datos para facturar. Mandar a Adrián. PAGAR HOY.',
  'pending', 'urgent', 7, 2, 1
);

-- #14
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Solicitud de árboles presidencia - actualizar solicitud',
  'Continuidad del 2025, no nos resolvieron. Actualizar solicitud (poner sin fines de lucro y sin propaganda política). Corregir.',
  'pending', 'medium', 1, 2, 1
);

-- #16
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Pago de taxi envío 3 paquetes bolsa 15x25 a Nuevo Ideal',
  'Una vez llegada a Dgo. Maniobra MOR00503010 Insumos FER. MONITOREAR.',
  'pending', 'medium', 6, 2, 1
);

-- #17
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Pago pendiente Adrián estancia ($300)',
  'Si no va hoy. Continuidad al proyecto URGENTE.',
  'pending', 'urgent', 1, 2, 1
);

-- #18
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Pago mensual Adriana - falta Nov 2025, Dic 2025, Ene 2026',
  'Aportación de $3,500.00',
  'pending', 'high', 1, 2, 1
);

-- #20
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Seguimiento envío cot HO192 - 6 paquetes a llegar a Dgo capital',
  NULL,
  'pending', 'medium', 6, 2, 1
);

-- #21
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Seguimiento rastreo 2 mallas Popusa - guía cot 493HJL pedido #440',
  NULL,
  'pending', 'medium', 6, 2, 1
);

-- #22
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Cotización charolas Sergio García Tamazula - 77 cavidades unicel, 10 pzas',
  NULL,
  'pending', 'medium', 8, 2, 1
);

-- #24
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Jesús Salazar - Bomba de superficie para paneles solares',
  'Falta información de paneles e inversor, no los tiene a la mano.',
  'pending', 'medium', 8, 2, 1
);

-- #25
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Monitoreo 3 mallas y 1 plástico Popusa - guía PUE01397408',
  'Distribuir en Dgo.',
  'pending', 'medium', 6, 2, 1
);

-- #26
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Factura y guía Fernanda Molina - mallas y ground cover $30,640',
  'Pagado cot HO199. Guía ground cover + 1 malla 50%: PUE01397751. 3 mallas 35%: TRN01228664.',
  'pending', 'medium', 6, 2, 1
);

-- #27
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Anayeli Rosas (Toluca) - estanque geomembrana pequeño',
  'Para recreación de animales.',
  'pending', 'medium', 8, 2, 1
);

-- #28
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Genaro Bueno - malla Alamillos Hidalgo',
  'Confirmará el sábado si requiere la malla. Mandar cotización formal. Falta cotización de bomba, pedir información.',
  'pending', 'medium', 8, 2, 1
);

-- #31
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Cotización invernadero para 10 mil plántulas de chile - Villa Hermosa Dgo',
  'Falta.',
  'pending', 'medium', 8, 2, 1
);

-- #32
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Cotización Julio Márquez - Bomba para riego 8 ha',
  'Ya tiene tiempo, URGE.',
  'pending', 'urgent', 8, 2, 1
);

-- #33
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Pago Rogelio - quedó en venir',
  'Pendiente.',
  'pending', 'medium', 1, 2, 1
);

-- #36
INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Semilla maíz Poanas - falta cotización',
  'Mandar a Alonso cotización. 6181208162 Guadalupe Victoria.',
  'pending', 'medium', 8, 2, 1
);

-- ============================================================
-- ADDITIONAL TASKS FROM FOLLOW-UP MESSAGES
-- ============================================================

INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Enviar información faltante de cotizaciones por WhatsApp',
  'Involucrar cosas faltantes de WhatsApp por cotizar.',
  'pending', 'medium', 8, 2, 1
);

INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Solicitar todas las facturas de febrero',
  NULL,
  'pending', 'medium', 7, 2, 1
);

INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Rastrear todas las paqueterías y checar estatus',
  NULL,
  'pending', 'medium', 6, 2, 1
);

INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Cotización geomembranas para tinas - están muy caras',
  'Terminar cotización.',
  'pending', 'medium', 8, 2, 1
);

INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Actualizar cotización - cliente la vio cara',
  NULL,
  'pending', 'low', 8, 2, 1
);

INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Lunes mandar correos de facturas para cerrar facturación con Adriana',
  NULL,
  'pending', 'medium', 7, 2, 1
);

INSERT INTO task (title, description, status, priority, category_id, created_by, assigned_to)
VALUES (
  'Solicitar factura de la presidencia',
  NULL,
  'pending', 'medium', 7, 2, 1
);

COMMIT;
