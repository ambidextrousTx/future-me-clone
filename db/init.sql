CREATE TABLE emails (
  id                    SERIAL PRIMARY KEY,
  recipient_email       TEXT NOT NULL,
  subject               TEXT NOT NULL,
  body_html             TEXT NOT NULL,
  send_date             TIMESTAMPTZ NOT NULL,
  status                TEXT NOT NULL DEFAULT 'pending' 
                        CHECK (status in ('pending', 'sent', 'failed')),
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  sent_at               TIMESTAMPTZ,
  send_attempts         INT NOT NULL DEFAULT 0,
  last_error            TEXT
);

CREATE INDEX idx_emails_pending_due
  ON emails (status, send_date)
  WHERE status = 'pending';
