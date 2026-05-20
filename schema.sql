PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS appointment_services;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS beauty_services;
DROP TABLE IF EXISTS clients;

CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL
);

CREATE INDEX idx_clients_email ON clients(email);

CREATE TABLE beauty_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255) NULL,
    duration INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'solicitado', -- solicitado, confirmado, cancelado, concluido
    notes VARCHAR(500) NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

-- Índices para otimização de consultas da agenda e filtros por data
CREATE INDEX idx_appointments_client_id ON appointments(client_id);
CREATE INDEX idx_appointments_start_time ON appointments(start_time);

CREATE TABLE appointment_services (
    appointment_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pendente', -- pendente, em_andamento, concluido, cancelado
    price_at_booking DECIMAL(10, 2) NOT NULL, -- Preço praticado no ato da reserva (snapshot)
    duration_at_booking INTEGER NOT NULL, -- Duração do serviço no ato da reserva (snapshot)
    PRIMARY KEY (appointment_id, service_id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES beauty_services(id) ON DELETE CASCADE
);

-- Dados Seed 
INSERT INTO beauty_services (name, description, duration, price) VALUES 
('Corte Feminino', 'Lavagem, corte de pontas ou franja, modelagem e secagem simples.', 45, 80.00),
('Corte Masculino', 'Lavagem e corte clássico ou degradê com máquina/tesoura.', 30, 50.00),
('Manicure', 'Corte, lixamento, remoção de cutículas e esmaltação simples.', 40, 40.00),
('Pedicure', 'Corte, lixamento, cuidados com os pés e esmaltação simples.', 50, 45.00),
('Escova Progressiva', 'Alinhamento térmico capilar de alta performance com lavagem especial.', 120, 250.00),
('Hidratação Loreal', 'Nutrição profunda e selamento de cutículas capilares.', 60, 120.00);

-- Inserção de clientes fictícios para testes operacionais
INSERT INTO clients (name, email, phone) VALUES
('Maria Silva', 'maria.silva@email.com', '(11) 98888-7777'),
('João Santos', 'joao.santos@email.com', '(11) 97777-6666'),
('Ana Oliveira', 'ana.oliveira@email.com', '(21) 96666-5555');
