// frontend/src/app.js
import { createEditor } from "./editor.js";

const API_URL = "http://localhost:8000";
const editor = createEditor("#editor");
const form = document.querySelector('#email-form');
const message = document.querySelector('#message');

function describeError(body) {
  // FastAPI validation errors: {"detail": [{"loc": ["body", "send_date"], "msg": "..."}]}
  if (Array.isArray(body.detail)) {
    return body.detail
      .map((d) => `${d.loc.slice(1).join(".")}: ${d.msg}`)
      .join("\n");
  }
  return "Something went wrong.";
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  if (editor.isEmpty()) {
    message.textContent = "Write something in the body first.";
    return;
  }

  const data = Object.fromEntries(new FormData(form));
  const payload = {
    ...data,
    body_html: editor.getHtml(),
    // datetime-local gives "2027-03-15T09:00" (no timezone). Interpreting it
    // as local time and converting to UTC gives the ISO string with an
    // explicit zone that our API's validator requires.
    send_date: new Date(data.send_date).toISOString(),
  }

  try {
    const response = await fetch(`${API_URL}/emails`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      message.textContent = "Scheduled!";
      form.reset();
      editor.clear();
    } else {
      message.textContent = describeError(await response.json());
    }
  } catch (err) {
    message.textContent = "Could not reach the server.";
  }

})
