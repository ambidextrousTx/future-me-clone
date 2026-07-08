CREATE TABLE email (
  id SERIAL PRIMARY KEY,
  recipient_email TEXT,
  subject TEXT,
  body_html TEXT,
  send_date TIMESTAMPTZ,
  status TEXT CHECK (status in 'pending', 'sent', 'failed'),
  created_at TIMESTAMPTZ
  sent_at TIMESTAMPTZ nullable,
  send_attempts INT,
  last_error TEXT
)
