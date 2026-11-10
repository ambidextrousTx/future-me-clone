// frontend/src/app.js
import { createEditor } from "./editor.js";

const editor = createEditor("#editor");

document.querySelector("#show-html").addEventListener("click", () => {
  document.querySelector("#html-output").textContent = editor.getHtml();
});
