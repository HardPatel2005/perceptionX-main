document.addEventListener("DOMContentLoaded", function () {
  const icon = document.querySelector(".scroll-icon");
  const body = document.body;
  const toggle = document.querySelectorAll(".light-theme");
  const toggleShadow = document.querySelectorAll(".light-theme-shadow");
  const heading = document.querySelector(".light-theme-h1");
  const buttons = document.querySelectorAll(".button-light");
  const themeToggle = document.getElementById("theme");

  // Hide scroll icon on scroll
  if (icon) {
    window.addEventListener("scroll", function () {
      if (window.scrollY > 0) {
        icon.classList.add("hidden");
      }
    });
  }

  // Set default theme on load
  if (themeToggle) {
    themeToggle.checked = false;
    themeToggle.dispatchEvent(new Event("change"));

    themeToggle.addEventListener("change", function () {
      if (!themeToggle.checked) {
        body.classList.add("light-theme");
        body.classList.remove("dark-theme");

        toggle.forEach((t) => t.classList.replace("dark-theme", "light-theme"));
        toggleShadow.forEach((t) =>
          t.classList.replace("dark-theme-shadow", "light-theme-shadow")
        );

        body.classList.replace("dark-theme-shadow", "light-theme-shadow");
        if (heading)
          heading.classList.replace("dark-theme-h1", "light-theme-h1");

        buttons.forEach((btn) =>
          btn.classList.replace("button-dark", "button-light")
        );
      } else {
        body.classList.add("dark-theme");
        body.classList.remove("light-theme");

        toggle.forEach((t) => t.classList.replace("light-theme", "dark-theme"));
        toggleShadow.forEach((t) =>
          t.classList.replace("light-theme-shadow", "dark-theme-shadow")
        );

        body.classList.replace("light-theme-shadow", "dark-theme-shadow");
        if (heading)
          heading.classList.replace("light-theme-h1", "dark-theme-h1");

        buttons.forEach((btn) =>
          btn.classList.replace("button-light", "button-dark")
        );
      }
    });
  }
});

async function getFileDisplayHTML(fileUrl) {
  try {
    const response = await fetch(fileUrl, { method: "HEAD" });
    const contentType = response.headers.get("Content-Type");

    if (!contentType) return `<p>Error loading file.</p>`;

    if (contentType.startsWith("video")) {
      return `<video controls style="max-width: 100%" loop autoplay>
                <source src="${fileUrl}" type="${contentType}">
              </video>`;
    } else if (contentType.startsWith("image")) {
      return `<img src="${fileUrl}" style="max-width: 100%">`;
    } else if (contentType.startsWith("application/json")) {
      const jsonResponse = await fetch(fileUrl);
      const jsonData = await jsonResponse.json();
      return `<pre>${JSON.stringify(jsonData, null, 2)}</pre>`;
    } else {
      return `<p>Unsupported file type: ${contentType}</p>`;
    }

  } catch (err) {
    return `<p>Error: ${err.message}</p>`;
  }
}

document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("fileInput");
  if (!fileInput.files.length) {
    alert("Please select a file.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    document.getElementById("progressBar-div").style.display = "block";
    document.getElementById("upload-form").style.display = "none";

    const response = await fetch("/process", {
      method: "POST",
      body: formData,
    });

    const contentType = response.headers.get("Content-Type");
    console.log("📦 Content-Type received:", contentType);

    if (contentType.includes("text/html")) {
      throw new Error("HTML response received from /process. Detection server may be down or misconfigured.");
    }

    const data = await response.json();

    if (response.ok) {
      const fileId = data.filename;
      document.getElementById("output-div").style.display = "block";
      displayFilesFromServer(fileId);
    } else {
      const errorMsg = data?.error || "Failed to process the file.";
      document.getElementById("output").innerHTML = `<p>${errorMsg}</p>`;
    }
  } catch (err) {
    console.error("Error:", err);
    document.getElementById("output").innerHTML = `<p>Error: ${err.message}</p>`;
  }
});

async function displayFilesFromServer(filename) {
  const uploadedUrl = `/file/${filename}`;

  const uploadedHTML = await getFileDisplayHTML(uploadedUrl);

  document.getElementById("output").innerHTML = `
    <div class="uploads">
        <h4>Uploaded File:</h4>
        ${uploadedHTML}
    </div>
    <button onclick="window.location.reload()">Try Another File</button>
  `;
}
