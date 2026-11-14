// frontend/src/editor.js — the only file that knows Quill exists
export function createEditor(selector) {
  const quill = new Quill(selector, {
    theme: "snow",
    placeholder: "Dear Future Me ...",
    modules: {
      toolbar: [
        ["bold", "italic", "underline"],
        [{ list: "ordered" }, { list: "bullet" }],
        ["link"],
        ["clean"],
      ],
    },
  });

  return {
    // Clean <ul>/<ol>/<p> output, but Quill turns every space into &nbsp;,
    // which would stop paragraphs from wrapping. Normalize them back.
    getHtml: () => quill.getSemanticHTML().replaceAll("&nbsp;", " "),
    isEmpty: () => quill.getText().trim().length === 0,
    clear: () => quill.setText("")
  };
}
